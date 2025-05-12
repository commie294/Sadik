import telebot
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
source_channel_id = int(os.getenv('SOURCE_CHANNEL'))  # Конвертируем в число
target_channel_id = int(os.getenv('TARGET_CHANNEL')) # Конвертируем в число

if not bot_token or not source_channel_id or not target_channel_id:
    print("Пожалуйста, заполните BOT_TOKEN, SOURCE_CHANNEL и TARGET_CHANNEL в файле .env")
    exit(1)

bot = telebot.TeleBot(bot_token)

@bot.channel_post_handler(chat_id=[source_channel_id])
def repost_message(message):
    print(f"Получено новое сообщение в канале {source_channel_id}: {message.text[:50] if message.text else message.caption[:50] if message.caption else 'Медиа'}")
    try:
        if message.text:
            sent_msg = bot.send_message(target_channel_id, message.text)
        elif message.photo:
            sent_msg = bot.send_photo(target_channel_id, message.photo[-1].file_id, caption=message.caption)
        elif message.video:
            sent_msg = bot.send_video(target_channel_id, message.video.file_id, caption=message.caption)
        elif message.document:
            sent_msg = bot.send_document(target_channel_id, message.document.file_id, caption=message.caption)
        else:
            print("Неподдерживаемый тип сообщения")
            return

        print(f"Успешно переслано сообщение ID {message.message_id}")
        
    except Exception as e:
        print(f"Ошибка при пересылке: {e}")

if name == 'main':
    print("Бот запущен и ожидает сообщения...")
    bot.polling(none_stop=True)
