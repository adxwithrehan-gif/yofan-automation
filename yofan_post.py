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
      print("Navigating to YoFan homepage...")
      page.goto("https://yo.fan/", timeout=60000)
      page.wait_for_load_state("networkidle")
      time.sleep(5)

      # Agar login button screen par ho toh click karein
      try:
        login_nav = page.locator(
            "a:has-text('Login'), button:has-text('Login'),"
            " a:has-text('Sign in'), a[href*='login']"
        ).first
        if login_nav.is_visible():
          login_nav.click()
          time.sleep(3)
      except:
        pass

      print("Filling login credentials...")
      email_input = page.locator(
          "input[type='email'], input[name='email'], input[type='text'],"
          " input:not([type='password']):not([type='hidden'])"
      ).first
      email_input.fill(email)

      pass_input = page.locator(
          "input[type='password'], input[name='password']"
      ).first
      pass_input.fill(password)

      submit_btn = page.locator(
          "button[type='submit'], button:has-text('Login'),"
          " button:has-text('Sign in'), button:has-text('Log in')"
      ).first
      submit_btn.click()
      time.sleep(10)

      # Har run par pehli available pin ka data fetch karna aur post process
      for i, pin_url in enumerate(pin_links[:1]):
        title, image_url = get_pinterest_data(pin_url)

        if not image_url:
          print(f"[{i+1}] ❌ Data fetch nahi ho saka is pin ke liye: {pin_url}")
          continue

        print(f"\n[🚀 Publishing Post]")
        print(f"Title: {title}")
        print(f"Image: {image_url}")

        page.goto("https://yo.fan/", timeout=60000)
        page.wait_for_load_state("networkidle")
        time.sleep(5)

        print("[✔] Successfully logged in and ready for posting!")

    except Exception as e:
      print(f"❌ Error during execution: {e}")
      try:
        print("Page HTML snippet:", page.content()[:1000])
      except:
        pass
    finally:
      browser.close()


if __name__ == "__main__":
  run_yofan_automation()
