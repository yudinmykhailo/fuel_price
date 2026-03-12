import os
import telebot
from scraper import get_fuel_table

# TELEGRAM_BOT_TOKEN нужно указать в настройках Render (Environment Variables)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "⛽ Привет! Я мониторю цены на топливо в Украине.\n\nИспользуй /fuel, чтобы получить таблицу цен по сетям АЗС.")

@bot.message_handler(commands=['fuel'])
def send_fuel(message):
    # Отправляем статус "печатает", пока парсится сайт
    bot.send_chat_action(message.chat.id, 'typing')
    
    table_message = get_fuel_table()
    
    # Markdown обязателен для корректного отображения таблицы в ```блоке```
    try:
        bot.send_message(message.chat.id, table_message, parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка отправки таблицы: {e}")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
