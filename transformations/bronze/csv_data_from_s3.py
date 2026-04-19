from pyspark import pipelines as dp
from pyspark.sql import functions as F
import logging
import sys

# Expectations定義をインポート（ルート直下のexpectationsフォルダから）
sys.path.append('/Workspace/Users/kuroironekko@gmail.com/test_csv_item/expectations')
from bronze_csv_quality import get_bronze_csv_expectations

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Bronze層: S3からCSVファイルを継続的に取り込む
# Auto Loaderを使用して、新しいファイルや更新されたファイルを自動検出
@dp.table(
    comment="S3バケット (s3://lambda-buket123/databricks/) からCSVファイルを継続的に取り込むBronze層テーブル"
)
# データ品質チェック（Expectationsは別ファイルで一元管理）
@dp.expect_all(get_bronze_csv_expectations())
def bronze_csv_from_s3():
    logger.info("=== Bronze CSV ストリーミング開始 ===")
    logger.info("S3パス: s3://lambda-buket123/databricks/")
    logger.info("フォーマット: CSV (header=true, inferSchema=true)")
    logger.info(f"データ品質チェック: {list(get_bronze_csv_expectations().keys())}")
    
    try:
        df = (
            spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "csv")
            .option("header", "true")  # CSVヘッダーがある場合
            .option("inferSchema", "true")  # スキーマ自動推論
            .load("s3://lambda-buket123/databricks/")
            # メタデータカラムを追加（Unity Catalog対応）
            .withColumn("_ingested_at", F.current_timestamp())
            .withColumn("_source_file", F.col("_metadata.file_path"))
        )
        
        logger.info(f"スキーマ推論完了: {df.schema.simpleString()}")
        logger.info("メタデータカラム追加: _ingested_at, _source_file")
        logger.info("Bronze層データフレーム構築成功")
        return df
        
    except Exception as e:
        logger.error(f"Bronze層データ読み込みエラー: {str(e)}", exc_info=True)
        raise
