# python バージョン設定
FROM python:3.13

# 環境変数設定
# ターミナル出力設定 - 標準出力・エラーをバッファリングしない
ENV PYTHONUNBUFFERED=1  

# ワークスペース設定
WORKDIR /workspace

# パッケージ等をインストール
COPY ../requirements.txt .
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    locales
RUN echo "ja_JP.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen && update-locale LANG=ja_JP.UTF-8
RUN pip install --no-cache-dir -r requirements.txt

COPY .deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# ロケール設定 - Ja
ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8

