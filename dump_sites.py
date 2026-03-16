import asyncio, json
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def dump_site(url, prefix):
    print(f"Testing {prefix}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        api_responses = []
        async def handle_response(response):
            try:
                if 'api' in response.url.lower() or 'graphql' in response.url.lower():
                    if response.status == 200:
                        js = await response.json()
                        api_responses.append(js)
            except:
                pass
        page.on("response", handle_response)
        
        await page.goto(url, wait_until="domcontentloaded")
        
        # Human scroll to trigger lazy loading and solve CAPTCHA
        for i in range(15):
             await page.mouse.wheel(0, 800)
             await asyncio.sleep(1)
             
        html = await page.content()
        with open(f"debug_{prefix}.html", "w", encoding="utf-8") as f:
             f.write(html)
             
        with open(f"debug_{prefix}_apis.json", "w", encoding="utf-8") as f:
             json.dump(api_responses, f)
             
        print(f"Dumped {prefix} HTML ({len(html)} bytes) and {len(api_responses)} API responses")
        await browser.close()

async def main():
    await dump_site("https://www.yelp.com/biz/fratelli-pizza-san-francisco", "yelp")
    await dump_site("https://www.meesho.com/sports-black-01/p/bcfgqu", "meesho")

if __name__ == "__main__":
    asyncio.run(main())
