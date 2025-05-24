import asyncio
from playwright.async_api import async_playwright
import os

INPUT_FILE = "urls.txt"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.txt")

async def accept_cookies(page):
    try:
        await page.wait_for_selector(".button_test", timeout=5000)
        await page.click(".button_test")
        await page.wait_for_timeout(1000)
        print("✅ Cookies accepted.")
    except Exception:
        print("⚠️  Cookie accept button not found or already accepted.")

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

async def main():
    print("🚀 Starting extraction script...")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Created output directory: {OUTPUT_DIR}")

    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file '{INPUT_FILE}' not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("⚠️ No URLs found in input file.")
        return

    async with async_playwright() as playwright:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
            for url in urls:
                print(f"\n➡️  Processing {url}")
                matches = await extract_assets(playwright, url)

                out_file.write(f"{url}:\n\n")
                for match in sorted(matches):
                    out_file.write(f"{match}\n")
                out_file.write("\n")

    print(f"\n✅ Done! Results saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
