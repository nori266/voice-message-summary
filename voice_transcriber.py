import asyncio
import os

import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh
from telethon import TelegramClient

import config

load_dotenv()

# Auto-refresh every 10 seconds
st_autorefresh(interval=10 * 1000, key="voice-transcriber-refresh")
st.write("🎤 Voice Transcriber daemon is running...")

# Track processed voice messages to avoid re-processing
processed_messages = set()


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
        st.error(f"Transcription error: {e}")
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
        response = requests.post(f"{config.GROQ_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Summarization error: {e}")
        return None


async def process_voice_message(client, voice_msg):
    """Process a voice message: transcribe, summarize, and send to destination."""
    try:
        # Download voice message
        audio_path = f"temp_voice_{voice_msg.id}.ogg"
        await voice_msg.download_media(file=audio_path)
        
        st.write(f"📥 Downloaded voice message {voice_msg.id}")
        
        # Transcribe
        transcription = await transcribe_audio(audio_path)
        if not transcription:
            st.error(f"Failed to transcribe voice message {voice_msg.id}")
            os.remove(audio_path)
            return
        
        st.write(f"✍️ Transcribed: {transcription[:100]}...")
        
        # Summarize
        summary = await summarize_text(transcription)
        if not summary:
            st.error(f"Failed to summarize transcription for message {voice_msg.id}")
            os.remove(audio_path)
            return
        
        st.write(f"📝 Summary created")
        
        # Send summary and voice message to destination chat
        await client.send_message(
            config.DESTINATION_CHAT_ID,
            f"🎤 **Voice Message Summary:**\n\n{summary}"
        )
        
        # Forward the original voice message
        await client.forward_messages(
            config.DESTINATION_CHAT_ID,
            voice_msg
        )
        
        st.success(f"✅ Processed and sent voice message {voice_msg.id}")
        
        # Clean up temporary file
        os.remove(audio_path)
        
        # Mark as processed
        processed_messages.add(voice_msg.id)
        
    except Exception as e:
        st.error(f"Error processing voice message: {e}")
        if os.path.exists(audio_path):
            os.remove(audio_path)


async def check_for_voice_messages():
    """Main function to check for voice messages and process them."""
    async with TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH) as client:
        
        if config.AUTO_PROCESS:
            # AUTO MODE: Process all new voice messages
            st.write(f"🤖 AUTO MODE: Processing all voice messages from chat {config.SOURCE_CHAT_ID}")
            
            # Get recent messages from source chat
            async for msg in client.iter_messages(config.SOURCE_CHAT_ID, limit=10):
                if msg.voice and msg.id not in processed_messages:
                    await process_voice_message(client, msg)
        
        else:
            # COMMAND MODE: Wait for transcribe command from destination chat
            st.write(f"⌨️ COMMAND MODE: Waiting for '{config.TRANSCRIBE_COMMAND}' command from chat {config.DESTINATION_CHAT_ID}")
            
            # Check for transcribe command in destination chat
            last_message = await client.get_messages(config.DESTINATION_CHAT_ID, limit=1)
            
            if last_message and last_message[0].message:
                command = last_message[0].message.lower().strip()
                
                if command == config.TRANSCRIBE_COMMAND:
                    st.write(f"🎯 Transcribe command received!")
                    
                    # Find unprocessed voice messages in source chat
                    voice_messages_found = False
                    async for msg in client.iter_messages(config.SOURCE_CHAT_ID, limit=20):
                        if msg.voice and msg.id not in processed_messages:
                            await process_voice_message(client, msg)
                            voice_messages_found = True
                    
                    if not voice_messages_found:
                        await client.send_message(
                            config.DESTINATION_CHAT_ID,
                            "No new voice messages to process."
                        )


try:
    asyncio.run(check_for_voice_messages())
except Exception as e:
    st.error(f"Error in voice transcriber: {e}")
