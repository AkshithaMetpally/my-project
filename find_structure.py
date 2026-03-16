from bs4 import BeautifulSoup
import re

with open("debug_apple_macbook.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for tag in soup.find_all(string=re.compile("So beautiful, so elegant")):
    print(f"Found TEXT: {tag}".encode('ascii', 'ignore').decode())
    parent = tag.parent
    while parent and parent.name != 'body':
        print(f"<{parent.name} class='{parent.get('class', [])}'>".encode('ascii', 'ignore').decode())
        parent = parent.parent
