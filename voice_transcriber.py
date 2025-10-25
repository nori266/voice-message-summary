import asyncio
import datetime
import logging
import os
import sys

import requests
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

# Track processed messages to avoid duplicates
processed_messages = set()
start_time = datetime.datetime.now(datetime.timezone.utc)


async def transcribe_audio(audio_file_path):
    """Transcribe audio file using Groq STT model."""
    try:
        headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}"}
        
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "file": (os.path.basename(audio_file_path), audio_file, "audio/ogg"),
                "model": (None, config.GROQ_STT_MODEL),
                "response_format": (None, "text")
            }
            response = requests.post(
                f"{config.GROQ_BASE_URL}/audio/transcriptions",
                headers=headers,
                files=files,
                timeout=120
            )
            response.raise_for_status()
            return response.text
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return None


async def summarize_text(text):
    """Summarize text to bullet-point list using Groq LLM."""
    prompt = f"""Summarize the following text into a clear, concise bullet-point list. The summary should be in the same language as the original text. Focus on the key points and main ideas:

{text}

Provide the summary as a bullet-point list."""
    
    try:
        headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": config.GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }
        response = requests.post(
            f"{config.GROQ_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
            timeout=120
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        return None


async def process_voice_message(client, voice_msg):
    """Process a voice message: transcribe, summarize, and send to destination."""
    try:
        # Check if already processed
        if voice_msg.id in processed_messages:
            logger.info(f"Message {voice_msg.id} already processed, skipping")
            return
        
        # Download voice message
        audio_path = f"temp_voice_{voice_msg.id}.ogg"
        await voice_msg.download_media(file=audio_path)
        
        logger.info(f"📥 Downloaded voice message {voice_msg.id}")
        
        # Transcribe
        transcription = await transcribe_audio(audio_path)
        if not transcription:
            logger.error(f"Failed to transcribe voice message {voice_msg.id}")
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return
        
        logger.info(f"✍️ Transcribed: {transcription[:100]}...")
        
        # Summarize
        summary = await summarize_text(transcription)
        if not summary:
            logger.error(f"Failed to summarize transcription for message {voice_msg.id}")
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return
        
        logger.info(f"📝 Summary created")
        
        # Send summary and voice message to destination chat
        await client.send_message(
            config.DESTINATION_CHAT_ID,
            f"🎤 **Voice Message Summary:**\n\n{summary}"
        )
        
        # Forward the original voice message (if configured)
        if config.FORWARD_VOICE_MESSAGE:
            await client.forward_messages(
                config.DESTINATION_CHAT_ID,
                voice_msg
            )
        
        logger.info(f"✅ Processed and sent voice message {voice_msg.id}")
        
        # Clean up temporary file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        # Mark as processed
        processed_messages.add(voice_msg.id)
        
    except Exception as e:
        logger.error(f"Error processing voice message: {e}", exc_info=True)
        if 'audio_path' in locals() and os.path.exists(audio_path):
            os.remove(audio_path)


async def main():
    """Main function to run the voice transcriber bot."""
    logger.info("🚀 Starting Voice Transcriber Bot...")
    logger.info(f"📅 Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info(f"📊 Mode: {'AUTO' if config.AUTO_PROCESS else 'COMMAND'}")
    logger.info(f"📱 Source Chat: {config.SOURCE_CHAT_ID}")
    logger.info(f"📤 Destination Chat: {config.DESTINATION_CHAT_ID}")
    
    # Initialize Telegram client
    # Use StringSession if SESSION_STRING is set (for Heroku), otherwise use file-based session
    if config.SESSION_STRING:
        logger.info("🔐 Using session string from environment variable")
        client = TelegramClient(StringSession(config.SESSION_STRING), config.API_ID, config.API_HASH)
    else:
        logger.info("📁 Using session file")
        client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)
    
    await client.start()
    logger.info("✅ Connected to Telegram")
    
    if config.AUTO_PROCESS:
        # AUTO MODE: Process new voice messages automatically
        logger.info("🤖 AUTO MODE: Will process voice messages automatically")
        
        @client.on(events.NewMessage(chats=config.SOURCE_CHAT_ID))
        async def handle_new_message(event):
            """Handle new messages in the source chat."""
            if event.message.voice and event.message.date > start_time:
                logger.info(f"🎤 New voice message detected: {event.message.id}")
                await process_voice_message(client, event.message)
        
        logger.info("👂 Listening for voice messages...")
        
    else:
        # COMMAND MODE: Wait for transcribe command
        logger.info(f"⌨️ COMMAND MODE: Waiting for '{config.TRANSCRIBE_COMMAND}' command")
        
        @client.on(events.NewMessage(chats=config.DESTINATION_CHAT_ID))
        async def handle_command(event):
            """Handle transcribe command in destination chat."""
            if event.message.message and event.message.message.lower().strip() == config.TRANSCRIBE_COMMAND:
                logger.info(f"🎯 Transcribe command received!")
                
                # Find and process unprocessed voice messages
                voice_messages_found = False
                async for msg in client.iter_messages(config.SOURCE_CHAT_ID, limit=20):
                    if msg.voice and msg.date > start_time and msg.id not in processed_messages:
                        await process_voice_message(client, msg)
                        voice_messages_found = True
                
                if not voice_messages_found:
                    await client.send_message(
                        config.DESTINATION_CHAT_ID,
                        "No new voice messages to process."
                    )
                    logger.info("No unprocessed voice messages found")
        
        logger.info(f"👂 Listening for '{config.TRANSCRIBE_COMMAND}' command...")
    
    # Keep the bot running
    logger.info("✅ Bot is now running. Press Ctrl+C to stop.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
