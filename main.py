import asyncio
import os
import sys
from dotenv import load_dotenv
from telethon import TelegramClient, events

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значений переменных окружения
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# Получение значений каналов из переменных окружения
source_channel = os.getenv('SOURCE_CHANNEL')
target_channel = os.getenv('TARGET_CHANNEL')

# Проверка наличия необходимых переменных окружения
if not all([api_id, api_hash, bot_token, source_channel, target_channel]):
    print("Ошибка: Пожалуйста, заполните все необходимые переменные окружения в файле .env")
    sys.exit(1)

# Создаем клиент Telegram
client = TelegramClient('bot_session', int(api_id), api_hash).start(bot_token=bot_token)

async def main():
    @client.on(events.NewMessage(chats=source_channel))
    async def repost(event):
        """Пересылает новые сообщения из исходного канала в целевой."""
        try:
            await client.send_message(
                entity=target_channel,
                message=event.message.text,
                file=event.message.media if event.message.media else None,
                link_preview=False
            )
            print(f"Переслано сообщение из {source_channel} в {target_channel}: {event.message.text[:50]}...")
        except Exception as e:
            print(f"Ошибка при пересылке сообщения: {e}")

    print("Бот запущен и ожидает новые сообщения...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
