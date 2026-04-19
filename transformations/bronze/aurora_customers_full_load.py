"""
Aurora MySQL - 初回全データロード（DMS Full Load）

DMSが実行した初回全データロードの結果をS3から読み取り、
Bronze層テーブルとして取り込みます。
"""

from pyspark import pipelines as dp
from pyspark.sql import functions as F
import logging
import sys

# 設定とExpectationsをインポート
sys.path.append('/Workspace/Users/kuroironekko@gmail.com/test_csv_item/config')
sys.path.append('/Workspace/Users/kuroironekko@gmail.com/test_csv_item/expectations')
from aurora_dms_config import DMSConfig
from aurora_quality import get_aurora_customer_full_load_expectations

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dp.materialized_view(
    comment="Aurora MySQL顧客データの初回全データロード（DMS Full Load）"
)
@dp.expect_all(get_aurora_customer_full_load_expectations())
def bronze_aurora_customers_full_load():
    """
    DMSのFull Load結果をS3から読み取る
    
    このテーブルは初回のみ実行し、以降はCDCで差分を取り込みます。
    """
    logger.info("=== Aurora DMS Full Load 読み取り開始 ===")
    logger.info(f"S3パス: {DMSConfig.FULL_LOAD_PATH}")
    logger.info(f"ファイル形式: {DMSConfig.FILE_FORMAT}")
    
    try:
        df = (
            spark.read
            .format(DMSConfig.FILE_FORMAT)
            .load(DMSConfig.FULL_LOAD_PATH)
            .withColumn("_ingested_at", F.current_timestamp())
            .withColumn("_source_system", F.lit("aurora_mysql_dms"))
            .withColumn("_load_type", F.lit("full_load"))
        )
        
        logger.info(f"Full Load完了: {df.count()}行")
        return df
        
    except Exception as e:
        logger.error(f"Full Load読み取りエラー: {str(e)}", exc_info=True)
        raise
