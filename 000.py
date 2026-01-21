import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://www.ua-region.com.ua"
START_URL = BASE + "/biznes-katalog"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ---------- Шаг 1. Собираем категории ----------
resp = requests.get(START_URL, headers=HEADERS)
soup = BeautifulSoup(resp.text, "html.parser")

category_links = set()

for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.startswith("/biznes-katalog/") and href.count("/") == 2:
        category_links.add(urljoin(BASE, href))

print(f"Категорий найдено: {len(category_links)}")

# ---------- Шаг 2. Из категорий собираем КВЕД ----------
kved_links = set()

for cat_url in category_links:
    resp = requests.get(cat_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/kved/"):
            full_url = urljoin(BASE, href)
            code = href.split("/kved/")[-1]
            kved_links.add((code, full_url))

print(f"КВЕД найдено: {len(kved_links)}")

# ---------- Шаг 3. Сохраняем в CSV с разделителем | ----------
with open("kved_links.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="|")
    writer.writerow(["level", "code", "url"])

    for code, url in sorted(kved_links):
        writer.writerow(["CLASS", code, url])

print("Файл kved_links.csv успешно создан")