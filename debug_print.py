import asyncio
from scraper import GhostScraper

async def run_and_print(url):
    s = GhostScraper()
    print(f"Scraping {url}...")
    reviews = await s.scrape_url(url)
    print(f"Extracted: {len(reviews)} reviews")
    for idx, r in enumerate(reviews[:3]):
        print(f"[{idx+1}] Rating: {r['rating_raw']} | Text: {r['text'][:150]}...")
        
async def main():
    await run_and_print("https://www.nykaa.com/l-oreal-paris-revitalift-hyaluronic-acid-plumping-day-cream/p/823018")
    print("\n------------------\n")
    await run_and_print("https://www.yelp.com/biz/gary-danko-san-francisco")

if __name__ == "__main__":
    asyncio.run(main())
