from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import time, random, traceback
from datetime import datetime

# 로컬 테스트용 (headless 끄기)
options = Options()
# options.add_argument("--headless")  # 로컬 테스트 시 주석 해제해서 브라우저 보이게
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--window-size=1920,1080")

# 파일 로드
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
with open("realtime_links.txt", "w", encoding="utf-8") as f:
    f.write(f"=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 로컬 테스트 ===\n")

for site in sites:
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        print(f"\n로그인 시도: {site['login']}")
        driver.get(site["login"])
        time.sleep(10)

        # 로그인 입력 (모든 경우 시도)
        try:
            driver.find_element(By.NAME, "member_id").send_keys(site["id"])
            driver.find_element(By.NAME, "member_passwd").send_keys(site["pw"])
            print("member_id / member_passwd 사용")
        except:
            driver.find_element(By.NAME, "user_id").send_keys(site["id"])
            driver.find_element(By.NAME, "user_pw").send_keys(site["pw"])
            print("user_id / user_pw 사용")
        
        login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], a[href*='login']")
        login_btn.click()
        time.sleep(15)

        # 로그인 성공 확인
        if "login" in driver.current_url.lower():
            print("로그인 실패 - ID/PW 또는 페이지 구조 확인!")
            continue
        print("로그인 성공!")

        # 포스팅 (새 탭으로 5개만 테스트 – 로컬에서 확인)
        for i in range(5):  # 로컬 테스트용 5개만
            try:
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(site["url"])
                time.sleep(8)

                write_btn = driver.find_element(By.XPATH, "//a[contains(text(),'글쓰기')] | //button[contains(text(),'글쓰기')]")
                write_btn.click()
                time.sleep(10)

                a = random.choice(keywords["a"])
                b = random.choice(keywords["b"])
                c = random.choice(keywords["c"])
                title = f"{a} {b} {c}"

                subject = driver.find_element(By.NAME, "subject")
                subject.clear()
                subject.send_keys(title)

                # 내용 입력 (iframe 대응)
                try:
                    iframe = driver.find_element(By.CSS_SELECTOR, "iframe")
                    driver.switch_to.frame(iframe)
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.clear()
                    body.send_keys(content)
                    driver.switch_to.default_content()
                    print("iframe 성공")
                except:
                    content_field = driver.find_element(By.NAME, "content")
                    content_field.clear()
                    content_field.send_keys(content)
                    print("textarea 성공")

                # alert 처리
                try:
                    alert = driver.switch_to.alert
                    alert.dismiss()
                    time.sleep(2)
                except:
                    pass

                submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                submit_btn.click()
                time.sleep(15)

                url = driver.current_url
                total += 1
                with open("realtime_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{total}. {datetime.now().strftime('%H:%M:%S')} | {title} | {url}\n")
                print(f"로컬 성공 {total}개: {url}")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"로컬 포스팅 실패 {i+1}: {e}")
                traceback.print_exc()
                try:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    pass
                time.sleep(10)
                continue

    except Exception as e:
        print(f"로컬 사이트 실패: {e}")
        traceback.print_exc()
    finally:
        driver.quit()

print(f"로컬 테스트 완료! 총 {total}개 성공")
