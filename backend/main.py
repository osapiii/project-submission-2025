from firebase_functions import firestore_fn
from firebase_functions.firestore_fn import Event, DocumentSnapshot
import requests
import logging
import sys
from functools import wraps
import google.auth
from google.auth.transport.requests import Request
import json

# Cloud Logging用の設定
def setup_logging():
    """Cloud Logging用のロガーを設定"""
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 既存のハンドラーをクリア
    root_logger.handlers.clear()
    
    # StreamHandlerを追加（Cloud Functionsでは標準出力がCloud Loggingに転送される）
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # フォーマッターを設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    root_logger.addHandler(handler)
    
    return root_logger

def get_cloud_run_auth_headers(target_url: str) -> dict:
    """Cloud Run認証用のヘッダーを取得"""
    try:
        from google.oauth2 import id_token
        from google.auth.transport.requests import Request
        
        # IDトークンを取得（Cloud Run認証用）
        auth_req = Request()
        id_token_value = id_token.fetch_id_token(auth_req, target_url)
        
        logger.info(f"🔐 IDトークンを正常に取得しました for URL: {target_url}")
        
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {id_token_value}"
        }
    except Exception as e:
        logger.error(f"❌ IDトークン取得エラー: {e}")
        # フォールバック: 従来のアクセストークンを使用
        logger.info("🔄 フォールバック: アクセストークンを使用します")
        credentials, project = google.auth.default()
        auth_req = Request()
        credentials.refresh(auth_req)
        
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {credentials.token}"
        }

# ロガーを初期化
logger = setup_logging()

# また、モジュールレベルのロガーも設定
module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.INFO)

def extract_event_info_from_firestore_event(event: Event[DocumentSnapshot | None]):
    """Extract necessary information from Firestore event"""
    try:
        if not event.data:
            return None
        
        doc_data = event.data.to_dict()
        doc_id = event.data.id
        collection_path = event.data.reference.parent.id
        
        return {
            "docData": doc_data,
            "docId": doc_id,
            "collectionFullPath": collection_path
        }
    except Exception as e:
        logger.error(f"Failed to extract event information: {e}")
        return None

def extract_organization_id_from_collection_name(path: str) -> str:
    """Extract organization ID from collection path"""
    try:
        parts = path.split("/")
        if len(parts) >= 2:
            return parts[1]
        return ""
    except Exception as e:
        logger.error(f"Failed to extract organization ID: {e}")
        return ""

def update_document(collectionName, documentId, data):
    """Update Firestore document"""
    try:
        # 🎯 Target locked! Writing to collection and document
        logger.info(f"🚀 FIRESTORE WRITE INCOMING! Collection: '{collectionName}' | Document: '{documentId}'")
        
        from firebase_admin import firestore
        db = firestore.client()
        doc_ref = db.collection(collectionName).document(documentId)
        doc_ref.update(data)
        logger.info(f"✅ Document updated successfully: {collectionName}/{documentId}")
    except Exception as e:
        logger.error(f"❌ Failed to update document: {e}")

def saveLog(logType: str, logMessage: str, isWriteToDoc: bool = False, docInfo: dict = None):
    """Save log with improved Cloud Logging support"""
    try:
        # Cloud Loggingに確実に出力するため、printも併用
        log_entry = f"[{logType.upper()}] {logMessage}"
        print(log_entry)  # Cloud Functionsでは print も Cloud Logging に転送される
        
        if logType == "info":
            logger.info(logMessage)
        elif logType == "error":
            logger.error(logMessage)
        elif logType == "warning":
            logger.warning(logMessage)
        elif logType == "debug":
            logger.debug(logMessage)
        
        if isWriteToDoc and docInfo:
            from firebase_admin import firestore
            update_document(
                collectionName=docInfo["collectionName"],
                documentId=docInfo["docId"],
                data={
                    f"logs": firestore.ArrayUnion([{
                        "type": logType,
                        "message": logMessage,
                        "timestamp": firestore.SERVER_TIMESTAMP
                    }])
                }
            )
    except Exception as e:
        print(f"[ERROR] Failed to save log: {e}")
        logger.error(f"Failed to save log: {e}")

