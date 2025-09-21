import asyncio
from playwright.async_api import async_playwright
import os
import json
from urllib.parse import urljoin

# ---------------- CONFIG ----------------
IS_AUTHOR = False  # Toggle between live and author
HEADLESS = True    # True = headless browser for speed

AUTHOR_BASE = "https://author.company.com"
LOGIN_PATH = "/libs/granite/core/content/login.html"
USERNAME = "your_username"
PASSWORD = "your_password"
LOGIN_TRIGGER_SELECTOR = "div.login-toggle"
USERNAME_SELECTOR = "input[name='username']"
PASSWORD_SELECTOR = "input[name='password']"
SUBMIT_SELECTOR = "button[type='submit']"

INPUT_FILE = "urls.txt"
OUTPUT_FILE = "results.json"
CONFIG_FILE = "config.json"
# -----------------------------------------

async def accept_cookies(page):
    try:
        await page.wait_for_selector(".button_accept", timeout=5000)
        await page.click(".button_accept")
        await page.wait_for_timeout(1000)
        print("✅ Cookies accepted.")
    except Exception:
        print("⚠️ Cookie accept button not found or already accepted.")

async def extract_assets_from_page(page, base_url):
    """Extract assets with src/srcset starting with /content/dam"""
    matches = set()
    elements = await page.query_selector_all("[src], [srcset]")

    for element in elements:
        src = await element.get_attribute("src")
        srcset = await element.get_attribute("srcset")

        if src and src.startswith("/content/dam"):
            matches.add(urljoin(base_url, src))

        if srcset:
            for item in srcset.split(","):
                path = item.strip().split(" ")[0]
                if path.startswith("/content/dam"):
                    matches.add(urljoin(base_url, path))

    return matches

def segregate_assets(assets, unsupported_exts):
    supported, unsupported = [], []
    for asset in assets:
        ext = os.path.splitext(asset.split("?")[0])[1].lower().lstrip(".")
        if ext in unsupported_exts:
            unsupported.append(asset)
        else:
            supported.append(asset)
    return supported, unsupported

async def process_url(playwright, url):
    browser = await playwright.chromium.launch(headless=HEADLESS)
    context = await browser.new_context()
    page = await context.new_page()

    # Handle author login if needed
    if IS_AUTHOR:
        login_url = urljoin(AUTHOR_BASE, LOGIN_PATH)
        print(f"🔐 Logging in at {login_url}")
        await page.goto(login_url)
        await page.click(LOGIN_TRIGGER_SELECTOR)
        await page.fill(USERNAME_SELECTOR, USERNAME)
        await page.fill(PASSWORD_SELECTOR, PASSWORD)
        await page.click(SUBMIT_SELECTOR)
        await page.wait_for_load_state("networkidle")

    # Navigate to the target URL
    target_url = url
    if IS_AUTHOR:
        target_url = urljoin(AUTHOR_BASE, url)

    try:
        print(f"🌐 Navigating to {target_url}")
        await page.goto(target_url, timeout=60000)
        await accept_cookies(page)
        matches = await extract_assets_from_page(page, target_url)
        print(f"✅ Extracted {len(matches)} assets from {target_url}")
    except Exception as e:
        print(f"❌ Error processing {target_url}: {e}")
        matches = set()

    await browser.close()
    return matches

async def main():
    print("🚀 Starting asset extraction...")

    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file '{INPUT_FILE}' not found.")
        return

    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Config file '{CONFIG_FILE}' not found.")
        return

    # Load config
    with open(CONFIG_FILE, "r", encoding="utf-8") as cfg:
        config = json.load(cfg)
        unsupported_exts = set(config.get("unsupported_extensions", []))

    # Load URLs
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("⚠️ No URLs found in input file.")
        return

    results = {}
    async with async_playwright() as playwright:
        for url in urls:
            print(f"\n➡️ Processing {url}")
            matches = await process_url(playwright, url)
            supported, unsupported = segregate_assets(matches, unsupported_exts)

            results[url] = {
                "scene7_supported": sorted(supported),
                "scene7_unsupported": sorted(unsupported),
            }

    # Save output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
        json.dump(results, out_file, indent=4, ensure_ascii=False)

    print(f"\n✅ Done! Results saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
