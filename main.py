import telebot
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
source_channel_id = os.getenv('SOURCE_CHANNEL')
target_channel_id = os.getenv('TARGET_CHANNEL')

if not bot_token or not source_channel_id or not target_channel_id:
    print("Пожалуйста, заполните BOT_TOKEN, SOURCE_CHANNEL и TARGET_CHANNEL в файле .env")
    exit(1)

try:
    source_channel_id = int(source_channel_id)
    target_channel_id = int(target_channel_id)
except ValueError:
    print("Ошибка: SOURCE_CHANNEL и TARGET_CHANNEL должны быть целыми числами.")
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
        elif message.audio:
            sent_msg = bot.send_audio(target_channel_id, message.audio.file_id, caption=message.caption)
        elif message.voice:
            sent_msg = bot.send_voice(target_channel_id, message.voice.file_id, caption=message.caption)
        elif message.sticker:
            sent_msg = bot.send_sticker(target_channel_id, message.sticker.file_id)
        elif message.animation:
            sent_msg = bot.send_animation(target_channel_id, message.animation.file_id, caption=message.caption)
        elif message.contact:
            sent_msg = bot.send_contact(target_channel_id, message.contact.phone_number, message.contact.first_name, last_name=message.contact.last_name)
        elif message.location:
            sent_msg = bot.send_location(target_channel_id, message.location.latitude, message.location.longitude)
        elif message.poll:
            sent_msg = bot.send_poll(target_channel_id, message.poll.question, [option.text for option in message.poll.options], is_anonymous=message.poll.is_anonymous, type=message.poll.type, allows_multiple_answers=message.poll.allows_multiple_answers)
        elif message.venue:
            sent_msg = bot.send_venue(target_channel_id, message.venue.latitude, message.venue.longitude, message.venue.title, message.venue.address)
        elif message.game:
            # Обработка game требует дополнительных действий, так как это комплексный тип
            print("Пересылка сообщений типа 'game' не поддерживается.")
            return
        else:
            print("Неподдерживаемый тип сообщения")
            return

        print(f"Успешно переслано сообщение ID {message.message_id}")

    except Exception as e:
        print(f"Ошибка при пересылке: {e}")

if __name__ == '__main__':
    print("Бот запущен и ожидает сообщения...")
    bot.polling(none_stop=True)
