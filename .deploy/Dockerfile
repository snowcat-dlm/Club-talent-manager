FROM python:3.13

#標準出力・エラーをバッファリングしない
ENV PYTHONUNBUFFERED 1

#作業ディレクトリ
WORKDIR /workspace
# 必要なファイルをコピー
COPY ../requirements.txt .
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && pip install --no-cache-dir -r requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]


