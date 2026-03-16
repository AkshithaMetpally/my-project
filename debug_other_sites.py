import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def get_html(url, filename):
    print(f"Fetching {url}...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            await Stealth().apply_stealth_async(page)
            
            response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            if response:
                 print(f"Status for {url}: {response.status}")
                 
            # Scroll down to trigger lazy loading
            for i in range(10):
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(1)
                
            html = await page.content()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved {filename} ({len(html)} bytes)")
            await browser.close()
    except Exception as e:
         print(f"Error on {url}: {e}")

async def main():
    await get_html("https://www.nykaa.com/l-oreal-paris-revitalift-hyaluronic-acid-plumping-day-cream/p/823018", "debug_nykaa.html")
    await get_html("https://www.meesho.com/elegant-georgette-sarees/p/2i1o6h", "debug_meesho.html")
    await get_html("https://www.yelp.com/biz/gary-danko-san-francisco", "debug_yelp.html")

if __name__ == "__main__":
    asyncio.run(main())
