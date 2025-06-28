import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Any, Optional
from google.oauth2 import service_account

# 環境変数を読み込む
load_dotenv()

class FirestoreHelper:
    def __init__(self):
        """FirestoreHelperクラスの初期化（環境変数ベース）"""
        # Firebase Admin SDKが既に初期化されているかチェック
        if not firebase_admin._apps:
            try:
                # 環境変数SERVICE_ACCOUNT_KEYから認証情報を取得
                service_account_key = os.environ.get('SERVICE_ACCOUNT_KEY')
                if not service_account_key:
                    raise ValueError("SERVICE_ACCOUNT_KEY環境変数が設定されていません。環境変数を設定してください。")
                
                # JSON文字列をパース
                service_account_info = json.loads(service_account_key)
                
                # Firebase Admin SDK用の認証情報を作成
                cred = credentials.Certificate(service_account_info)
                
                # Firebase Admin SDKを初期化
                firebase_admin.initialize_app(cred)
                print("✅ SERVICE_ACCOUNT_KEY環境変数からFirebase Admin SDKを初期化しました")
                
            except json.JSONDecodeError as e:
                raise ValueError(f"SERVICE_ACCOUNT_KEY のJSONパースエラー: {e}")
            except Exception as e:
                raise ValueError(f"Firebase Admin SDK初期化エラー: {e}")
        
        # Firestoreクライアントを取得
        self.db = firestore.client()
    
    def add_document(self, collection_name: str, document_data: Dict[str, Any], document_id: Optional[str] = None) -> str:
        """ドキュメントをコレクションに追加します
        
        Args:
            collection_name (str): コレクション名
            document_data (Dict[str, Any]): ドキュメントのデータ
            document_id (Optional[str]): ドキュメントID（指定しない場合は自動生成）
            
        Returns:
            str: 追加されたドキュメントのID
        """
        collection_ref = self.db.collection(collection_name)
        
        # タイムスタンプを追加
        document_data['created_at'] = datetime.now()
        document_data['updated_at'] = datetime.now()
        
        if document_id:
            # 指定されたIDでドキュメントを作成
            doc_ref = collection_ref.document(document_id)
            doc_ref.set(document_data)
            return document_id
        else:
            # 自動生成IDでドキュメントを作成
            _, doc_ref = collection_ref.add(document_data)
            return doc_ref.id
    
    def get_document(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """指定されたドキュメントを取得します
        
        Args:
            collection_name (str): コレクション名
            document_id (str): ドキュメントID
            
        Returns:
            Optional[Dict[str, Any]]: ドキュメントのデータ（存在しない場合はNone）
        """
        try:
            print(f"🔍 DEBUG: FirestoreHelper.get_document called")
            print(f"   📁 Collection: {collection_name}")
            print(f"   🆔 Document ID: {document_id}")
            
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc = doc_ref.get()
            
            print(f"   📄 Document exists: {doc.exists}")
            
            if doc.exists:
                doc_data = doc.to_dict()
                print(f"   📋 Document keys: {list(doc_data.keys()) if isinstance(doc_data, dict) else 'Not a dict'}")
                print(f"   📊 Document type: {type(doc_data)}")
                print(f"   📝 Document content preview: {str(doc_data)[:200]}...")
                return doc_data
            else:
                print(f"   ❌ Document does not exist")
                return None
                
        except Exception as e:
            print(f"❌ ERROR in FirestoreHelper.get_document: {str(e)}")
            print(f"   🔍 Exception type: {type(e)}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
            raise e
    
    def update_document(self, collection_name: str, document_id: str, update_data: Dict[str, Any]) -> bool:
        """ドキュメントを更新します
        
        Args:
            collection_name (str): コレクション名
            document_id (str): ドキュメントID
            update_data (Dict[str, Any]): 更新するデータ
            
        Returns:
            bool: 更新が成功したかどうか
        """
        try:
            # 更新タイムスタンプを追加
            update_data['updated_at'] = datetime.now()
            
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc_ref.update(update_data)
            return True
        except Exception as e:
            print(f"ドキュメントの更新に失敗しました: {e}")
            return False
    
    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """ドキュメントを削除します
        
        Args:
            collection_name (str): コレクション名
            document_id (str): ドキュメントID
            
        Returns:
            bool: 削除が成功したかどうか
        """
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"ドキュメントの削除に失敗しました: {e}")
            return False
    
    def get_all_documents(self, collection_name: str) -> List[Dict[str, Any]]:
        """コレクション内の全ドキュメントを取得します
        
        Args:
            collection_name (str): コレクション名
            
        Returns:
            List[Dict[str, Any]]: ドキュメントのリスト
        """
        docs = self.db.collection(collection_name).stream()
        documents = []
        
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id  # ドキュメントIDも含める
            documents.append(doc_data)
        
        return documents
    
    def query_documents(self, collection_name: str, field: str, operator: str, value: Any) -> List[Dict[str, Any]]:
        """条件に基づいてドキュメントをクエリします
        
        Args:
            collection_name (str): コレクション名
            field (str): フィールド名
            operator (str): 比較演算子 ('==', '!=', '<', '<=', '>', '>=', 'in', 'not-in', 'array-contains')
            value (Any): 比較する値
            
        Returns:
            List[Dict[str, Any]]: 条件に一致するドキュメントのリスト
        """
        query = self.db.collection(collection_name).where(field, operator, value)
        docs = query.stream()
        documents = []
        
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id
            documents.append(doc_data)
        
        return documents
    
    def batch_write(self, operations: List[Dict[str, Any]]) -> bool:
        """バッチ書き込みを実行します
        
        Args:
            operations (List[Dict[str, Any]]): 実行する操作のリスト
                例: [
                    {
                        'operation': 'set',
                        'collection': 'users',
                        'document_id': 'user1',
                        'data': {'name': '太郎', 'age': 30}
                    },
                    {
                        'operation': 'update',
                        'collection': 'users', 
                        'document_id': 'user2',
                        'data': {'age': 31}
                    }
                ]
                
        Returns:
            bool: バッチ書き込みが成功したかどうか
        """
        try:
            batch = self.db.batch()
            
            for op in operations:
                collection_name = op['collection']
                document_id = op['document_id']
                data = op['data']
                operation = op['operation']
                
                doc_ref = self.db.collection(collection_name).document(document_id)
                
                if operation == 'set':
                    data['created_at'] = datetime.now()
                    data['updated_at'] = datetime.now()
                    batch.set(doc_ref, data)
                elif operation == 'update':
                    data['updated_at'] = datetime.now()
                    batch.update(doc_ref, data)
                elif operation == 'delete':
                    batch.delete(doc_ref)
            
            # バッチを実行
            batch.commit()
            return True
        except Exception as e:
            print(f"バッチ書き込みに失敗しました: {e}")
            return False 