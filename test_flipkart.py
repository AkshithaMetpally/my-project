import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
        """)
        
        # Intercept background API requests
        api_responses = []
        async def handle_response(response):
            if "api" in response.url or "graphql" in response.url or "review" in response.url.lower():
                if response.status == 200:
                    try:
                        js = await response.json()
                        api_responses.append((response.url, js))
                    except:
                        pass
        
        page.on("response", handle_response)
        
        url = "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4"
        print(f"Navigating to {url}")
        
        response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        print("Status:", response.status)
        
        # Scroll to bottom slowly
        for i in range(10):
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(1)
            
        # Click on 'All [number] Reviews' or similar if it exists
        try:
             # Click "All reviews" text
             await page.get_by_text("All ", exact=False).filter(has_text="reviews").first.click(timeout=3000)
             await asyncio.sleep(3)
        except Exception:
             print("Could not find 'All reviews' button.")
             
        html = await page.content()
        with open("debug_flipkart_pw.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        print("HTML length:", len(html))
        print(f"Captured {len(api_responses)} background API responses.")
        
        # Write captured APIs to a file
        import json
        with open("debug_flipkart_api.json", "w", encoding="utf-8") as f:
            json.dump([url for url, data in api_responses], f, indent=2)
            
        # Search for reviews in the APIs
        reviews_found = 0
        for url, data in api_responses:
             s = json.dumps(data)
             if "REVIEW" in s or "review" in s or "author" in s:
                 print(f"Potential reviews found in: {url}")
                 reviews_found += 1
                 with open("debug_flipkart_reviews.json", "w", encoding="utf-8") as f:
                     json.dump(data, f, indent=2)
                     break
                     
        if not reviews_found:
             print("No reviews found in API responses either.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
