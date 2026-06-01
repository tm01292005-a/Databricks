■前提条件

| No | 前提条件                          | 設計への影響                      |
| -- | ----------------------------- | --------------------------- |
| 1  | Databricks + Unity Catalogを利用 | Catalog / Schema / Tableで管理 |
| 2  | ソースDBはAWS・OCI等に5システム程度存在      | ソース単位の管理が必要                 |
| 3  | テーブル数は数百規模                    | 業務ドメイン分割は困難                 |
| 4  | 利用者は国内・海外グループ会社・社外利用者         | マルチテナント設計が必要                |
| 5  | 利用会社は数百社規模                    | 会社単位Catalogは非現実的            |
| 6  | 利用者はBronzeを参照しない              | Bronzeは運用専用                 |
| 7  | 利用者はSilverとGoldのみ利用           | 利用者向け公開レイヤーが必要              |
| 8  | Bronze→Silverはほぼ同一構造          | Silverは公開用データ               |
| 9  | Bronze→Silverでマスキング・品質補正を実施   | Silverが公開データの起点             |
| 10 | Bronzeは運用者が管理                 | 利用者は変更不可                    |
| 11 | Silver(運用データ)は運用者が管理          | 利用者は参照のみ                    |
| 12 | 利用者自身もSilverにデータ作成する          | Silver内に運用領域と利用者領域が存在       |
| 13 | 利用者はGoldにもデータ作成する             | 利用者専用領域が必要                  |
| 14 | 運用者は利用者作成データを管理しない            | 管理責任境界が必要                   |
| 15 | 社外共有が存在する                     | Delta Sharingや共有領域が必要       |
| 16 | 利用者数は数百社規模                    | Row Filter / ABAC活用を検討      |



■カタログとアクセス制御

| Catalog       | Schema単位                  | 管理者 | 主なデータ           | 利用者権限                | 運用者権限    | アクセス制御方針            |
| ------------- | ------------------------- | --- | --------------- | -------------------- | -------- | ------------------- |
| bronze        | ソースDB単位                   | 運用  | 生データ            | なし                   | ALL      | Catalog単位で閉鎖        |
| silver_shared | ソースDB単位                   | 運用  | マスキング済・品質補正済データ | SELECT               | ALL      | Schema単位で参照許可       |
| silver_user   | 利用者種別（internal/external等） | 利用者 | 利用者作成の中間データ     | CREATE/SELECT/MODIFY | 参照のみ（原則） | Schema単位で利用者グループへ付与 |
| gold          | 利用者種別（internal/external等） | 利用者 | 分析成果物・公開データ     | CREATE/SELECT/MODIFY | 参照のみ（原則） | Schema単位で利用者グループへ付与 |
| shared        | 共有先種別                     | 運用  | 外部共有データ         | なし                   | ALL      | Delta Sharing管理     |
| admin         | audit/monitoring          | 運用  | 監査・運用データ        | なし                   | ALL      | 運用者のみ               |



■UnityCatalog権限レベル

| レベル         | 制御対象    | 制御内容                                |
| ----------- | ------- | ----------------------------------- |
| Catalog     | 管理責任境界  | bronzeは運用者のみ、silver_shared以降を利用者へ公開 |
| Schema      | 利用者種別   | internal / external 等で作成権限を分離       |
| Table/View  | データセット  | 個別の公開制御                             |
| Row Filter  | 会社単位    | `company_id` による行制御                 |
| Column Mask | データ分類単位 | 個人情報・機微情報のマスキング                     |


■グループ設計

| グループ             | 権限対象                                               | 側 |
| ---------------- | -------------------------------------------------- | --- |
| platform_admin   | 全Catalog                                           | 運用 |
| data_engineer    | bronze, silver_shared                              | 運用 |
| internal_user    | silver_shared, silver_user.internal, gold.internal | 利用者/運用 |
| external_user    | silver_shared, silver_user.external, gold.external | 利用者/運用 |
| data_share_admin | shared                                             | 利用者/運用 |
| auditor          | admin                                              | 運用 |





＜考え方＞
・Catalogは管理責任単位で分ける
・Schemaは利用者管理のデータの場合、利用者単位で分ける
・Schemaは運用管理のデータの場合、運用単位で分ける

