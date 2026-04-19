"""
Bronze層データ品質基準の定義

このファイルは、Bronze層のデータセットに適用するExpectationsを一元管理します。
将来的に複数のBronze層データセットで共通の品質基準を再利用できます。
"""

# Bronze層CSV取り込みの品質基準
BRONZE_CSV_EXPECTATIONS = {
    "has_id": "id IS NOT NULL",
    "has_text": "text IS NOT NULL"
}

# スキーマ不一致検出のExpectation
BRONZE_SCHEMA_EXPECTATIONS = {
    "no_rescued_data": "_rescued_data IS NULL"
}

# 全Bronze層共通の品質基準（将来の拡張用）
COMMON_BRONZE_EXPECTATIONS = {
    # 共通チェックをここに追加
    # 例: "has_ingestion_timestamp": "_ingested_at IS NOT NULL",
}


def get_bronze_csv_expectations():
    """
    Bronze層CSV用のExpectations辞書を取得
    
    Returns:
        dict: Expectations辞書
    """
    expectations = {}
    expectations.update(BRONZE_CSV_EXPECTATIONS)
    expectations.update(BRONZE_SCHEMA_EXPECTATIONS)
    expectations.update(COMMON_BRONZE_EXPECTATIONS)
    return expectations
