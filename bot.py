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

# 실시간 파일 초기화
open("realtime_links.txt", "w").close()

sites = [line.split("|") for line in open("sites.txt").read().strip().split("\n") if line.strip() and not line.startswith("#")]
keywords = {"a": [], "b": [], "c": []}
for line in open("keywords.txt"):
    if "|" in line:
        k, v = line.strip().split("|")
        keywords[k] = v.split(",")
content = open("contents.txt", "r", encoding="utf-8").read().strip()

total = 0
for s in sites:
    url, _, _, id_, pw, login = s
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(login); time.sleep(3)
        driver.find_element(By.NAME, "user_id").send_keys(id_)
        driver.find_element(By.NAME, "user_pw").send_keys(pw)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(5)

        for _ in range(100):
            a = random.choice(keywords["a"])
            b = random.choice(keywords["b"])
            c = random.choice(keywords["c"])
            title = f"{a} {b} {c}"

            driver.get(url); time.sleep(3)
            driver.find_element(By.LINK_TEXT, "글쓰기").click(); time.sleep(3)
            driver.find_element(By.NAME, "subject").send_keys(title)
            driver.find_element(By.NAME, "content").send_keys(content)
            driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
            time.sleep(8)

            link = driver.current_url
            total += 1
            with open("realtime_links.txt", "a", encoding="utf-8") as f:
                f.write(f"{total}. {datetime.now().strftime('%H:%M:%S')} | {title} | {link}\n")
            print(f"성공 {total}개: {link}")
    except Exception as e:
        print("에러:", e)
    finally:
        driver.quit()

print(f"\n완료! 총 {total}개 포스팅")
