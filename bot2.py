from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random
from datetime import datetime

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

open("realtime_links.txt", "w").close()

sites = []
with open("sites.txt") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            p = line.split("|")
            if len(p) >= 6:
                sites.append({"url": p[0], "id": p[3], "pw": p[4], "login": p[5]})

keywords = {"a": [], "b": [], "c": []}
with open("keywords.txt", encoding="utf-8") as f:
    for line in f:
        if "|" in line:
            k, v = line.strip().split("|", 1)
            keywords[k] = [x.strip() for x in v.split(",")]

with open("contents.txt", encoding="utf-8") as f:
    content = f.read().strip()

total = 0
for s in sites:
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(s["login"])
        time.sleep(5)
        driver.find_element(By.NAME, "user_id").send_keys(s["id"])
        driver.find_element(By.NAME, "user_pw").send_keys(s["pw"])
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(10)

        for _ in range(100):
            driver.get(s["url"])
            time.sleep(5)
            driver.find_element(By.LINK_TEXT, "글쓰기").click()
            time.sleep(5)
            title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"
            driver.find_element(By.NAME, "subject").send_keys(title)
            driver.find_element(By.NAME, "content").send_keys(content)
            driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
            time.sleep(10)
            total += 1
            with open("realtime_links.txt", "a", encoding="utf-8") as f:
                f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {driver.current_url}\n")
            print(f"성공 {total}개")
    except Exception as e:
        print("에러:", e)
    finally:
        driver.quit()

print(f"총 {total}개 완료")
