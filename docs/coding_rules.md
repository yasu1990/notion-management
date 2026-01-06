
# Coding Rules (notion-manager)

本ドキュメントは **notion-manager を Colab + GitHub + Notion API で安全・再現性高く運用するためのコーディングルール** を定義する。  
感情・判断・記憶に依存せず、**常に実行できるコードだけが残る状態**を作ることを目的とする。

---

## 1. 基本原則（最重要）

### 1.1 常に「実行可能なコード」を書く

- README 用の疑似コードは禁止
- 動かないコードは「コード」と呼ばない
- **実行セル単位で完結していること**

---

### 1.2 Colab では `%%writefile` を必ず使う

- ファイルを生成・更新する場合は **必ず `%%writefile`**
- 口頭説明・擬似コードは禁止

❌ **NG:**
```python
# こんな感じで書いてください
def foo():
    pass
```

✅ **OK:**
```python
%%writefile foo.py
def foo():
    pass
```

---

## 2. 実行コードのルール

### 2.1 import の順序

1. 標準ライブラリ
2. サードパーティ
3. 自作モジュール

**例:**
```python
import os
import json

import requests

from notion.executor import apply_plan
```

### 2.2 環境変数の扱い

- コード内で Token / DB ID を直接書かない
- `os.environ` から取得する
- 未設定時は明示的にエラーを出す
```python
def require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"環境変数が未設定です: {key}")
    return value
```

---

## 3. Notion 操作ルール

### 3.1 DB構造を勝手に推測しない

- プロパティ名は Master DB 定義と完全一致
- spell / 日本語名を変えない

### 3.2 親子関係（relation）は executor に任せる

- JSON 側では **親は title 名で指定**
- ID を JSON に書かない
```json
{
  "title": "日次スクリーニングを実装する",
  "type": "タスク",
  "parent": "小型株150億以下で監視する仕組みを作る"
}
```

### 3.3 登録日・更新日の扱い

- **登録日**: 初回作成時のみセット
- **更新日**: Notion 側の自動更新に任せる
- 手動で上書きしない

---

## 4. plan(JSON) 運用ルール

### 4.1 plan は「実行単位」

- `plan` = 1回の `apply_plan()` 実行
- DBの状態に依存しない設計を心がける

### 4.2 plan JSON の必須構造
```json
{
  "items": [
    {
      "title": "...",
      "type": "...",
      "parent": "...",
      "priority": "...",
      "status": "..."
    }
  ]
}
```

- `items` が無い JSON は **即エラー**
- executor 側で例外を出すのは正しい挙動

---

## 5. GitHub 運用ルール

### 5.1 Colab は「作業場」

- 正式なコードは GitHub
- Colab 上で動作確認 → commit → push

### 5.2 commit メッセージ

- 何を直したかを1行で
- 感情・雑談は禁止

**例:**
```
Fix parent resolution and stabilize apply_plan execution
```

---

## 6. 禁止事項（重要）

- ❌ 実行できないコードを貼る
- ❌ `%%writefile` を省略する
- ❌ 「こういう感じで」という説明
- ❌ DB構造を無視した JSON
- ❌ 親ゴール未作成のまま子を登録する

---

## 7. 判断に迷ったら

**「このセルをそのまま実行して事故らないか?」**

- **YES** → OK
- **NO** → 書き直す

---

## 8. このルールの位置づけ

- **思考・設計ルール** → `docs/ai_prompt.md`
- **実装・運用ルール** → `docs/coding_rules.md`

混ぜない。役割を分ける。

---

**以上**
