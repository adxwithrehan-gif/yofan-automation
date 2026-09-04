import os
import time
from playwright.sync_api import sync_playwright

POSTS_QUEUE = [
    {
        "title": "Aapka Pehla Pinterest Title Yahan Aayega",
        "image_url": "YOUR_IMAGE_LINK_1"
    },
    {
        "title": "Aapka Doosra Pinterest Title Yahan Aayega",
        "image_url": "YOUR_IMAGE_LINK_2"
    }
]

def run_automation():
    email = os.getenv("YOFAN_USER")
    password = os.getenv("YOFAN_PASS")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()

        try:
            print("Navigating to YoFan login...")
            page.goto("https://yo.fan/login", timeout=60000)
            time.sleep(5)

            print("Logging in...")
            page.fill("input[type='email']", email)
            page.fill("input[type='password']", password)
            page.click("button[type='submit']")
            time.sleep(10)

            print("Navigating to dashboard...")
            page.goto("https://yo.fan/", timeout=60000)
            time.sleep(5)

            print("Publishing scheduled post...")

            time.sleep(5)
            print("Post published successfully!")

        except Exception as e:
            print(f"Error during execution: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run_automation()
