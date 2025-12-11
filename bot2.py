from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
from datetime import datetime

# Chrome 옵션
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 실시간 링크 파일 초기화 (빈 파일 대신 기본 텍스트 입력)
with open("realtime_links.txt", "w", encoding="utf-8") as f:
    f.write("=== 글 작성 시작 ===\n")

# 사이트 로드
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
        # 1) 로그인
        driver.get(site["login"])
        time.sleep(7)

        driver.find_element(By.NAME, "member_id").send_keys(site["id"])
        driver.find_element(By.NAME, "member_passwd").send_keys(site["pw"])

        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except:
            login_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")

        login_btn.click()
        time.sleep(10)

        # 2) 100개 반복 작성
        for _ in range(100):

            try:
                driver.get(site["write_url"])
                time.sleep(8)

                try:
                    wait.until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.dismiss()
                    print("경고창 감지 → 취소")
                    time.sleep(3)
                except:
                    pass

                title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"

                subject = wait.until(
                    EC.presence_of_element_located((By.NAME, "subject"))
                )
                subject.clear()
                subject.send_keys(title)

                body_written = False
                iframes = driver.find_elements(By.TAG_NAME, "iframe")

                if iframes:
                    try:
                        driver.switch_to.frame(iframes[0])
                        body = driver.find_element(By.TAG_NAME, "body")
                        body.clear()
                        body.send_keys(content)
                        body_written = True
                        driver.switch_to.default_content()
                    except:
                        driver.switch_to.default_content()

                if not body_written:
                    try:
                        textarea = driver.find_element(By.NAME, "content")
                        textarea.clear()
                        textarea.send_keys(content)
                        body_written = True
                    except:
                        print("본문 입력 실패 → 넘어감")
                        continue

                try:
                    submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                except NoSuchElementException:
                    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

                submit_btn.click()
                time.sleep(8)

                url = driver.current_url
                total += 1

                with open("realtime_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {url}\n")

                print(f"성공 {total} → {url}")

            except Exception as e:
                print("개별 작성 실패 → 다음 반복:", e)
                time.sleep(5)
                continue

    except Exception as e:
        print("사이트 전체 실패:", e)

    finally:
        driver.quit()

print(f"\n=== 완료: 총 {total}개 작성 성공 ===")
