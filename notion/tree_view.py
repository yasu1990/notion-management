import os
import requests

NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"


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
    results = []
    payload = {}

    while True:
        res = requests.post(url, headers=headers(), json=payload)
        res.raise_for_status()
        data = res.json()
        results.extend(data["results"])
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]

    return results


def get_text(prop):
    if not prop:
        return ""
    return prop[0]["plain_text"]


def build_nodes(pages):
    nodes = {}
    children = {}

    for p in pages:
        pid = p["id"]
        props = p["properties"]

        title = get_text(props["タイトル"]["title"])
        type_ = props["種別"]["select"]["name"]
        status = props["ステータス"]["select"]["name"]

        parent_rel = props.get("親ゴール", {}).get("relation", [])
        parent_id = parent_rel[0]["id"] if parent_rel else None

        nodes[pid] = {
            "id": pid,
            "title": title,
            "type": type_,
            "status": status,
            "parent": parent_id,
        }
        children.setdefault(pid, [])

    for n in nodes.values():
        if n["parent"] and n["parent"] in nodes:
            children[n["parent"]].append(n["id"])

    return nodes, children


def print_tree(nodes, children, node_id, level=0):
    n = nodes[node_id]
    indent = "  " * level
    print(f"{indent}- {n['title']} [{n['type']} / {n['status']}]")
    for cid in children.get(node_id, []):
        print_tree(nodes, children, cid, level + 1)


def show_tree():
    database_id = os.environ.get("NOTION_DATABASE_ID")
    if not database_id:
        raise RuntimeError("NOTION_DATABASE_ID が未設定")

    pages = fetch_all_pages(database_id)
    nodes, children = build_nodes(pages)

    # ★ ルートは「設計ゴール」
    roots = [
        nid for nid, n in nodes.items()
        if n["type"] == "設計ゴール"
    ]

    if not roots:
        print("⚠ 設計ゴールが見つかりません")
        return

    for r in roots:
        print_tree(nodes, children, r)


if __name__ == "__main__":
    show_tree()
