import requests
import csv
import time
from urllib.parse import quote

start_time = time.time()

def writeCsvFile(fname, data):
    with open(fname, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)

url = "https://en.wikipedia.org/w/api.php"
headers = {"User-Agent": "PythonScraper/1.0 (your_email@example.com)"}

titles = []
rccontinue = None
target = 10000  # Number of articles you want

while len(titles) < target:
    params = {
        "action": "query",
        "list": "recentchanges",
        "rctype": "new",
        "rcprop": "title",
        "rclimit": "500",  # max allowed per request
        "format": "json"
    }
    if rccontinue:
        params["rccontinue"] = rccontinue

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    articles = data['query']['recentchanges']

    for article in articles:
        title = article['title']
        if not title.startswith(("User:", "User talk:", "Talk:", "Draft:", "Template:", "Category:", "File:", "Wikipedia:")):
            full_link = f"https://en.wikipedia.org/wiki/{quote(title)}"
            titles.append([title, full_link])
        if len(titles) >= target:
            break

    rccontinue = data.get('continue', {}).get('rccontinue')
    if not rccontinue:
        print("Reached the end of recent changes.")
        break

writeCsvFile('data_serial.csv', titles[:target])

end_time = time.time()
print(f"Done! Saved {len(titles)} new Wikipedia article titles with links.")
print(f"Time taken: {end_time - start_time:.2f} seconds")
