import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

def get_fuel_table():
    url = "https://index.minfin.com.ua/ua/markets/fuel/tm/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', class_='list')
        if not table:
            return "❌ Ошибка: Таблица с ценами не найдена на странице."

        rows = table.find_all('tr')[1:] # Пропускаем заголовок таблицы
        data = []
        # Короткие заголовки для экономии места
        headers_list = ["АЗС", "95+", "95", "92", "ДП", "Газ"]

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 6:
                name = cols[0].text.strip()[:10] # Обрезаем название АЗС
                p95p = cols[1].text.strip() or "-"
                p95 = cols[2].text.strip() or "-"
                p92 = cols[3].text.strip() or "-"
                pdt = cols[4].text.strip() or "-"
                pgas = cols[5].text.strip() or "-"
                data.append([name, p95p, p95, p92, pdt, pgas])

        if not data:
            return "❌ Данные отсутствуют."

        # Формируем таблицу
        table_str = tabulate(data, headers=headers_list, tablefmt="psql")
        return f"```\n{table_str}\n```"

    except Exception as e:
        return f"⚠️ Произошла ошибка при получении данных: {str(e)}"
