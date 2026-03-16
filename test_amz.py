import traceback, json
from bs4 import BeautifulSoup
from curl_cffi import requests

try:
    r = requests.get('https://www.amazon.in/KLOSIA-Women-Embroidery-Anarkali-Dupatta/dp/B0FMYLBCXW/', impersonate='chrome120')
    soup=BeautifulSoup(r.text, 'html.parser')
    print('Title:', soup.title.string if soup.title else 'No Title')
    print('JS Blocks:', len(soup.find_all('script', type='application/ld+json')))
    print('Review text blocks:', len(soup.select('div[data-hook="review"]')))
    for s in soup.find_all('script', type='application/ld+json'):
        data = json.loads(s.string)
        print("Schema Type:", data.get('@type'))
except Exception as e:
    print(e)
