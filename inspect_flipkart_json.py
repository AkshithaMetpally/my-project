import json, re
from bs4 import BeautifulSoup

with open('debug_flipkart_pw.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

scripts = soup.find_all('script')
hydration_data = None
for s in scripts:
    if s.string and 'window.__staticRouterHydrationData =' in s.string:
        hydration_data = s.string
        break

if hydration_data:
    try:
        # Extract the JSON string
        json_str = hydration_data.split('window.__staticRouterHydrationData = JSON.parse("')[1].split('");')[0]
        # Unescape the JSON string
        json_str = json_str.replace('\\"', '"').replace('\\\\', '\\')
        data = json.loads(json_str)
        print("Successfully loaded hydration data dict!")
        
        # Recursively search for reviews
        def find_reviews(d, results):
            if isinstance(d, dict):
                for k, v in d.items():
                    if k == 'reviews' or k == 'reviewList':
                        results.append(v)
                    elif k == 'text' and isinstance(v, str) and len(v) > 50:
                        # might be a review text
                        pass
                    find_reviews(v, results)
            elif isinstance(d, list):
                for item in d:
                    find_reviews(item, results)
                    
        reviews_found = []
        find_reviews(data, reviews_found)
        print(f"Found {len(reviews_found)} review blocks in JSON.")
        if reviews_found:
             print(json.dumps(reviews_found[0])[:1000])
             
    except Exception as e:
        print("Error parsing:", e)
else:
    print("No hydration data found.")
