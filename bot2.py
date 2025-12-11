from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import time, random
from datetime import datetime

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 실시간 파일 초기화
open("realtime_links.txt", "w", encoding="utf-8").close()

sites = []
with open("sites.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            p = line.split("|")
            sites.append({"list_url": p[0], "id": p[1], "pw": p[2], "login": p[3]})

keywords = {"a": [], "b": [], "c": []}
with open("keywords.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "|" in line:
            k, v = line.strip().split("|", 1)
            keywords[k] = [w.strip() for w in v.split(",")]

content = open("contents.txt", "r", encoding="utf-8").read().strip()

total = 0

for site in sites:
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # 로그인
        driver.get(site["login"])
        time.sleep(10)
        driver.find_element(By.NAME, "user_id").send_keys(site["id"])
        driver.find_element(By.NAME, "user_pw").send_keys(site["pw"])
        driver.find_element(By.CSS_SELECTOR, "button, input[type='submit']").click()
        time.sleep(15)

        for _ in range(100):
            try:
                # 1. list.html 로 이동
                driver.get(site["list_url"])
                time.sleep(8)

                # 2. 글쓰기 클릭
                driver.find_element(By.LINK_TEXT, "글쓰기").click()
                time.sleep(10)

                # 3. alert 뜨면 무조건 "취소" 클릭
                try:
                    alert = wait.until(EC.alert_is_present())
                    alert.dismiss()  # 취소 클릭
                    print("alert '취소' 클릭함")
                    time.sleep(5)
                except:
                    pass

                # 4. 제목 + 내용 입력
                title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"
                driver.find_element(By.NAME, "subject").send_keys(title)

                try:
                    iframe = driver.find_element(By.TAG_NAME, "iframe")
                    driver.switch_to.frame(iframe)
                    driver.find_element(By.TAG_NAME, "body").send_keys(content)
                    driver.switch_to.default_content()
                except:
                    driver.find_element(By.NAME, "content").send_keys(content)

                # 5. 등록
                driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
                time.sleep(15)

                url = driver.current_url
                total += 1
                with open("realtime_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{total}. {time.strftime('%H:%M:%S')} | {title} | {url}\n")
                print(f"성공 {total}개: {url}")

            except Exception as e:
                print(f"포스팅 실패: {e}")
                time.sleep(10)
                continue

    except Exception as e:
        print(f"사이트 실패: {e}")
    finally:
        driver.quit()

print(f"완료! 총 {total}개 성공")
