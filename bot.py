import os
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_fuel_prices():
    # Используем Минфин для Киева
    url = "https://index.minfin.com.ua/ua/markets/fuel/tm/kiev/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем таблицу с ценами
        table = soup.find('table', class_='idx-pay')
        if not table:
            return "❌ Не удалось найти таблицу с ценами на сайте."

        rows = table.find_all('tr')[1:] # Пропускаем заголовок
        
        text = "⛽️ **Цены на АЗС в Киеве (Минфин):**\n\n"
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                # Название сети часто в первом <td> внутри ссылки или просто текстом
                brand = cols[0].text.strip()
                a95 = cols[1].text.strip()
                diesel = cols[3].text.strip() if len(cols) > 3 else "н/д"
                
                # Добавляем только если есть название бренда
                if brand:
                    text += f"📍 **{brand}**\n95-й: `{a95}` | ДТ: `{diesel}`\n\n"
        
        return text if len(text) > 50 else "❌ Данные временно отсутствуют."
    except Exception as e:
        print(f"Error: {e}")
        return "⚠️ Ошибка связи с сервером цен. Попробуйте через 5 минут."

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я мониторю цены на топливо в Киеве. Нажми /prices.")

@dp.message(Command("prices"))
async def prices(message: types.Message):
    data = get_fuel_prices()
    await message.answer(data, parse_mode="Markdown")

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
