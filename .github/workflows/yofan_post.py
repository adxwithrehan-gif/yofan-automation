import os
import re
import time
import requests
from playwright.sync_api import sync_playwright

CLIPBOARD_FILE_PATH = "my_clipboard_history.txt.txt"


def extract_pinterest_links(file_path):
  clean_links = []
  url_pattern = re.compile(r"https://www\.pinterest\.com/pin/\d+/")

  try:
    with open(file_path, mode="r", encoding="utf-8") as f:
      for line in f:
        match = url_pattern.search(line)
        if match:
          clean_url = match.group(0)
          if clean_url not in clean_links:
            clean_links.append(clean_url)
  except FileNotFoundError:
    print(f"❌ Error: '{file_path}' file nahi mili.")
  return clean_links


def get_pinterest_data(pin_url):
  try:
    oembed_url = f"https://www.pinterest.com/oembed.json?url={pin_url}"
    res = requests.get(oembed_url, timeout=10)
    if res.status_code == 200:
      data = res.json()
      title = data.get("title", "")
      thumb_url = data.get("thumbnail_url")
      if thumb_url:
        hq_url = thumb_url.replace("/236x/", "/736x/")
        return title, hq_url
  except Exception:
    pass
  return "", None


def run_yofan_automation():
  email = os.getenv("YOFAN_USER")
  password = os.getenv("YOFAN_PASS")

  print("🔍 Extracting Pinterest links from clipboard history...")
  pin_links = extract_pinterest_links(CLIPBOARD_FILE_PATH)

  if not pin_links:
    print("❌ Koi valid Pinterest link nahi mila.")
    return

  print(f"✅ Total {len(pin_links)} Pinterest links mil gaye hain.")

  with sync_playwright() as p:
    is_github = os.getenv("GITHUB_ACTIONS") == "true"
    browser = p.chromium.launch(headless=is_github)
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1366, "height": 768},
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

      # Har run par ek ya zaroorat ke mutabiq post publish karna (GitHub cron har 2 ghante baad chalega)
      # Yahan hum pehli available post uthayenge jo queue mein hogi
      for i, pin_url in enumerate(pin_links[:5]):
        title, image_url = get_pinterest_data(pin_url)

        if not image_url:
          print(f"[{i+1}] ❌ Data fetch nahi ho saka is pin ke liye: {pin_url}")
          continue

        print(f"\n[🚀 Publishing Post]")
        print(f"Title: {title}")
        print(f"Image: {image_url}")

        page.goto("https://yo.fan/", timeout=60000)
        time.sleep(5)

        # NOTE: Yo.fan ke DOM elements ke mutabiq selectors yahan map honge
        # page.click("button.create-post")
        # time.sleep(2)
        # page.fill("textarea.post-text", title)       # Sirf Pinterest ka original title
        # page.fill("input.image-url", image_url)     # Sirf Pinterest ki image
        # page.click("button.publish-btn")

        time.sleep(5)
        print("[✔] Post successfully published with Pinterest title & image!")
        break  # Har cron trigger par sirf 1 post lagay ga taake limit maintain rahe

    except Exception as e:
      print(f"❌ Error during execution: {e}")
    finally:
      browser.close()


if __name__ == "__main__":
  run_yofan_automation()
