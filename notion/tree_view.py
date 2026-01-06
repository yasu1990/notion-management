from collections import defaultdict


def show_tree(nodes):
    """
    nodes: List[dict]
      {
        id,
        title,
        type,
        status,
        genre,
        parent_ids
      }
    """

    node_map = {n["id"]: n for n in nodes}
    children = defaultdict(list)

    for n in nodes:
        for pid in n.get("parent_ids", []):
            children[pid].append(n["id"])

    # ルート判定：親を持たない or parent_ids が空
    roots = [
        n["id"] for n in nodes
        if not n.get("parent_ids")
    ]

    def print_tree(node_id, level=0, visited=None):
        if visited is None:
            visited = set()
        if node_id in visited:
            return
        visited.add(node_id)

        n = node_map[node_id]
        indent = "  " * level
        print(f"{indent}- {n['title']} [{n['type']} / {n['status']}]")

        for cid in children.get(node_id, []):
            print_tree(cid, level + 1, visited)

    for rid in roots:
        print_tree(rid)
