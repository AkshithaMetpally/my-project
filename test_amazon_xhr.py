import asyncio
from playwright.async_api import async_playwright
import time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        requests_urls = []
        page.on("request", lambda request: requests_urls.append(request.url))

        print("Navigating to Amazon...")
        # Use stealth directly via script injection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        await page.goto("https://www.amazon.in/iPhone-17-256-Promotion-Resistance/dp/B0FQFQ576F/", wait_until="networkidle")
        
        print(f"Captured {len(requests_urls)} requests.")
        
        # print any request containing "review"
        print("Requests with 'review':")
        for u in requests_urls:
            if 'review' in u.lower():
                print(u)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
