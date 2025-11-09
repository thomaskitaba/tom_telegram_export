#!/usr/bin/python3
import os
import asyncio
import argparse
import sys
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

# replace with your own values from my.telegram.org
api_id = 38468061
api_hash = '2a9d1bc0fbc68f726e084d86ca59f25b'
client = TelegramClient('telegram_backup', api_id, api_hash)


async def main():
    parser = argparse.ArgumentParser(description='Export Telegram chats/messages to files')
    parser.add_argument('-c', '--chat', help='Chat name (substring). If omitted or empty, export all', default=None)
    parser.add_argument('--max-messages', type=int, default=0, help='Limit number of messages to export per chat (0 = no limit)')
    args = parser.parse_args()

    chat_query = args.chat
    max_messages = args.max_messages or None

    if chat_query is None:
        try:
            chat_query = input('Enter chat name (leave empty to export all): ').strip()
        except EOFError:
            chat_query = ''

    interactive = sys.stdin.isatty()

    def prompt_yes_no(question: str, default: bool = False) -> bool:
        if not interactive:
            return True
        default_str = 'Y/n' if default else 'y/N'
        while True:
            try:
                resp = input(f"{question} [{default_str}] ").strip().lower()
            except EOFError:
                return default
            if resp == '':
                return bool(default)
            if resp in ('y', 'yes'):
                return True
            if resp in ('n', 'no'):
                return False
            print("Please answer 'y' or 'n'.")

    await client.start(phone='+251986689373')

    base_dir = 'telegram_exports'
    os.makedirs(base_dir, exist_ok=True)

    async for dialog in client.iter_dialogs():
        chat_name = getattr(dialog, 'name', None)
        if not chat_name:
            ent = getattr(dialog, 'entity', None)
            chat_name = getattr(ent, 'title', None) or getattr(ent, 'first_name', None) or str(dialog.id)
        chat_name = str(chat_name).replace('/', '_')

        if chat_query:
            if chat_query.lower() not in chat_name.lower():
                continue
        else:
            if interactive:
                ok = prompt_yes_no(f"Export chat '{chat_name}'?")
                if not ok:
                    continue

        chat_dir = os.path.join(base_dir, chat_name)
        os.makedirs(chat_dir, exist_ok=True)

        messages_file = os.path.join(chat_dir, 'messages.txt')
        files_dir = os.path.join(chat_dir, 'files')
        os.makedirs(files_dir, exist_ok=True)

        print(f"Exporting {chat_name}...")

        sender_cache = {}
        with open(messages_file, 'w', encoding='utf-8') as f:
            async for message in client.iter_messages(dialog.id, limit=max_messages):
                sender_name = 'System'
                sid = getattr(message, 'sender_id', None)
                if sid:
                    if sid in sender_cache:
                        sender_name = sender_cache[sid]
                    else:
                        try:
                            sender = await message.get_sender()
                        except Exception:
                            sender = None
                        if sender is not None:
                            uname = getattr(sender, 'username', None)
                            if uname:
                                name = f"@{uname}"
                            else:
                                first = getattr(sender, 'first_name', '') or ''
                                last = getattr(sender, 'last_name', '') or ''
                                name = (first + (' ' + last if last else '')).strip() or str(sid)
                            sender_cache[sid] = name
                            sender_name = name
                        else:
                            sender_name = str(sid)

                text = getattr(message, 'text', None) or getattr(message, 'message', '') or ''

                # Export files (skip videos)
                if message.media:
                    if isinstance(message.media, MessageMediaDocument):
                        mime_type = getattr(message.media.document, 'mime_type', '')
                        if not mime_type.startswith('video/'):
                            try:
                                file_path = await client.download_media(message, file=files_dir)
                                text += f" [File: {os.path.basename(file_path)}]"
                            except Exception as e:
                                text += f" [File download failed: {e}]"
                    elif isinstance(message.media, MessageMediaPhoto):
                        try:
                            file_path = await client.download_media(message, file=files_dir)
                            text += f" [Photo: {os.path.basename(file_path)}]"
                        except Exception as e:
                            text += f" [Photo download failed: {e}]"

                if not str(text).strip():
                    continue

                try:
                    dt = message.date.astimezone()
                    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S %Z')
                except Exception:
                    dt_str = str(message.date)

                line = f"[{dt_str}] {sender_name}: {text}\n"
                f.write(line)

    print("All chats exported successfully!")


if __name__ == '__main__':
    asyncio.run(main())
