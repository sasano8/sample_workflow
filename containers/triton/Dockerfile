FROM nvcr.io/nvidia/tritonserver:25.01-trtllm-python-py3

# blinker は apt 経由でインストールされたパッケージで mlflow インストール時にエラーになる
RUN apt remove -y python3-blinker && pip install mlflow

RUN mkdir -p plugins \
    && cd plugins \
    && git clone https://github.com/triton-inference-server/server.git triton-inference-server \
    && cp -r triton-inference-server/deploy/mlflow-triton-plugin mlflow-triton-plugin \
    && rm -rf triton-inference-server

RUN cd plugins/mlflow-triton-plugin \
    && python setup.py install
