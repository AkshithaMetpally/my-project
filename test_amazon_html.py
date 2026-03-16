from bs4 import BeautifulSoup
import re

with open("debug_amazon.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

reviews = soup.select('div[data-hook="review"]')
print(f"Found {len(reviews)} reviews with data-hook='review'")
if not reviews:
    reviews = soup.select('div.a-section.review')
    print(f"Found {len(reviews)} reviews with class a-section review")

for i, r in enumerate(reviews[:3]):
    body = r.select_one('span[data-hook="review-body"]')
    if body:
        print(f"Review {i}: {body.get_text(strip=True)[:100]}")
    else:
        print(f"Review {i}: HTML: {r.prettify()[:200]}")

if not reviews:
    print("Looking for any element with 'review' in id or data attributes:")
    count = 0
    for tag in soup.find_all(True):
        id_str = tag.get('id', '')
        hook_str = tag.get('data-hook', '')
        if id_str and 'review' in id_str.lower():
            if count < 5:
                print(f"ID Match: {tag.name}#{id_str}")
                count += 1
        if hook_str and 'review' in hook_str.lower():
            if count < 5:
                print(f"Data-Hook Match: {tag.name}[data-hook='{hook_str}']")
                count += 1
