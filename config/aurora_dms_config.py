"""
AWS DMS設定の一元管理

このファイルはAurora MySQL → DMS → S3 → Databricksのデータフローに関する
設定情報を一元管理します。
"""

class DMSConfig:
    """DMS設定クラス"""
    
    # ===== S3パス設定 =====
    # DMSが出力するS3バケットとパス
    S3_BUCKET = "s3://lambda-buket123"
    
    # 初回全データロード（Full Load）の出力先
    FULL_LOAD_PATH = f"{S3_BUCKET}/dms/full-load/customers/"
    
    # CDC（Change Data Capture）の出力先
    CDC_PATH = f"{S3_BUCKET}/dms/cdc/customers/"
    
    # Auto Loaderのスキーマ保存場所（Unity Catalog管理領域）
    SCHEMA_LOCATION = f"{S3_BUCKET}/schemas/aurora_dms/customers"
    
    # ===== ファイル形式設定 =====
    # DMSの出力形式（parquet, csv, json）
    FILE_FORMAT = "parquet"
    
    # ===== テーブル設定 =====
    # Auroraのソーステーブル名
    SOURCE_TABLE = "customers"
    
    # Databricks側のテーブル名
    TARGET_TABLE_FULL_LOAD = "bronze_aurora_customers_full_load"
    TARGET_TABLE_CDC_SOURCE = "bronze_aurora_customers_cdc_source"
    TARGET_TABLE_CURRENT = "bronze_aurora_customers_current"
    
    # ===== CDC設定 =====
    # プライマリキー
    PRIMARY_KEYS = ["customer_id"]
    
    # シーケンス列（順序付けに使用）
    SEQUENCE_COLUMN = "updated_at"
    
    # CDC操作列（DMSのデフォルト）
    OPERATION_COLUMN = "Op"
    
    # CDC操作タイプ
    OP_INSERT = "I"
    OP_UPDATE = "U"
    OP_DELETE = "D"
    
    @classmethod
    def get_cdc_operation_expression(cls):
        """削除操作の判定式を取得"""
        return f"{cls.OPERATION_COLUMN} = '{cls.OP_DELETE}'"
