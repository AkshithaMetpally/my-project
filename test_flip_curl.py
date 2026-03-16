from curl_cffi import requests

url = "https://www.flipkart.com/puma-buzz-sneakers-men/p/itm5f31fa50a9482"
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

print("Fetching URL...")
r = requests.get(url, impersonate='chrome120', headers=headers)
print("Status:", r.status_code)
html = r.text

if "review" in html.lower():
    print("Contains 'review'")
else:
    print("Does not contain 'review'")

import re
matches = re.findall(r'<div class="t-ZTKy">.*?</div>', html)
print(f"Old selector div.t-ZTKy found: {len(matches)}")
