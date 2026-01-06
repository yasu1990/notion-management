from collections import defaultdict

def show_tree(nodes):
    by_id = {n["id"]: n for n in nodes}
    children = defaultdict(list)

    for n in nodes:
        for pid in n.get("parent_ids", []):
            children[pid].append(n["id"])

    genre_map = defaultdict(list)
    for n in nodes:
        genre = n.get("genre") or "未分類"
        genre_map[genre].append(n)

    def print_tree(node_id, level, visited):
        if node_id in visited:
            return
        visited.add(node_id)

        node = by_id[node_id]
        indent = "  " * level
        print(f"{indent}- {node['title']} [{node['type']} / {node['status']}]")

        for cid in children.get(node_id, []):
            print_tree(cid, level + 1, visited)

    for genre, genre_nodes in genre_map.items():
        print(f"\n[{genre}]")

        genre_ids = {n["id"] for n in genre_nodes}

        # ★ 修正ポイント ★
        # 親が「同ジャンル内に存在しない」ものをルートとする
        roots = []
        for n in genre_nodes:
            parents = n.get("parent_ids", [])
            if not parents:
                roots.append(n["id"])
            elif not any(p in genre_ids for p in parents):
                roots.append(n["id"])

        for rid in roots:
            print_tree(rid, 1, set())
