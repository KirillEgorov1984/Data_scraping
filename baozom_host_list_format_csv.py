import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

# ==========================
# Параметры
# ==========================
LOGIN_PAGE = "https://baozam.net/index.php?obj=usr&act=login"
LOGIN_ACTION = "https://baozam.net/index.php"
DATA_URL_TEMPLATE = "https://baozam.net/hostinventories.php?page={}"

USERNAME = "knigarnia2"
PASSWORD = "BAZ2023m"

session = requests.Session()

# ==========================
# 1️⃣ ЛОГИН
# ==========================
login_html = session.get(LOGIN_PAGE).text
soup = BeautifulSoup(login_html, "html.parser")
sid = soup.find("input", {"name": "sid"})["value"]
obj = soup.find("input", {"name": "obj"})["value"]

payload = {
    "sid": sid,
    "obj": obj,
    "bidentity": USERNAME,
    "password": PASSWORD,
    "autologin": "on",
    "act": "login"
}

resp = session.post(LOGIN_ACTION, data=payload)
if "Logout" not in resp.text and "logout" not in resp.text.lower():
    print("❌ Логин не удался")
    exit()
print("✅ Логин успешен!")

# ==========================
# 2️⃣ Определяем количество страниц
# ==========================
first_page_html = session.get(DATA_URL_TEMPLATE.format(1)).text
soup = BeautifulSoup(first_page_html, "html.parser")
pages = soup.select("a[href*='page=']")
if pages:
    last_page = max(int(a.get_text()) for a in pages if a.get_text().isdigit())
else:
    last_page = 1
print(f"📄 Найдено страниц: {last_page}")

# ==========================
# 3️⃣ Собираем все ссылки на хосты со всех страниц
# ==========================
host_links = []
for page in range(1, last_page + 1):
    html = session.get(DATA_URL_TEMPLATE.format(page)).text
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a"):
        href = a.get("href")
        if href and "obj=host" in href and "preview" in href:
            host_links.append("https://baozam.net" + href)
    print(f"⏳ Пауза 2 сек после страницы {page}")
    time.sleep(2)  # пауза 2 сек между страницами

host_links = list(set(host_links))  # убираем дубликаты
print(f"🔗 Всего ссылок на хосты: {len(host_links)}")

# ==========================
# 4️⃣ Функция для извлечения полей
# ==========================
def extract_field(soup, field_name):
    b_tags = soup.find_all("b")
    for b in b_tags:
        if b.text.strip() == field_name:
            i_tag = b.find_next("i")
            return i_tag.text.strip() if i_tag else None
    return None

# ==========================
# 5️⃣ Собираем данные каждого хоста
# ==========================
data = []
for url in host_links:
    print("📥 Читаю:", url)
    r = session.get(url).text
    s = BeautifulSoup(r, "html.parser")
    host = {
        "HOSTID": extract_field(s, "HOSTID"),
        "Name": extract_field(s, "Name"),
        "Serial": extract_field(s, "Serial"),
        "IP address": extract_field(s, "IP address"),
        "Serial number A": extract_field(s, "Serial number A"),
        "URL": url
    }
    data.append(host)
    print("⏳ Пауза 2 сек перед следующим хостом")
    time.sleep(2)  # пауза 2 сек между хостами

# ==========================
# 6️⃣ Добавляем дату запуска и сохраняем в CSV с |
# ==========================
df = pd.DataFrame(data)
today_str = datetime.now().strftime("%d.%m.%Y")  # формат дд.мм.гггг
df["Date_of_request"] = today_str

filename = f"baozam_full_inventory_{today_str}.csv"
df.to_csv(filename, index=False, sep='|', encoding='utf-8')

print(f"🎉 Файл сохранён: {filename}")




