"""
Aurora MySQLデータ品質基準の定義

このファイルは、Aurora MySQLから取り込むデータに適用するExpectationsを一元管理します。
"""

# Aurora顧客データの基本品質基準
AURORA_CUSTOMER_EXPECTATIONS = {
    "has_customer_id": "customer_id IS NOT NULL",
    "has_email": "email IS NOT NULL",
    "valid_email_format": "email LIKE '%@%'",
}

# CDC操作の品質基準
CDC_OPERATION_EXPECTATIONS = {
    "valid_operation": "Op IN ('I', 'U', 'D')",  # DMSの操作タイプ
    "has_sequence": "updated_at IS NOT NULL",     # シーケンス列は必須
}

# 全Aurora層共通の品質基準
COMMON_AURORA_EXPECTATIONS = {
    # 共通チェックをここに追加
    # 例: "no_future_dates": "created_at <= current_timestamp()",
}


def get_aurora_customer_full_load_expectations():
    """
    初回全データロード用のExpectations辞書を取得
    
    Returns:
        dict: Expectations辞書
    """
    expectations = {}
    expectations.update(AURORA_CUSTOMER_EXPECTATIONS)
    expectations.update(COMMON_AURORA_EXPECTATIONS)
    return expectations


def get_aurora_cdc_expectations():
    """
    CDC用のExpectations辞書を取得
    
    Returns:
        dict: Expectations辞書
    """
    expectations = {}
    expectations.update(AURORA_CUSTOMER_EXPECTATIONS)
    expectations.update(CDC_OPERATION_EXPECTATIONS)
    expectations.update(COMMON_AURORA_EXPECTATIONS)
    return expectations
