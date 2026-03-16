import json
import re
from bs4 import BeautifulSoup

with open("debug_apple_macbook.html", "r", encoding="utf-8") as f:
    html = f.read()

# Try to find window.__INITIAL_STATE__ or similar JSON where Flipkart stores data
match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', html)
if match:
    state_str = match.group(1)
    with open("flipkart_state.json", "w", encoding="utf-8") as out:
        out.write(state_str)
    print("Found INITIAL_STATE!")
else:
    print("No INITIAL_STATE found.")
