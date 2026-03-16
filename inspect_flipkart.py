from bs4 import BeautifulSoup
import json

with open('debug_flipkart_pw.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("Title:", soup.title.string if soup.title else "None")

# Search for JSON-LD Application Data
ld_json_scripts = soup.find_all('script', type='application/ld+json')
print(f"Found {len(ld_json_scripts)} application/ld+json scripts.")
for script in ld_json_scripts:
    try:
        data = json.loads(script.string)
        # FlipKart sometimes wraps in an array or dict
        if isinstance(data, list):
            for item in data:
                if item.get('@type') == 'Product':
                     print("Product JSON-LD found:")
                     # print nicely formatted json
                     print(json.dumps(item, indent=2)[:2000] + "...")
        elif isinstance(data, dict):
             if data.get('@type') == 'Product':
                 print("Product JSON-LD found:")
                 print(json.dumps(data, indent=2)[:2000] + "...")
    except Exception as e:
        pass

# Check for window.__INITIAL_STATE__
scripts = soup.find_all('script')
for s in scripts:
    if s.string and 'window.__INITIAL_STATE__' in s.string:
        print("Found window.__INITIAL_STATE__ snippet (length: %d)" % len(s.string))

# Fallback: find any element that contains text likely to be a review (e.g. "READ MORE")
read_mores = soup.find_all(string=lambda text: text and "READ MORE" in text)
print(f"Found {len(read_mores)} 'READ MORE' texts.")
if read_mores:
    for rm in read_mores:
        parent = rm.parent
        print("  Parent tags:", parent.name, "classes:", parent.get('class'))
        grandparent = parent.parent if parent else None
        if grandparent:
             print("  Grandparent tags:", grandparent.name, "classes:", grandparent.get('class'))

# Search for any div containing "rating" class
rating_divs = soup.select('div[class*="rating"]')
print(f"Found {len(rating_divs)} divs with 'rating' in class.")
for div in rating_divs[:5]:
    print("  Class:", div.get('class'), "Text length:", len(div.text))
