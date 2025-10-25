"""
Authentication script for voice_transcriber.py
Run this once to authenticate and create the session file.
"""
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = "voice_transcriber_session"

print(f"Authenticating for session: {session_name}")
print("Please enter your phone number, code, and password when prompted.")

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print(f"\n✅ Authentication successful!")
    print(f"Session file created: {session_name}.session")
    
    # Save session string for Heroku deployment
    session_string = client.session.save()
    
    # Also save to file for local development
    client.session.save(session_name)
    
    print("\n" + "="*70)
    print("🔐 SESSION STRING FOR HEROKU:")
    print("="*70)
    print(session_string)
    print("="*70)
    print("\n📝 DEPLOYMENT INSTRUCTIONS:")
    print("1. Copy the session string above")
    print("2. Set it as a Heroku config var:")
    print(f"   heroku config:set SESSION_STRING=\"{session_string[:20]}...\"")
    print("\n💻 Local development: The session file has been saved for local use.")
    print("You can now run voice_transcriber.py")
