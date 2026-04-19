"""
pytest設定ファイル

このファイルは、pytestの共通設定とフィクスチャを定義します。
"""

import pytest
import sys
from pyspark.sql import SparkSession

# パイプラインのルートパスをPYTHONPATHに追加
sys.path.insert(0, '/Workspace/Users/kuroironekko@gmail.com/test_csv_item')


@pytest.fixture(scope="session")
def spark():
    """
    SparkSessionフィクスチャ
    
    全テストで共有されるSparkSessionを提供します。
    """
    # Databricks環境では既存のSparkSessionを使用
    from pyspark.sql import SparkSession
    return SparkSession.getActiveSession() or SparkSession.builder.getOrCreate()


@pytest.fixture(scope="function")
def sample_data(spark):
    """
    サンプルデータフィクスチャ
    
    テスト用のサンプルDataFrameを生成します。
    """
    data = [
        ("1", "aaa"),
        ("2", "bbb"),
        ("3", "ccc"),
    ]
    return spark.createDataFrame(data, ["id", "text"])
