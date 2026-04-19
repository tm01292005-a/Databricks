"""
Bronze層CSV取り込みの単体テスト
モックデータを使用してデータ読み込み、スキーマ検証、データ品質を検証
"""

from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql import functions as F
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BronzeCSVTest:
    """Bronze層CSV取り込みのテストクラス"""
    
    def __init__(self, spark_session):
        self.spark = spark_session
        self.test_results = []
    
    def create_mock_csv_data(self):
        """モックCSVデータを作成"""
        logger.info("=== モックデータ作成開始 ===")
        
        # テスト用のCSVデータを模倣
        mock_schema = StructType([
            StructField("id", StringType(), True),
            StructField("text", StringType(), True),
        ])
        
        mock_data = [
            ("1", "aaa"),
            ("2", "bbb"),
            ("3", "ccc"),
            ("4", "ddd"),
            ("5", "test_data"),
        ]
        
        df = self.spark.createDataFrame(mock_data, schema=mock_schema)
        logger.info(f"モックデータ作成完了: {df.count()}行")
        return df
    
    def test_schema_validation(self, df):
        """スキーマ検証テスト"""
        logger.info("=== スキーマ検証テスト開始 ===")
        
        try:
            # 期待されるカラムが存在するか確認
            expected_columns = ["id", "text"]
            actual_columns = df.columns
            
            for col in expected_columns:
                assert col in actual_columns, f"カラム '{col}' が見つかりません"
            
            logger.info(f"✅ スキーマ検証成功: {actual_columns}")
            self.test_results.append(("スキーマ検証", "PASS"))
            return True
            
        except AssertionError as e:
            logger.error(f"❌ スキーマ検証失敗: {str(e)}")
            self.test_results.append(("スキーマ検証", "FAIL", str(e)))
            return False
    
    def test_data_quality(self, df):
        """データ品質テスト"""
        logger.info("=== データ品質テスト開始 ===")
        
        try:
            # NULL値チェック
            null_count = df.filter(F.col("id").isNull()).count()
            assert null_count == 0, f"IDにNULL値が{null_count}件存在します"
            
            # 重複チェック
            total_count = df.count()
            distinct_count = df.select("id").distinct().count()
            assert total_count == distinct_count, f"重複IDが存在します（全体: {total_count}, ユニーク: {distinct_count}）"
            
            # データ件数チェック
            assert total_count > 0, "データが0件です"
            
            logger.info(f"✅ データ品質テスト成功: {total_count}行, NULL: 0件, 重複: 0件")
            self.test_results.append(("データ品質", "PASS"))
            return True
            
        except AssertionError as e:
            logger.error(f"❌ データ品質テスト失敗: {str(e)}")
            self.test_results.append(("データ品質", "FAIL", str(e)))
            return False
    
    def test_data_transformation(self, df):
        """データ変換テスト（オプション）"""
        logger.info("=== データ変換テスト開始 ===")
        
        try:
            # ID列が数値形式に変換可能か確認
            df_transformed = df.withColumn("id_int", F.col("id").cast(IntegerType()))
            invalid_count = df_transformed.filter(F.col("id_int").isNull()).count()
            
            assert invalid_count == 0, f"数値に変換できないIDが{invalid_count}件存在します"
            
            logger.info(f"✅ データ変換テスト成功: 全てのIDが数値に変換可能")
            self.test_results.append(("データ変換", "PASS"))
            return True
            
        except AssertionError as e:
            logger.error(f"❌ データ変換テスト失敗: {str(e)}")
            self.test_results.append(("データ変換", "FAIL", str(e)))
            return False
    
    def run_all_tests(self):
        """全テストを実行"""
        logger.info("========================================")
        logger.info("Bronze CSV 単体テスト実行開始")
        logger.info("========================================")
        
        # モックデータ作成
        mock_df = self.create_mock_csv_data()
        
        # 各テストを実行
        self.test_schema_validation(mock_df)
        self.test_data_quality(mock_df)
        self.test_data_transformation(mock_df)
        
        # 結果サマリー
        logger.info("========================================")
        logger.info("テスト結果サマリー")
        logger.info("========================================")
        
        passed = sum(1 for r in self.test_results if r[1] == "PASS")
        failed = sum(1 for r in self.test_results if r[1] == "FAIL")
        
        for result in self.test_results:
            status_emoji = "✅" if result[1] == "PASS" else "❌"
            logger.info(f"{status_emoji} {result[0]}: {result[1]}")
            if len(result) > 2:
                logger.info(f"   理由: {result[2]}")
        
        logger.info(f"\n合計: {passed}件成功, {failed}件失敗")
        logger.info("========================================")
        
        return failed == 0


def run_bronze_csv_tests(spark_session):
    """テストエントリーポイント（sparkセッションを引数で受け取る）"""
    tester = BronzeCSVTest(spark_session)
    success = tester.run_all_tests()
    return success
