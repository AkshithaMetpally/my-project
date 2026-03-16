with open("debug_apple_macbook.html", "r", encoding="utf-8") as f:
    html = f.read()

import re
matches = re.finditer(r'.{0,50}Nikhil Kumar.{0,50}', html, re.IGNORECASE)
for m in matches:
    print(m.group(0))
