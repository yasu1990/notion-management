import os
import requests
from datetime import datetime

NOTION_VERSION = "2022-06-28"

# =========================
# 内部ルール定義
# =========================

TYPE_LEVEL = {
    "設計ゴール": 4,
    "中間ゴール": 4,
    "タスク": 5,
}

PARENT_REQUIRED = {
    "設計ゴール": False,
    "中間ゴール": True,
    "タスク": True,
}

# =========================
# Notion API helpers
# =========================

def notion_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def get_title(page):
    t = page["properties"]["タイトル"]["title"]
    return t[0]["plain_text"] if t else ""


def query_all_pages(database_id: str, token: str):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    results = []
    payload = {}

    while True:
        res = requests.post(url, headers=notion_headers(token), json=payload)
        res.raise_for_status()
        data = res.json()
        results.extend(data["results"])

        if not data.get("has_more"):
            break

        payload["start_cursor"] = data["next_cursor"]

    return results


def create_page(database_id: str, token: str, properties: dict):
    url = "https://api.notion.com/v1/pages"
    res = requests.post(
        url,
        headers=notion_headers(token),
        json={
            "parent": {"database_id": database_id},
            "properties": properties,
        },
    )
    res.raise_for_status()
    return res.json()


def update_page(page_id: str, token: str, properties: dict):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    res = requests.patch(
        url,
        headers=notion_headers(token),
        json={"properties": properties},
    )
    res.raise_for_status()
    return res.json()

# =========================
# validation
# =========================

def validate_item(item: dict):
    item_type = item.get("type")

    if item_type not in TYPE_LEVEL:
        raise ValueError(f"不正な種別: {item_type}")

    if PARENT_REQUIRED[item_type] and not item.get("parent"):
        raise ValueError(
            f"{item_type} には parent（親ゴール）が必須です: {item.get('title')}"
        )

# =========================
# property builder
# =========================

def build_properties(item, now_iso: str, is_create: bool):
    props = {
        "タイトル": {"title": [{"text": {"content": item["title"]}}]},
        "種別": {"select": {"name": item["type"]}},
        "ステータス": {"select": {"name": item.get("status", "未着手")}},
        "優先度": {"select": {"name": item.get("priority", "中")}},
        "更新日": {"date": {"start": now_iso}},
    }

    if is_create:
        props["登録日"] = {"date": {"start": now_iso}}

    if item.get("status") == "完了":
        props["完了日"] = {"date": {"start": now_iso}}

    if item.get("parent_id"):
        props["親ゴール"] = {"relation": [{"id": item["parent_id"]}]}

    return props

# =========================
# main executor
# =========================

def apply_plan(plan: dict):
    token = os.environ["NOTION_TOKEN"]
    database_id = os.environ["NOTION_DATABASE_ID"]

    now_iso = datetime.utcnow().isoformat()

    existing_pages = query_all_pages(database_id, token)
    title_map = {get_title(p): p for p in existing_pages}

    # validation
    for item in plan["items"]:
        validate_item(item)

    # upsert
    for item in plan["items"]:
        title = item["title"]
        is_create = title not in title_map

        if item.get("parent"):
            parent_page = title_map.get(item["parent"])
            if not parent_page:
                raise ValueError(f"親ゴールが見つかりません: {item['parent']}")
            item["parent_id"] = parent_page["id"]

        props = build_properties(item, now_iso, is_create)

        if is_create:
            create_page(database_id, token, props)
        else:
            update_page(title_map[title]["id"], token, props)

    return "OK"
