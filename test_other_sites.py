import asyncio
from scraper import GhostScraper

async def test():
    scraper = GhostScraper(headless=True) # Let's try headless first to see if WAFs block us
    
    urls = [
        "https://www.amazon.in/Apple-New-MacBook-Air-chip/dp/B08N5W4NNB",
        "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4",
        "https://www.nykaa.com/m-a-c-retro-matte-lipstick/p/8904"
    ]
    
    for url in urls:
        print(f"\n--- Testing {url} ---")
        try:
             reviews = await scraper.scrape_url(url)
             print(f"Extracted {len(reviews)} reviews.")
             if reviews:
                  print(f"Sample: {reviews[0]}")
        except Exception as e:
             print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
