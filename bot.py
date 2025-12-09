from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time, random
from datetime import datetime

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

open("realtime_links.txt", "w").close()

sites = [line.strip().split("|") for line in open("sites.txt") if line.strip()]
keywords = {"a": [], "b": [], "c": []}
for line in open("keywords.txt", encoding="utf-8"):
    if "|" in line:
        k, v = line.strip().split("|", 1)
        keywords[k] = [x.strip() for x in v.split(",")]

content = open("contents.txt", "r", encoding="utf-8").read().strip()

total = 0
for site in sites:
    url, _, _, uid, upw, login_url = site
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(login_url)
        time.sleep(8)

        # 로그인 입력 (모든 input 잡음)
        driver.execute_script(f"""
            let idField = document.querySelector('input[type="text"], input[type="email"], input[name*="id"], input[id*="id"]');
            let pwField = document.querySelector('input[type="password"]');
            if(idField) idField.value = '{uid}';
            if(pwField) pwField.value = '{upw}';
        """)

        # 로그인 버튼 클릭 (순수 JS로 안전하게)
        driver.execute_script("""
            let btns = document.querySelectorAll('button, input[type="submit"], a');
            for(let b of btns){
                if(b.innerText.includes('로그인') || b.value.includes('로그인') || b.type === 'submit'){
                    b.click(); break;
                }
            }
        """)
        time.sleep(12)

        for i in range(100):
            driver.get(url)
            time.sleep(6)

            # 글쓰기 버튼 클릭
            try:
                driver.find_element(By.PARTIAL_LINK_TEXT, "글쓰기").click()
            except:
                driver.execute_script("document.querySelector('a[href*="write"], a:contains(\"글쓰기\")')?.click();")
            time.sleep(6)

            # 제목
            title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"
            driver.find_element(By.CSS_SELECTOR, "input[name='subject'], input[name*='subject'], input[name*='title']").send_keys(title)

            # 내용
            driver.find_element(By.CSS_SELECTOR, "textarea[name='content'], textarea[name*='content']").send_keys(content)

            # 등록
            driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
            time.sleep(12)

            link = driver.current_url
            if len(link) > 30 and "list" not in link.lower():
                total += 1
                with open("realtime_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {link}\n")
                print(f"성공 {total}개: {link}")

    except Exception as e:
        print("사이트 에러:", str(e)[:200])
    finally:
        driver.quit()

print(f"최종 완료! 총 {total}개 성공")
