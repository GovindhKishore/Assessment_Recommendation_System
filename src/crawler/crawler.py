import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
from details_parser import get_details

HEADERS = {"User-Agent": "Mozilla/5.0"}
BASE_URL = "https://www.shl.com/products/product-catalog/"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "shl_assessments.csv")


def crawl_shl():

    all_assessments = []
    PAGE_SIZE = 12
    MAX_ITEMS = 500
    for start_index in range(0, MAX_ITEMS, PAGE_SIZE):

        url = f"{BASE_URL}?start={start_index}&type=1&type=1"
        print(f"Processing batch start={start_index} (URL: {url})...", end=" ")

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            print(f"HTTP {response.status_code}", end=" ")

            # save HTML for debugging when things go wrong
            debug_path = os.path.join(os.path.dirname(__file__), "html_debugging_files", f"last_page_debug_{start_index}.html")
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(response.text or f"Status: {response.status_code}\nNo body.")
            # Validate successful HTTP response status before parsing
            if response.status_code != 200:
                print(f"- Saved debug HTML to `{debug_path}`. Skipping batch.")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            target_text = soup.find(string=lambda t: t and "Individual Test Solutions" in t)
            if not target_text:
                print("No trigger text found. Ending crawl.")
                break

            # Crawl up the DOM tree to find the specific table holding the data
            table = None
            table = target_text.find_parent("table")


            if not table:
                print("No table found. Saved page for inspection. Ending crawl.")
                print(f"Debug HTML: `{debug_path}`")
                break

            rows = table.find_all("tr")[1:]  # Skip header which have the column names
            if not rows:
                print("No rows found (End of catalog?).")
                break

            count_on_page = 0
            for row in rows:
                cols = row.find_all("td")
                if not cols: continue

                link_tag = cols[0].find("a", href=True)
                if not link_tag: continue

                name = link_tag.get_text(strip=True)
                raw_link = link_tag['href']
                link = raw_link if raw_link.startswith("http") else "https://www.shl.com" + raw_link

                # Capture ADAPTIVE STATUS
                adaptive_status = "No"
                if len(cols) > 2:
                    adaptive_col = cols[2]

                    # Found during inspection: the '-yes' class inside the span marks a green 'Adaptive' indicator.
                    if adaptive_col.find("span", class_="catalogue_circle -yes"):
                        adaptive_status = "Yes"
                    
                    elif adaptive_col.find(class_=lambda c: c and "-yes" in str(c)):
                        adaptive_status = "Yes"

                details = get_details(link)
                details["adaptive_support"] = adaptive_status

                all_assessments.append({
                    "name": name,
                    "url": link,
                    **details
                })
                count_on_page += 1

            print(f"Added {count_on_page} items.")

            if count_on_page < PAGE_SIZE:
                print("Reached the last page.")
                break

            time.sleep(1)

        except Exception as e:
            print(f"Error on start={start_index}: {e}")
            continue

    df = pd.DataFrame(all_assessments)
    print(f"Crawling Complete. Total Assessments: {len(df)}")
    if len(df) < 377:
        print(f"WARNING: Found {len(df)} items (Target: 377+).")
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    crawl_shl()


