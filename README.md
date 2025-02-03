


```
make reload
```


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
