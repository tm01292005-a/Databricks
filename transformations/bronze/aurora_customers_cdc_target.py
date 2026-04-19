"""
Aurora MySQL - CDCターゲットテーブル

CDCイベント（INSERT/UPDATE/DELETE）を適用して、
Aurora MySQLの顧客データの最新状態を維持します。
"""

from pyspark import pipelines as dp
from pyspark.sql.functions import expr
import logging
import sys

# 設定をインポート
sys.path.append('/Workspace/Users/kuroironekko@gmail.com/test_csv_item/config')
from aurora_dms_config import DMSConfig

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ===== ステップ1: CDCターゲットテーブルを作成 =====
dp.create_streaming_table(
    name=DMSConfig.TARGET_TABLE_CURRENT,
    comment="Aurora MySQL顧客データの最新状態（CDC適用済み）"
    # 注意: スキーマは自動推論されます
    # 明示的にスキーマを定義する場合は、schema パラメータを使用
)


# ===== ステップ2: Auto CDCフローを定義 =====
logger.info("=== Aurora Auto CDC フロー定義 ===")
logger.info(f"ソース: {DMSConfig.TARGET_TABLE_CDC_SOURCE}")
logger.info(f"ターゲット: {DMSConfig.TARGET_TABLE_CURRENT}")
logger.info(f"プライマリキー: {DMSConfig.PRIMARY_KEYS}")
logger.info(f"シーケンス列: {DMSConfig.SEQUENCE_COLUMN}")

dp.create_auto_cdc_flow(
    target=DMSConfig.TARGET_TABLE_CURRENT,
    source=DMSConfig.TARGET_TABLE_CDC_SOURCE,
    keys=DMSConfig.PRIMARY_KEYS,
    sequence_by=DMSConfig.SEQUENCE_COLUMN,
    apply_as_deletes=expr(DMSConfig.get_cdc_operation_expression()),
    ignore_null_updates=True,
    stored_as_scd_type=1  # SCD Type 1: 最新状態のみ保持
)

logger.info("Auto CDC フロー定義完了")
logger.info("""
CDCフローの動作:
- INSERT (Op='I'): 新しいレコードを追加
- UPDATE (Op='U'): 既存レコードを更新
- DELETE (Op='D'): レコードを削除
- 順序: updated_at カラムで順序付け
- NULL更新: 無視（ignore_null_updates=True）
""")
