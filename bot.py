import requests
from bs4 import BeautifulSoup
import telebot
from tabulate import tabulate

# Замените на ваш токен от @BotFather
TOKEN = 'ВАШ_ТОКЕН_ЗДЕСЬ'
bot = telebot.TeleBot(TOKEN)

def get_fuel_data():
    url = "https://index.minfin.com.ua/ua/markets/fuel/tm/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Находим таблицу с ценами
        table = soup.find('table', class_='list')
        if not table:
            return "Не удалось найти таблицу на странице."

        rows = table.find_all('tr')[1:] # Пропускаем заголовок
        table_data = []
        
        # Сокращаем названия колонок для мобильных экранов
        headers_table = ["АЗС", "95+", "95", "92", "ДТ", "Газ"]

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 6:
                name = cols[0].text.strip()
                # Берем только значения, если пусто — ставим прочерк
                p95_plus = cols[1].text.strip() or "-"
                p95 = cols[2].text.strip() or "-"
                p92 = cols[3].text.strip() or "-"
                p_dp = cols[4].text.strip() or "-"
                p_gas = cols[5].text.strip() or "-"
                
                table_data.append([name, p95_plus, p95, p92, p_dp, p_gas])

        # Форматируем в таблицу (используем формат 'simple' или 'grid')
        formatted_table = tabulate(table_data, headers=headers_table, tablefmt="simple")
        return f"```\n{formatted_table}\n```"

    except Exception as e:
        return f"Ошибка при парсинге: {e}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Нажми /fuel, чтобы получить таблицу цен на всех АЗС.")

@bot.message_handler(commands=['fuel'])
def send_fuel_prices(message):
    bot.send_message(message.chat.id, "📊 Получаю свежие данные...")
    table_text = get_fuel_data()
    # parse_mode='MarkdownV2' или 'Markdown' критичен для отображения моноширинного шрифта
    bot.send_message(message.chat.id, table_text, parse_mode='Markdown')

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
