from curl_cffi.requests import AsyncSession
import asyncio
from bs4 import BeautifulSoup
import json

async def test_amazon():
    # URL to test on
    url = "https://www.amazon.in/iPhone-17-256-Promotion-Resistance/dp/B0FQFQ576F/"
    
    async with AsyncSession(impersonate="chrome120") as session:
        print("Fetching with curl_cffi...")
        try:
            response = await session.get(url, timeout=15)
            html = response.text
            
            soup = BeautifulSoup(html, "html.parser")
            print(f"Title: {soup.title.string if soup.title else 'No Title'}")
            
            # Check JSON-LD
            reviews_found = 0
            for script_tag in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script_tag.string)
                    # Helper to check
                    def check_obj(obj):
                        count = 0
                        if obj.get('@type') == 'Review':
                            count += 1
                        elif 'review' in obj:
                            reviews_data = obj['review']
                            if isinstance(reviews_data, list):
                                count += len(reviews_data)
                            else:
                                count += 1
                        return count
                    
                    if isinstance(data, list):
                        for item in data:
                            reviews_found += check_obj(item)
                    elif isinstance(data, dict):
                        if '@graph' in data:
                            for item in data['@graph']:
                                reviews_found += check_obj(item)
                        else:
                            reviews_found += check_obj(data)
                except Exception as e:
                    pass
            print(f"Found {reviews_found} reviews in JSON-LD.")
            
            # Dump to file to investigate
            with open("debug_amazon_curl.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Wrote html to debug_amazon_curl.html")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_amazon())
