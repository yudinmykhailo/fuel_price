import os
import requests
import asyncio
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# Конфигурация из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_fuel_prices():
    # Используем информер vseazs (регион 9 = Киев)
    url = "https://vseazs.com/inf.php?reg=9&fuels=00110101"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8' # Важно для корректного отображения кириллицы
        
        raw_text = response.text
        if "document.write" not in raw_text:
            return "❌ Ошибка: Информер вернул пустой ответ или заблокирован."

        # Извлекаем HTML-контент из document.write('...')
        try:
            start = raw_text.find("'") + 1
            end = raw_text.rfind("'")
            html_segment = raw_text[start:end]
            # Очищаем экранированные символы
            html_segment = html_segment.replace("\\/", "/").replace("\\'", "'").replace('\\"', '"')
        except Exception:
            return "❌ Ошибка при обработке структуры данных."

        soup = BeautifulSoup(html_segment, 'html.parser')
        
        # Извлекаем все ячейки таблицы
        cells = [td.text.strip() for td in soup.find_all('td') if td.text.strip()]
        
        if not cells:
            return "❌ Данные внутри информера не найдены."

        text = "⛽️ **Цены на АЗС в Киеве (vseazs):**\n\n"
        count = 0
        
        # Данные в информере идут тройками: Сеть | Тип топлива | Цена
        for i in range(0, len(cells), 3):
            if i + 2 < len(cells):
                brand = cells[i]
                fuel = cells[i+1]
                price = cells[i+2]
                
                # Фильтруем пустые значения
                if price and price not in ['-', '0.00', '0']:
                    text += f"📍 **{brand}**\n{fuel}: `{price} грн`\n\n"
                    count += 1
        
        if count == 0:
            return "❌ Актуальных цен на данный момент не найдено."
            
        return text
        
    except Exception as e:
        print(f"Detailed Error: {e}")
        return "⚠️ Ошибка связи с сервером цен."

# Обработчики команд Telegram
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для мониторинга цен на топливо в Киеве.\n\n"
        "Нажми /prices, чтобы получить актуальные данные."
    )

@dp.message(Command("prices"))
async def prices_handler(message: types.Message):
    # Отправляем уведомление, что мы ищем данные (чтобы пользователь не скучал)
    wait_message = await message.answer("⏳ Запрашиваю данные, подождите...")
    
    data = get_fuel_prices()
    
    # Удаляем сообщение об ожидании и присылаем результат
    await wait_message.delete()
    await message.answer(data, parse_mode="Markdown")

# Веб-сервер для "здоровья" Render (Health Check)
async def handle_ping(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render автоматически назначает порт через переменную PORT
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# Главная функция запуска
async def main():
    # Запускаем веб-сервер и бота параллельно
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
