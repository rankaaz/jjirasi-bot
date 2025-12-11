from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
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
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

open("realtime_links.txt", "w", encoding="utf-8").close()

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
        driver.get(site["login"])
        time.sleep(8)
        try:
            driver.find_element(By.NAME, "member_id").send_keys(site["id"])
            driver.find_element(By.NAME, "member_passwd").send_keys(site["pw"])
        except:
            driver.find_element(By.NAME, "user_id").send_keys(site["id"])
            driver.find_element(By.NAME, "user_pw").send_keys(site["pw"])
        driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()
        time.sleep(10)

        for i in range(100):
            try:
                # 1. 글쓰기 전에 alert 있으면 무조건 "아니오" 클릭
                try:
                    alert = driver.switch_to.alert
                    print("alert 감지 → '아니오' 클릭")
                    alert.dismiss()  # "아니오" 클릭
                    time.sleep(2)
                except NoAlertPresentException:
                    pass

                driver.get(site["url"])
                time.sleep(6)
                driver.find_element(By.LINK_TEXT, "글쓰기").click()
                time.sleep(8)

                # 2. 제목 입력
                driver.find_element(By.NAME, "subject").clear()
                a = random.choice(keywords["a"])
                b = random.choice(keywords["b"])
                c = random.choice(keywords["c"])
                title = f"{a} {b} {c}"
                driver.find_element(By.NAME, "subject").send_keys(title)

                # 3. 내용 입력 (iframe 있으면 무조건 들어감)
                try:
                    iframe = driver.find_element(By.CSS_SELECTOR, "iframe")
                    driver.switch_to.frame(iframe)
                    driver.find_element(By.TAG_NAME, "body").clear()
                    driver.find_element(By.TAG_NAME, "body").send_keys(content)
                    driver.switch_to.default_content()
                except:
                    # iframe 없으면 일반 textarea
                    driver.find_element(By.NAME, "content").clear()
                    driver.find_element(By.NAME, "content").send_keys(content)

                # 4. 등록
                driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
                time.sleep(12)

                url = driver.current_url
                total += 1
                with open("realtime_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {url}\n")
                print(f"성공 {total}개: {title}")

            except UnexpectedAlertPresentException:
                print("alert 무시하고 계속")
                try: driver.switch_to.alert.dismiss()
                except: pass
                time.sleep(3)
                continue
            except Exception as e:
                print(f"포스팅 실패 {i+1}회: {e}")
                traceback.print_exc()
                time.sleep(10)
                continue

    except Exception as e:
        print(f"전체 실패: {e}")
        traceback.print_exc()
    finally:
        driver.quit()

print(f"\n최종 완료! 총 {total}개 성공")
