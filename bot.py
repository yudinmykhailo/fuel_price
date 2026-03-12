import os
import cloudscraper
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_fuel_prices():
    url = "https://index.minfin.com.ua/ua/markets/fuel/tm/kiev/"
    # Создаем scraper, который обходит Cloudflare
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(url, timeout=15)
        if response.status_code != 200:
            return f"⚠️ Сайт вернул ошибку {response.status_code}. Возможно, IP заблокирован."
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем таблицу. На Минфине она обычно вложена в div с классом 'm-0' или 'idx-pay'
        table = soup.find('table', class_='idx-pay')
        
        if not table:
            # Запасной вариант: ищем любую таблицу с ключевым словом
            for t in soup.find_all('table'):
                if 'А-95' in t.text:
                    table = t
                    break
        
        if not table:
            print("Debug: Table not found. Page content snippet:", response.text[:500])
            return "❌ Сайт защищен или изменил структуру. Пробуем другой метод..."

        rows = table.find_all('tr')[1:]
        text = "⛽️ **Цены на топливо в Киеве:**\n\n"
        count = 0
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                brand = cols[0].text.strip()
                a95 = cols[1].text.strip().replace('\xa0', ' ')
                diesel = cols[3].text.strip().replace('\xa0', ' ') if len(cols) > 3 else "-"
                
                if brand and a95 and a95 != '-':
                    text += f"📍 **{brand}**\n95-й: `{a95}` | ДТ: `{diesel}`\n\n"
                    count += 1
        
        if count == 0:
            return "❌ Цены временно не найдены в таблице."
            
        return text
    except Exception as e:
        print(f"Scraper error: {e}")
        return "⚠️ Ошибка при обходе защиты сайта."

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Бот запущен! Нажми /prices для получения цен (через обход защиты).")

@dp.message(Command("prices"))
async def prices(message: types.Message):
    data = get_fuel_prices()
    await message.answer(data, parse_mode="Markdown")

async def handle_ping(request):
    return web.Response(text="OK")

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
