import os
import json
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, TelegramError

# Загрузка переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID'))
THREAD_ID = os.getenv('TELEGRAM_THREAD_ID')
THREAD_ID = int(THREAD_ID) if THREAD_ID else None

STATE_FILE = 'state.json'
bot = Bot(token=TOKEN)

# Текст и кнопки
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

message_id = state.get('message_id')

try:
    if message_id is None:
        # Первый запуск: отправляем основное сообщение
        sent = bot.send_message(
            chat_id=CHAT_ID,
            text=message_text,
            parse_mode='HTML',
            reply_markup=keyboard,
            message_thread_id=THREAD_ID
        )

        state['message_id'] = sent.message_id
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)

        print(f"Первый запуск. Отправлено сообщение с ID {sent.message_id}")

    else:
        # Отправляем вспомогательное сообщение
        helper = bot.send_message(
            chat_id=CHAT_ID,
            text="Проверка, без звука",
            disable_notification=True,
            message_thread_id=THREAD_ID
        )

        state['previous_helper_id'] = helper.message_id

        print(f"Основное сообщение ID: {message_id}")
        print(f"Вспомогательное сообщение ID: {helper.message_id}")

        if helper.message_id == message_id + 1:
            # Всё хорошо — удаляем только вспомогательное
            bot.delete_message(chat_id=CHAT_ID, message_id=helper.message_id)
            print("Всё чисто. Никто не писал после основного сообщения.")

        else:
            # Кто-то написал — удаляем всё и публикуем заново
            print("После основного сообщения что-то написали. Перепубликуем.")

            # Удаляем старые сообщения
            bot.delete_message(chat_id=CHAT_ID, message_id=helper.message_id)
            bot.delete_message(chat_id=CHAT_ID, message_id=message_id)

            # Отправляем новое основное сообщение
            new_msg = bot.send_message(
                chat_id=CHAT_ID,
                text=message_text,
                parse_mode='HTML',
                reply_markup=keyboard,
                disable_notification=True,
                message_thread_id=THREAD_ID
            )

            # Обновляем состояние
            state['message_id'] = new_msg.message_id
            state['previous_helper_id'] = None  # обнуляем — вспомогательное уже удалено

            print(f"Новое основное сообщение отправлено с ID {new_msg.message_id}")

        # Сохраняем состояние
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)

except TelegramError as e:
    print(f"Ошибка: {e}")
