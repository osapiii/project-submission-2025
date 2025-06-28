import datetime
import os
import sys
from datetime import datetime
from typing import Dict, Any
import requests
import json

from zoneinfo import ZoneInfo
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from google.oauth2 import service_account
from dotenv import load_dotenv
# スクリプトのディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 環境変数を読み込む
load_dotenv()

# 通常の絶対インポート
from firestore_helper import FirestoreHelper
from gcs_helper import GCSHelper
from step1_pdf_download_test import execute_pdf_download_test
from step2_download_target_pdf_assets import (
    get_analysis_json_from_step1_output,
    create_simple_analysis_description,
    save_step2_output_to_firestore
)
from step3_product_identification_agent import (
    getAnalysisJson,
    createProductionList,
    saveProductionListToFirestore
)
from step4_parts_breakdown_agent import (
    getStep3Output,
    createPartsBreakdown,
    savePartsBreakdownToFirestore
)

# 認証情報の初期化（環境変数から取得）
def get_credentials_from_env():
    """環境変数SERVICE_ACCOUNT_KEYからGoogle認証情報を取得します"""
    try:
        service_account_key = os.environ.get('SERVICE_ACCOUNT_KEY')
        if not service_account_key:
            raise ValueError("SERVICE_ACCOUNT_KEY環境変数が設定されていません。環境変数を設定してください。")
        
        # JSON文字列をパース
        service_account_info = json.loads(service_account_key)
        
        # Firebase Admin SDKに必要なスコープを指定
        scopes = [
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/firebase.database',
            'https://www.googleapis.com/auth/firebase.messaging',
            'https://www.googleapis.com/auth/userinfo.email'
        ]
        
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, 
            scopes=scopes
        )
        project = service_account_info.get('project_id')
        
        print("✅ SERVICE_ACCOUNT_KEY環境変数から認証情報を読み込みました")
        return credentials, project
        
    except json.JSONDecodeError as e:
        raise ValueError(f"SERVICE_ACCOUNT_KEY のJSONパースエラー: {e}")
    except Exception as e:
        raise ValueError(f"認証情報取得エラー: {e}")

# Vertex AI/Google認証の初期化
credentials, project = get_credentials_from_env()

def get_firestore_helper():
    """統一されたFirestoreHelperインスタンスを取得します（環境変数ベース）"""
    # FirestoreHelperにデフォルトパスを渡すが、実際は環境変数から認証情報を取得
    return FirestoreHelper()

