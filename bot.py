import os
import requests
import re
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_fuel_prices():
    # Прямая ссылка на данные информера (регион 9 = Киев)
    url = "https://vseazs.com/inf.php?reg=9&fuels=00110101"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Скрипт возвращает JS-код вида: document.write('HTML_TABLE');
        # Нам нужно вытащить то, что внутри кавычек
        html_content = re.search(r"document\.write\('(.*)'\);", response.text)
        
        if not html_content:
            return "❌ Не удалось обработать данные информера."
            
        clean_html = html_content.group(1).replace("\\", "") # Убираем экранирование
        soup = BeautifulSoup(clean_html, 'html.parser')
        
        # На vseazs данные лежат в таблице
        rows = soup.find_all('tr')
        text = "⛽️ **Цены на АЗС в Киеве (vseazs):**\n\n"
        
        for row in rows:
            cols = row.find_all('td')
            # Обычно в информере: 0 - бренд, 1 - тип топлива, 2 - цена
            if len(cols) >= 3:
                brand = cols[0].text.strip()
                fuel_type = cols[1].text.strip()
                price = cols[2].text.strip()
                
                if price and price != '0.00':
                    text += f"📍 **{brand}**\n{fuel_type}: `{price} грн`\n\n"
        
        return text if len(text) > 50 else "❌ Данные в информере временно пусты."
        
    except Exception as e:
        print(f"Informer error: {e}")
        return "⚠️ Ошибка при обращении к vseazs.com"

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Бот настроен на официальный информер vseazs! Нажми /prices.")

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
