import os
from dotenv import load_dotenv

load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "moonshotai/kimi-k2-instruct"
GROQ_STT_MODEL = "whisper-large-v3-turbo"

# Telegram Configuration
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = "voice_transcriber_session"
SESSION_STRING = os.getenv("SESSION_STRING")  # For Heroku deployment (optional, falls back to session file)

# Chat IDs (to be configured)
SOURCE_CHAT_ID = os.getenv("VOICE_SOURCE_CHAT_ID", "0")  # Chat to monitor for voice messages
DESTINATION_CHAT_ID = os.getenv("VOICE_DESTINATION_CHAT_ID", "0")  # Chat to send summaries to

# Processing Mode Configuration
AUTO_PROCESS = True
TRANSCRIBE_COMMAND = "stt"  # Command to trigger transcription (used when AUTO_PROCESS=False)

# Forward Original Voice Message
FORWARD_VOICE_MESSAGE = False  # Whether to forward the original voice message to destination chat
