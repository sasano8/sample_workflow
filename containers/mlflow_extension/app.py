import logging

import requests
import json

from flask import Flask, Response, request
from werkzeug.wrappers import Request, Response as WerkzeugResponse
from mlflow.server import app

# https://github.com/mlflow/mlflow/blob/v2.3.0/tests/resources/mlflow-test-plugin/mlflow_test_plugin/app.py

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# @app.before_request
# def before_req_hook():
#     raise Exception()

filters = set([
    # "/api/2.0/mlflow/registered-models/create",
    # "/api/2.0/mlflow/model-versions/create",
    "/api/2.0/mlflow/runs/update"
])

keys = set([
    "run",
    "registered_model",
    "model_version",
    "run_info"
])

@app.after_request
def after_request(response: Response):
    logger.debug(request.path)
    data = response.get_json(silent=True)  # silent: エラーの場合にNoneを返す
    if isinstance(data, dict):
        data["x-path"] = request.path
        if keys & set(data.keys()):
            with open("response.log", "a") as f:
                json.dump(data, f, ensure_ascii=False)
                f.write("\n")

    return response


# やること
# run_info の "status": "FINISHED" をフィルタする
# model_version, registered_model も監視する
# model_name or run_id or run_uuid に紐づくモデルを取得する
# staging, production に応じてデプロイする。デプロイはKestra経由でロギングできるのがよい


def deploy():
    TRACKINGURL =""
    DEPLOY_INFER_MODEL_STORAGE = ""
    TRITONSERVERURL = ""

    """
    イベントが流れてきたら、
    1. TRACKINGURL から ARTIFACT を取得する
    2. DEPLOY_INFER_MODEL_STORAGE にモデルをアップロードする
    3. TRITONSERVERURL でモデルのロード要求を行う
    """
