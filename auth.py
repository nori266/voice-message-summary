"""
Authentication script for voice_transcriber.py
Run this once to authenticate and create the session file.
"""
import os

from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = "voice_transcriber_session"

print(f"Authenticating for session: {session_name}")
print("Please enter your phone number, code, and password when prompted.")

with TelegramClient(session_name, api_id, api_hash) as client:
    print(f"\n✅ Authentication successful!")
    print(f"Session file created: {session_name}.session")
    print("You can now run voice_transcriber.py with Streamlit.")
