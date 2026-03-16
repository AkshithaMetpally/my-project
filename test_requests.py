import urllib.request

url = "https://www.meesho.com/trending-hand-bag/p/9zlore"
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
)

try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        print(f"Success. HTML length: {len(html)}")
        if 'sec-if-cpt-container' in html:
            print("Akamai Block detected in HTML!")
        else:
            print("Looks like a clean response!")
            with open("meesho_req.html", "w", encoding="utf-8") as f:
                f.write(html)
except Exception as e:
    print(f"Request failed: {e}")
