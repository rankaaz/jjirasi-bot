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

# 실시간 파일 초기화
with open("realtime_links.txt", "w", encoding="utf-8") as f:
    f.write(f"=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 시작 ===\n\n")

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
            k, v = line.split("|", 1)
            keywords[k] = [w.strip() for w in v.split(",")]

content = open("contents.txt", "r", encoding="utf-8").read().strip()

total = 0

for site in sites:
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(site["login"])
        time.sleep(10)
        
        # 로그인 (둘 다 시도)
        try:
            driver.find_element(By.NAME, "member_id").send_keys(site["id"])
            driver.find_element(By.NAME, "member_passwd").send_keys(site["pw"])
        except:
            driver.find_element(By.NAME, "user_id").send_keys(site["id"])
            driver.find_element(By.NAME, "user_pw").send_keys(site["pw"])
        
        driver.find_element(By.CSS_SELECTOR, "button, input[type='submit']").click()
        time.sleep(15)

        for _ in range(100):
            try:
                driver.get(site["url"])
                time.sleep(8)

                # 글쓰기 클릭 전에 무조건 alert 처리
                try:
                    WebDriverWait(driver, 5).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.dismiss()  # "아니오" 클릭
                    print("alert 처리 완료")
                    time.sleep(3)
                except:
                    pass

                driver.find_element(By.LINK_TEXT, "글쓰기").click()
                time.sleep(10)

                # 제목
                title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"
                driver.find_element(By.NAME, "subject").send_keys(title)

                # 내용 (iframe 자동 처리)
                try:
                    iframe = driver.find_element(By.TAG_NAME, "iframe")
                    driver.switch_to.frame(iframe)
                    driver.find_element(By.TAG_NAME, "body").send_keys(content)
                    driver.switch_to.default_content()
                except:
                    driver.find_element(By.NAME, "content").send_keys(content)

                # 등록
                driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
                time.sleep(15)

                url = driver.current_url
                total += 1
                with open("realtime_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {url}\n")
                print(f"성공 {total}개: {url}")

            except Exception as e:
                print(f"포스팅 실패: {e}")
                traceback.print_exc()
                time.sleep(10)
                continue

    except Exception as e:
        print(f"사이트 실패: {e}")
    finally:
        driver.quit()

print(f"최종 완료! 총 {total}개")
