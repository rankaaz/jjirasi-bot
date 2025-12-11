from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time, random
from datetime import datetime

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

open("realtime_links.txt", "w", encoding="utf-8").close()

sites = []
with open("sites = []
with open("sites.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            p = line.split("|")
            sites.append({"write_url": p[0], "id": p[1], "pw": p[2], "login": p[3]})

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
    wait = WebDriverWait(driver, 30)
    
    try:
        # 1. 진짜 로그인 (JS 강제 클릭)
        driver.get(site["login"])
        time.sleep(10)
        driver.find_element(By.NAME, "member_id").send_keys(site["id"])
        driver.find_element(By.NAME, "member_passwd").send_keys(site["pw"])
        driver.execute_script("document.querySelector('a.btnSubmit').click();")
        time.sleep(20)  # 로그인 완료까지 충분히 기다림

        # 2. 100개 반복
        for _ in range(100):
            try:
                driver.get(site["write_url"])
                time.sleep(10)

                # alert 있으면 취소
                try:
                    wait.until(EC.alert_is_present(), timeout=5)
                    driver.switch_to.alert.dismiss()
                    time.sleep(3)
                except:
                    pass

                # 제목
                title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"
                subject = wait.until(EC.element_to_be_clickable((By.NAME, "subject")))
                driver.execute_script("arguments[0].scrollIntoView(true);", subject)
                subject.send_keys(title)

                # 내용
                try:
                    iframe = driver.find_element(By.TAG_NAME, "iframe")
                    driver.switch_to.frame(iframe)
                    driver.find_element(By.TAG_NAME, "body").clear()
                    driver.find_element(By.TAG_NAME, "body").send_keys(content)
                    driver.switch_to.default_content()
                except:
                    driver.find_element(By.NAME, "content").clear()
                    driver.find_element(By.NAME, "content").send_keys(content)

                # 등록 (JS 강제 클릭)
                driver.execute_script("document.querySelector('input[type=\\\"submit\\\"], button, a').click();")
                time.sleep(15)

                url = driver.current_url
                total += 1
                with open("realtime_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {url}\n")
                print(f"성공 {total}개 → {url}")

            except Exception as e:
                print(f"실패 → 다음: {e}")
                time.sleep(8)
                continue

    finally:
        driver.quit()

print(f"\n완료! 총 {total}개 성공")
