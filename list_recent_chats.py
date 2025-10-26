import asyncio
from datetime import datetime, timezone, timedelta

from telethon import TelegramClient
from telethon.sessions import StringSession

import config

# how far back to look (last week)
CUTOFF = datetime.now(timezone.utc) - timedelta(days=7)

async def list_recent_chats():
    # Use StringSession if SESSION_STRING is set, otherwise use file-based session
    if config.SESSION_STRING:
        client = TelegramClient(StringSession(config.SESSION_STRING), config.API_ID, config.API_HASH)
    else:
        client = TelegramClient('parse_session', config.API_ID, config.API_HASH)
    
    async with client:
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
