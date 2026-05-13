必須に近いもの（Databricks ワークスペース側）

VPC。Databricks ワークスペースを置くための Customer-managed VPC です。1つのVPCを複数ワークスペースで共有できますが、Databricks はワークスペースごとに一意のサブネットとセキュリティグループを推奨しています。
プライベートサブネット 2つ以上。少なくとも2つのAZにまたがる必要があり、各サブネットは /17〜/26 の範囲で、プライベートである必要があります。
ルートテーブル。ワークスペース用サブネットのルートに、0.0.0.0/0 を NAT Gateway もしくは Network Firewall に向ける設定と、S3 Gateway VPC Endpoint へのルートが必要です。
NAT Gateway。インターネット向けのアウトバウンド通信のために必要で、HAを狙うならAZごとに配置します。NAT 用の別サブネットと、その先に接続された Internet Gateway が必要です。
セキュリティグループ。ワークスペースは少なくとも1つ、最大5つまでのSGにアクセスできる必要があります。少なくとも、内部トラフィック許可と、443 / 3306 / 8443 / 8445 / 8444 などのアウトバウンド許可が必要です。
サブネットNACL。Databricks の要件では、NACLはトラフィックを拒否してはいけず、0.0.0.0/0 を許可する前提です。
DNS有効化。VPCで DNS hostnames と DNS resolution を有効にしておく必要があります。

接続・AWSサービス連携で必要になりやすいもの

S3 Gateway VPC Endpoint。ワークスペースからS3へアクセスするための基本要素です。
Interface VPC Endpoint（STS / Kinesis）。公式ガイドでは、AWSのSTSとKinesisへプライベートにアクセスするために別サブネットへ配置する想定です。S3を完全にプライベート化したい場合は、S3のInterface Endpointも追加します。
S3バケット。Unity Catalog の管理対象ストレージや外部テーブル用に、メタストアレベルで0または1個、カタログ/スキーマレベルで0個以上、外部テーブル用に0個以上の S3 バケットを使います。
クロスアカウント IAM ロール。Unity Catalog のストレージ認証情報として、Databricks がバケットにアクセスするための信頼関係付きクロスアカウント IAM ロールが必要です。

条件付きで追加するもの

AWS PrivateLink 用のエンドポイント。Backend PrivateLink を使うなら Customer-managed VPC が必要で、フロントエンド/バックエンド両方の設計を検討します。
Network Firewall / プロキシ用の専用サブネット。送信制御やデータ漏洩対策を強める場合に追加します。
Route 53 / DNS設定。PrivateLink や名前解決を使う場合に、DNSまわりの設定が必要になります。

外部データソース側（別AWSアカウント）

ここは Databricks 固有のAWSリソースというより、接続先の側にある VPC / サブネット / ルートテーブル / セキュリティグループ の調整です。公式の VPC Peering 文書は、Databricks クラスターから他の AWS 基盤へ接続する例として説明しています。DirectConnect が既にあるなら、あとはその経路で到達できるように、相手側の SG とルートを合わせるのが主な作業になります。