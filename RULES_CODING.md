# Notion Manager コーディングルール

## 0. 絶対ルール（最重要）
- **この環境では「実行できるコード」以外は価値がない**
- すべてのコードは **Colabでコピペ即実行可能**であること
- ファイル生成・更新は必ず `%%writefile` を使う
- 「例」「擬似コード」「口頭説明のみ」は禁止

---

## 1. ファイル作成ルール

### 必須
新規ファイル・修正ファイルは必ず以下の形式：
```python
%%writefile path/to/file.py
# code here
```

### 禁止
- ChatGPT上だけにコードを書く
- 「このコードを〜に保存してください」という曖昧な指示

---

## 2. 実行コードの原則

すべての処理は **この形で実行できること**：
```python
from notion.executor import apply_plan
import json

with open("plans/xxx.json", encoding="utf-8") as f:
    plan = json.load(f)

apply_plan(plan)
```

### 必須条件
- import 不足は禁止
- グローバル変数依存は禁止
- 実行手順を省略しない

---

## 3. 環境変数ルール

### 使用する環境変数
- `NOTION_TOKEN`
- `NOTION_DATABASE_ID`

### 取り扱いルール
- コード内で再定義しない
- `os.environ.get()` で取得
- 未設定時は明示的にエラーを出す
```python
token = os.environ.get("NOTION_TOKEN")
db_id = os.environ.get("NOTION_DATABASE_ID")

if not token or not db_id:
    raise RuntimeError("NOTION_TOKEN / NOTION_DATABASE_ID が未設定")
```

---

## 4. executor 実装ルール

- `apply_plan(plan)` は **1エントリポイント**
- plan の構造は executor 側で厳密に検証
- 以下は必須キー：
```json
{
  "items": []
}
```

- 存在しない parent を参照した場合は即エラー

---

## 5. JSON（plan）設計ルール

### 基本原則
- JSONは「人が読むもの」ではない
- AIが生成
- executor が厳密に解釈
- 曖昧なフィールドは禁止

### 最低限の構造
```json
{
  "items": [
    {
      "title": "",
      "type": "",
      "parent": null
    }
  ]
}
```

---

## 6. 更新処理ルール

### upsert ロジック
- title 一致で upsert

### 更新時
- 登録日は維持
- 更新日のみ変更

### 完了時
- 完了日を自動セット

---

## 7. エラー設計ルール

- 黙って失敗しない
- 必ず **意味のある日本語メッセージで例外を投げる**
```python
raise ValueError("親ゴールが存在しない: 投資OS 設計図")
```

---

## 8. 禁止事項まとめ

- ❌ `%%writefile` を使わない
- ❌ 実行方法を書かない
- ❌ JSONの仕様を曖昧にする
- ❌ 人間の記憶に依存する設計

---

## 9. このルールの目的

- 「毎回説明しなくていい」状態を作る
- AIが忘れても **ファイルが真実になる**
- 永続的に開発を回すための強制レール
