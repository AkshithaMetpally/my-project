from bs4 import BeautifulSoup

with open("debug_nykaa.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

print(f"File size chars: {len(str(soup))}")
text = soup.get_text(separator=' ', strip=True)[:1000]
print(f"Nykaa Page Text: {text}")

if "Akamai" in str(soup) or "captcha" in soup.get_text().lower() or "bot" in soup.get_text().lower():
    print("Bot protection detected.")
