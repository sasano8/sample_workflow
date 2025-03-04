# Open-WebUI と ollama の連携

docker コンテナ上の Open-WebUI から ollama に接続するために、次の構成変更が必要です。

* sudo vi /etc/systemd/system/ollama.service
  * Environment="OLLAMA_HOST=0.0.0.0:11434"
* sudo systemctl daemon-reload
* sudo systemctl restart ollama

連携がうまくいってる場合、ollama で管理されているモデルが Open-WebUI にも表示されます。


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


# 推論サーバーへのデプロイ管理

Triton 上で mlflow（リモート接続） を使ってデプロイすればいい？
どこに何がデプロイされるのか理解していない。
MLFlow Triton Plugin は上手く動作させられなかった。
Onnx を単に置けばいいだけなので、あまり MLFlow Triton Plugin の必要性を感じなかった。

```
mlflow deployments create -t triton --flavor triton --name yolov6n -m models:/yolov6n/1
mlflow deployments delete -t triton --name yolov6n
mlflow deployments update -t triton --flavor triton --name yolov6n -m models:/yolov6n/2
```


# 目的

- [x] : ワークフローの構築を学ぶ
- [x] : データビルド
  - [x] : dbt を構築する
- [ ] : データセット管理
  - [x] : Iceberg を構築する
  - [x] : UnityCatalog を構築する
  - [x] : 機械学習向けデータセット
    - [x] : Huggingface datasets
    - 動画データセット
      - [ ] : webdataset（CVAT・Supervisely などの様々なアノテーションツールでサポートされていて一番有力そう。datasets とも連携できそう）
      - [ ] : その他（deeplake, zarr, Petastorm, LMDB）
- [ ] : 機械学習・推論
  - [x] : MLFlow の導入
  - [x] : MlFlow と連携した学習
  - [x] : Triton の導入
  - [x] : 推論モデルをデプロイ
  - [x] : 推論結果で期待する分類結果を得る
  - [ ] : Minio から MQTT などでイベントを連携して、そのモデルを Triton にデプロイ（Kestra などで実行するのがログに残ってよいだろう）
  - [ ] : MLFlow のイベントを購読した方がスマートだが、MLFlow自体にはイベントのpush機構はないようだ。ポーリングなどで実装もできる。rising wave で sync でもよいな。
  - [ ] : 分散学習
    - [ ] : Ray
- [ ] : 分析
  - [ ] : DuckDB で分析する
  - [ ] : spark を学ぶ
  - [ ] : flink などリアルタイムストリーム処理と推論を組み合わせたい



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
