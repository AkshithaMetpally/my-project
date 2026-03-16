import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def solve_datadome():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        url = "https://www.yelp.com/biz/fratelli-pizza-san-francisco"
        await page.goto(url)
        
        await asyncio.sleep(4)
        
        # Check for Datadome
        frames = page.frames
        for frame in frames:
            if "geo.captcha-delivery.com" in frame.url:
                print("Found Datadome Captcha!")
                # Datadome has a press and hold or slider.
                # Usually it's a slider.
                # Let's try to find the button and slide it.
                slider = frame.locator('.slider')
                if await slider.count() > 0:
                     print("Found slider! Attempting to slide...")
                     box = await slider.bounding_box()
                     if box:
                         await page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                         await page.mouse.down()
                         await page.mouse.move(box['x'] + 300, box['y'] + box['height'] / 2, steps=20)
                         await page.mouse.up()
                else:
                    # Maybe it's a press and hold
                     print("No slider, attempting press & hold on the frame...")
                     box = await frame.locator('body').bounding_box()
                     if box:
                         await page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                         await page.mouse.down()
                         await asyncio.sleep(5)
                         await page.mouse.up()
                         
        await asyncio.sleep(5)
        print("Final title:", await page.title())
        await browser.close()

if __name__ == "__main__":
    asyncio.run(solve_datadome())
