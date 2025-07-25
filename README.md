# Talent Manager 運動部 部員身体能力 記録管理サービス
運動部における日々の能力測定の記録を保存し、時系列で確認できます。

## 機能一覧

- 監督・コーチ 共通
    - 部員の管理（入部によるアカウント作成、退部）
    - 全部員の記録を確認
- コーチ
    - プレーヤー(選手)承認済みの測定記録結果を承認
- マネージャー
    - 測定結果の入力
    - 入力した測定結果の承認要求を発行
- プレーヤー
    - 登録された自己の測定記録結果を承認
    - 自己の記録のみが時系列で確認

## システム構成
### システム構成図

### ER図
![ER図](documents/ER図/他形式ファイル/ER図.png)
documents/ER図/他形式ファイル/ER図.md

### ユースケース図

### 測定記録登録時の承認フロー

## デプロイ方法
- .env_templete ファイルを.deployへコピーして、本番用環境変数を設定してください。


## クローンによる開発環境構築
### 起動まで
- VSCodeを起動 
- 開発コンテナ:コンテナーでフォルダを開く...（Open folder in container...）でプロジェクトを開く
- 初期化のため以下のコマンドを実行
    - djangoのプロジェクトフォルダへ移動  
        >　cd talentManager
    - マイグレーションファイルを作成
        > python manage.py makemigrations  
    - マイグレーションを実行
        > python manage.py migrate  
- TestServerの起動準備完了！

### TestServer起動
- djangoのプロジェクトフォルダへ移動（移動済みの場合は不要）
    >　cd talentManager
- 以下のコマンドでサーバーを起動する
    > python manage.py runserver  
