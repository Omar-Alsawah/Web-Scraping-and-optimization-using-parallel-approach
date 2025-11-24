import requests
import csv
import time
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

start_time = time.time()

def writeCsvFile(fname, data):
    with open(fname, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)

def fetch_articles(rccontinue=None):
    url = "https://en.wikipedia.org/w/api.php"
    headers = {"User-Agent": "PythonScraper/1.0 (your_email@example.com)"}
    params = {
        "action": "query",
        "list": "recentchanges",
        "rctype": "new",
        "rcprop": "title",
        "rclimit": "500",
        "format": "json"
    }
    if rccontinue:
        params["rccontinue"] = rccontinue

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    articles = data['query']['recentchanges']
    rccontinue_next = data.get('continue', {}).get('rccontinue')

    results = []
    for article in articles:
        title = article['title']
        if not title.startswith(("User:", "User talk:", "Talk:", "Draft:", "Template:", "Category:", "File:", "Wikipedia:")):
            full_link = f"https://en.wikipedia.org/wiki/{quote(title)}"
            results.append([title, full_link])
    return results, rccontinue_next

# ---- Parallel fetching ----
target = 10000
all_articles = []
rccontinue = None
max_workers = 5  # Number of parallel threads

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = []
    while len(all_articles) < target:
        futures.append(executor.submit(fetch_articles, rccontinue))

        for future in as_completed(futures):
            articles, rccontinue = future.result()
            all_articles.extend(articles)
            if len(all_articles) >= target:
                break

        if not rccontinue:
            print("Reached the end of recent changes.")
            break

# Trim to target
all_articles = all_articles[:target]

# Write to CSV
writeCsvFile('data_parallel.csv', all_articles)

end_time = time.time()
print(f"Done! Saved {len(all_articles)} new Wikipedia article titles with links.")
print(f"Time taken: {end_time - start_time:.2f} seconds")
