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
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

open("realtime_links.txt", "w").close()

sites = [line.strip().split("|") for line in open("sites.txt").readlines() if line.strip() and not line.startswith("#")]
keywords = {"a": [], "b": [], "c": []}
for line in open("keywords.txt"):
    if "|" in line:
        k, v = line.strip().split("|", 1)
        keywords[k] = [x.strip() for x in v.split(",")]
content = open("contents.txt", "r", encoding="utf-8").read().strip()

total = 0
for s in sites:
    url, _, _, id_, pw, login = s
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    try:
        # 로그인 페이지 로드
        driver.get(login)
        time.sleep(5)

        # ID 입력 (여러 셀렉터 시도)
        id_selectors = ["input[name='user_id']", "input[name='mb_id']", "input[id='user_id']", "input[type='text'], input[type='email']"]
        for selector in id_selectors:
            try:
                elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                elem.clear()
                elem.send_keys(id_)
                break
            except:
                continue

        # PW 입력
        pw_selectors = ["input[name='user_pw']", "input[name='mb_password']", "input[id='user_pw']", "input[type='password']"]
        for selector in pw_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                elem.clear()
                elem.send_keys(pw)
                break
            except:
                continue

        # 로그인 버튼 클릭
        submit_selectors = ["button[type='submit']", "input[type='submit']", "button:contains('로그인')", ".btn_login"]
        for selector in submit_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                elem.click()
                break
            except:
                continue
        time.sleep(10)  # 로그인 대기

        # 100회 반복 포스팅
        for _ in range(100):
            driver.get(url)
            time.sleep(5)

            # 글쓰기 버튼 클릭 (LINK_TEXT로 안전하게)
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "글쓰기"))).click()
            time.sleep(5)

            # 제목 입력
            title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"
            subject_elem = wait.until(EC.presence_of_element_located((By.NAME, "subject")))
            subject_elem.clear()
            subject_elem.send_keys(title)

            # 내용 입력
            content_elem = driver.find_element(By.NAME, "content")
            content_elem.clear()
            content_elem.send_keys(content)

            # 등록 버튼 클릭
            submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
            submit_btn.click()
            time.sleep(10)

            # 링크 저장
            link = driver.current_url
            total += 1
            with open("realtime_links.txt", "a", encoding="utf-8") as f:
                f.write(f"{total}. {datetime.now().strftime('%H:%M:%S')} | {title} | {link}\n")
            print(f"성공 {total}개: {link}")

    except Exception as e:
        print(f"에러: {str(e)}")
    finally:
        driver.quit()

print(f"\n완료! 총 {total}개 포스팅")
