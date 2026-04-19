# Tests

このディレクトリには、パイプラインのテストコードが含まれています。

## ディレクトリ構造

```
tests/
├── conftest.py           # pytest設定・共通フィクスチャ
├── unit/                 # 単体テスト
│   ├── __init__.py
│   └── test_bronze_csv.py
└── integration/          # 統合テスト
    └── __init__.py
```

## テストの実行方法

### ノートブック/コードセルから実行

```python
import sys
sys.path.append('/Workspace/Users/kuroironekko@gmail.com/test_csv_item/tests/unit')

# モジュールキャッシュをクリア（更新時）
if 'test_bronze_csv' in sys.modules:
    del sys.modules['test_bronze_csv']

from test_bronze_csv import run_bronze_csv_tests

# テスト実行
test_success = run_bronze_csv_tests(spark)

if test_success:
    print("\n🎉 全てのテストが成功しました！")
else:
    print("\n⚠️ 一部のテストが失敗しました。")
```

### pytestを使用（CI/CD環境）

```bash
cd /Workspace/Users/kuroironekko@gmail.com/test_csv_item
pytest tests/unit/ -v
```

## テストの種類

### 単体テスト（Unit Tests）
* **目的**: 個別の関数・変換ロジックの検証
* **データ**: モックデータ使用
* **実行タイミング**: 開発時・コミット前
* **例**: `test_bronze_csv.py`

### 統合テスト（Integration Tests）
* **目的**: パイプライン全体のE2Eテスト
* **データ**: 実データまたは本番相当のデータ
* **実行タイミング**: デプロイ前・スケジュール実行
* **例**: （将来追加予定）

## ベストプラクティス

1. **テストの独立性**: 各テストは他のテストに依存しない
2. **命名規則**: `test_*.py` または `*_test.py`
3. **モックデータ使用**: 外部依存を最小化
4. **高速実行**: 単体テストは数秒以内に完了
5. **明確なアサーション**: 何をテストしているか明確に

## パイプライン実行との関係

* **テストコードはパイプライン設定に含まれません**
* パイプライン実行に影響を与えません
* 開発時・CI/CD時に独立して実行されます

## Expectations との違い

| 項目 | Tests | Expectations |
|---|---|---|
| 目的 | コードロジックの検証 | 本番データの品質保証 |
| 実行タイミング | 開発時・デプロイ前 | パイプライン実行時 |
| データ | モックデータ | 実データ |
| 場所 | `tests/` | `expectations/` |
