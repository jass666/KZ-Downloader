from playwright.sync_api import sync_playwright
import csv, time, re

PAGE_URL = "https://www.linkedin.com/company/TATA-MOTORS/posts/"
MAX_SCROLLS = 80

def clean_post_url(url):
    m = re.search(r"(https://www\.linkedin\.com/feed/update/[^/?#]+)", url)
    return m.group(1) if m else url.split("?")[0]

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="linkedin_browser_profile",
        headless=False,
        viewport={"width": 1366, "height": 900}
    )

    page = browser.new_page()
    page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=60000)

    input("Login if needed, open the posts/videos page, then press ENTER here...")

    found = set()

    for i in range(MAX_SCROLLS):
        posts = page.locator("div.feed-shared-update-v2").all()

        for post in posts:
            try:
                has_video = post.locator("video").count() > 0
                if not has_video:
                    continue

                links = post.locator("a[href*='/feed/update/']").all()
                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        found.add(clean_post_url(href))
            except:
                pass

        print(f"Scroll {i+1}/{MAX_SCROLLS} | Video posts found: {len(found)}")
        page.mouse.wheel(0, 2500)
        time.sleep(2.5)

    browser.close()

with open("linkedin_video_posts.txt", "w", encoding="utf-8") as f:
    for url in sorted(found):
        f.write(url + "\n")

with open("linkedin_video_posts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["post_url"])
    for url in sorted(found):
        writer.writerow([url])

print(f"\nDone. Saved {len(found)} video post links.")
print("Files: linkedin_video_posts.txt and linkedin_video_posts.csv")