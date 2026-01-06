from collections import defaultdict

def show_tree(nodes):
    """
    ジャンル(select)をルートとしてツリー表示する
    """

    # -----------------------------
    # 前処理
    # -----------------------------
    by_id = {n["id"]: n for n in nodes}
    children = defaultdict(list)

    for n in nodes:
        for pid in n.get("parent_ids", []):
            children[pid].append(n["id"])

    # -----------------------------
    # ジャンルごとに分類
    # -----------------------------
    genre_map = defaultdict(list)
    for n in nodes:
        genre = n.get("genre") or "未分類"
        genre_map[genre].append(n)

    # -----------------------------
    # 再帰表示（循環防止）
    # -----------------------------
    def print_tree(node_id, level, visited):
        if node_id in visited:
            return
        visited.add(node_id)

        node = by_id[node_id]
        indent = "  " * level
        print(f"{indent}- {node['title']} [{node['type']} / {node['status']}]")

        for cid in children.get(node_id, []):
            print_tree(cid, level + 1, visited)

    # -----------------------------
    # 表示
    # -----------------------------
    for genre, genre_nodes in genre_map.items():
        print(f"\n[{genre}]")

        # ルート候補：
        # ・親を持たない
        # ・親がDB内に存在しない
        roots = []
        for n in genre_nodes:
            parents = n.get("parent_ids", [])
            if not parents or not any(p in by_id for p in parents):
                roots.append(n["id"])

        for rid in roots:
            print_tree(rid, 1, set())
