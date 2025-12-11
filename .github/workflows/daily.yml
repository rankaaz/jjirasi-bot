from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random
from datetime import datetime

# 봇 탐지 완전 우회 + 최고 안정성
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36")

# 실시간 파일 초기화
open("realtime_links.txt", "w", encoding="utf-8").close()

# 사이트 로드
sites = []
with open("sites.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split("|")
            sites.append({"url": parts[0], "id": parts[1], "pw": parts[2], "login": parts[3]})

# 키워드 로드
keywords = {"a": [], "b": [], "c": []}
with open("keywords.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and "|" in line:
            k, words = line.split("|", 1)
            keywords[k] = [w.strip() for w in words.split(",")]

# 내용 로드
with open("contents.txt", "r", encoding="utf-8") as f:
    content = f.read().strip()

total = 0

for site in sites:
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        print(f"\n사이트 접속: {site['url']}")
        driver.get(site["login"])
        time.sleep(8)

        # 로그인 (hongsthetic과 reanswer 둘 다 대응)
        try:
            driver.find_element(By.NAME, "member_id").send_keys(site["id"])
            driver.find_element(By.NAME, "member_passwd").send_keys(site["pw"])
        except:
            driver.find_element(By.NAME, "user_id").send_keys(site["id"])
            driver.find_element(By.NAME, "user_pw").send_keys(site["pw"])
        
        driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], a.btnSubmit").click()
        time.sleep(10)

        # 100개 포스팅
        for i in range(100):
            driver.get(site["url"])
            time.sleep(6)
            
            driver.find_element(By.LINK_TEXT, "글쓰기").click()
            time.sleep(6)

            a = random.choice(keywords["a"])
            b = random.choice(keywords["b"])
            c = random.choice(keywords["c"])
            title = f"{a} {b} {c}"

            driver.find_element(By.NAME, "subject").send_keys(title)
            driver.find_element(By.NAME, "content").send_keys(content)

            driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
            time.sleep(12)

            url = driver.current_url
            total += 1
            
            with open("realtime_links.txt", "a", encoding="utf-8") as f:
                f.write(f"{total}. {datetime.now().strftime('%H:%M:%S')} | {title} | {url}\n")
            
            print(f"성공 {total}개: {title} → {url}")

    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        driver.quit()

print(f"\n완료! 총 {total}개 포스팅 성공!")
print("realtime_links.txt 파일에 모든 링크 저장됨")
