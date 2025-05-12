import telebot
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
source_channel_id = os.getenv('SOURCE_CHANNEL')
target_channel_id = os.getenv('TARGET_CHANNEL')

if not bot_token or not source_channel_id or not target_channel_id:
    print("Пожалуйста, заполните BOT_TOKEN, SOURCE_CHANNEL и TARGET_CHANNEL в файле .env")
    sys.exit(1)

bot = telebot.TeleBot(bot_token)

@bot.message_handler(chat_types=['channel'], func=lambda message: str(message.chat.id) == source_channel_id)
def repost_message(message):
    try:
        if message.text:
            bot.send_message(target_channel_id, message.text)
        elif message.photo:
            bot.send_photo(target_channel_id, message.photo[-1].file_id, caption=message.caption)
        elif message.video:
            bot.send_video(target_channel_id, message.video.file_id, caption=message.caption)
        # Добавьте обработку других типов медиа, если необходимо
        print(f"Переслано сообщение из {source_channel_id} в {target_channel_id}")
    except Exception as e:
        print(f"Ошибка при пересылке: {e}")

async def main():
    print("Бот запущен и ожидает сообщения...")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    asyncio.run(main())
