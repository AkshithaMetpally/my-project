import asyncio
from scraper import GhostScraper

async def main():
    scraper = GhostScraper(headless=False)
    reviews = await scraper.scrape_url("https://www.meesho.com/trending-hand-bag/p/9zlore")
    print(f"Extracted {len(reviews)} reviews")
    if reviews:
        print(reviews[0])

if __name__ == "__main__":
    asyncio.run(main())
