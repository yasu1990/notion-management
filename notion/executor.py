import os
import requests
from datetime import datetime

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

NOTION_VERSION = "2022-06-28"


def notion_headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def apply_plan(plan: dict):
    # ===== ① genre 必須チェック =====
    genre = plan.get("genre")
    if not genre:
        raise ValueError("plan に genre が指定されていません（例: 開発 / 学習）")

    items = plan.get("items")
    if not items:
        raise KeyError("plan に items が存在しません")

    # ===== ② 既存ページ取得（title → id）=====
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    res = requests.post(url, headers=notion_headers(), json={})
    res.raise_for_status()

    title_map = {}
    for r in res.json()["results"]:
        title = r["properties"]["タイトル"]["title"][0]["plain_text"]
        title_map[title] = r["id"]

    created = []

    # ===== ③ 作成処理 =====
    for item in items:
        title = item["title"]

        # genre 自動注入
        item["genre"] = genre

        parent_title = item.get("parent")
        parent_id = None

        if parent_title:
            parent_id = title_map.get(parent_title)
            if not parent_id:
                raise ValueError(f"親ゴールが存在しない: {parent_title}")

        payload = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "タイトル": {"title": [{"text": {"content": title}}]},
                "ジャンル": {"select": {"name": genre}},
                "種別": {"select": {"name": item["type"]}},
                "ステータス": {"select": {"name": item.get("status", "未着手")}},
                "優先度": {"select": {"name": item.get("priority", "中")}},
                "登録日": {"date": {"start": datetime.utcnow().isoformat()}},
            },
        }

        if parent_id:
            payload["properties"]["親ゴール"] = {
                "relation": [{"id": parent_id}]
            }

        res = requests.post(
            "https://api.notion.com/v1/pages",
            headers=notion_headers(),
            json=payload,
        )
        res.raise_for_status()

        page_id = res.json()["id"]
        title_map[title] = page_id
        created.append(title)

    print(f"作成完了: {len(created)} 件")
