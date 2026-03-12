import os
import telebot
from scraper import get_fuel_table

# Токен берем из переменных окружения (настройте в Render)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "⛽ Привет! Чтобы получить таблицу цен на топливо, используй команду /fuel")

@bot.message_handler(commands=['fuel'])
def send_fuel(message):
    bot.send_chat_action(message.chat.id, 'typing')
    table = get_fuel_table()
    bot.send_message(message.chat.id, table, parse_mode='Markdown')

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
