# Aurora MySQL CDC実装ガイド

AWS DMS経由でAurora MySQLからデータを取り込むパイプラインの実装です。

## 📁 ファイル構成

```
test_csv_item/
├── config/
│   └── aurora_dms_config.py           # DMS設定の一元管理
├── expectations/
│   ├── bronze_csv_quality.py          # CSV品質基準
│   └── aurora_quality.py              # Aurora品質基準
└── transformations/
    └── bronze/
        ├── csv_data_from_s3.py                      # S3 CSV取り込み
        ├── aurora_customers_full_load.py            # Aurora初回全データ
        ├── aurora_customers_cdc_source.py           # Aurora CDCソース
        └── aurora_customers_cdc_target.py           # Aurora CDCターゲット
```

## 🔄 データフロー

```
Aurora MySQL
    ↓ (Binlog)
AWS DMS
    ↓
S3 (Full Load + CDC)
    ↓
Databricks Auto Loader
    ↓
Bronze層（最新状態）
```

## 🚀 セットアップ手順

### 1. AWS DMS設定

#### DMSレプリケーションインスタンスの作成

```bash
# AWS CLI例
aws dms create-replication-instance \
  --replication-instance-identifier aurora-to-s3 \
  --replication-instance-class dms.t3.medium
```

#### Auroraエンドポイント作成

```bash
aws dms create-endpoint \
  --endpoint-identifier aurora-source \
  --endpoint-type source \
  --engine-name aurora \
  --server-name your-aurora-cluster.cluster-xxx.rds.amazonaws.com \
  --port 3306 \
  --database-name production \
  --username your_user \
  --password your_password
```

#### S3エンドポイント作成

```bash
aws dms create-endpoint \
  --endpoint-identifier s3-target \
  --endpoint-type target \
  --engine-name s3 \
  --s3-settings '{
    "BucketName": "lambda-buket123",
    "BucketFolder": "dms",
    "DataFormat": "parquet",
    "CompressionType": "gzip",
    "CdcPath": "cdc/customers",
    "EnableStatistics": true
  }'
```

#### レプリケーションタスクの作成

```json
{
  "rules": [
    {
      "rule-type": "selection",
      "rule-id": "1",
      "rule-name": "customers-table",
      "object-locator": {
        "schema-name": "production",
        "table-name": "customers"
      },
      "rule-action": "include"
    }
  ]
}
```

```bash
aws dms create-replication-task \
  --replication-task-identifier aurora-customers-replication \
  --source-endpoint-arn <aurora-source-arn> \
  --target-endpoint-arn <s3-target-arn> \
  --replication-instance-arn <instance-arn> \
  --migration-type full-load-and-cdc \
  --table-mappings file://table-mappings.json
```

### 2. Aurora MySQL設定

#### Binlogの有効化

```sql
-- パラメータグループで設定
binlog_format = ROW
binlog_row_image = FULL
```

### 3. Databricks設定

#### config/aurora_dms_config.py の更新

```python
class DMSConfig:
    S3_BUCKET = "s3://your-bucket-name"  # 実際のバケット名に変更
    FULL_LOAD_PATH = f"{S3_BUCKET}/dms/full-load/customers/"
    CDC_PATH = f"{S3_BUCKET}/dms/cdc/customers/"
    PRIMARY_KEYS = ["customer_id"]  # 実際のPKに変更
    SEQUENCE_COLUMN = "updated_at"  # 実際のカラム名に変更
```

## 📊 実行手順

### ステップ1: DMS Full Loadを実行

DMSタスクを開始して、初回全データロードを実行します。

```bash
aws dms start-replication-task \
  --replication-task-arn <task-arn> \
  --start-replication-task-type start-replication
```

### ステップ2: Databricksパイプラインを実行

```python
# パイプライン実行
# 初回は bronze_aurora_customers_full_load のみ実行
# その後、bronze_aurora_customers_cdc_source と bronze_aurora_customers_current を実行
```

### ステップ3: CDCの継続実行

DMSがCDCモードに入ると、Auroraの変更が継続的にS3に出力されます。
パイプラインをContinuous Modeまたはスケジュール実行で定期的に実行してください。

## 🔍 データの確認

### Full Loadデータの確認

```sql
SELECT * FROM test_catalog.test_schema.bronze_aurora_customers_full_load LIMIT 10;
```

### CDCソースデータの確認

```sql
SELECT * FROM test_catalog.test_schema.bronze_aurora_customers_cdc_source
ORDER BY updated_at DESC LIMIT 10;
```

### 最新状態の確認（CDC適用済み）

```sql
SELECT * FROM test_catalog.test_schema.bronze_aurora_customers_current LIMIT 10;
```

## 🎯 CDC操作の確認

```sql
-- INSERT/UPDATE/DELETEの統計
SELECT 
    Op as operation_type,
    COUNT(*) as event_count
FROM test_catalog.test_schema.bronze_aurora_customers_cdc_source
GROUP BY Op;
```

## ⚠️ トラブルシューティング

### S3パスが存在しない

**症状**: `Path does not exist: s3://...`

**解決策**: 
- DMSタスクが正常に実行されているか確認
- S3バケットのパスが正しいか確認

### スキーマエラー

**症状**: スキーマが一致しない

**解決策**:
- DMSの出力形式を確認（parquet推奨）
- Auto LoaderのschemaLocationをクリアして再実行

### CDCが適用されない

**症状**: DELETEが反映されない

**解決策**:
- `Op` カラムがデータに含まれているか確認
- `apply_as_deletes` の式が正しいか確認

## 📖 参考資料

- [AWS DMS Documentation](https://docs.aws.amazon.com/dms/)
- [Databricks Auto Loader](https://docs.databricks.com/ingestion/auto-loader/)
- [Spark Declarative Pipelines Auto CDC](https://docs.databricks.com/delta-live-tables/cdc.html)
