import json
from bs4 import BeautifulSoup

with open("debug_apple_macbook.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for tag in soup.find_all("script", type="application/ld+json"):
    try:
        data = json.loads(tag.string)
        if isinstance(data, list):
            data = data[0]
        if data.get("@type") == "Product" and "review" in data:
            with open("test_reviews.txt", "w", encoding="utf-8") as out:
                out.write(f"Found {len(data['review'])} reviews in JSON-LD!\n")
                for review in data["review"]:
                    rating = review.get("reviewRating", {}).get("ratingValue")
                    body = review.get("reviewBody", "")
                    out.write(f"Rating: {rating}, Body: {body}\n")
    except Exception as e:
        print(f"Error parsing JSON-LD: {e}")
