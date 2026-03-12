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
    # Актуальная ссылка на таблицу цен по Киеву
    url = "https://index.minfin.com.ua/ua/markets/fuel/tm/kiev/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем таблицу, которая содержит слово 'А-95'
        table = None
        for t in soup.find_all('table'):
            if 'А-95' in t.text:
                table = t
                break
        
        if not table:
            return "❌ Не удалось найти таблицу с актуальными ценами."

        rows = table.find_all('tr')[1:] # Пропускаем заголовок
        
        text = "⛽️ **Цены на топливо в Киеве:**\n\n"
        count = 0
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                brand = cols[0].text.strip()
                a95 = cols[1].text.strip().replace('\xa0', ' ')
                diesel = cols[3].text.strip().replace('\xa0', ' ') if len(cols) > 3 else "-"
                
                if brand and a95:
                    text += f"📍 **{brand}**\n95-й: `{a95}` | ДТ: `{diesel}`\n\n"
                    count += 1
        
        if count == 0:
            return "❌ Данные на сайте временно недоступны."
            
        return text
    except Exception as e:
        print(f"Parsing error: {e}")
        return "⚠️ Ошибка при получении данных с сайта."

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
