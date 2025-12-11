# bot2.py – Playwright 버전 (카페24 완벽 통과)
from playwright.sync_api import sync_playwright
import time, random
from datetime import datetime

# 파일 초기화
open("realtime_links.txt", "w", encoding="utf-8").close()

# sites.txt 로드
sites = []
with open("sites.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            p = line.split("|")
            sites.append({"write_url": p[0], "id": p[1], "pw": p[2], "login": p[3]})

# 키워드 로드
keywords = {"a": [], "b": [], "c": []}
with open("keywords.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "|" in line:
            k, v = line.strip().split("|", 1)
            keywords[k] = [w.strip() for w in v.split(",")]

content = open("contents.txt", "r", encoding="utf-8").read().strip()

total = 0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = context.new_page()

    for site in sites:
        try:
            # 로그인
            page.goto(site["login"])
            page.wait_for_load_state("networkidle")
            page.fill("input[name='member_id']", site["id"])
            page.fill("input[name='member_passwd']", site["pw"])
            page.click("a.btnSubmit")
            page.wait_for_load_state("networkidle")

            for _ in range(100):
                try:
                    page.goto(site["write_url"])
                    page.wait_for_load_state("networkidle")

                    # alert 있으면 취소
                    try:
                        page.on("dialog", lambda dialog: dialog.dismiss())
                        page.wait_for_timeout(3000)
                    except:
                        pass

                    # 제목
                    title = f"{random.choice(keywords['a'])} {random.choice(keywords['b'])} {random.choice(keywords['c'])}"
                    page.fill("input[name='subject']", title)

                    # 내용 (iframe 처리)
                    try:
                        page.frame_locator("iframe").locator("body").fill(content)
                    except:
                        page.fill("textarea[name='content']", content)

                    # 등록 클릭
                    page.click("input[type='submit'], button:has-text('등록'), a:has-text('등록')")
                    page.wait_for_load_state("networkidle")

                    url = page.url
                    total += 1
                    with open("realtime_links.txt", "a", encoding="utf-8") as f:
                        f.write(f"{total}. {datetime.now():%H:%M:%S} | {title} | {url}\n")
                    print(f"성공 {total}개 → {url}")

                    time.sleep(8)

                except Exception as e:
                    print(f"한 개 실패 → 다음: {e}")
                    time.sleep(5)
                    continue

        except Exception as e:
            print(f"사이트 실패: {e}")

    browser.close()

print(f"\n완료! 총 {total}개 게시물 작성 성공")
