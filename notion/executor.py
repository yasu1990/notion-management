import os
import requests
from datetime import datetime

BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

def headers():
    return {
        "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

def fetch_pages(database_id):
    url = f"{BASE_URL}/databases/{database_id}/query"
    res = requests.post(url, headers=headers())
    res.raise_for_status()
    return res.json()["results"]

def build_title_map(pages):
    m = {}
    for p in pages:
        title = p["properties"]["タイトル"]["title"]
        if title:
            m[title[0]["plain_text"]] = p["id"]
    return m

def create_page(database_id, props):
    res = requests.post(
        f"{BASE_URL}/pages",
        headers=headers(),
        json={"parent": {"database_id": database_id}, "properties": props},
    )
    res.raise_for_status()
    return res.json()["id"]

def build_props(node, parent_id=None):
    props = {
        "タイトル": {"title": [{"text": {"content": node["title"]}}]},
        "ジャンル": {"select": {"name": node["genre"]}},
        "プロジェクト": {"select": {"name": node["project"]}},
        "種別": {"select": {"name": node["type"]}},
        "ステータス": {"select": {"name": node["status"]}},
        "優先度": {"select": {"name": node["priority"]}},
        "登録日": {"date": {"start": datetime.utcnow().isoformat()}},
    }
    if parent_id:
        props["親ゴール"] = {"relation": [{"id": parent_id}]}
    return props

def apply_plan(plan):
    db_id = os.environ["NOTION_DATABASE_ID"]
    pages = fetch_pages(db_id)
    title_map = build_title_map(pages)

    nodes = {n["title"]: n for n in plan["nodes"]}
    genre = plan["meta"]["genre"]
    project = plan["meta"]["project"]

    def ensure_node(title):
        if title in title_map:
            return title_map[title]

        node = nodes[title]
        node["genre"] = genre
        node["project"] = project

        parent_id = None
        if "parent" in node:
            parent_id = ensure_node(node["parent"])

        page_id = create_page(db_id, build_props(node, parent_id))
        title_map[title] = page_id
        return page_id

    for title in nodes:
        ensure_node(title)

    return "OK"
