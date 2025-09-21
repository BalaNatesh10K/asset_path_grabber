import asyncio
from playwright.async_api import async_playwright
import os
import json

INPUT_FILE = "urls.txt"
OUTPUT_FILE = "results.json"
CONFIG_FILE = "config.json"

async def accept_cookies(page):
    try:
        await page.wait_for_selector(".button_accept", timeout=5000)
        await page.click(".button_accept")
        await page.wait_for_timeout(1000)
        print("✅ Cookies accepted.")
    except Exception:
        print("⚠️ Cookie accept button not found or already accepted.")

async def extract_assets(playwright, url):
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()

    matches = set()

    try:
        print(f"🌐 Navigating to {url}")
        await page.goto(url, timeout=60000)
        await accept_cookies(page)

        elements = await page.query_selector_all("[src], [srcset]")
        print(f"🔍 Found {len(elements)} elements with src or srcset")

        for element in elements:
            src = await element.get_attribute("src")
            srcset = await element.get_attribute("srcset")

            if src and src.startswith("/content/dam"):
                matches.add(src)

            if srcset:
                for item in srcset.split(","):
                    path = item.strip().split(" ")[0]
                    if path.startswith("/content/dam"):
                        matches.add(path)

        print(f"✅ Extracted {len(matches)} matching paths from {url}")

    except Exception as e:
        print(f"❌ Error processing {url}: {e}")

    await browser.close()
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

async def main():
    print("🚀 Starting extraction script...")

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

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("⚠️ No URLs found in input file.")
        return

    results = {}

    async with async_playwright() as playwright:
        for url in urls:
            print(f"\n➡️ Processing {url}")
            matches = await extract_assets(playwright, url)

            supported, unsupported = segregate_assets(matches, unsupported_exts)

            results[url] = {
                "scene7_supported": sorted(supported),
                "scene7_unsupported": sorted(unsupported),
            }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
        json.dump(results, out_file, indent=4, ensure_ascii=False)

    print(f"\n✅ Done! Results saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
