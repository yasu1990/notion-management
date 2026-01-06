import os
import requests

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

NOTION_API_URL = "https://api.notion.com/v1/databases/{}/query".format(DATABASE_ID)

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def fetch_all_pages():
    """
    Master DB から全ページを取得し、
    tree_view が期待する node 形式に正規化して返す
    """
    results = []
    payload = {}

    while True:
        res = requests.post(NOTION_API_URL, headers=HEADERS, json=payload)
        res.raise_for_status()
        data = res.json()

        for page in data["results"]:
            props = page["properties"]

            results.append({
                "id": page["id"],
                "title": props["タイトル"]["title"][0]["plain_text"]
                         if props["タイトル"]["title"] else "(no title)",
                "type": props["種別"]["select"]["name"]
                        if props["種別"]["select"] else "未設定",
                "status": props["ステータス"]["select"]["name"]
                          if props["ステータス"]["select"] else "未設定",
                "genre": props["ジャンル"]["select"]["name"]
                         if props["ジャンル"]["select"] else "未分類",
                "parent_ids": [
                    r["id"] for r in props["親ゴール"]["relation"]
                ] if props["親ゴール"]["relation"] else [],
            })

        if not data.get("has_more"):
            break

        payload["start_cursor"] = data["next_cursor"]

    return results
