from google.cloud import storage
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from google.oauth2 import service_account

# 環境変数を読み込む
load_dotenv()

class GCSHelper:
    def __init__(self):
        """GCSHelperクラスの初期化（環境変数ベース）"""
        self.bucket_name = "knockai-106a4.firebasestorage.app"
        
        try:
            # 環境変数SERVICE_ACCOUNT_KEYから認証情報を取得
            service_account_key = os.environ.get('SERVICE_ACCOUNT_KEY')
            if not service_account_key:
                raise ValueError("SERVICE_ACCOUNT_KEY環境変数が設定されていません。環境変数を設定してください。")
            
            # JSON文字列をパース
            service_account_info = json.loads(service_account_key)
            
            # Google Cloud Storage用の認証情報を作成
            credentials = service_account.Credentials.from_service_account_info(service_account_info)
            
            # Storageクライアントを初期化
            self.storage_client = storage.Client(credentials=credentials)
            self.bucket = self.storage_client.bucket(self.bucket_name)
            
            print("✅ SERVICE_ACCOUNT_KEY環境変数からGoogle Cloud Storageクライアントを初期化しました")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"SERVICE_ACCOUNT_KEY のJSONパースエラー: {e}")
        except Exception as e:
            raise ValueError(f"Google Cloud Storage初期化エラー: {e}")

    def download_pdf(self, gcs_file_path: str) -> str:
        """GCSからファイルをダウンロードし、ローカルのダウンロードパスを返却します。

        Args:
            gcs_file_path (str): GCS上のファイルパス

        Returns:
            str: ダウンロードされたファイルのローカルパス
        """
        try:
            # ダウンロード先のディレクトリを作成
            download_dir = os.path.join(os.getcwd(), "downloads")
            os.makedirs(download_dir, exist_ok=True)
            
            # ファイル名を取得してローカルパスを生成
            file_name = os.path.basename(gcs_file_path)
            local_path = os.path.join(download_dir, file_name)
            
            # GCSからファイルをダウンロード
            blob = self.bucket.blob(gcs_file_path)
            blob.download_to_filename(local_path)
            
            return local_path
            
        except Exception as e:
            print(f"ファイルのダウンロードに失敗しました: {e}")
            raise

    def generate_download_url(self, gcs_file_path: str, expiration_hours: int = 1) -> str:
        """GCSファイルパスからダウンロード可能なURLを生成します。

        Args:
            gcs_file_path (str): GCS上のファイルパス
            expiration_hours (int): URLの有効期限（時間）

        Returns:
            str: ダウンロード可能なURL
        """
        try:
            from datetime import timedelta
            
            # GCSのblobオブジェクトを取得
            blob = self.bucket.blob(gcs_file_path)
            
            # 署名付きURLを生成（有効期限付き）
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=expiration_hours),
                method="GET"
            )
            
            return url
            
        except Exception as e:
            print(f"ダウンロードURLの生成に失敗しました: {e}")
            return None