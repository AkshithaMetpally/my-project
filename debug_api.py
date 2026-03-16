import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        jsons = []
        async def on_res(res):
            url_lower = res.url.lower()
            if 'api' in url_lower or 'graphql' in url_lower or 'review' in url_lower:
                try:
                    data = await res.json()
                    jsons.append({'url': res.url, 'data': data})
                except:
                    pass
                    
        page.on('response', on_res)
        await page.goto('https://www.nykaa.com/l-oreal-paris-revitalift-hyaluronic-acid-plumping-day-cream/p/823018', wait_until='networkidle')
        await asyncio.sleep(3)
        print(f"Captured {len(jsons)} JSON APIs.")
        
        for j in jsons:
            dump = json.dumps(j['data'])
            if 'review' in dump.lower() or 'rating' in dump.lower():
                print(f"Found review data in: {j['url']}")
                print(dump[:500])
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
