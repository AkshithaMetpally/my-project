from bs4 import BeautifulSoup
import re

with open("debug_meesho.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

text = soup.get_text(strip=True)[:500]
print(f"Meesho Page Text: {text}")
