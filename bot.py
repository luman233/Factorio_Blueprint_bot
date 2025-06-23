import os
import json
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, TelegramError

# Загрузка переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID'))
THREAD_ID = int(os.getenv('TELEGRAM_THREAD_ID'))  # если вы используете темы, иначе уберите
STATE_FILE = 'state.json'

bot = Bot(token=TOKEN)

# Сообщение и клавиатура
message_text = (
    "<b>🔷 Что должно быть в посте:</b>\n"
    "<b>1. Название —</b> кратко отражает суть, например: «Набор чертежей для ситиблоков»\n"
    "<b>2. Описание —</b> что делает чертёж, какие задачи решает, можно указать эффективность (например, производство ресурсов в секунду).\n"
    "<b>3. Изображения —</b> от 1 до 5 скриншотов. Видео можно, но нежелательно.\n"
    "<b>4. Ссылка или файл —</b> <i>txt</i> чертежа для использования другими игроками.\n"
    "По желанию: <i>теги.</i>\n\n"
)

keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📋 Инструкция", url="https://telegra.ph/CHertezhi-06-11"),
        InlineKeyboardButton("ℹ️ Подробнее", url="https://t.me/FCTostin/414/447")
    ]
])

# Загрузка состояния
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
else:
    state = {}

previous_message_id = state.get('previous_message_id')
previous_helper_id = state.get('previous_helper_id')

try:
    # Отправка основного сообщения
    sent_message = bot.send_message(
        chat_id=CHAT_ID,
        text=message_text,
        parse_mode='HTML',
        reply_markup=keyboard,
        message_thread_id=THREAD_ID if THREAD_ID else None
    )

    # Отправка вспомогательного сообщения
    helper_message = bot.send_message(
        chat_id=CHAT_ID,
        text="Проверка, без звука",
        disable_notification=True,
        message_thread_id=THREAD_ID if THREAD_ID else None
    )

    # Проверка разницы ID
    id_difference = helper_message.message_id - sent_message.message_id

    if previous_message_id and previous_helper_id:
        # Если в прошлый раз кто-то написал
        if (previous_helper_id - previous_message_id) != 1:
            # Удаляем старое сообщение
            bot.delete_message(chat_id=CHAT_ID, message_id=previous_message_id)
            print("Удалено старое сообщение")

    if id_difference == 1:
        print("Никто не написал после сообщения")
        bot.delete_message(chat_id=CHAT_ID, message_id=helper_message.message_id)
    else:
        print("Кто-то написал после сообщения, пересоздаём")
        bot.delete_message(chat_id=CHAT_ID, message_id=helper_message.message_id)
        bot.delete_message(chat_id=CHAT_ID, message_id=sent_message.message_id)
        # Публикуем заново без звука
        bot.send_message(
            chat_id=CHAT_ID,
            text=message_text,
            parse_mode='HTML',
            reply_markup=keyboard,
            disable_notification=True,
            message_thread_id=THREAD_ID if THREAD_ID else None
        )

    # Сохраняем новые ID
    state['previous_message_id'] = sent_message.message_id
    state['previous_helper_id'] = helper_message.message_id

    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

except TelegramError as e:
    print(f"Ошибка: {e}")
