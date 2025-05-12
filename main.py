import asyncio
import os
import sys
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import MemorySession

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

if not all([api_id, api_hash, bot_token]):
    print("Ошибка: Пожалуйста, заполните API ID, API HASH и BOT TOKEN в файле .env")
    sys.exit(1)

client = TelegramClient(MemorySession(), int(api_id), api_hash).start(bot_token=bot_token)

async def main():
    try:
        await client.connect()
        print("Бот успешно подключен. Ожидаю...")
        await asyncio.sleep(30)  # Подождать 30 секунд
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
