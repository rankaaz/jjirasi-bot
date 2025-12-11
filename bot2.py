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

# 실시간 파일 초기화
open("realtime_links.txt", "w", encoding="utf-8").close()

sites = []
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
    wait = WebDriverWait(driver, 20)
    
    try:
        # 로그인
        driver.get(site["login"])
        time.sleep(8)
        driver.find_element(By.NAME, "member_id").send_keys(site["id"])
        driver.find_element(By.NAME, "member_passwd").send_keys(site["pw"])
        driver.find_element(By.CSS_SELECTOR, "button, input[type='submit'], a.btnSubmit").click()
        time.sleep(12)

        for _ in range(100):
            try:
                driver.get(site["write_url"])
                time.sleep(8)

                # alert 있으면 취소
                try:
                    wait.until(EC.alert_is_present())
                    driver.switch_to.alert.dismiss()
                    print("alert → 취소 클릭")
                    time.sleep(3)
                except:
                    pass

                # 제목
                title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"
                driver.find_element(By.NAME, "subject").clear()
                driver.find_element(By.NAME, "subject").send_keys(title)

                # 내용 (iframe 먼저)
                try:
                    iframe = driver.find_element(By.TAG_NAME, "iframe")
                    driver.switch_to.frame(iframe)
                    driver.find_element(By.TAG_NAME, "body").clear()
                    driver.find_element(By.TAG_NAME, "body").send_keys(content)
                    driver.switch_to.default_content()
                except:
                    driver.find_element(By.NAME, "content").clear()
                    driver.find_element(By.NAME, "content").send_keys(content)

                # 등록 버튼 (input, button, a 태그 모두 대응)
                driver.find_element(By.XPATH, "//input[@type='submit'] | //button[contains(text(),'등록')] | //a[contains(text(),'등록')]").click()
                time.sleep(15)

                url = driver.current_url
                total += 1
                with open("realtime_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {url}\n")
                print(f"성공 {total}개 → {url}")

            except Exception as e:
                print(f"한 개 실패 → 다음으로: {e}")
                time.sleep(8)
                continue

    finally:
        driver.quit()

print(f"\n완료! 총 {total}개 성공")
