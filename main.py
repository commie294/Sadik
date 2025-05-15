import telebot
import vk_api
import os
import logging
import signal
import sys
import requests
from dotenv import load_dotenv
from telebot.types import InputMediaPhoto
from io import BytesIO

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Обработчик сигналов
def signal_handler(sig, frame):
    print('Бот останавливается...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Загрузка переменных окружения
load_dotenv()

# Проверка переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN') or '7719604591:AAElNOS0FaSr6hcj2vMsZyGgFgg84573TuY'
SOURCE_CHANNEL = os.getenv('SOURCE_CHANNEL') or '-1002205252392'
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL') or '-1009876543210'
VK_TOKEN = os.getenv('VK_TOKEN') or 'c575ef7dc575ef7dc575ef7d0fc52ded9fcc575c575ef7da52735119770785cb5d70f6e'
VK_GROUP_ID = os.getenv('VK_GROUP_ID') or '-73354327'

if not all([BOT_TOKEN, SOURCE_CHANNEL, TARGET_CHANNEL]):
    logging.error("❌ Ошибка: Не заданы Telegram переменные (BOT_TOKEN, SOURCE_CHANNEL, TARGET_CHANNEL)")
    exit(1)

if not all([VK_TOKEN, VK_GROUP_ID]):
    logging.warning("⚠️ VK_TOKEN или VK_GROUP_ID не заданы, отправка в VK отключена")
    vk_session = None
else:
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        vk_upload = vk_api.VkUpload(vk_session)
        VK_GROUP_ID = int(VK_GROUP_ID)
        logging.info("✅ VK API успешно инициализирован")
    except Exception as e:
        logging.error(f"❌ Ошибка инициализации VK API: {str(e)}")
        vk_session = None

try:
    SOURCE_CHANNEL = int(SOURCE_CHANNEL)
    TARGET_CHANNEL = int(TARGET_CHANNEL)
except ValueError:
    logging.error("❌ Ошибка: SOURCE_CHANNEL и TARGET_CHANNEL должны быть числами")
    exit(1)

# Инициализация Telegram бота
try:
    bot = telebot.TeleBot(BOT_TOKEN)
    logging.info("✅ Telegram бот успешно инициализирован")
except Exception as e:
    logging.error(f"❌ Ошибка инициализации Telegram бота: {str(e)}")
    exit(1)

def upload_photo_to_vk(file_id):
    """Загрузка фото из Telegram на сервер VK"""
    try:
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        response = requests.get(file_url)
        if response.status_code != 200:
            raise Exception("Не удалось скачать фото")
        
        photo = BytesIO(response.content)
        photo.name = 'photo.jpg'
        upload_server = vk_upload.photos.getWallUploadServer(group_id=-VK_GROUP_ID)
        upload_response = requests.post(
            upload_server['upload_url'],
            files={'photo': photo}
        ).json()
        
        if 'photo' not in upload_response:
            raise Exception("Ошибка загрузки фото на VK")
        
        saved_photo = vk.photos.saveWallPhoto(
            group_id=-VK_GROUP_ID,
            photo=upload_response['photo'],
            server=upload_response['server'],
            hash=upload_response['hash']
        )[0]
        return f"photo{saved_photo['owner_id']}_{saved_photo['id']}"
    except Exception as e:
        logging.error(f"❌ Ошибка загрузки фото в VK: {str(e)}")
        return None

@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'sticker', 'animation', 'voice', 'audio', 'poll'])
def handle_message(message):
    try:
        # Игнорировать сообщения из целевого канала или других каналов
        if message.chat.id != SOURCE_CHANNEL:
            logging.info(f"ℹ️ Игнорировано сообщение из chat_id {message.chat.id}")
            return

        # Подготовка для VK
        vk_text = None
        vk_attachments = []
        # Обработка типов сообщений
        if message.text:
            # Текст
            bot.send_message(
                chat_id=TARGET_CHANNEL,
                text=message.text,
                parse_mode='Markdown'
            )
            vk_text = message.text
            logging.info(f"✅ Отправлено текстовое сообщение {message.message_id}")

        elif message.photo:
            # Альбом или фото
            media = [
                InputMediaPhoto(
                    media=photo.file_id,
                    caption=message.caption if idx == 0 else None,
                    parse_mode='Markdown'
                ) for idx, photo in enumerate(message.photo)
            ]
            bot.send_media_group(
                chat_id=TARGET_CHANNEL,
                media=media
            )
            # Загрузка фото в VK
            for photo in message.photo:
                vk_photo = upload_photo_to_vk(photo.file_id)
                if vk_photo:
                    vk_attachments.append(vk_photo)
            vk_text = message.caption
            logging.info(f"✅ Отправлен альбом/фото {message.message_id}")

        elif message.video:
            # Видео
            bot.send_video(
                chat_id=TARGET_CHANNEL,
                video=message.video.file_id,
                caption=message.caption,
                parse_mode='Markdown'
            )
            vk_text = message.caption or "Видео"
            logging.info(f"✅ Отправлено видео {message.message_id}")

        elif message.document:
            # Документ
            bot.send_document(
                chat_id=TARGET_CHANNEL,
                document=message.document.file_id,
                caption=message.caption,
                parse_mode='Markdown'
            )
            vk_text = message.caption or "Документ"
            logging.info(f"✅ Отправлен документ {message.message_id}")

        elif message.sticker:
            # Стикер
            bot.send_sticker(
                chat_id=TARGET_CHANNEL,
                sticker=message.sticker.file_id
            )
            vk_text = "Стикер"
            logging.info(f"✅ Отправлен стикер {message.message_id}")

        elif message.animation:
            # Анимация (GIF)
            bot.send_animation(
                chat_id=TARGET_CHANNEL,
                animation=message.animation.file_id,
                caption=message.caption,
                parse_mode='Markdown'
            )
            vk_text = message.caption or "Анимация"
            logging.info(f"✅ Отправлена анимация {message.message_id}")

        elif message.voice:
            # Голосовое сообщение
            bot.send_voice(
                chat_id=TARGET_CHANNEL,
                voice=message.voice.file_id,
                caption=message.caption,
                parse_mode='Markdown'
            )
            vk_text = message.caption or "Голосовое сообщение"
            logging.info(f"✅ Отправлено голосовое сообщение {message.message_id}")

        elif message.audio:
            # Аудио
            bot.send_audio(
                chat_id=TARGET_CHANNEL,
                audio=message.audio.file_id,
                caption=message.caption,
                parse_mode='Markdown'
            )
            vk_text = message.caption or "Аудио"
            logging.info(f"✅ Отправлено аудио {message.message_id}")

        elif message.poll:
            # Опрос
            bot.send_poll(
                chat_id=TARGET_CHANNEL,
                question=message.poll.question,
                options=[option.text for option in message.poll.options],
                is_anonymous=message.poll.is_anonymous,
                type=message.poll.type,
                allows_multiple_answers=message.poll.allows_multiple_answers
            )
            vk_text = f"Опрос: {message.poll.question}\n" + "\n".join(option.text for option in message.poll.options)
            logging.info(f"✅ Отправлен опрос {message.message_id}")
        else:
            logging.warning(f"⚠️ Неподдерживаемый тип сообщения: {message.content_type}")
            bot.send_message(
                chat_id=TARGET_CHANNEL,
                text="Неподдерживаемый тип сообщения"
            )
            vk_text = "Неподдерживаемый тип сообщения"

        # Отправка в VK
        if vk_session and (vk_text or vk_attachments):
            try:
                vk.wall.post(
                    owner_id=VK_GROUP_ID,
                    message=vk_text or "",
                    attachments=','.join(vk_attachments) if vk_attachments else None,
                    from_group=1
                )
                logging.info(f"✅ Отправлено в VK сообщение {message.message_id}")
            except Exception as e:
                logging.error(f"❌ Ошибка отправки в VK: {str(e)}")

    except telebot.apihelper.ApiTelegramException as e:
        logging.error(f"❌ Ошибка Telegram API: {str(e)}")
    except Exception as e:
        logging.error(f"❌ Общая ошибка: {str(e)}")

if name == 'main':
    logging.info("===== БОТ ЗАПУЩЕН =====")
    try:
        bot.polling(none_stop=True, interval=2)
    except Exception as e:
        logging.error(f"❌ Ошибка polling: {str(e)}")
        bot.stop_polling()
        exit(1)
        
