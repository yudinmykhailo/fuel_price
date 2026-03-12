import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

def get_fuel_table():
    url = "https://index.minfin.com.ua/ua/markets/fuel/tm/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', class_='list')
        if not table:
            return "❌ Не удалось найти таблицу на сайте."

        rows = table.find_all('tr')[1:]
        data = []
        # Заголовки для таблицы
        headers_list = ["АЗС", "95+", "95", "92", "ДП", "Газ"]

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 6:
                # Обрезаем длинные названия АЗС для компактности
                name = cols[0].text.strip()[:10]
                p95p = cols[1].text.strip() or "-"
                p95 = cols[2].text.strip() or "-"
                p92 = cols[3].text.strip() or "-"
                pdt = cols[4].text.strip() or "-"
                pgas = cols[5].text.strip() or "-"
                data.append([name, p95p, p95, p92, pdt, pgas])

        # Форматируем в таблицу. 'simple' хорошо выглядит в Telegram
        table_str = tabulate(data, headers=headers_list, tablefmt="simple")
        return f"```\n{table_str}\n```"

    except Exception as e:
        return f"⚠️ Ошибка при получении данных: {str(e)}"
