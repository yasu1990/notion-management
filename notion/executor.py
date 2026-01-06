import os
import requests
from notion.client import notion_headers
from notion.builder import build_properties


def get_database_id():
    if "NOTION_DATABASE_ID" not in os.environ:
        raise RuntimeError("NOTION_DATABASE_ID is not set")
    return os.environ["NOTION_DATABASE_ID"]


def query_by_domain(domain):
    database_id = get_database_id()
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {
        "filter": {
            "property": "ドメイン",
            "select": {"equals": domain}
        }
    }
    r = requests.post(url, headers=notion_headers(), json=payload)
    r.raise_for_status()
    return r.json()["results"]


def get_title(page):
    t = page["properties"]["タイトル"]["title"]
    return t[0]["plain_text"] if t else ""


def create_page(props):
    database_id = get_database_id()
    url = "https://api.notion.com/v1/pages"
    r = requests.post(
        url,
        headers=notion_headers(),
        json={
            "parent": {"database_id": database_id},
            "properties": props
        }
    )
    r.raise_for_status()


def update_page(page_id, props):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    r = requests.patch(
        url,
        headers=notion_headers(),
        json={"properties": props}
    )
    r.raise_for_status()


def archive_page(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    r = requests.patch(
        url,
        headers=notion_headers(),
        json={"archived": True}
    )
    r.raise_for_status()


def apply_plan(plan):
    domain = plan["domain"]
    existing = query_by_domain(domain)
    by_title = {get_title(p): p for p in existing}

    for item in plan["items"]:
        props = build_properties(domain, item)
        title = item["title"]

        if title in by_title:
            update_page(by_title[title]["id"], props)
        else:
            create_page(props)

    for a in plan.get("archive_candidates", []):
        title = a["title"]
        if title in by_title:
            archive_page(by_title[title]["id"])

    return "OK"
