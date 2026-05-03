import os
from dotenv import load_dotenv

load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_STT_MODEL = "whisper-large-v3-turbo"

# Telegram Configuration
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = "voice_transcriber_session"
SESSION_STRING = os.getenv("SESSION_STRING")  # For Heroku deployment (optional, falls back to session file)

# Chat pairs for AUTO MODE
# Comma-separated list of source:destination chat ID pairs
# Example: CHAT_PAIRS=-1001234567890:-1009876543210,-1001111111111:-1002222222222
_chat_pairs_raw = os.getenv("CHAT_PAIRS", "")
CHAT_PAIRS = {}
if _chat_pairs_raw:
    for pair in _chat_pairs_raw.split(","):
        pair = pair.strip()
        if ":" in pair:
            src, dst = pair.split(":", 1)
            CHAT_PAIRS[int(src.strip())] = int(dst.strip())

# Processing Mode Configuration
# The bot now supports BOTH modes simultaneously:
# 1. AUTO MODE: Automatically processes voice messages from source chats and forwards to destination chats
# 2. COMMAND MODE: In ANY chat, reply "stt" or "Stt" to a voice message to process it in that chat
AUTO_PROCESS = True  # Set to False to disable automatic processing of source chats
TRANSCRIBE_COMMAND = "stt"  # Command to trigger transcription (case-insensitive)

# Command Mode Whitelist
# Comma-separated list of Telegram user IDs allowed to use the transcribe command
# If not set, all users can use the command.
# Example: ALLOWED_USER_IDS=123456789,987654321
ALLOWED_USER_IDS = os.getenv("ALLOWED_USER_IDS", "")

# Parse allowed user IDs into a set for efficient lookup
# None means no restriction (everyone allowed); a set means only listed users are allowed
if ALLOWED_USER_IDS:
    ALLOWED_USERS = set(uid.strip() for uid in ALLOWED_USER_IDS.split(",") if uid.strip())
else:
    ALLOWED_USERS = None  # None = no restriction, all users allowed

# Forward Original Voice Message (only applies to AUTO MODE)
# Set FORWARD_VOICE_MESSAGE=true in environment to enable forwarding the original voice message
FORWARD_VOICE_MESSAGE = os.getenv("FORWARD_VOICE_MESSAGE", "false").lower() == "true"
