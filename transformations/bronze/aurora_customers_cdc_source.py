"""
Aurora MySQL - CDCストリーミングソース

DMSが継続的にS3に出力するCDCデータ（INSERT/UPDATE/DELETE）を
Auto Loaderでストリーミング読み取りします。
"""

from pyspark import pipelines as dp
from pyspark.sql import functions as F
import logging
import sys

# 設定とExpectationsをインポート
sys.path.append('/Workspace/Users/kuroironekko@gmail.com/test_csv_item/config')
sys.path.append('/Workspace/Users/kuroironekko@gmail.com/test_csv_item/expectations')
from aurora_dms_config import DMSConfig
from aurora_quality import get_aurora_cdc_expectations

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dp.table(
    comment="Aurora MySQL CDCイベントをストリーミング読み取り（DMS CDC）"
)
@dp.expect_all(get_aurora_cdc_expectations())
def bronze_aurora_customers_cdc_source():
    """
    DMSのCDC出力をAuto Loaderでストリーミング読み取り
    
    DMSが出力するCDCデータには以下が含まれます：
    - Op: 操作タイプ（I=INSERT, U=UPDATE, D=DELETE）
    - データカラム: 実際のテーブルカラム
    - updated_at: シーケンス用タイムスタンプ
    """
    logger.info("=== Aurora DMS CDC ストリーミング開始 ===")
    logger.info(f"S3パス: {DMSConfig.CDC_PATH}")
    logger.info(f"ファイル形式: {DMSConfig.FILE_FORMAT}")
    logger.info(f"操作カラム: {DMSConfig.OPERATION_COLUMN}")
    
    try:
        df = (
            spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", DMSConfig.FILE_FORMAT)
            .option("cloudFiles.schemaLocation", DMSConfig.SCHEMA_LOCATION)
            .load(DMSConfig.CDC_PATH)
            .withColumn("_ingested_at", F.current_timestamp())
            .withColumn("_source_system", F.lit("aurora_mysql_dms"))
        )
        
        logger.info("CDC ストリーミングソース構築完了")
        logger.info(f"スキーマ: {df.schema.simpleString()}")
        return df
        
    except Exception as e:
        logger.error(f"CDC読み取りエラー: {str(e)}", exc_info=True)
        raise
