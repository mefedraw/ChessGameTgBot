from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent, InlineQueryResultArticle
import logging
import config
import func
import db_requests
from enum import Enum

API_TOKEN = config.BOT_TOKEN

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


class GameStatus(Enum):
    NotStarted = 1
    InProgress = 2
    Finished = 3


# Предопределенные игры
PREDEFINED_GAMES = [
    {"id": "bullet", "title": "Bullet (1 мин + 0 сек)", "rules": "Таймер: 1 мин + 0 сек. Случайный цвет.",
     "thumbnail": "https://example.com/bullet.png"},
    {"id": "blitz", "title": "Blitz (3 мин + 2 сек)", "rules": "Таймер: 3 мин + 2 сек. Случайный цвет.",
     "thumbnail": "https://example.com/blitz.png"},
    {"id": "rapid", "title": "Rapid (10 мин + 5 сек)", "rules": "Таймер: 10 мин + 5 сек. Случайный цвет.",
     "thumbnail": "https://example.com/rapid.png"}
]

# Структура для хранения игровых комнат
rooms = {}


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # Генерируем сообщение с кнопкой для выбора контакта
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Играть", switch_inline_query_chosen_chat={
            "query": "",
            "allow_bot_chats": False,
            "allow_channel_chats": False,
            "allow_group_chats": True,
            "allow_user_chats": True
        })]
    ])

    TG_ID = message.from_user.id
    TG_USERNAME = message.from_user.username or message.from_user.first_name
    avatar_url = await func.get_user_avatar(TG_ID)
    db_requests.send_user_data(message.from_user.id, TG_USERNAME, avatar_url)

    await message.answer("Нажмите кнопку ниже, чтобы выбрать контакт и начать игру.", reply_markup=keyboard)


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
