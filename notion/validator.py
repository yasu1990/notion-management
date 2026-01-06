# Plan JSON validator for notion-manager

ALLOWED_TYPES = {"設計ゴール", "中間ゴール", "タスク"}
ALLOWED_STATUS = {"未着手", "進行中", "完了"}
ALLOWED_PRIORITY = {"高", "中", "低"}


def validate_plan(plan: dict):
    if "items" not in plan:
        raise ValueError("plan に 'items' が存在しません")

    items = plan["items"]
    if not isinstance(items, list) or not items:
        raise ValueError("items は空でない配列である必要があります")

    titles = set()

    # 1. title 重複チェック
    for item in items:
        title = item.get("title")
        if not title:
            raise ValueError("title が未定義の item があります")
        if title in titles:
            raise ValueError(f"title が重複しています: {title}")
        titles.add(title)

    # 2. 各 item の基本構造チェック
    for item in items:
        _require(item, "type", ALLOWED_TYPES)
        _require(item, "status", ALLOWED_STATUS)
        _require(item, "priority", ALLOWED_PRIORITY)
        _require(item, "ジャンル")
        _require(item, "プロジェクト")

    # 3. 階層ルールチェック
    for item in items:
        item_type = item["type"]
        parent = item.get("parent")

        if item_type == "設計ゴール":
            if parent is not None:
                raise ValueError("設計ゴールに parent は指定できません")

        elif item_type == "中間ゴール":
            if not parent:
                raise ValueError(f"中間ゴールに parent がありません: {item['title']}")
            _assert_parent_exists(parent, titles)

        elif item_type == "タスク":
            if not parent:
                raise ValueError(f"タスクに parent がありません: {item['title']}")
            _assert_parent_exists(parent, titles)

    # 4. タスクの親は中間ゴールであること
    title_to_type = {i["title"]: i["type"] for i in items}
    for item in items:
        if item["type"] == "タスク":
            parent_type = title_to_type[item["parent"]]
            if parent_type != "中間ゴール":
                raise ValueError(
                    f"タスク '{item['title']}' の親は中間ゴールである必要があります"
                )


def _require(item, key, allowed=None):
    if key not in item:
        raise ValueError(f"{key} が未定義です: {item.get('title')}")
    if allowed and item[key] not in allowed:
        raise ValueError(
            f"{key} の値が不正です ({item.get(key)}): {item.get('title')}"
        )


def _assert_parent_exists(parent_title, titles):
    if parent_title not in titles:
        raise ValueError(f"parent が items 内に存在しません: {parent_title}")
