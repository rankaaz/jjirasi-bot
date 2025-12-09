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
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(s["login"])
        time.sleep(8)

        # 1. 모든 가능한 ID 입력칸 시도
        id_found = False
        for selector in ['[name="user_id"]', '[name="mb_id"]', '[id="user_id"]', '[id="mb_id"]', 'input[type="text"]', 'input[type="email"]']:
            try:
                elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                elem.clear()
                elem.send_keys(s["id"])
                id_found = True
                print(f"ID 입력 성공: {selector}")
                break
            except:
                continue

        # 2. 모든 가능한 PW 입력칸 시도
        pw_found = False
        for selector in ['[name="user_pw"]', '[name="mb_password"]', '[id="user_pw"]', '[id="mb_password"]', 'input[type="password"]']:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                elem.clear()
                elem.send_keys(s["pw"])
                pw_found = True
                print(f"PW 입력 성공: {selector}")
                break
            except:
                continue

        # 3. 로그인 버튼 클릭
        for selector in ["button[type='submit']", "input[type='submit']", ".btn_login", "button:contains('로그인')"]:
            try:
                driver.find_element(By.CSS_SELECTOR, selector).click()
                print("로그인 버튼 클릭 성공")
                break
            except:
                continue

        time.sleep(12)

        # 여기서부터는 기존 그대로
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
        print("최종 에러:", e)
    finally:
        driver.quit()

print(f"총 {total}개 완료")
