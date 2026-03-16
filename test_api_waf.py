import urllib.request, urllib.error, json
req = urllib.request.Request(
    'http://127.0.0.1:5000/api/analyze',
    data=json.dumps({'url': 'https://www.yelp.com/biz/fratelli-pizza-san-francisco'}).encode(),
    headers={'Content-Type': 'application/json'}
)
try:
    urllib.request.urlopen(req, timeout=120)
    print("Success?")
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())
