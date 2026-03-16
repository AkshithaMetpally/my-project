from curl_cffi import requests

url = "https://www.meesho.com/trending-hand-bag/p/9zlore"
try:
    # impersonate a real modern browser
    response = requests.get(url, impersonate="chrome120")
    print(f"Status Code: {response.status_code}")
    html = response.text
    print(f"HTML Length: {len(html)}")
    
    if 'sec-if-cpt-container' in html:
        print("Akamai Block detected in HTML!")
    else:
        print("Looks like a clean response!")
        with open("meesho_req.html", "w", encoding="utf-8") as f:
            f.write(html)
except Exception as e:
    print(f"Request failed: {e}")
