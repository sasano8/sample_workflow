# https://github.com/unitycatalog/unitycatalog/blob/main/docs/docker_compose.md

FROM openjdk:17-jdk-slim

# sbt を実行するために curl または wget が必要です
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# リポジトリをクローンする
RUN git clone https://github.com/unitycatalog/unitycatalog /app/unitycatalog

# 作業ディレクトリを移動
WORKDIR /app/unitycatalog

# 環境変数を設定（JDK 17が使われるように）
ENV JAVA_HOME=/usr/local/openjdk-17

# リポジトリの依存関係をインストールし、アプリケーションをビルド
RUN ./build/sbt package


### Node.js のインストール
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash


SHELL ["/bin/bash", "--login", "-c"]
ENV NODE_VERSION 16
RUN nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default \
    && npm install --global yarn \
    && cd ui && yarn install


# rest=8080 UI=3000
EXPOSE 8080
EXPOSE 3000

# CMD ["./bin/start-uc-server & (cd ui && yarn start > /dev/null 2>&1) & wait"]
# CMD ["/bin/bash", "--login", "-c", "cd ui && yarn start"]
# CMD ["/bin/bash", "--login", "-c", "./bin/start-uc-server & cd ui && yarn start > /dev/null 2>&1 & wait"]
# CMD ["/bin/bash", "--login", "-c", "./bin/start-uc-server"]  # java: command not found
CMD ["./bin/start-uc-server"]
