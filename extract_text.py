import sys
from bs4 import BeautifulSoup
with open("debug_apple_macbook.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")
    
# output all text
text = soup.get_text(separator=' ', strip=True)

with open("debug_macbook_text.txt", "w", encoding="utf-8", errors="ignore") as f2:
    f2.write(text)
