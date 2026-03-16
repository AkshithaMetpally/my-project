import asyncio
from scraper import GhostScraper

async def test():
    print("Initializing GhostScraper...")
    scraper = GhostScraper(headless=True)
    
    url1 = "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4"
    print(f"Testing URL: {url1}")
    reviews1 = await scraper.scrape_url(url1)
    print(f"Extracted {len(reviews1)} reviews from iPhone URL:")
    for i, r in enumerate(reviews1):
         print(f"{i+1}: {r['text'][:100]}...")
         
    url2 = "https://www.flipkart.com/puma-buzz-sneakers-men/p/itm5f31fa50a9482"
    print(f"\nTesting URL: {url2}")
    reviews2 = await scraper.scrape_url(url2)
    print(f"Extracted {len(reviews2)} reviews from Puma URL.")
    if reviews2:
         print(reviews2[0])

if __name__ == "__main__":
    asyncio.run(test())
