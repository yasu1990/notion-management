import os
import requests

NOTION_VERSION = "2022-06-28"

def headers():
    return {
        "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

def fetch_all_pages(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    pages = []
    payload = {}

    while True:
        res = requests.post(url, headers=headers(), json=payload)
        res.raise_for_status()
        data = res.json()

        pages.extend(data["results"])

        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]

    return pages

def archive_page(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    res = requests.patch(
        url,
        headers=headers(),
        json={"archived": True}
    )
    res.raise_for_status()

def main():
    db_id = os.environ["NOTION_DATABASE_ID"]
    pages = fetch_all_pages(db_id)

    print(f"Found {len(pages)} pages. Archiving...")

    for p in pages:
        archive_page(p["id"])

    print("✅ Master DB cleared.")

if __name__ == "__main__":
    main()
