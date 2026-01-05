import requests
from bs4 import BeautifulSoup
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}
TYPE_MAP = {
    'A': 'Ability & Aptitude',
    'B': 'Biodata & Situational Judgement',
    'C': 'Competencies',
    'D': 'Development & 360',
    'E': 'Assessment Exercises',
    'K': 'Knowledge & Skills',
    'P': 'Personality & Behavior',
    'S': 'Simulations'
}

def get_details(url):

    data = {
        "description": "",
        "duration": 0,
        "test_type": [],
        "remote_support": "No"
    }

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        desc_header = soup.find(
            lambda tag: tag.name in ["h2", "h3", "h4"]
            and tag.get_text(strip=True) == "Description"
        )
        if desc_header:
            desc_content = desc_header.find_next_sibling("p")
            if desc_content:
                data["description"] = desc_content.get_text(strip=True)


        page_text = soup.get_text()
        dur_match = re.search(r"Approximate Completion Time in minutes\s*=\s*(\d+)", page_text, re.IGNORECASE)
        if dur_match:
            data["duration"] = int(dur_match.group(1))

        type_label = soup.find(string=re.compile(r"Test\s*Type\s*:", re.I))
        if type_label:
            container = type_label.parent
            found_text = container.get_text(separator=" ", strip=True)
            matches = re.findall(r"\b([A-Z])\b", found_text)
            for m in matches:
                if m in TYPE_MAP:
                    data["test_type"].append(TYPE_MAP[m])

        remote_label = soup.find(string=re.compile(r"Remote\s*Testing", re.I))

        if remote_label:
            container = remote_label.parent
            # look for a span whose class contains "yes" or the word "yes" in nearby text
            if (container.find("span", class_=re.compile(r"yes", re.I))
                or re.search(r"\byes\b", container.get_text(), re.I)):
                data["remote_support"] = "Yes"

    except Exception as e:
        print(f"Error fetching details from {url}: {e}")

    return data



if __name__ == "__main__":
    get_details("https://www.shl.com/products/product-catalog/view/Apprentice + 8.0 Job Focused Assessment/")

