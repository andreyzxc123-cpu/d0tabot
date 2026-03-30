import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from datetime import datetime, timedelta

TOKEN = os.environ.get("8609001889:AAG9EFaKG-xHbDZ74dEi8MDZ0XhLrU0__OU")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Русский → ключи API OpenDota
rank_map = {
    "Рекрут": "1",
    "Страж": "2",
    "Рыцарь": "3",
    "Герой": "4",
    "Легенда": "5",
    "Властелин": "6",
    "Божество": "7",
    "Титан": "8"
}

# Кэш героев
heroes = {}
heroes_last_update = datetime.min  # время последнего обновления
HEROES_UPDATE_INTERVAL = timedelta(hours=6)  # обновляем каждые 6 часов

def update_heroes_cache():
    global heroes, heroes_last_update
    try:
        response = requests.get("https://api.opendota.com/api/heroes").json()
        heroes = {h["localized_name"].lower(): h for h in response}
        heroes_last_update = datetime.now()
    except:
        pass  # если ошибка сети, оставляем старый кэш

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.reply(
        "Бот работает ✅\nОтправь: Hero;Rank\nПример: Lone Druid;Герой"
    )

@dp.message_handler()
async def hero_rank_handler(message: types.Message):
    global heroes_last_update

    # Обновляем кэш если прошло больше HEROES_UPDATE_INTERVAL
    if datetime.now() - heroes_last_update > HEROES_UPDATE_INTERVAL or not heroes:
        update_heroes_cache()

    text = message.text.strip()
    try:
        hero_name_input, rank_input = text.split(";")
    except ValueError:
        await message.reply("Неверный формат. Используй: Hero;Rank")
        return

    hero_name = hero_name_input.lower()
    hero = heroes.get(hero_name)
    if not hero:
        await message.reply(f"Герой '{hero_name_input}' не найден.")
        return

    rank_key = rank_map.get(rank_input)
    if not rank_key:
        await message.reply(f"Ранг '{rank_input}' не найден.")
        return

    pick = hero.get(f"{rank_key}_pick", 0)
    win = hero.get(f"{rank_key}_win", 0)
    if pick == 0:
        await message.reply(f"Нет данных по {hero_name_input} для ранга {rank_input}.")
        return

    winrate = win / pick * 100
    await message.reply(
        f"Герой: {hero_name_input}\nРанг: {rank_input}\nИгр: {pick}\nВыигрышей: {win}\nВинрейт: {winrate:.1f}%"
    )

if name == "__main__":
    # обновляем кэш при старте
    update_heroes_cache()
    executor.start_polling(dp)
