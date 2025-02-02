


```
make reload
```


```
bin/uc table list --catalog unity --schema default
```


# 目的

* ワークフローの構築を学ぶ
* dbt を学ぶ
* Iceberg を学ぶ
* DuckDB で分析する


# kestra 環境のセットアップ

以下の順でフローを実行してください。

- setup_kestra.yml: kestra の環境設定（KVSTORE, VARIABLES, SECRETS）を行います
- setup_minio.yml: minio(S3互換のオブジェクトストレージ)の初期設定を行います
