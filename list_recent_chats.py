import asyncio
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# how far back to look (e.g. today only)
CUTOFF = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

async def list_recent_chats():
    async with TelegramClient('parse_session', API_ID, API_HASH) as client:
        seen_chats = set()

        async for dialog in client.iter_dialogs():
            messages = await client.get_messages(dialog.id, limit=1)
            if messages and messages[0].date >= CUTOFF:
                name = dialog.name or "(no name)"
                username = getattr(dialog.entity, "username", None)
                identifier = f"@{username}" if username else dialog.id
                print(f"- {name} — {identifier}")
                seen_chats.add(identifier)

        if not seen_chats:
            print("No chats active today.")

asyncio.run(list_recent_chats())
