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
    db_requests.send_user_data(message.from_user.id, TG_USERNAME, avatar_url)

    await message.answer("Нажмите кнопку ниже, чтобы выбрать контакт и начать игру.", reply_markup=keyboard)


# Обработчик inline-запроса выбора игры
@dp.inline_handler()
async def inline_query_handler(inline_query: types.InlineQuery):
    query = inline_query.query.lower()

    results = []
    for game in PREDEFINED_GAMES:
        results.append(
            InlineQueryResultArticle(
                id=game["id"],
                title=game["title"],
                description=game["rules"],
                thumb_url=game["thumbnail"],
                input_message_content=InputTextMessageContent(
                    message_text=f"Правила игры: {game['rules']}\nНажмите на кнопку, чтобы присоединиться к игре.",
                    parse_mode="Markdown"
                ),
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("Присоединиться", callback_data=f"join_game_{game['id']}"))
                .add(
                    InlineKeyboardButton("Отменить игру", callback_data=f"cancel_game_{game['id']}")
                )
            )
        )

    await bot.answer_inline_query(inline_query.id, results)


# Обработчик inline-результата (создание комнаты)
@dp.chosen_inline_handler(lambda chosen_inline_result: True)
async def inline_result_handler(chosen_inline_result: types.ChosenInlineResult):
    result_id = chosen_inline_result.result_id
    user = chosen_inline_result.from_user

    # Создаем комнату для игры
    room_id = f"room_{user.id}_{result_id}"
    room = {
        "host": user,
        "status": GameStatus.NotStarted,
        "game_id": result_id
    }
    rooms[room_id] = room

    game_url = f"https://t.me/your_bot_username/{room_id}?startapp={room_id}"

    # Отправляем сообщение с возможностью присоединиться к игре
    join_button = InlineKeyboardButton("Присоединиться", url=game_url)
    markup = InlineKeyboardMarkup().add(join_button)

    await bot.send_message(user.id, f"Игра {room_id} создана. Ожидаем присоединения второго игрока.", reply_markup=markup)

    # Обновление статуса
    room["status"] = GameStatus.InProgress


# Обработчик нажатия на inline-кнопку "Присоединиться"
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('join_game_'))
async def process_callback_button(callback_query: types.CallbackQuery):
    game_id = callback_query.data.split('_')[-1]
    game = next((g for g in PREDEFINED_GAMES if g["id"] == game_id), None)

    if game:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, f"Вы присоединились к игре: {game['title']}")
    else:
        await bot.answer_callback_query(callback_query.id, "Игра не найдена", show_alert=True)


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
