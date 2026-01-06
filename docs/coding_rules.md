
# Coding Rules（Notion Management Project）

## 目的

- Colab 上で **毎回そのまま実行できる**
- 実行できないコード・中途半端なコードを排除する
- Notion / JSON / Python の責務を明確に分離する

---

## 【最重要ルール】絶対遵守

### 1. 実行可能な形でしかコードを書かない

- 説明だけのコードは禁止
- 擬似コード禁止
- 「あとで埋める」前提のコード禁止

👉 **そのセルを実行すれば結果が出る状態のみ可**

---

### 2. ファイル作成・更新は必ず `%%writefile` を使う

#### ✅ OK
```python
%%writefile plans/example.json
{ ... }
```

#### ❌ NG
```python
# このJSONを保存してください
```

---

### 3. JSON は「保存 → 読み込み → 実行」の順を厳守

#### 正しい流れ
```python
%%writefile plans/sample.json
{ ... }
```
```python
import json
from notion.executor import apply_plan

with open("plans/sample.json", encoding="utf-8") as f:
    plan = json.load(f)

apply_plan(plan)
```

#### ❌ NG

- JSONを直接変数に書く
- 保存せずに apply_plan に渡す

---

### 4. Notion に反映する処理は必ず明示する

- Notion に **反映する** → `apply_plan`
- **表示するだけ** → `show_tree`
- **確認のみ** → `fetch_*`

👉 「これは何をするコードか」を曖昧にしない

---

### 5. apply_plan 前提の JSON 構造

#### 必須キー

- `genre`
- `items`

#### ルール

- `items` は **親 → 子の順**
- `parent` は title 名で指定
- 存在しない parent を指定しない

---

### 6. DB構造ルール（再確認）
```
1 ホーム（DB外）
└ 2 ジャンル（select）
  └ 3 プロジェクト
    └ 4 ゴール（設計ゴール / 中間ゴール）
      └ 5 タスク
```

- ジャンルは必ず設定する
- 親ゴールなしで中間ゴール・タスクを作らない

---

### 7. 更新系の注意

- **登録日**：初回のみ
- **更新日**：Notion側で自動更新
- コード側で登録日を上書きしない

---

### 8. エラーは「構造違反」として扱う

`KeyError` / `ValueError` は  
👉 JSON or 親子構造のミス

- コードで握りつぶさない
- 例外はそのまま出す

---

## 禁止事項まとめ

- ❌ `%%writefile` を忘れる
- ❌ 実行できないコードを書く
- ❌ JSONを保存せずに使う
- ❌ 親なしタスクを作る
- ❌ `genre` を省略する

---

## 合言葉

**「そのセル、今すぐ実行できる？」**

- **YES** なら OK
- **NO** なら 書き直し

---