@firestore_fn.on_document_created(
    document="organizations/{organizationId}/requests/convertPdfToPngAndCaptureRequests/logs/{requestId}",
    memory=1024,
    timeout_sec=300
)
def convert_pdf_to_png_and_capture_job(event: Event[DocumentSnapshot | None]) -> None:
    try:
        # Extract necessary information from event
        event_data = extract_event_info_from_firestore_event(event)
        if not event_data:
            logger.warning("No event data found, returning early")
            return
        doc_info = extract_event_info_from_firestore_event(event)
        fields = doc_info["docData"]
        request_id = doc_info["docId"]
        organization_id = fields["input"]["organizationId"]
        blueprint_id = fields["input"]["blueprintId"]
        
        # ログを強化して確実に出力
        print(f"[INFO] Processing PDF conversion request: {request_id}")
        logger.info(f"Fields: {fields}")
        logger.info(f"Request ID: {request_id}")
        logger.info(f"Organization ID: {organization_id}")
        logger.info(f"Blueprint ID: {blueprint_id}")
        
        # Convert PDF to PNG and save
        url = "https://convert-pdf-to-png-and-capture-208707381956.us-central1.run.app/convert-pdf-to-png"
        payload = {
            "bucket_name": "knockai-106a4.firebasestorage.app",
            "gcsInputPdfFilePath": f"organizations/{organization_id}/blueprints/{blueprint_id}/pdf/blueprint.pdf",
            "gcsOutputPreviewPngFilePath": f"organizations/{organization_id}/blueprints/{blueprint_id}/png/blueprint.png"
        }
        
        # Get authentication headers for Cloud Run
        headers = get_cloud_run_auth_headers(url)
        
        logger.info(f"Sending request to: {url}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        print(f"[INFO] Successfully converted PDF to PNG: {response.json()}")
        logger.info(f"Successfully converted PDF to PNG: {response.json()}")
        
        # Save Blueprint data to Firestore
        update_document(
            collectionName=f"organizations/{organization_id}/requests/convertPdfToPngAndCaptureRequests/logs",
            documentId=request_id,
            data={
                "status": "completed",
            }
        )
        print(f"[INFO] Process completed successfully for request: {request_id}")
    except Exception as e:
        error_msg = f"Failed to convert PDF to PNG and capture pages: {e}"
        print(f"[ERROR] {error_msg}")
        logger.error(error_msg)


@firestore_fn.on_document_created(
    document="organizations/{organizationId}/requests/startEstimateCreateProcessRequests/logs/{requestId}",
    memory=1024,
    timeout_sec=300
)
def start_estimate_create_process(event: Event[DocumentSnapshot | None]) -> None:
    try:
        # Extract necessary information from event
        event_data = extract_event_info_from_firestore_event(event)
        if not event_data:
            logger.warning("No event data found, returning early")
            return
        doc_info = extract_event_info_from_firestore_event(event)
        fields = doc_info["docData"]
        request_id = doc_info["docId"]
        organization_id = fields["input"]["organizationId"]
        session_id = fields["input"]["sessionId"]
        app_name = fields["input"]["appName"]
        user_id = fields["input"]["userId"]
        
        # ログを強化して確実に出力
        print(f"[INFO] Starting estimate create process: {session_id}")
        logger.info(f"Fields: {fields}")
        logger.info(f"Request ID: {request_id}")
        logger.info(f"Organization ID: {organization_id}")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"App Name: {app_name}")
        logger.info(f"User ID: {user_id}")
        
        # Create new session
        session_url = f"https://adk-default-service-name-208707381956.us-central1.run.app/apps/{app_name}/users/{user_id}/sessions/{session_id}"
        
        # Get authentication headers for Cloud Run
        headers = get_cloud_run_auth_headers(session_url)
        
        logger.info(f"Sending request to create session: {session_url}")
        
        # Send POST request to create new session
        response = requests.post(session_url, headers=headers)
        response.raise_for_status()
        
        print(f"[INFO] Successfully created new session: {response.text}")
        logger.info(f"Successfully created new session: {response.text}")
        
        # Update document status to completed
        update_document(
            collectionName=f"organizations/{organization_id}/requests/startEstimateCreateProcessRequests/logs",
            documentId=request_id,
            data={
                "status": "completed",
            }
        )
        
        success_msg = f"Estimate create process started successfully for session_id: {session_id}"
        print(f"[INFO] {success_msg}")
        logger.info(success_msg)
        
    except Exception as e:
        error_msg = f"Failed to start estimate create process: {e}"
        print(f"[ERROR] {error_msg}")
        logger.error(error_msg)
        
        # Update document status to failed
        try:
            update_document(
                collectionName=f"organizations/{organization_id}/requests/startEstimateCreateProcessRequests/logs",
                documentId=request_id,
                data={
                    "status": "failed"
                }
            )
        except Exception as update_error:
            update_error_msg = f"Failed to update document status to failed: {update_error}"
            print(f"[ERROR] {update_error_msg}")
            logger.error(update_error_msg)


