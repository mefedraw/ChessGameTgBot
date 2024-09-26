import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent, InlineQueryResultArticle
import logging
import config
import func
import db_requests, hashlib
from enum import Enum
from datetime import datetime

API_TOKEN = config.BOT_TOKEN

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

game_sessions = {}

def save_game_session(button_id: str, username: str):
    # Сохраняем информацию о сессии игры с уникальным button_id
    game_sessions[button_id] = {
        "creator": username,
        "game_id": button_id
    }


def generate_game_id(username: str) -> str:
    # Получаем текущее время в формате UTC до cекунд
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # Создаем строку на основе никнейма и времени (убрали фигурные скобки)
    data_to_hash = f"{username}{current_time}"

    # Вычисляем SHA-256 хэш
    return hashlib.sha256(data_to_hash.encode('utf-8')).hexdigest()

class GameStatus(Enum):
    NotStarted = 1
    InProgress = 2
    Finished = 3


# Предопределенные игры
PREDEFINED_GAMES = [
    {"id": "bullet", "title": "Bullet (1 мин + 0 сек)", "rules": "Таймер: 1 мин + 0 сек. Случайный цвет.",
     "thumbnail": "https://imgur.com/oJIJOP3.png"},  # Замените на реальный URL для иконки
    {"id": "blitz", "title": "Blitz (3 мин + 2 сек)", "rules": "Таймер: 3 мин + 2 сек. Случайный цвет.",
     "thumbnail": "https://imgur.com/tBZ2kq7.png"},  # Замените на реальный URL для иконки
    {"id": "rapid", "title": "Rapid (10 мин + 5 сек)", "rules": "Таймер: 10 мин + 5 сек. Случайный цвет.",
     "thumbnail": "https://imgur.com/0KoUo6P.png"}  # Замените на реальный URL для иконки
]


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
    if(db_requests.user_exists(TG_ID)==False):
        db_requests.auth_user(message.from_user.id, TG_USERNAME, avatar_url)
    else:
        print("User already exists")

    await message.answer("Нажмите кнопку ниже, чтобы выбрать контакт и начать игру.", reply_markup=keyboard)


@dp.inline_handler()
async def inline_query_handler(inline_query: types.InlineQuery):
    query = inline_query.query.lower()

    results = []
    for game in PREDEFINED_GAMES:
        # Получаем имя пользователя из inline-запроса
        username = inline_query.from_user.username or inline_query.from_user.first_name
        game_id = generate_game_id(username)

        results.append(
            InlineQueryResultArticle(
                id=game["id"],
                title=game["title"],
                description=game["rules"],
                thumb_url=game["thumbnail"],
                input_message_content=InputTextMessageContent(
                    message_text=f"Хамстер криминал под ником @{username} хочет сыграть с вами в шахматы\n"
                                 f"Если вы считаете себя настоящим сигма котиком, то скорее принимайте вызов \n\nПравила игры: {game['rules']}\n\nНажмите на кнопку, чтобы присоединиться к игре.",
                    parse_mode="Markdown"
                ),
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(
                        "Присоединиться",
                        url="t.me/SigmaChessBot/SigmaChessWebApp",

                    )
                )
            )
        )
        save_game_session(game_id, username)

    await bot.answer_inline_query(inline_query.id, results)


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
