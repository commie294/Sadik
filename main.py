import asyncio
import os
import sys
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import MemorySession

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
source_channel = os.getenv('SOURCE_CHANNEL')
target_channel = os.getenv('TARGET_CHANNEL')

if not all([api_id, api_hash, bot_token, source_channel, target_channel]):
    print("Ошибка: Пожалуйста, заполните все необходимые переменные окружения в файле .env")
    sys.exit(1)

client = TelegramClient(MemorySession(), int(api_id), api_hash).start(bot_token=bot_token)

async def main():
    try:
        await client.connect()
        print("Бот запущен и ожидает новые сообщения...")

        @client.on(events.NewMessage(chats=int(source_channel)))
        async def repost(event):
            try:
                await client.send_message(
                    entity=int(target_channel),
                    message=event.message.text,
                    file=event.message.media if event.message.media else None,
                    link_preview=False
                )
                print(f"Переслано сообщение из {source_channel} в {target_channel}: {event.message.text[:50]}...")
            except Exception as e:
                print(f"Произошла ошибка при пересылке сообщения: {e}")

        await client.run_until_disconnected()

    except Exception as e:
        print(f"Произошла ошибка на верхнем уровне: {e}")
    finally:
        if client.is_connected():
            await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
