from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random, re
from datetime import datetime

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

open("realtime_links.txt", "w").close()

sites = [line.strip().split("|") for line in open("sites.txt") if line.strip() and not line.startswith("#")]
keywords = {"a": [], "b": [], "c": []}
for line in open("keywords.txt", encoding="utf-8"):
    if "|" in line:
        k, v = line.strip().split("|", 1)
        keywords[k] = v.split(",")

content = open("contents.txt", "r", encoding="utf-8").read().strip()

total = 0
for site in sites:
    url, _, _, uid, upw, login_url = site
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    
    try:
        driver.get(login_url)
        time.sleep(8)

        # 로그인: 가능한 모든 방법 총동원
        driver.execute_script(f"""
            let id_inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[name*="id"], input[id*="id"]');
            if(id_inputs.length > 0) id_inputs[0].value = '{uid}';
            let pw_inputs = document.querySelectorAll('input[type="password"]');
            if(pw_inputs.length > 0) pw_inputs[0].value = '{upw}';
        """)
        time.sleep(2)
        driver.execute_script("""
            let btn = document.querySelector('button[type="submit"], input[type="submit"], button:contains("로그인"), a:contains("로그인")');
            if(btn) btn.click();
        """)
        time.sleep(12)

        # 100개 반복
        for i in range(100):
            driver.get(url)
            time.sleep(6)

            # 글쓰기 버튼: 가능한 모든 경우 다 잡음
            write_clicked = False
            for text in ["글쓰기", "새글쓰기", "작성하기", "등록하기", "쓰기"]:
                try:
                    btn = driver.find_element(By.PARTIAL_LINK_TEXT, text)
                    driver.execute_script("arguments[0].click();", btn)
                    write_clicked = True
                    break
                except:
                    continue
            if not write_clicked:
                driver.execute_script("""
                    let links = document.querySelectorAll('a[href*="write"], a[href*="bbs/write"], a[href*="board/write"]');
                    if(links.length > 0) links[0].click();
                """)
            time.sleep(7)

            # 제목 랜덤 생성
            title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"

            # 제목 입력: 가능한 모든 name/id 잡음
            driver.execute_script(f"""
                let subj = document.querySelector('input[name="subject"], input[name="wr_subject"], input[name="title"], input[id*="subject"]');
                if(subj) subj.value = '{title}';
            """)

            # 내용 입력: textarea 또는 contenteditable 모두 지원
            driver.execute_script(f"""
                let content_area = document.querySelector('textarea[name="content"], textarea[name="wr_content"], div[contenteditable="true"]');
                if(content_area) {{
                    if(content_area.tagName === 'TEXTAREA') content_area.value = `{content.replace('`', '\\`')}`;
                    else content_area.innerHTML = `{content.replace('`', '\\`')}`;
                }}
            """)

            time.sleep(3)

            # 등록 버튼 클릭: 모든 가능성 다 시도
            driver.execute_script("""
                let submit = document.querySelector('button[type="submit"], input[type="submit"], button:contains("등록"), button:contains("작성"), a:contains("등록")');
                if(submit) submit.click();
            """)
            time.sleep(12)

            # 성공 여부 확인
            current = driver.current_url
            if "list" not in current and len(current) > 30:
                total += 1
                with open("realtime_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {current}\n")
                print(f"성공 {total}개: {current}")

            time.sleep(random.uniform(5, 12))  # 자연스럽게

    except Exception as e:
        print("사이트 에러:", e)
    finally:
        driver.quit()

print(f"\n최종 완료! 총 {total}개 포스팅 성공")
