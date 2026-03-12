import os
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

# Берем токен из переменных окружения (настроим позже на Render)
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_fuel_prices():
    url = "https://auto.ria.com/uk/toplivo/kiev/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='bold industries')
        rows = table.find_all('tr')[1:11] # Топ-10 заправок
        
        text = "⛽️ **Цены на топливо в Киеве:**\n\n"
        for row in rows:
            cols = row.find_all('td')
            brand = cols[0].text.strip()
            a95 = cols[2].text.strip()
            diesel = cols[4].text.strip()
            text += f"📍 {brand}: 95-й: {a95}грн | ДТ: {diesel}грн\n"
        return text
    except Exception:
        return "⚠️ Не удалось получить данные. Попробуйте позже."

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Нажми /prices чтобы узнать цены на бензин в Киеве.")

@dp.message(Command("prices"))
async def prices(message: types.Message):
    data = get_fuel_prices()
    await message.answer(data, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
