# 共有ディレクトリの設定

システムでホスト側の共有ディレクトリからデータを参照できると、データの取り込みが便利なため、共有ディレクトリを作成します。

共有ディレクトリのルートと共有ディレクトリグループを作成します。

```
sudo groupadd -g 980 sharedgroup
sudo mkdir -p /mnt/share
sudo chown :sharedgroup /mnt/share
sudo chmod 2775 /mnt/share # 配下に作成されるファイル/ディレクトリのグループは/mnt/shareを引き継ぎます
```

共有ディレクトリを作成します。

```
sudo mkdir -p /mnt/share/local && sudo chmod g+w /mnt/share/local && sudo chown :sharedgroup /mnt/share/local && sudo chmod 2775 /mnt/share/local
```

ユーザーにグループ権限を付与します。

グループは再ログインで反映されます。
また、VSCODE のターミナル上などで再ログインをした場合、変更が反映されないことがあります。

```
sudo usermod -aG sharedgroup user1
```

読み書きができるか確認します。

```
cat << EOF > /mnt/share/local/sample.txt
This is sample.
EOF

cat /mnt/share/local/sample.txt
```


# サービスの起動

docker compose でサービス群を起動します。

```
make reload
```

# 初期セットアップ

Kestra UI から以下のフローを実行します。

* setup_default_kv: デフォルトの環境変数を設定する
* setup_minio: デフォルトのオブジェクトストレージ（バケット）を構成する


```
bin/uc table list --catalog unity --schema default
```


# 目的

- [x] : ワークフローの構築を学ぶ
- [x] : dbt を学ぶ
- [ ] : Iceberg を学ぶ
- [ ] : UnityCatalog を学ぶ
- [ ] : DuckDB で分析する
- [ ] : spark を学ぶ
- [ ] : データの管理方法を学ぶ
  - [ ] : 動画（webdataset, deeplake, zarr, Petastorm, LMDB）
    - [ ] : ざっくりとした感触だと webdataset がよさそう。CVAT・Supervisely などのアノテーションツールとも連携可能。
    - [ ] : Huggingface datasets でも webdataset の連携ができるっぽい


# kestra 環境のセットアップ

以下の順でフローを実行してください。

- setup_kestra.yml: kestra の環境設定（KVSTORE, VARIABLES, SECRETS）を行います
- setup_minio.yml: minio(S3互換のオブジェクトストレージ)の初期設定を行います


# spark 環境

* https://iceberg.apache.org/spark-quickstart/#writing-data-to-a-table

```
/opt/spark/bin/spark-sql --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.7.1\
    --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
    --conf spark.sql.catalog.spark_catalog=org.apache.iceberg.spark.SparkSessionCatalog \
    --conf spark.sql.catalog.spark_catalog.type=hive \
    --conf spark.sql.catalog.local=org.apache.iceberg.spark.SparkCatalog \
    --conf spark.sql.catalog.local.type=hadoop \
    --conf spark.sql.catalog.local.warehouse=$PWD/warehouse \
    --conf spark.sql.defaultCatalog=local
```


```
/opt/spark/bin/spark-sql --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.7.1 \
    --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
    --conf spark.sql.catalog.spark_catalog=org.apache.iceberg.spark.SparkSessionCatalog \
    --conf spark.sql.catalog.spark_catalog.type=hive \
    --conf spark.sql.catalog.rest=org.apache.iceberg.spark.SparkCatalog \
    --conf spark.sql.catalog.rest.type=rest \
    --conf spark.sql.catalog.rest.uri=http://your-rest-catalog-endpoint \
    --conf spark.sql.defaultCatalog=rest
```

```
/opt/spark/bin/spark-sql --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.7.1 \
    --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
    --conf spark.sql.catalog.spark_catalog=org.apache.iceberg.spark.SparkSessionCatalog \
    --conf spark.sql.catalog.spark_catalog.type=hive \
    --conf spark.sql.catalog.s3=org.apache.iceberg.spark.SparkCatalog \
    --conf spark.sql.catalog.s3.type=hadoop \
    --conf spark.sql.catalog.s3.warehouse=s3a://your-bucket-name/warehouse \
    --conf spark.sql.catalog.s3.hadoop.fs.s3a.access.key=your-access-key \
    --conf spark.sql.catalog.s3.hadoop.fs.s3a.secret.key=your-secret-key \
    --conf spark.sql.defaultCatalog=s3
```


## 動画データセット

WebDataset は次のような構造を持つ。

```
dataset.tar
├── video_0001.mp4
├── video_0001.json
├── frame_0001_0000.jpg
├── frame_0001_0000.json
├── frame_0001_0001.jpg
├── frame_0001_0001.json
```


# YouTube-BoundingBoxes Dataset
