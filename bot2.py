from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time, random
from datetime import datetime

# 봇 탐지 완전 우회 옵션 (이게 핵심!)
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-infobars")
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36")

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
        time.sleep(8)

        # 사이트별 정확한 입력칸
        if "hongsthetic" in s["login"]:
            driver.find_element(By.NAME, "member_id").send_keys(s["id"])
            driver.find_element(By.NAME, "member_passwd").send_keys(s["pw"])
        else:
            driver.find_element(By.NAME, "user_id").send_keys(s["id"])
            driver.find_element(By.NAME, "user_pw").send_keys(s["pw"])

        driver.find_element(By.CSS_SELECTOR, "a.btnSubmit, button[type='submit'], input[type='submit']").click()
        time.sleep(12)

        # 로그인 후 세션 살리기 (필수!)
        driver.get("https://hongsthetic.com" if "hongsthetic" in s["login"] else "https://reanswer.co.kr")
        time.sleep(5)

        # 100개 포스팅
        for _ in range(100):
            driver.get(s["url"])
            time.sleep(6)
            driver.find_element(By.LINK_TEXT, "글쓰기").click()
            time.sleep(6)
            title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"
            driver.find_element(By.NAME, "subject").send_keys(title)
            driver.find_element(By.NAME, "content").send_keys(content)
            driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
            time.sleep(12)

            total += 1
            with open("realtime_links.txt", "a", encoding="utf-8") as f:
                f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {driver.current_url}\n")
            print(f"성공 {total}개")

    except Exception as e:
        print("에러:", e)
    finally:
        driver.quit()

print(f"총 {total}개 완료")
