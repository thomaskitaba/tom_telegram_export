# Telegram Chat Exporter

> A minimal script that exports Telegram chat messages (text only) to plain text files using Telethon.

## Overview

This utility connects to your Telegram account with Telethon and exports textual messages from chats into `telegram_exports/<ChatName>/messages.txt` files. It does not download media (audio, video, images) — captions and emojis are preserved.

Key features:
- Exports messages only (no media downloads)
- Human-readable local timestamps
- Resolves and caches sender names (uses `@username` or full name)
- Interactive per-chat confirmation when exporting all chats (y/n/exit)
- CLI option to filter by chat substring and limit messages

## Prerequisites

- Python 3.8 or newer
- Telethon

Install Telethon (user install):

```bash
python3 -m pip install --user telethon
```

Or with a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install telethon
```

## Files

- `telegram_chat_export.py` — main script
- `telegram_backup.session` — created after initial login (Telethon session)
- `telegram_exports/` — output folder created by the script
 - `.env` — (optional) file with TELEGRAM_API_ID and TELEGRAM_API_HASH; the script will load credentials from this file if present

## Usage

Run the script from the project folder:

```bash
python3 ./telegram_chat_export.py
```

The script will prompt:
- Enter a chat name substring to export only matching chats (case-insensitive), or
- Leave empty (press Enter) to export all; when exporting all you will be asked per chat:
  - `y` / `yes` — export this chat
  - `n` / `no`  — skip this chat and continue
  - `exit` / `quit` — stop exporting immediately and exit cleanly
  - Press Enter defaults to No

On first run you will be prompted for the Telegram login code sent to your account (and possibly 2FA). The session is stored in `telegram_backup.session`.

### CLI options

```text
-c, --chat        Chat name substring to filter (case-insensitive). If omitted, you can leave the prompt empty to export all.
--max-messages    Limit number of messages to export per chat (0 = no limit).
```

Examples:

Export a specific chat (substring match):

```bash
python3 ./telegram_chat_export.py -c "MyGroup"
```

Export all chats (interactive per-chat confirmation):

```bash
python3 ./telegram_chat_export.py
```

Export only the first 200 messages of a chat:

```bash
python3 ./telegram_chat_export.py -c "MyGroup" --max-messages 200
```

## Output format

Each `messages.txt` contains lines like:

```
[2025-11-09 14:23:01 EAT] @username: Hello 😊
[2025-11-08 09:10:05 EAT] John Doe: Here's the link — check it out
```

- Timestamps are in local timezone.
- Sender is `@username` when available, otherwise full name or numeric id.
- Emojis and non-ASCII characters are preserved (UTF-8 encoding).

## Behavior

- Pure-media messages with no caption/text are skipped to avoid empty lines.
- Non-interactive runs (stdin not a TTY) export all matching chats without per-chat prompts.
- Typing `exit` during per-chat prompts stops the run and disconnects cleanly.

## Troubleshooting

- `ImportError: telethon` — install Telethon as shown above.
- If exports are slow, use `--max-messages` to benchmark or only export messages (no media downloads by design).
- To re-login, remove `telegram_backup.session` and re-run.

## Next steps / enhancements

- Add `--yes` / `--no-prompt` flag to skip per-chat confirmation.
- Add CSV/JSON export option for data analysis.
- Add a `requirements.txt` if you want to pin versions.

---

If you'd like, I can also add a `requirements.txt` containing `telethon`.
