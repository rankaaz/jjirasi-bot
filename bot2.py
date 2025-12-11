from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
from datetime import datetime

# Chrome 옵션
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 실시간 링크 파일 초기화
open("realtime_links.txt", "w", encoding="utf-8").close()

# sites.txt 로드 (write.html 그대로 사용)
sites = []
with open("sites.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split("|")
            sites.append({
                "write_url": parts[0],
                "id": parts[1],
                "pw": parts[2],
                "login": parts[3]
            })

# 키워드 로드
keywords = {"a": [], "b": [], "c": []}
with open("keywords.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "|" in line:
            k, v = line.strip().split("|", 1)
            keywords[k] = [w.strip() for w in v.split(",")]

# 본문 내용 로드
content = open("contents.txt", "r", encoding="utf-8").read().strip()

total = 0

for site in sites:
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # 1. 로그인 (두 사이트 모두 member_id / member_passwd)
        driver.get(site["login"])
        time.sleep(10)
        driver.find_element(By.NAME, "member_id").send_keys(site["id"])
        driver.find_element(By.NAME, "member_passwd").send_keys(site["pw"])
        driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()
        time.sleep(15)

        # 2. 100개 반복
        for _ in range(100):
            try:
                # 바로 write.html 접속
                driver.get(site["write_url"])
                time.sleep(10)

                # alert 뜨면 무조건 취소 (기록 있으면 뜸)
                try:
                    wait.until(EC.alert_is_present())
                    driver.switch_to.alert.dismiss()
                    print("기록 alert → 취소 클릭")
                    time.sleep(5)
                except TimeoutException:
                    pass  # alert 없으면 바로 진행

                # 제목 입력
                title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"
                subject = driver.find_element(By.NAME, "subject")
                subject.clear()
                subject.send_keys(title)

                # 내용 입력 (iframe 자동 처리)
                try:
                    iframe = driver.find_element(By.TAG_NAME, "iframe")
                    driver.switch_to.frame(iframe)
                    driver.find_element(By.TAG_NAME, "body").clear()
                    driver.find_element(By.TAG_NAME, "body").send_keys(content)
                    driver.switch_to.default_content()
                except:
                    driver.find_element(By.NAME, "content").clear()
                    driver.find_element(By.NAME, "content").send_keys(content)

                # 등록 버튼 클릭
                driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
                time.sleep(15)

                url = driver.current_url
                total += 1
                with open("realtime_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {url}\n")
                print(f"성공 {total}개: {url}")

            except Exception as e:
                print(f"한 개 실패 → 다음으로: {e}")
                time.sleep(10)
                continue

    except Exception as e:
        print(f"사이트 전체 실패: {e}")
    finally:
        driver.quit()

print(f"\n완료! 총 {total}개 게시물 작성 성공")
