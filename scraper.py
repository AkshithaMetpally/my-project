"""
Platform-Agnostic Fake Review Detection Web Application
Scraping Module

Developed for Team: Akshitha, Poojitha, Zeeshan, and Manmath
"""

import random
import time
import asyncio
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
try:
    from curl_cffi import requests as curl_requests
except ImportError:
    curl_requests = None

class GhostScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def _human_mimicry_scroll(self, page) -> None:
        """
        Simulate human-like gradual scrolling with random pauses
        to bypass basic anti-bot security.
        """
        body_exists = await page.evaluate("document.body !== null")
        if not body_exists:
            return
            
        scroll_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = await page.evaluate("window.innerHeight")
        current_scroll = 0

        while current_scroll < scroll_height:
            # Scroll down by a random fraction of the viewport height
            scroll_step = random.uniform(0.3, 0.8) * viewport_height
            current_scroll += scroll_step
            
            await page.evaluate(f"window.scrollTo(0, {current_scroll})")
            
            # Random delay between scrolls
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Update scroll_height in case of infinite scroll loaders
            body_exists = await page.evaluate("document.body !== null")
            if body_exists:
                new_scroll_height = await page.evaluate("document.body.scrollHeight")
                if new_scroll_height > scroll_height:
                    scroll_height = new_scroll_height
            else:
                break

    def extract_reviews(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Use BeautifulSoup4 for DOM analysis to extract reviews.
        Note: Exact selectors will vary by platform.
        This provides a generic fallback approach with JSON-LD.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        reviews = []
        
        # 0. Platform-Agnostic JSON-LD Schema Extraction
        # Many modern e-commerce sites use Schema.org which is highly robust
        # Expanded to support Product, LocalBusiness, Hotel, Restaurant, and standalone Reviews
        valid_schema_types = {'Product', 'LocalBusiness', 'Hotel', 'Restaurant', 'Organization', 'Service', 'TravelAgency', 'TouristAttraction', 'LodgingBusiness'}
        
        def extract_from_jsonld_obj(obj):
            extracted = []
            # If the object itself is a Review
            if obj.get('@type') == 'Review':
                body = obj.get('reviewBody') or obj.get('description')
                if body:
                    rating = obj.get('reviewRating', {}).get('ratingValue')
                    extracted.append({
                        "id": len(extracted),
                        "text": body.strip(),
                        "rating_raw": str(rating) if rating else None,
                        "timestamp": obj.get('datePublished'),
                    })
            # If the object contains a list of reviews
            elif obj.get('@type') in valid_schema_types and 'review' in obj:
                reviews_data = obj['review']
                if isinstance(reviews_data, dict):
                    reviews_data = [reviews_data] # Sometimes it's a single dict instead of list
                for idx, review in enumerate(reviews_data):
                    body = review.get('reviewBody') or review.get('description')
                    if body:
                        rating = review.get('reviewRating', {}).get('ratingValue')
                        extracted.append({
                            "id": idx,
                            "text": body.strip(),
                            "rating_raw": str(rating) if rating else None,
                            "timestamp": review.get('datePublished'),
                        })
            return extracted

        for script_tag in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script_tag.string)
                if isinstance(data, list):
                    for item in data:
                        reviews.extend(extract_from_jsonld_obj(item))
                elif isinstance(data, dict):
                    # Sometimes the main schema is a dict that contains a 'mainEntity' or '@graph'
                    if '@graph' in data:
                        for item in data['@graph']:
                            reviews.extend(extract_from_jsonld_obj(item))
                    else:
                        reviews.extend(extract_from_jsonld_obj(data))
            except Exception as e:
                print(f"Failed to parse JSON-LD: {e}")
                
        # If JSON-LD provided reviews, return them as they are the most reliable
        if reviews:
            # deduplicate by text
            seen = set()
            unique_reviews = []
            for r in reviews:
                if r['text'] not in seen:
                    seen.add(r['text'])
                    unique_reviews.append(r)
            return unique_reviews

        # 1. Broad approach: Generic review blocks
        # Added broad classes to cover Nykaa, Myntra, Google Maps, MakeMyTrip, RedBus, etc.
        review_class_keywords = ['review', 'comment', 'testimonial', 'feedback', 'user-review', 'customer-review']
        platform_specific_classes = [
            'col _2wzg', 'z9e2', # Flipkart Old
            'wiI7pd', 'MyEned', 'OA1nbd', # Google Maps
            'review-text', 'review-card', 'review-desc', # Nykaa / Myntra
            'rvw-cnt', 'review-content', # General Travel
            'user-review-desc', # RedBus
            'comment__09f24', 'margin-b2__09f24' # Yelp
        ]
        
        def is_review_block(c):
            if not c:
                return False
            c_lower = c.lower()
            return any(k in c_lower for k in review_class_keywords) or any(k.lower() in c_lower for k in platform_specific_classes)

        possible_review_blocks = soup.find_all(['div', 'article', 'section', 'li'], class_=is_review_block)
        
        # 2. Hardcoded fallbacks
        if not possible_review_blocks:
             possible_review_blocks = soup.select('div.col._2wzg32, div.ZmyqYM, div.EKFha-, div.RcXBOT, span.wiI7pd, div.MyEned')
             
        # Add exact Amazon matches
        amazon_blocks = soup.select('div[data-hook="review"]')
        for b in amazon_blocks:
            if b not in possible_review_blocks:
                possible_review_blocks.append(b)

        for idx, block in enumerate(possible_review_blocks):
            # Attempt to extract text
            text_element = block.find(attrs={"data-hook": "review-body"}) # Amazon
            if not text_element:
                 text_element = block.find(['p', 'span', 'div'], class_=lambda c: c and any(k in c.lower() for k in ['text', 'body', 'desc', 'content', 'z9e2', 'wiI7pd']))
            if not text_element:
                 text_element = block.find('div', class_='ZmyqYM') # Flipkart specific
            
            # If no specific text container is found, use the block itself if it has enough text
            text = text_element.get_text(strip=True) if text_element else block.get_text(separator=' ', strip=True)

            # Attempt to extract star rating (common pattern: '5 stars' or aria-label)
            rating = None
            rating_element = block.find(lambda tag: tag.has_attr('aria-label') and 'star' in tag['aria-label'].lower())
            if rating_element:
                rating = rating_element['aria-label']
                
            # Attempt to extract timestamp
            date_element = block.find(['span', 'time', 'div'], class_=lambda c: c and any(k in c.lower() for k in ['date', 'time', 'ago']))
            timestamp = date_element.get_text(strip=True) if date_element else None

            # Stricter heuristic: if we used the whole block text, make sure it's long enough and lacks excessive links
            if len(text) > 30:
                reviews.append({
                    "id": idx,
                    "text": text,
                    "rating_raw": rating,
                    "timestamp": timestamp,
                })
                
        # 3. New Flipkart React UI Extraction
        if not reviews:
            flipkart_new_blocks = soup.find_all('div', class_=lambda c: c and 'v1zwn2' in c and len(c.split()) >= 2)
            for block in flipkart_new_blocks:
                flip_text = block.get_text(separator=' ', strip=True)
                if flip_text.endswith('...more') or flip_text.endswith('... more'):
                    if len(flip_text) > 30 and 'Warranty' not in flip_text.title() and 'Flipkart' not in flip_text:
                        flip_text = flip_text.replace('...more', '').replace('... more', '').strip()
                        reviews.append({'id': len(reviews) + 1, 'text': flip_text, 'rating_raw': None, 'timestamp': None})
                        
        # 4. Universal NLP-driven Heuristic Parsing 
        # For completely unknown sites (Meesho, Yelp, etc) where CSS is obfuscated
        if not reviews:
            all_divs_and_lis = soup.find_all(['div', 'li', 'article', 'section'])
            from collections import defaultdict
            import re
            
            cluster_candidates = defaultdict(list)
            # Group nodes by their parent's class + tag structure to find repeating lists
            for node in all_divs_and_lis:
                parent = node.parent
                if not parent: continue
                # We want leaf-ish nodes that contain a decent chunk of text
                text = node.get_text(separator=' ', strip=True)
                words = text.split()
                # Reviews are usually 40 to 2000 characters and have actual words
                if 40 < len(text) < 3000 and len(words) >= 8 and len(node.find_all(['div', 'li', 'p'])) < 5:
                    parent_sig = f"{parent.name}_{parent.get('class', [''])[0]}" if parent.get('class') else parent.name
                    node_sig = f"{node.name}_{node.get('class', [''])[0]}" if node.get('class') else node.name
                    sig = f"{parent_sig}>{node_sig}"
                    cluster_candidates[sig].append((node, text))
            
            best_cluster = []
            highest_score = 0
            
            for sig, nodes in cluster_candidates.items():
                if len(nodes) >= 3: # A review section usually has 3+ reviews
                    score = len(nodes)
                    sample_text = " ".join([n[1] for n in nodes[:5]]).lower()
                    
                    # Must contain basic punctuation to be a real review block (not just menu names)
                    if not re.search(r'[.,!?]', sample_text):
                        score -= 20
                        
                    # Positive markers
                    if re.search(r'\b(star|rating|review|date|ago|verified|helpful|purchased)\b', sample_text):
                        score += 5
                    if re.search(r'\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', sample_text):
                        score += 5 # Contains dates
                        
                    # Negative markers (e.g., related products, navigation, addresses)
                    if re.search(r'\b(cart|price|buy|₹|\$|shipping|delivery|size|color|shop by|tools|floor|st|ave|blvd)\b', sample_text):
                         score -= 10
                         
                    if score > highest_score:
                         highest_score = score
                         best_cluster = nodes
                         
            if highest_score > 0 and best_cluster:
                 for idx, (node, text) in enumerate(best_cluster):
                      # Heuristic check for date/rating inside the specific node
                      rating = None
                      if 'star' in text.lower() or '★' in text:
                          rating = "Found via heuristic"
                      reviews.append({'id': len(reviews) + 1, 'text': text, 'rating_raw': rating, 'timestamp': None})
                      if len(reviews) > 20: # Cap at 20
                          break
                
        # Deduplicate
        seen = set()
        unique_reviews = []
        for r in reviews:
            if r['text'] not in seen:
                seen.add(r['text'])
                unique_reviews.append(r)
                
        return unique_reviews
        
    async def scrape_url(self, url: str) -> List[Dict[str, Any]]:
        reviews: List[Dict[str, Any]] = []
        try:
             async with async_playwright() as p:
                # 1. These specific flags are CRITICAL for Railway/Linux servers
                browser = await p.chromium.launch(
                    headless=True, 
                    args=[
                        "--no-sandbox", 
                        "--disable-setuid-sandbox", 
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled"
                    ]
                )
                
                # 2. Use a mobile user agent (Amazon blocks servers, but rarely blocks mobile Safari)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
                    viewport={'width': 390, 'height': 844}
                )
                page = await context.new_page()
                
                from playwright_stealth import stealth_async
                await stealth_async(page)
                
                try:
                    # 3. Increase timeout and wait for network to be idle
                    await page.goto(url, wait_until="networkidle", timeout=90000)
                    
                    # 4. Human behavior: A long pause and a scroll
                    await asyncio.sleep(random.uniform(5.0, 8.0))
                    await page.evaluate("window.scrollBy(0, 500)")
                    
                    # 5. Amazon Bypass: Redirect to the dedicated review page
                    if 'amazon.' in url:
                        try:
                            # Try to find the "See all reviews" link
                            see_all_link = await page.locator("a[data-hook='see-all-reviews-link-foot']").get_attribute('href', timeout=5000)
                            if see_all_link:
                                full_url = f"https://www.amazon.in{see_all_link}" if see_all_link.startswith('/') else see_all_link
                                await page.goto(full_url, wait_until="networkidle")
                                await asyncio.sleep(3)
                        except:
                            pass

                    # 6. Final check for the review containers
                    try:
                        await page.wait_for_selector('div[data-hook="review"]', timeout=15000)
                    except:
                        print("Reviews didn't appear in time, attempting extraction anyway.")

                    html_content = await page.content()
                    reviews = self.extract_reviews(html_content)
                    
                except Exception as e:
                    print(f"Scrape attempt failed: {e}")
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"Playwright error: {e}")
            
        return reviews

# Optional: Run directly for testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        scraper = GhostScraper(headless=False)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        extracted = loop.run_until_complete(scraper.scrape_url(test_url))
        print(f"Extracted {len(extracted)} reviews.")
        limit = min(3, len(extracted))
        for i in range(limit):
            print(extracted[i])
