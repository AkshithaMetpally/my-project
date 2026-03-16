from curl_cffi import requests
url_m = 'https://www.meesho.com/sports-black-01/p/bcfgqu'
url_y = 'https://www.yelp.com/biz/fratelli-pizza-san-francisco'
import time

for imp in ['chrome110', 'safari15_3', 'chrome104', 'safari15_5', 'chrome120', 'safari17_0']:
    try:
        r_m = requests.get(url_m, impersonate=imp, timeout=10)
        r_y = requests.get(url_y, impersonate=imp, timeout=10)
        print(f"{imp:<12} Meesho: {r_m.status_code} ({len(r_m.text)}b) Yelp: {r_y.status_code} ({len(r_y.text)}b)")
    except Exception as e:
        print(imp, e)
    time.sleep(1)
