# Voice Message Summary Bot

A Telegram userbot that transcribes voice messages and summarizes them into bullet points using Groq (Whisper STT + LLM).

## Modes

The bot runs both modes simultaneously.

### Auto Mode

Monitors a source chat for new voice messages and automatically sends a summary to a destination chat. Optionally forwards the original voice message alongside the summary.

**Required env vars:**
- `VOICE_SOURCE_CHAT_ID` — chat to watch for voice messages
- `VOICE_DESTINATION_CHAT_ID` — chat to send summaries to

**Optional:**
- `AUTO_PROCESS=False` — disable auto mode entirely
- `FORWARD_VOICE_MESSAGE=False` — don't forward the original voice message

### Command Mode

In any chat where the account is a member, reply to a voice message with `stt` to get it transcribed and summarized in that same chat.

By default any user can trigger the command. Set `ALLOWED_USER_IDS` to restrict it to specific users.

**Optional:**
- `ALLOWED_USER_IDS` — comma-separated Telegram user IDs allowed to use the command. If not set, all users can use it.

## Setup

1. Copy `env` to `.env` and fill in the required values.
2. Run `python auth.py` once to generate a session string (for Heroku) or session file (for local).
3. Start the bot: `python voice_transcriber.py`

See `HEROKU_DEPLOYMENT.md` for deployment instructions.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key |
| `API_ID` | Yes | Telegram API ID |
| `API_HASH` | Yes | Telegram API hash |
| `SESSION_STRING` | Heroku | Telegram session string (falls back to session file) |
| `VOICE_SOURCE_CHAT_ID` | Auto mode | Source chat ID |
| `VOICE_DESTINATION_CHAT_ID` | Auto mode | Destination chat ID |
| `ALLOWED_USER_IDS` | No | Comma-separated user IDs for command mode whitelist |
| `AUTO_PROCESS` | No | Set to `False` to disable auto mode (default: `True`) |
| `FORWARD_VOICE_MESSAGE` | No | Set to `False` to skip forwarding original message (default: `True`) |