def update_current_step(step: int, document_id: str = "ABCD", collection_name: str = "agent_job") -> dict:
    """指定されたステップ番号でドキュメントのcurrentStepフィールドを更新します。

    Args:
        step (int): 更新するステップ番号
        document_id (str): FirestoreのドキュメントID
        collection_name (str): Firestoreのコレクション名

    Returns:
        dict: 更新の結果
    """
    try:
        print(f"🔍 DEBUG: update_current_step called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        print(f"   🔢 Step: {step}")
        
        # Firestoreヘルパーを初期化
        firestore_helper = get_firestore_helper()
        
        # 更新するデータを準備
        update_data = {
            'currentStep': step,
            'updatedAt': datetime.now()
        }
        
        print(f"📋 STEP 1: 更新データを準備中...")
        print(f"   📊 Update data: {update_data}")
        
        # ドキュメントを更新
        print(f"📋 STEP 2: Firestoreに更新中...")
        success = firestore_helper.update_document(
            collection_name=collection_name,
            document_id=document_id,
            update_data=update_data
        )
        
        print(f"   📊 Update result: {success}")
        
        if success:
            print(f"   ✅ Current step updated successfully")
            return {
                "status": "success",
                "message": f"ステップ {step} に更新しました"
            }
        else:
            print(f"   ❌ Document update failed")
            return {
                "status": "error",
                "error_message": "ドキュメントの更新に失敗しました"
            }
            
    except Exception as e:
        print(f"❌ ERROR in update_current_step: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"ステップ更新中にエラーが発生しました: {str(e)}"
        }

def get_current_step(document_id: str = "adk", collection_name: str = "agent_job") -> dict:
    """指定されたドキュメントのcurrentStepフィールドを取得します。

    Args:
        document_id (str): FirestoreのドキュメントID
        collection_name (str): Firestoreのコレクション名

    Returns:
        dict: 取得結果
    """
    try:
        print(f"🔍 DEBUG: get_current_step called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        
        # Firestoreヘルパーを初期化
        firestore_helper = get_firestore_helper()
        
        # ドキュメントを取得
        doc = firestore_helper.get_document(
            collection_name=collection_name,
            document_id=document_id
        )
        
        print(f"🔍 DEBUG: Firestore取得結果")
        print(f"   📄 Document exists: {doc is not None}")
        
        if doc and 'currentStep' in doc:
            current_step = doc['currentStep']
            print(f"   ✅ Current step found: {current_step}")
            return {
                "status": "success",
                "current_step": current_step,
                "message": f"現在のステップは {current_step} です"
            }
        else:
            print(f"   ❌ Document or currentStep field not found")
            if doc:
                print(f"   🔍 Available fields: {list(doc.keys()) if isinstance(doc, dict) else 'Not a dict'}")
            return {
                "status": "error",
                "error_message": f"ドキュメントが見つからないか、currentStepフィールドが存在しません。利用可能なフィールド: {list(doc.keys()) if doc and isinstance(doc, dict) else 'Not a dict'}"
            }
            
    except Exception as e:
        print(f"❌ ERROR in get_current_step: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"ステップ取得中にエラーが発生しました: {str(e)}"
        }
        
def get_selected_step_output(document_id: str = "adk", stepIndex: int = 1, collection_name: str = "agent_job") -> dict:
    """指定されたステップ番号のOutputを取得します。各ステップを開始する前に1つ前のステップのOutputを取得してください。"""
    try:
        print(f"🔍 DEBUG: get_selected_step_output called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        print(f"   🔢 Step Index: {stepIndex}")
        
        # Firestoreヘルパーを初期化
        firestore_helper = get_firestore_helper()
        
        # ドキュメントを取得
        doc = firestore_helper.get_document(
            collection_name=collection_name,
            document_id=document_id
        )
        
        print(f"🔍 DEBUG: Firestore取得結果")
        print(f"   📄 Document exists: {doc is not None}")
        
        field_name = f"step{stepIndex}_output"
        print(f"   🔍 Looking for field: {field_name}")
        
        if doc and field_name in doc:
            step_output = doc[field_name]
            print(f"   ✅ Step output found")
            print(f"   📋 Step output keys: {list(step_output.keys()) if isinstance(step_output, dict) else 'Not a dict'}")
            return {
                "status": "success",
                "step_output": step_output
            }
        else:
            print(f"   ❌ Document or step output field not found")
            if doc:
                print(f"   🔍 Available fields: {list(doc.keys()) if isinstance(doc, dict) else 'Not a dict'}")
            return {
                "status": "error",
                "error_message": f"ドキュメントが見つからないか、{field_name}フィールドが存在しません。利用可能なフィールド: {list(doc.keys()) if doc and isinstance(doc, dict) else 'Not a dict'}"
            }
    except Exception as e:
        print(f"❌ ERROR in get_selected_step_output: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"ステップ{stepIndex}のOutput取得中にエラーが発生しました: {str(e)}"
        }

def execute_step_1(document_id: str = "adk",collection_name: str = "agent_job") -> dict:
    """Step1の実行 - 図面情報取得（PDFダウンロード + analysisJSON解析を統合）"""
    try:
        print(f"🎯 DEBUG: execute_step_1 started")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        print(f"   ⏰ Timestamp: {datetime.now().isoformat()}")
        
        # 🔄 Step1開始時にcurrentStepを1に更新
        print(f"📋 STEP 0: currentStepを1に更新中...")
        step_update_result = update_current_step(1, document_id, collection_name)
        if step_update_result.get("status") != "success":
            print(f"   ⚠️ Step update warning: {step_update_result.get('error_message', 'Unknown error')}")
            # ステップ更新失敗は警告扱いとし、処理は継続
        else:
            print(f"   ✅ Current step updated to 1")
        
        # Step1のPDFダウンロードテストを実行
        print(f"📋 STEP 1-1: PDFダウンロードテストを実行中...")
        pdf_result = execute_pdf_download_test(document_id,collection_name)
        
        print(f"📊 PDF download result status: {pdf_result.get('status', 'unknown')}")
        if pdf_result.get('status') != 'success':
            print(f"   ❌ PDF download failed: {pdf_result.get('error_message', 'Unknown error')}")
            return pdf_result
        
        print(f"   ✅ PDF download completed successfully")
        
        # Step1の出力からanalysisJSONを取得・解析
        print(f"📋 STEP 1-2: AnalysisJSONを解析中...")
        json_result = get_analysis_json_from_step1_output(document_id, collection_name)
        print(f"   📊 JSON result status: {json_result.get('status', 'unknown')}")
        
        if json_result["status"] != "success":
            print(f"   ❌ JSON retrieval failed: {json_result.get('error_message', 'Unknown error')}")
            return json_result
        
        analysis_data = json_result["analysis_data"]
        print(f"   ✅ Analysis JSON retrieved successfully")
        print(f"   📊 Analysis data keys: {list(analysis_data.keys()) if isinstance(analysis_data, dict) else 'Not a dict'}")
        
        # 出力フォーマット
        print(f"📋 STEP 1-3: 出力フォーマット中...")
        format_result = create_simple_analysis_description(analysis_data)
        print(f"   📊 Format result status: {format_result.get('status', 'unknown')}")
        
        if format_result["status"] != "success":
            print(f"   ❌ Formatting failed: {format_result.get('error_message', 'Unknown error')}")
            return format_result
        
        print(f"   ✅ Output formatted successfully")
        
        # 統合結果をFirestoreに保存
        print(f"📋 STEP 1-4: 統合結果をFirestoreに保存中...")
        save_result = save_step2_output_to_firestore(
            analysis_data=analysis_data,
            description=format_result["description"],
            document_id=document_id,
            collection_name=collection_name
        )
        print(f"   📊 Save result status: {save_result.get('status', 'unknown')}")
        
        if save_result["status"] != "success":
            print(f"   ❌ Save failed: {save_result.get('error_message', 'Unknown error')}")
            return save_result
        
        print(f"   ✅ Step1 completed successfully")
        
        return {
            "status": "success",
            "message": f"Step1: 図面情報取得が完了しました\n\n{format_result['description']}",
            "description": format_result["description"],
            "production_info": format_result.get("production_info", []),
            "download_url": pdf_result.get("download_url", ""),
            "pdf_info": pdf_result.get("pdf_info", {}),
            "analysis_data": analysis_data,
            "next_step": "Step2: 制作物特定に進む準備が整いました"
        }
        
    except Exception as e:
        print(f"❌ ERROR in execute_step_1: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"Step1実行中にエラーが発生しました: {str(e)}"
        }
              

def execute_step_2(document_id: str = "ABCD", collection_name: str = "agent_job", user_instructions: str = "") -> dict:
    """ステップ2の実行 - 制作物特定（旧Step3相当）"""
    try:
        print(f"🎯 DEBUG: execute_step_2 started")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        print(f"   📝 User instructions: {user_instructions}")
        print(f"   ⏰ Timestamp: {datetime.now().isoformat()}")
        
        # 🔄 Step2開始時にcurrentStepを2に更新
        print(f"📋 STEP 0: currentStepを2に更新中...")
        step_update_result = update_current_step(2, document_id, collection_name)
        if step_update_result.get("status") != "success":
            print(f"   ⚠️ Step update warning: {step_update_result.get('error_message', 'Unknown error')}")
            # ステップ更新失敗は警告扱いとし、処理は継続
        else:
            print(f"   ✅ Current step updated to 2")
        
        # Firestoreヘルパーを初期化
        firestore_helper = get_firestore_helper()
        
        # 1. Step1のanalysis.json結果を取得
        print(f"📋 STEP 1: Step1のanalysis.json結果を取得中...")
        analysis_result = getAnalysisJson(document_id, collection_name)
        print(f"   📊 Analysis result status: {analysis_result.get('status', 'unknown')}")
        
        if analysis_result["status"] != "success":
            print(f"   ❌ Analysis retrieval failed: {analysis_result.get('error_message', 'Unknown error')}")
            return analysis_result
        
        analysis_json = analysis_result["analysis_json"]
        print(f"   ✅ Analysis JSON retrieved successfully")
        
        # 2. Step1のdownload_url結果を取得
        print(f"📋 STEP 2: Step1のdownload_url結果を取得中...")
        doc = firestore_helper.get_document(
            collection_name=collection_name,
            document_id=document_id
        )
        
        if not doc or 'tmpPdfBlueprintDlUrl' not in doc:
            print(f"   ❌ Download URL not found")
            return {
                "status": "error",
                "error_message": "Step1のダウンロードURLが見つかりません。Step1を先に実行してください。"
            }
        
        download_url = doc['tmpPdfBlueprintDlUrl']
        print(f"   ✅ Download URL retrieved: {download_url}")
        
        # 3. LLMを使用して製品リストを生成
        print(f"📋 STEP 3: LLMを使用して製品リストを生成中...")
        production_result = createProductionList(analysis_json, download_url, user_instructions)
        print(f"   📊 Production result status: {production_result.get('status', 'unknown')}")
        
        if production_result["status"] != "success":
            print(f"   ❌ Production list generation failed: {production_result.get('error_message', 'Unknown error')}")
            return production_result
        
        # 4. production_listを抽出（重要：辞書からリストを取り出す）
        production_list = production_result["production_list"]
        print(f"   ✅ Production list generated with {len(production_list)} items")
        
        # 5. Firestoreに保存（step2_outputとして保存）
        print(f"📋 STEP 4: Firestoreにstep2_outputとして保存中...")
        save_result = saveProductionListToFirestore(production_list, document_id, collection_name, step_number=2)
        print(f"   📊 Save result status: {save_result.get('status', 'unknown')}")
        
        if save_result["status"] != "success":
            print(f"   ❌ Save failed: {save_result.get('error_message', 'Unknown error')}")
            return save_result
        
        print(f"   ✅ Step2 completed successfully")
        
        return {
            "status": "success",
            "message": f"Step2: 制作物特定が完了しました\n\n{save_result['description']}",
            "production_list": production_list,
            "formatted_table": save_result["formatted_table"],
            "summary": {
                "total_product_types": production_result["total_items"],
                "total_quantity": production_result["total_quantity"],
                "extraction_method": production_result["extraction_source"]
            },
            "gemini_response": production_result.get("gemini_response", ""),
            "next_step": "Step3: 部材/数量/単価特定に進む準備が整いました"
        }
        
    except Exception as e:
        print(f"❌ ERROR in execute_step_2: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"ステップ2実行中にエラーが発生しました: {str(e)}"
        }

def execute_step_3(document_id: str = "ABCD", collection_name: str = "agent_job", user_instructions: str = "") -> dict:
    """ステップ3の実行 - 部材/数量/単価特定（旧Step4相当）"""
    try:
        print(f"🎯 DEBUG: execute_step_3 started")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        print(f"   📝 User instructions: {user_instructions}")
        print(f"   ⏰ Timestamp: {datetime.now().isoformat()}")
        
        # 🔄 Step3開始時にcurrentStepを3に更新
        print(f"📋 STEP 0: currentStepを3に更新中...")
        step_update_result = update_current_step(3, document_id, collection_name)
        if step_update_result.get("status") != "success":
            print(f"   ⚠️ Step update warning: {step_update_result.get('error_message', 'Unknown error')}")
            # ステップ更新失敗は警告扱いとし、処理は継続
        else:
            print(f"   ✅ Current step updated to 3")
        
        # Firestoreヘルパーを初期化
        firestore_helper = get_firestore_helper()
        
        # 1. Step2の製品リスト結果を取得
        print(f"📋 STEP 1: Step2の製品リスト結果を取得中...")
        step2_result = getStep2Output(document_id, collection_name)
        print(f"   📊 Step2 result status: {step2_result.get('status', 'unknown')}")
        
        if step2_result["status"] != "success":
            print(f"   ❌ Step2 retrieval failed: {step2_result.get('error_message', 'Unknown error')}")
            return step2_result
        
        production_list = step2_result["production_list"]
        print(f"   ✅ Production list retrieved with {len(production_list)} items")
        
        # 2. Step1のanalysis.json結果を取得
        print(f"📋 STEP 2: Step1のanalysis.json結果を取得中...")
        analysis_result = getAnalysisJson(document_id, collection_name)
        print(f"   📊 Analysis result status: {analysis_result.get('status', 'unknown')}")
        
        if analysis_result["status"] != "success":
            print(f"   ❌ Analysis retrieval failed: {analysis_result.get('error_message', 'Unknown error')}")
            return analysis_result
        
        analysis_json = analysis_result["analysis_json"]
        print(f"   ✅ Analysis JSON retrieved successfully")
        
        # 3. Step1のdownload_url結果を取得
        print(f"📋 STEP 3: Step1のdownload_url結果を取得中...")
        doc = firestore_helper.get_document(
            collection_name=collection_name,
            document_id=document_id
        )
        
        if not doc or 'tmpPdfBlueprintDlUrl' not in doc:
            print(f"   ❌ Download URL not found")
            return {
                "status": "error",
                "error_message": "Step1のダウンロードURLが見つかりません。Step1を先に実行してください。"
            }
        
        download_url = doc['tmpPdfBlueprintDlUrl']
        
        print(f"   ✅ Download URL retrieved: {download_url}")
        
        # 4. LLMを使用して部品一覧を分解
        print(f"📋 STEP 4: LLMを使用して部品一覧を分解中...")
        parts_result = createPartsBreakdown(production_list, analysis_json, download_url, user_instructions)
        print(f"   📊 Parts result status: {parts_result.get('status', 'unknown')}")
        
        if parts_result["status"] != "success":
            print(f"   ❌ Parts breakdown failed: {parts_result.get('error_message', 'Unknown error')}")
            return parts_result
        
        # 5. parts_breakdownを抽出
        parts_breakdown = parts_result["parts_breakdown"]
        print(f"   ✅ Parts breakdown generated with {len(parts_breakdown)} products")
        
        # 6. Firestoreに保存（step3_outputとして保存）
        print(f"📋 STEP 5: Firestoreにstep3_outputとして保存中...")
        save_result = savePartsBreakdownToFirestore(parts_breakdown, document_id, collection_name, step_number=3)
        print(f"   📊 Save result status: {save_result.get('status', 'unknown')}")
        
        if save_result["status"] != "success":
            print(f"   ❌ Save failed: {save_result.get('error_message', 'Unknown error')}")
            return save_result
        
        print(f"   ✅ Step3 completed successfully")
        
        return {
            "status": "success",
            "message": f"Step3: 部材/数量/単価特定が完了しました\n\n{save_result['description']}",
            "parts_breakdown": parts_breakdown,
            "formatted_table": save_result["formatted_table"],
            "summary": {
                "total_products": parts_result["total_products"],
                "total_parts_types": parts_result["total_parts_types"],
                "total_parts_quantity": parts_result["total_parts_quantity"],
                "total_estimated_cost": parts_result.get("total_estimated_cost", 0),
                "extraction_method": parts_result["extraction_source"]
            },
            "gemini_response": parts_result.get("gemini_response", ""),
            "next_step": "Step4: 見積書作成（最終ステップ）に進む準備が整いました"
        }
        
    except Exception as e:
        print(f"❌ ERROR in execute_step_3: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"ステップ3実行中にエラーが発生しました: {str(e)}"
        }

def execute_step_4(document_id: str = "ABCD", collection_name: str = "agent_job", user_instructions: str = "",organization_id: str = "") -> dict:
    """ステップ4の実行 - 外部API経由での見積書・明細書生成（最終ステップ）"""
    try:
        print(f"🎯 DEBUG: execute_step_4 started")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        print(f"   📝 User instructions: {user_instructions}")
        print(f"   ⏰ Timestamp: {datetime.now().isoformat()}")
        
        # 🔄 Step4開始時にcurrentStepを4に更新
        print(f"📋 STEP 0: currentStepを4に更新中...")
        step_update_result = update_current_step(4, document_id, collection_name)
        if step_update_result.get("status") != "success":
            print(f"   ⚠️ Step update warning: {step_update_result.get('error_message', 'Unknown error')}")
            # ステップ更新失敗は警告扱いとし、処理は継続
        else:
            print(f"   ✅ Current step updated to 4")
        
        # Firestoreヘルパーを初期化
        firestore_helper = get_firestore_helper()
        
        # 1. Step3の部品一覧結果を取得
        print(f"📋 STEP 1: Step3の部品一覧結果を取得中...")
        print(f"   🔍 DEBUG: Calling getStep3Output with document_id='{document_id}', collection_name='{collection_name}'")
        
        step3_result = getStep3Output(document_id, collection_name)
        
        print(f"   📊 Step3 result status: {step3_result.get('status', 'unknown')}")
        print(f"   🔍 DEBUG: Step3 result type: {type(step3_result)}")
        print(f"   🔍 DEBUG: Step3 result keys: {list(step3_result.keys()) if isinstance(step3_result, dict) else 'Not a dict'}")
        
        if step3_result.get("status") != "success":
            print(f"   ❌ Step3 retrieval failed: {step3_result.get('error_message', 'Unknown error')}")
            print(f"   🔍 DEBUG: Full step3_result: {step3_result}")
            return step3_result
        
        # step3_outputから直接parts_breakdownを取得
        print(f"   🔍 DEBUG: Extracting parts_breakdown from step3_output...")
        step3_output = step3_result.get("step3_output", {})
        print(f"   📋 Step3 output keys: {list(step3_output.keys()) if isinstance(step3_output, dict) else 'Not a dict'}")
        
        if "parts_breakdown" not in step3_output:
            print(f"   ❌ ERROR: 'parts_breakdown' key not found in step3_output")
            print(f"   🔍 DEBUG: Available keys in step3_output: {list(step3_output.keys()) if isinstance(step3_output, dict) else 'Not a dict'}")
            print(f"   🔍 DEBUG: Full step3_output content: {step3_output}")
            return {
                "status": "error",
                "error_message": f"Step3の結果(step3_output)に'parts_breakdown'キーが見つかりません。利用可能なキー: {list(step3_output.keys()) if isinstance(step3_output, dict) else 'Not a dict'}"
            }
        
        parts_breakdown = step3_output["parts_breakdown"]
        print(f"   ✅ Parts breakdown retrieved successfully")
        print(f"   📊 Parts breakdown type: {type(parts_breakdown)}")
        print(f"   📊 Parts breakdown length: {len(parts_breakdown) if isinstance(parts_breakdown, (list, dict)) else 'Not list/dict'}")
        
        if isinstance(parts_breakdown, list):
            print(f"   🔍 DEBUG: First few items in parts_breakdown: {parts_breakdown[:2] if len(parts_breakdown) > 0 else 'Empty list'}")
        elif isinstance(parts_breakdown, dict):
            print(f"   🔍 DEBUG: Parts breakdown dict keys: {list(parts_breakdown.keys())}")
        else:
            print(f"   ⚠️ WARNING: Parts breakdown is not a list or dict: {parts_breakdown}")
        
        # 2. 外部API用のリクエストボディを生成
        print(f"📋 STEP 2: 外部API用のリクエストボディを生成中...")
        print(f"   🔍 DEBUG: Calling generate_api_request_body with parts_breakdown type: {type(parts_breakdown)}")
        
        api_request_body = generate_api_request_body(parts_breakdown, document_id, user_instructions,organization_id)
        
        print(f"   📊 API request body generated")
        print(f"   🔍 DEBUG: API request body type: {type(api_request_body)}")
        print(f"   🔍 DEBUG: API request body keys: {list(api_request_body.keys()) if isinstance(api_request_body, dict) else 'Not a dict'}")
        
        # エラーチェック
        if isinstance(api_request_body, dict) and "error" in api_request_body:
            print(f"   ❌ API request body generation failed: {api_request_body['error']}")
            return {
                "status": "error",
                "error_message": f"APIリクエストボディ生成エラー: {api_request_body['error']}"
            }
        
        # 3. 外部APIに見積書生成リクエストを送信
        print(f"📋 STEP 3: 外部APIに見積書生成リクエストを送信中...")
        print(f"   🔍 DEBUG: API request body estimateData: {api_request_body.get('estimateData', 'Missing')}")
        
        api_result = call_estimate_generation_api(api_request_body)
        
        print(f"   📊 API result status: {api_result.get('status', 'unknown')}")
        print(f"   🔍 DEBUG: API result type: {type(api_result)}")
        print(f"   🔍 DEBUG: API result keys: {list(api_result.keys()) if isinstance(api_result, dict) else 'Not a dict'}")
        
        if api_result.get("status") != "success":
            print(f"   ❌ API call failed: {api_result.get('error_message', 'Unknown error')}")
            print(f"   🔍 DEBUG: Full API result: {api_result}")
            return api_result
        
        print(f"   ✅ 見積書・明細書がGCSに正常に生成されました")
        
        # 4. step4_outputにAPIリクエストボディを保存
        print(f"📋 STEP 4: step4_outputにAPIリクエストボディを保存中...")
        print(f"   🔍 DEBUG: Calling save_step4_output_to_firestore")
        
        save_result = save_step4_output_to_firestore(api_request_body, api_result, document_id, collection_name)
        
        print(f"   📊 Save result status: {save_result.get('status', 'unknown')}")
        print(f"   🔍 DEBUG: Save result: {save_result}")
        
        if save_result.get("status") != "success":
            print(f"   ❌ Save failed: {save_result.get('error_message', 'Unknown error')}")
            return save_result
        
        print(f"   ✅ Step4 completed successfully")
        
        # 5. currentStepを5に更新（全プロセス完了）
        print(f"📋 STEP 5: currentStepを5に更新中（全プロセス完了）...")
        print(f"   🔍 DEBUG: Calling update_current_step(5, '{document_id}', '{collection_name}')")
        
        final_step_update_result = update_current_step(5, document_id, collection_name)
        
        print(f"   📊 Final step update result: {final_step_update_result.get('status', 'unknown')}")
        print(f"   🔍 DEBUG: Final step update result: {final_step_update_result}")
        
        if final_step_update_result.get("status") != "success":
            print(f"   ⚠️ Final step update warning: {final_step_update_result.get('error_message', 'Unknown error')}")
            # ステップ更新失敗は警告扱いとし、処理は継続
        else:
            print(f"   ✅ Current step successfully updated to 5 (process completed)")
        
        # 6. allProcessCompletedをtrueに更新
        print(f"📋 STEP 6: allProcessCompletedをtrueに更新中...")
        print(f"   🔍 DEBUG: Calling update_all_process_completed(True, '{document_id}', '{collection_name}')")
        
        update_result = firestore_helper.update_document(
            collection_name,
            document_id,
            {
                "allProcessCompleted": True
            }
        )
        
        
        return {
            "status": "success",
            "message": f"Step4: 見積書・明細書作成が完了しました\n\n{save_result['description']}",
            "api_request_body": api_request_body,
            "api_response": api_result.get("response_data", {}),
            "gcs_urls": api_result.get("file_urls", []),
            "current_step": 5,
            "next_step": "全ステップが完了しました！"
        }
        
    except Exception as e:
        print(f"❌ ERROR in execute_step_4: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"ステップ4実行中にエラーが発生しました: {str(e)}"
        }

def generate_api_request_body(parts_breakdown: list, document_id: str, user_instructions: str = "",organization_id: str = "") -> dict:
    """Step3の結果からtestRequestフォーマットのAPIリクエストボディを生成します。

    Args:
        parts_breakdown (list): Step3で生成された部品一覧
        document_id (str): ドキュメントID（フォルダパスに使用）
        user_instructions (str): ユーザーからの追加指示

    Returns:
        dict: APIリクエスト用のボディ
    """
    try:
        print(f"🔍 DEBUG: generate_api_request_body called")
        print(f"   📊 Parts breakdown type: {type(parts_breakdown)}")
        print(f"   📊 Parts breakdown length: {len(parts_breakdown) if isinstance(parts_breakdown, (list, dict)) else 'Not list/dict'}")
        print(f"   🆔 Document ID: {document_id}")
        print(f"   📝 User instructions: {user_instructions}")
        print(f"   🆔 Organization ID: {organization_id}")
        
        # 入力データの型チェック
        if not isinstance(parts_breakdown, list):
            error_msg = f"parts_breakdownはリストである必要があります。実際の型: {type(parts_breakdown)}"
            print(f"   ❌ ERROR: {error_msg}")
            print(f"   🔍 DEBUG: parts_breakdown content: {parts_breakdown}")
            return {
                "error": error_msg
            }
        
        if len(parts_breakdown) == 0:
            error_msg = "parts_breakdownが空のリストです"
            print(f"   ❌ ERROR: {error_msg}")
            return {
                "error": error_msg
            }
        
        print(f"   🔍 DEBUG: First item in parts_breakdown: {parts_breakdown[0] if len(parts_breakdown) > 0 else 'None'}")
        
        # 製品リストとestimateDataを生成
        products = []
        total_price = 0
        
        for i, product in enumerate(parts_breakdown):
            print(f"   🔍 DEBUG: Processing product {i}: type={type(product)}")
            if not isinstance(product, dict):
                print(f"   ⚠️ WARNING: Product {i} is not a dict, skipping: {product}")
                continue
                
            product_name = product.get("product_name", "不明製品")
            product_quantity = product.get("product_quantity", 1)
            
            print(f"     🔍 DEBUG: Product {i} - name: '{product_name}', quantity: {product_quantity}")
            print(f"     🔍 DEBUG: Product {i} keys: {list(product.keys())}")
            
            # 製品単価を計算（全部品の合計価格）
            product_total_price = 0
            parts_list = product.get("parts", [])
            print(f"     🔍 DEBUG: Product {i} - parts count: {len(parts_list) if isinstance(parts_list, list) else 'Not a list'}")
            
            if isinstance(parts_list, list):
                for j, part in enumerate(parts_list):
                    if isinstance(part, dict):
                        part_total_price = part.get("total_price", 0)
                        product_total_price += part_total_price
                        print(f"       🔍 DEBUG: Part {j} - total_price: {part_total_price}")
                    else:
                        print(f"       ⚠️ WARNING: Part {j} is not a dict: {part}")
            else:
                print(f"     ⚠️ WARNING: Product {i} 'parts' is not a list: {parts_list}")
            
            # 製品単価（1個あたり）
            product_unit_price = product_total_price // product_quantity if product_quantity > 0 else 0
            
            print(f"     📊 Product {i} - total_price: {product_total_price}, unit_price: {product_unit_price}")
            
            products.append({
                "productName": product_name,
                "quantity": product_quantity,
                "price": product_unit_price
            })
            
            total_price += product_total_price
        
        # estimateDataを構築
        estimate_data = {
            "totalPrice": total_price,
            "products": products
        }
        
        # testRequestフォーマットに合わせてリクエストボディを構築
        request_body = {
            "estimateData": estimate_data,
            "partsBreakdown": parts_breakdown,  # Step3の結果をそのまま使用
            "bucket_name": "knockai-106a4.firebasestorage.app",
            "parentFolderPath": f"organizations/{organization_id}/estimate_documents/{document_id}"
        }
        
        # ユーザー指示がある場合は追加
        if user_instructions:
            request_body["userInstructions"] = user_instructions
        
        print(f"   ✅ API request body generated")
        print(f"   📊 Total price: ¥{total_price:,}")
        print(f"   📦 Products count: {len(products)}")
        print(f"   📁 Folder path: organizations/{organization_id}/estimate_documents/{document_id}")
        
        return request_body
        
    except Exception as e:
        print(f"❌ ERROR in generate_api_request_body: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "error": f"APIリクエストボディ生成中にエラーが発生しました: {str(e)}"
        }

def get_cloud_run_auth_headers_for_agent(target_url: str) -> dict:
    """Cloud Run認証用のヘッダーを取得（agent.py用）"""
    try:
        from google.oauth2 import id_token
        from google.auth.transport.requests import Request
        
        print(f"🔐 IDトークン取得を試行中 for URL: {target_url}")
        
        # IDトークンを取得（Cloud Run認証用）
        auth_req = Request()
        id_token_value = id_token.fetch_id_token(auth_req, target_url)
        
        print(f"✅ IDトークンを正常に取得しました")
        
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {id_token_value}"
        }
    except Exception as e:
        print(f"❌ IDトークン取得エラー: {e}")
        print(f"   🔍 エラータイプ: {type(e)}")
        
        # フォールバック: 既に取得済みのcredentialsを使用
        try:
            print("🔄 フォールバック: 既に取得済みのcredentialsを使用")
            auth_req = Request()
            credentials.refresh(auth_req)
            
            print(f"✅ 既存のcredentialsからアクセストークンを取得しました")
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {credentials.token}"
            }
        except Exception as e2:
            print(f"❌ 認証取得エラー: {e2}")
            raise Exception(f"Cloud Run認証に失敗しました: IDトークン取得エラー({e}) + credentials認証エラー({e2})")

def call_estimate_generation_api(request_body: dict) -> dict:
    """外部APIに見積書生成リクエストを送信します。

    Args:
        request_body (dict): APIリクエストボディ

    Returns:
        dict: API呼び出し結果
    """
    try:
        print(f"🔍 DEBUG: call_estimate_generation_api called")
        
        # API エンドポイント
        api_url = "https://create-estimation-document-208707381956.us-central1.run.app/create-estimate-document"
        
        # Cloud Run認証用のヘッダーを取得
        headers = get_cloud_run_auth_headers_for_agent(api_url)
        
        print(f"📋 STEP 1: APIリクエストを送信中...")
        print(f"   🌐 URL: {api_url}")
        print(f"   📊 Request body size: {len(json.dumps(request_body))} characters")
        print(f"   🔍 DEBUG: Request body keys: {list(request_body.keys()) if isinstance(request_body, dict) else 'Not a dict'}")
        print(f"   🔍 DEBUG: estimateData in request: {'estimateData' in request_body}")
        print(f"   🔍 DEBUG: partsBreakdown in request: {'partsBreakdown' in request_body}")
        print(f"   🔐 DEBUG: Authorization header present: {'Authorization' in headers}")
        if 'Authorization' in headers:
            auth_header = headers['Authorization']
            print(f"   🔐 DEBUG: Auth header type: {'Bearer' if auth_header.startswith('Bearer ') else 'Unknown'}")
            print(f"   🔐 DEBUG: Token length: {len(auth_header.split(' ', 1)[1]) if ' ' in auth_header else 0} characters")
        
        # APIリクエスト送信
        response = requests.post(
            url=api_url,
            headers=headers,
            json=request_body,
            timeout=300  # 5分のタイムアウト
        )
        
        print(f"   📊 Response status code: {response.status_code}")
        print(f"   📊 Response headers: {dict(response.headers)}")
        
        # 401エラーの場合は詳細ログを出力
        if response.status_code == 401:
            print(f"   🚨 401 Unauthorized Error Details:")
            print(f"      📄 Response text: {response.text}")
            print(f"      🔐 Request headers: {dict(headers)}")
            print(f"      🌐 Target URL: {api_url}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"   ✅ API call successful")
            print(f"   📊 Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
            
            # GCSファイルURLを抽出（レスポンス形式に応じて調整）
            file_urls = []
            if isinstance(response_data, dict):
                # レスポンスからファイルURLを抽出
                if "file_urls" in response_data:
                    file_urls = response_data["file_urls"]
                elif "urls" in response_data:
                    file_urls = response_data["urls"]
                elif "files" in response_data:
                    file_urls = response_data["files"]
            
            return {
                "status": "success",
                "message": "見積書・明細書が正常に生成されました",
                "response_data": response_data,
                "file_urls": file_urls,
                "api_status_code": response.status_code
            }
        else:
            error_message = f"API呼び出しが失敗しました (Status: {response.status_code})"
            try:
                error_detail = response.json()
                error_message += f" - {error_detail}"
            except:
                error_message += f" - {response.text}"
            
            print(f"   ❌ API call failed: {error_message}")
            return {
                "status": "error",
                "error_message": error_message,
                "api_status_code": response.status_code
            }
            
    except requests.exceptions.Timeout:
        error_message = "API呼び出しがタイムアウトしました（5分経過）"
        print(f"❌ ERROR: {error_message}")
        return {
            "status": "error",
            "error_message": error_message
        }
    except requests.exceptions.RequestException as e:
        error_message = f"API呼び出し中にネットワークエラーが発生しました: {str(e)}"
        print(f"❌ ERROR: {error_message}")
        return {
            "status": "error",
            "error_message": error_message
        }
    except Exception as e:
        print(f"❌ ERROR in call_estimate_generation_api: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"API呼び出し中にエラーが発生しました: {str(e)}"
        }

def save_step4_output_to_firestore(api_request_body: dict, api_result: dict, document_id: str = "ABCD", collection_name: str = "agent_job") -> dict:
    """Step4用：APIリクエストボディと結果をFirestoreに保存します。

    Args:
        api_request_body (dict): APIに送信したリクエストボディ
        api_result (dict): API呼び出し結果
        document_id (str): Firestoreのドキュメント ID
        collection_name (str): Firestoreのコレクション名

    Returns:
        dict: 保存結果
    """
    try:
        print(f"🔍 DEBUG: save_step4_output_to_firestore called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        
        # Firestoreヘルパーを初期化
        firestore_helper = get_firestore_helper()
        
        estimate_data = api_request_body.get("estimateData", {})
        total_price = estimate_data.get("totalPrice", 0)
        products_count = len(estimate_data.get("products", []))
        file_urls = api_result.get("file_urls", [])
        
        # 説明文を生成
        description = f"""
        📋 【Step4: 見積書・明細書作成完了】
        
        📊 見積概要:
        • 作成日: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
        • 対象製品数: {products_count}個
        • 総計: ¥{total_price:,}
        • 保存先: {api_request_body.get("parentFolderPath", "不明")}
        
        📁 生成されたファイル:
        • ファイル数: {len(file_urls)}個
        • GCSバケット: {api_request_body.get("bucket_name", "不明")}
        
        🌐 API呼び出し結果:
        • ステータス: {api_result.get("status", "不明")}
        • HTTPコード: {api_result.get("api_status_code", "不明")}
        
        ✅ 見積書・明細書の作成が完了しました。
        🎉 全ステップが正常に完了しました！
        """
        
        # Firestoreに保存するデータを準備
        save_data = {
            "step4_output": {
                "api_request_body": api_request_body,
                "api_result": api_result,
                "description": description,
                "status": "completed",
                "pdfFileIsExported": True
            },
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📋 STEP 1: Firestoreに保存中...")
        success = firestore_helper.update_document(
            collection_name=collection_name,
            document_id=document_id,
            update_data=save_data
        )
        
        print(f"   📊 Save result: {success}")
        
        if success:
            print(f"   ✅ Step4 output saved successfully")
            return {
                "status": "success",
                "message": "APIリクエストボディと結果をstep4_outputとしてFirestoreに保存しました",
                "description": description
            }
        else:
            print(f"   ❌ Firestore save failed")
            return {
                "status": "error",
                "error_message": "Firestoreへの保存に失敗しました"
            }
            
    except Exception as e:
        print(f"❌ ERROR in save_step4_output_to_firestore: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"Step4結果保存中にエラーが発生しました: {str(e)}"
        }

# STEP5は削除されました - STEP4で見積書作成まで完了します

def getStep2Output(document_id: str = "ABCD", collection_name: str = "agent_job") -> dict:
    """Step2の製品リスト結果をFirestoreから取得します。

    Args:
        document_id (str): Firestoreのドキュメント ID
        collection_name (str): Firestoreのコレクション名

    Returns:
        dict: Step2の結果データ
    """
    try:
        print(f"🔍 DEBUG: getStep2Output called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        
        # Firestoreヘルパーを初期化
        firestore_helper = get_firestore_helper()
        
        # Firestoreからドキュメントを取得
        doc = firestore_helper.get_document(
            collection_name=collection_name,
            document_id=document_id
        )
        
        print(f"🔍 DEBUG: Firestore取得結果")
        print(f"   📄 Document exists: {doc is not None}")
        
        if not doc or 'step2_output' not in doc:
            print(f"   ❌ Document or 'step2_output' field not found")
            if doc:
                print(f"   🔍 Available fields: {list(doc.keys()) if isinstance(doc, dict) else 'Not a dict'}")
            return {
                "status": "error",
                "error_message": f"Step2の結果が見つかりません。先にStep2を実行してください。利用可能なフィールド: {list(doc.keys()) if doc and isinstance(doc, dict) else 'Not a dict'}"
            }
        
        print(f"   ✅ 'step2_output' field found")
        step2_output = doc['step2_output']
        print(f"   📋 Step2 output keys: {list(step2_output.keys()) if isinstance(step2_output, dict) else 'Not a dict'}")
        
        production_list = step2_output.get('production_list', [])
        print(f"   📊 Production list length: {len(production_list)}")
        
        return {
            "status": "success",
            "step2_output": step2_output,
            "production_list": production_list,
            "message": f"Step2の結果を取得しました（{len(production_list)}製品）"
        }
        
    except Exception as e:
        print(f"❌ ERROR in getStep2Output: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"Step2結果取得中にエラーが発生しました: {str(e)}"
        }

# getStep4Output関数は削除されました - Step4が最終ステップになったため不要

# 以下の関数は新しいAPI連携版のSTEP4では不要になったため削除されました：
# - generate_estimate_data (ローカル見積書データ生成)
# - create_estimate_file (ローカルファイル作成)
# - save_final_estimate_to_firestore_step4 (旧版保存処理)
# 新しいSTEP4では外部API経由でGCSに見積書・明細書を直接生成します

root_agent = LlmAgent(
    name="financial_info_agent",
    model='gemini-2.0-flash',
    description=(
        """
        - あなたはマルチステップのエージェントで、CADのPDFファイルを受け取り、その内容を解析して見積書を作成します
        - 業界経験が豊富な見積もり天才的な見積り作成職人です。部下から依頼を受けて作業を代行しているイメージで話して下さい。
        - Stepの管理はFirestoreを使用して行います。
        - Stepの一覧は以下であり、初期値は1です
        ①図面情報取得（Step1 - execute_step_1で実行）
        ②制作物特定（Step2 - execute_step_2で実行）**【重要】製品リストが空になることは絶対に避けてください**
        ③部材/数量/単価特定（Step3 - execute_step_3で実行）
        ④見積書・明細書作成（Step4 - execute_step_4で実行）**最終ステップ：外部API経由でGCSに見積書・明細書を生成し、currentStep=5に更新**
        
        ## 【重要】逐次実行ルール - 絶対に守ること
        - **1回のメッセージで実行できるのは1つのステップのみです**
        - **各ステップ完了後は必ずユーザーの明示的な確認を待ってください**
        - **ユーザーから「次に進んでください」「OK」「はい」などの明確な承諾がない限り、絶対に次のステップを実行してはいけません**
        - **複数のステップを一度にまとめて実行することは強く禁止されています**
        - **次のステップに進む もしくは 指定したステップに戻る際には、必ず現在のステップを移動先に合わせて更新すること**
        - **ステップ完了後は必ず以下の形式で確認を求めてください：**
          ### 🎯 STEP[番号]が完了しました！
          ### 📋 結果概要：[簡潔な結果説明を行なってください]
          ### ⚠️ **次のSTEP[次の番号]に進む前に、必ず上記の結果をアウトプット確認タブで確認してください**
          ### ✅ 確認が完了しましたら、「次に進んでください」とお知らせください。
          ### 🚫 確認なしに次のステップは実行されません。
        - STEP名は 1:図面情報の取得 / 2:制作物特定 / 3:部材/数量/単価特定 / 4:見積書・明細書作成 です。
        - 各ステップの詳細の結果については、WEB UI上で表示するので、中身の詳細の出力は不要です。A:正常に完了しました! の報告 / B:エラーが発生しました! の報告 / C:出力を画面上で確認して準備が整ったら先に進め の案内のみを出力してください。
        - 各種タスクが完了したら、次のステップに進んで良いですか?の確認を行い、ユーザーから承諾を得たらupdate_current_stepを実行して次のステップに進んでください。各ステップの更新は確実に実施して下さい。
        - 1番最初はexecute_step_1を実行して、その後順番に1つ1つのステップを逐次的に実行していきます。
        - ユーザーのInputでFirestoreのCollection名とDocumentIdが最初に渡されます。
        - Collection名とDocumentIdは、最初に与えられたものを全てのStepで共通して使用してください。
        - Collection名のorganizations/{organizationId}フォーマットでユーザーからorganizationIdが渡されます。そのOrganizationIdを使用してファイル出力先を指定します。generate_api_request_bodyのorganization_idに渡してください。
        - ユーザーから指示があった場合は、各Stepを再度実行し、修正した結果をFirestoreに保存してから、次のステップに進むか?確認してください
        - Firestoreに保存されたデータはUI側で後追いで更新される可能性もあります。新しいステップを開始する際には、必ず前ステップのOutputを取得して、その内容を元に次のステップを実行してください。(例:STEP3の開始時にはSTEP2のOutputを取得して、その内容を元にSTEP3を実行してください。)
        - また、もし修正が検知された場合には、その旨をユーザーに伝えた後で次のステップを実行してください。
        - 次に進んでも良いのか?の確認は、ユーザーが見落とすことのないように、特に強調して表示して下さい
        - **Step2で製品リストが空になった場合は、必ずStep1のanalysis結果を再確認し、フォールバック処理で最低1つの製品を抽出してください**
        - **Step4で全ての処理が完了します。外部API経由でGCSに見積書・明細書を生成し、処理を完了します**
        - テキストが横に長すぎると、視認性が悪化するので、凡そ90文字を超えるような場合は積極的に改行を入れて下さい
        """
    ),
    instruction="こちらのIDを用いて直ちにexecute_step_1を呼び出して処理を開始してください。IDの取得に失敗した場合は、その旨をユーザーに伝えてください。【重要】1つのステップ完了後は必ずユーザーの確認を待ち、承諾を得てからのみ次のステップに進んでください。複数ステップの連続実行は絶対に禁止です。Step2では製品リストが空になることは絶対に避け、必ず1つ以上の製品を抽出してください。Step4で外部API経由の見積書・明細書作成まで完了し、currentStep=5に自動更新します。各execute_step_*メソッドは開始時に自動的にcurrentStepを適切な値に更新します。",
    tools=[
        get_current_step,
        get_selected_step_output,
        execute_step_1,
        execute_step_2,
        execute_step_3,
        execute_step_4
    ],
)