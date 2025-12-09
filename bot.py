from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import datetime

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

# 파일 초기화
open("realtime_links.txt", "w").close()

# sites.txt 읽기 (6개 컬럼 정확히)
sites = []
with open("sites.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split("|")
            if len(parts) >= 6:
                sites.append(parts)

# 키워드
keywords = {"a": [], "b": [], "c": []}
with open("keywords.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "|" in line:
            k, words = line.strip().split("|", 1)
            keywords[k] = [w.strip() for w in words.split(",") if w.strip()]

# 내용
with open("contents.txt", "r", encoding="utf-8") as f:
    content = f.read().strip()

total = 0

for site in sites:
    list_url = site[0]           # 게시판 리스트 URL
    login_id = site[3]           # 아이디
    login_pw = site[4]           # 비번
    login_url = site[5]          # 로그인 페이지 URL

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        # 1. 로그인
        driver.get(login_url)
        time.sleep(5)
        wait.until(EC.presence_of_element_located((By.NAME, "user_id"))).send_keys(login_id)
        driver.find_element(By.NAME, "user_pw").send_keys(login_pw)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(10)

        # 2. 100번 반복
        for _ in range(100):
            driver.get(list_url)
            time.sleep(5)

            # 글쓰기 클릭
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "글쓰기"))).click()
            time.sleep(5)

            # 제목
            title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"
            wait.until(EC.presence_of_element_located((By.NAME, "subject"))).send_keys(title)

            # 내용
            driver.find_element(By.NAME, "content").send_keys(content)

            # 등록
            driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
            time.sleep(10)

            # 성공 저장
            link = driver.current_url
            total += 1
            with open("realtime_links.txt", "a", encoding="utf-8") as f:
                f.write(f"{total}. {datetime.now().strftime('%H:%M:%S')} | {title} | {link}\n")
            print(f"성공 {total}개: {link}")

    except Exception as e:
        print("에러 발생:", str(e))
    finally:
        driver.quit()

print(f"\n최종 완료! 총 {total}개 포스팅 성공")
