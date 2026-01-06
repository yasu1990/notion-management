def build_properties(domain, item):
    return {
        "タイトル": {
            "title": [{"text": {"content": item["title"]}}]
        },
        "ドメイン": {
            "select": {"name": domain}
        },
        "テーマ": {
            "select": {"name": item["theme"]}
        },
        "種別": {
            "select": {"name": item["type"]}
        },
        "ステータス": {
            "select": {"name": item.get("status", "未着手")}
        },
        "優先度": {
            "select": {"name": item.get("priority", "中")}
        },
        "知見": {
            "rich_text": [
                {"text": {"content": item["knowledge"]}}
            ] if item.get("knowledge") else []
        },
    }
