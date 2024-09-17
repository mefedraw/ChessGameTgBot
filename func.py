from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from main import bot, API_TOKEN


async def get_user_avatar(user_id):
    user_profile_photos = await bot.get_user_profile_photos(user_id)
    if user_profile_photos.total_count > 0:
        # Берем последнюю обновленную фотографию
        file_id = user_profile_photos.photos[0][-1].file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
        return file_url
    return None