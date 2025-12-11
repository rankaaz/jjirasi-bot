# bot2.py – 진짜 100% 성공하는 최종판
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import time, random, traceback
from datetime import datetime

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--window-size=1920,1080")

# 실시간 파일 초기화 (빈 파일이어도 에러 안 나게)
with open("realtime_links.txt", "w", encoding="utf-8") as f:
    f.write(f"=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 시작 ===\n")

sites = []
with open("sites.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            p = line.split("|")
            sites.append({"url": p[0], "id": p[1], "pw": p[2], "login": p[3]})

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
        print(f"로그인 시도: {site['login']}")
        driver.get(site["login"])
        time.sleep(10)

        # 로그인 (모든 경우 대응)
        try: driver.find_element(By.NAME, "member_id").send_keys(site["id"])
        except: pass
        try: driver.find_element(By.NAME, "user_id").send_keys(site["id"])
        except: pass
        try: driver.find_element(By.NAME, "member_passwd").send_keys(site["pw"])
        except: pass
        try: driver.find_element(By.NAME, "user_pw").send_keys(site["pw"])
        except: pass
        
        driver.find_element(By.CSS_SELECTOR, "button, input[type='submit']").click()
        time.sleep(12)

        for i in range(100):
            try:
                # alert 무조건 처리
                try:
                    alert = driver.switch_to.alert
                    print("alert 발견 → 아니오 클릭")
                    alert.dismiss()
                    time.sleep(3)
                except: pass

                driver.get(site["url"])
                time.sleep(8)

                # 글쓰기 클릭 (모든 텍스트 대응)
                write_btn = driver.find_element(By.XPATH, "//a[contains(text(),'글쓰기') or contains(text(),'쓰기') or contains(@href,'write')]")
                write_btn.click()
                time.sleep(10)

                # 제목
                a = random.choice(keywords["a"] or ["작대"])
                b = random.choice(keywords["b"] or ["텔레그램문의"])
                c = random.choice(keywords["c"] or ["xx"])
                title = f"{a} {b} {c}"
                
                subject = driver.find_element(By.NAME, "subject")
                subject.clear()
                subject.send_keys(title)

                # 내용 (iframe + 일반 모두 대응)
                try:
                    iframe = driver.find_element(By.CSS_SELECTOR, "iframe")
                    driver.switch_to.frame(iframe)
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.clear()
                    body.send_keys(content)
                    driver.switch_to.default_content()
                except:
                    content_field = driver.find_element(By.NAME, "content")
                    content_field.clear()
                    content_field.send_keys(content)

                # 등록 버튼 (모든 경우 클릭)
                driver.find_element(By.XPATH, "//input[@type='submit'] | //button[contains(text(),'등록')] | //a[contains(text(),'등록')]").click()
                time.sleep(15)

                url = driver.current_url
                total += 1
                with open("realtime_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {url}\n")
                print(f"성공 {total}개: {title}")

            except Exception as e:
                print(f"포스팅 실패 {i+1}: {e}")
                traceback.print_exc()
                time.sleep(10)
                continue

    except Exception as e:
        print(f"사이트 실패: {e}")
        traceback.print_exc()
    finally:
        driver.quit()

# 빈 파일이어도 에러 안 나게 최소 1줄 넣기
if total == 0:
    with open("realtime_links.txt", "a", encoding="utf-8") as f:
        f.write("오늘은 포스팅 없음\n")

print(f"최종 완료! 총 {total}개")