@firestore_fn.on_document_created(
    document="organizations/{organizationId}/requests/sendQueryToGoogleAgentRequests/logs/{requestId}",
    memory=1024,
    timeout_sec=300
)
def send_query_to_google_agent(event: Event[DocumentSnapshot | None]) -> None:
    try:
        # 🎯 イベントから必要な情報を抽出
        event_data = extract_event_info_from_firestore_event(event)
        if not event_data:
            logger.warning("❌ イベントデータが見つかりませんでした、早期リターンします")
            return
        doc_info = extract_event_info_from_firestore_event(event)
        fields = doc_info["docData"]
        request_id = doc_info["docId"]
        organization_id = fields["input"]["organizationId"]
        session_id = fields["input"]["sessionId"]
        app_name = fields["input"]["appName"]
        user_id = fields["input"]["userId"]
        query = fields["input"]["query"]
        
        # 💾 エージェントレスポンスと共にドキュメントステータスを完了に更新
        collection_path = f"organizations/{organization_id}/requests/sendQueryToGoogleAgentRequests/logs"        
        
        # 📝 ログを強化して確実に出力
        logger.info(f"🤖 Google Agentにクエリを送信中: {query[:50]}...")
        logger.info(f"📋 Fields: {fields}")
        logger.info(f"🆔 Request ID: {request_id}")
        logger.info(f"🏢 Organization ID: {organization_id}")
        logger.info(f"💬 Session ID: {session_id}")
        logger.info(f"📱 App Name: {app_name}")
        logger.info(f"👤 User ID: {user_id}")
        logger.info(f"❓ Query: {query}")
        
        # 📦 Google Agent API用のペイロードを準備
        payload = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [{
                    "text": query
                }]
            }
        }
        
        # 🚀 Google Agentにクエリを送信
        agent_url = "https://adk-default-service-name-208707381956.us-central1.run.app/run_sse"
        
        # 🔐 認証ヘッダーを取得
        headers = get_cloud_run_auth_headers(agent_url)
        
        logger.info(f"🌐 Google Agentにクエリを送信中: {agent_url}")
        logger.info(f"📤 Payload: {payload}")
        
        # 📡 POSTリクエストをGoogle Agentに送信
        response = requests.post(agent_url, json=payload, headers=headers)
        response.raise_for_status()
        
        # 📊 レスポンスの詳細ログを強化
        logger.info(f"✅ Google Agent response status: {response.status_code}")
        logger.info(f"📋 Google Agent response headers: {dict(response.headers)}")
        logger.info(f"📄 Google Agent raw response text (length: {len(response.text)}): {repr(response.text)}")
        
        # 🔍 レスポンスを解析してエージェントの返答を抽出
        try:
            # 📝 複数の data: プレフィックス付きJSON文字列を処理
            response_text = response.text.strip()            
            logger.info(f"🔍 レスポンステキストを処理中: {repr(response_text)}")
            
            # 🧹 複数の "data: " 行を分割して処理
            data_lines = []
            for line in response_text.split('\n'):
                line = line.strip()
                if line.startswith("data: "):
                    json_str = line[6:]  # "data: "プレフィックスを削除
                    data_lines.append(json_str)
                    logger.info(f"🧹 data行を発見、JSON文字列: {repr(json_str)}")
            
            # 📊 見つかったdata行の数をログ出力
            logger.info(f"📊 見つかったdata行の数: {len(data_lines)}")
            
            # 🔄 data行が見つからない場合は元のテキストを使用
            if not data_lines:
                logger.info(f"ℹ️ data行が見つかりません、元のテキストを単一JSONとして処理")
                data_lines = [response_text]
            
            # 📝 全てのdata行からpartsを抽出
            all_agent_parts = []
            
            for i, json_str in enumerate(data_lines):
                try:
                    logger.info(f"🔧 data行 {i+1}/{len(data_lines)} のJSONを解析中: {repr(json_str)}")
                    response_data = json.loads(json_str)
                    logger.info(f"✅ data行 {i+1} のJSONレスポンス解析に成功: {response_data}")
                    
                    # 📝 content.partsからテキストを抽出
                    if "content" in response_data:
                        logger.info(f"✅ data行 {i+1} で'content'キーを発見")
                        
                        if "parts" in response_data["content"]:
                            logger.info(f"✅ data行 {i+1} のcontent内で'parts'を発見: {response_data['content']['parts']}")
                            
                            # 🔄 各パートを all_agent_parts に追加
                            for j, part in enumerate(response_data["content"]["parts"]):
                                logger.info(f"🔍 data行 {i+1} のパート {j} を処理中: {part}")
                                all_agent_parts.append(part)
                                logger.info(f"✅ data行 {i+1} のパート {j} を追加")
                        else:
                            logger.warning(f"⚠️ data行 {i+1} のcontent内で'parts'キーが見つかりません")
                    else:
                        logger.warning(f"⚠️ data行 {i+1} で'content'キーが見つかりません")
                        
                except json.JSONDecodeError as json_error:
                    logger.error(f"❌ data行 {i+1} のJSON decode error: {json_error}")
                    logger.error(f"❌ data行 {i+1} をJSONとして解析できませんでした: {repr(json_str)}")
                    # 🔄 JSONパースに失敗した場合はテキストとして追加
                    all_agent_parts.append({"text": json_str})
                except Exception as parse_error:
                    logger.error(f"❌ data行 {i+1} の解析エラー: {parse_error}")
                    all_agent_parts.append({"text": json_str})
            
            # 🔄 パーツが見つからない場合はフォールバック
            if not all_agent_parts:
                logger.warning(f"⚠️ エージェントパーツが抽出されませんでした、フォールバックを使用")
                all_agent_parts = [{"text": "No response content found"}]
            
            # 📊 最終的なagent_partsのログ出力
            logger.info(f"🎯 最終的に抽出されたエージェントパーツ数: {len(all_agent_parts)}")
            logger.info(f"🎯 最終的に抽出されたエージェントパーツ: {all_agent_parts}")
            
            agent_parts = all_agent_parts
            
            update_document(
                collectionName=collection_path,
                documentId=request_id,
                data={
                    "status": "completed",
                    "output": {
                        "parts": agent_parts
                    }
                }
            )
            
        except json.JSONDecodeError as json_error:
            logger.error(f"❌ JSON decode error: {json_error}")
            logger.error(f"❌ レスポンスをJSONとして解析できませんでした。生レスポンス: {repr(response.text)}")
            
            # 🔄 JSONパースに失敗した場合、レスポンステキストをそのまま使用
            collection_path = f"organizations/{organization_id}/requests/sendQueryToGoogleAgentRequests/logs"
            update_document(
                collectionName=collection_path,
                documentId=request_id,
                data={
                    "status": "completed",
                    "output": {
                        "parts": [{"text": response.text}],
                        "rawResponse": response.text
                    }
                }
            )
        except Exception as parse_error:
            logger.error(f"Parse error: {parse_error}")
            logger.error(f"Failed to parse response, treating as plain text. Raw response: {repr(response.text)}")
            
            # Fallback: treat response as plain text
            collection_path = f"organizations/{organization_id}/requests/sendQueryToGoogleAgentRequests/logs"
            update_document(
                collectionName=collection_path,
                documentId=request_id,
                data={
                    "status": "completed",
                    "output": {
                        "parts": [{"text": response.text}]
                    }
                }
            )
        
        success_msg = f"Query sent successfully to Google Agent for session: {session_id}"
        logger.info(success_msg)
        
    except Exception as e:
        error_msg = f"Failed to send query to Google Agent: {e}"
        logger.error(error_msg)
        
        # Update document status to failed
        try:
            # Extract organization_id safely for error handling
            organization_id = ""
            if event and event.data:
                doc_data = event.data.to_dict()
                if doc_data and "input" in doc_data and "organizationId" in doc_data["input"]:
                    organization_id = doc_data["input"]["organizationId"]
            
            collection_path = f"organizations/{organization_id}/requests/sendQueryToGoogleAgentRequests/logs" if organization_id else f"requests/sendQueryToGoogleAgentRequests/logs"
            update_document(
                collectionName=collection_path,
                documentId=request_id,
                data={
                    "status": "failed"
                }
            )
        except Exception as update_error:
            update_error_msg = f"Failed to update document status to failed: {update_error}"
            logger.error(update_error_msg)