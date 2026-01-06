import os
import requests
from datetime import datetime, timezone

NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def headers():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise RuntimeError("NOTION_TOKEN が未設定")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def fetch_all_pages(database_id):
    url = f"{BASE_URL}/databases/{database_id}/query"
    res = requests.post(url, headers=headers(), json={})
    res.raise_for_status()
    return res.json()["results"]


def get_title(page):
    t = page["properties"]["タイトル"]["title"]
    return t[0]["plain_text"] if t else ""


def create_page(database_id, properties):
    res = requests.post(
        f"{BASE_URL}/pages",
        headers=headers(),
        json={
            "parent": {"database_id": database_id},
            "properties": properties,
        },
    )
    res.raise_for_status()
    return res.json()["id"]


def update_page(page_id, properties):
    res = requests.patch(
        f"{BASE_URL}/pages/{page_id}",
        headers=headers(),
        json={"properties": properties},
    )
    res.raise_for_status()


def build_base_props(item, is_new):
    props = {
        "タイトル": {"title": [{"text": {"content": item["title"]}}]},
        "種別": {"select": {"name": item["type"]}},
        "ジャンル": {"select": {"name": item["ジャンル"]}},
        "プロジェクト": {"select": {"name": item["プロジェクト"]}},
        "ステータス": {"select": {"name": item["status"]}},
        "優先度": {"select": {"name": item["priority"]}},
    }

    if is_new:
        props["登録日"] = {"date": {"start": now_iso()}}
    else:
        props["更新日"] = {"date": {"start": now_iso()}}

    return props


def apply_plan(plan: dict):
    database_id = os.environ.get("NOTION_DATABASE_ID")
    if not database_id:
        raise RuntimeError("NOTION_DATABASE_ID が未設定")

    items = plan["items"]

    # 既存ページ取得
    pages = fetch_all_pages(database_id)
    title_to_id = {get_title(p): p["id"] for p in pages}

    # ========== 1パス目：ページ作成 or 更新（relation なし） ==========
    for item in items:
        title = item["title"]
        existing_id = title_to_id.get(title)

        if existing_id:
            props = build_base_props(item, is_new=False)
            update_page(existing_id, props)
        else:
            props = build_base_props(item, is_new=True)
            page_id = create_page(database_id, props)
            title_to_id[title] = page_id

    # ========== 2パス目：親子 relation を接続 ==========
    for item in items:
        parent_title = item.get("parent")
        if not parent_title:
            continue

        child_id = title_to_id[item["title"]]
        parent_id = title_to_id.get(parent_title)

        if not parent_id:
            raise ValueError(f"親ゴールが存在しない: {parent_title}")

        update_page(
            child_id,
            {
                "親ゴール": {
                    "relation": [{"id": parent_id}]
                }
            },
        )

    return "OK"
