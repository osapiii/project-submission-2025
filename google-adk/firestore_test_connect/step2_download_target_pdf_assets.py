import json
import os
import sys
from datetime import datetime
from typing import List, Dict
# スクリプトのディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
from firestore_helper import FirestoreHelper

# 現在のファイルのディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))

# Firestoreヘルパーを初期化（環境変数ベース）
firestore_helper = FirestoreHelper()

def get_analysis_json_from_step1_output(document_id: str = "adk", collection_name: str = "agent_job") -> dict:
    """Step1の出力からanalysisJSONを取得します。

    Args:
        document_id (str): Firestoreのドキュメント ID
        collection_name (str): Firestoreのコレクション名

    Returns:
        dict: analysisJSONデータの取得結果
    """
    try:
        print(f"🔍 DEBUG: get_analysis_json_from_step1_output called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        
        # Firestoreからドキュメントを取得
        doc = firestore_helper.get_document(
            collection_name=collection_name,
            document_id=document_id
        )
        
        print(f"🔍 DEBUG: Firestore取得結果")
        print(f"   📄 Document exists: {doc is not None}")
        
        if doc and 'step1_output' in doc:
            print(f"   ✅ 'step1_output' field found")
            step1_output = doc['step1_output']
            print(f"   📋 Step1 output keys: {list(step1_output.keys()) if isinstance(step1_output, dict) else 'Not a dict'}")
            
            if 'analysis_json' in step1_output:
                analysis_json_data = step1_output['analysis_json']
                print(f"   ✅ 'analysis_json' field found in step1_output")
                print(f"   📊 Analysis JSON keys: {list(analysis_json_data.keys()) if isinstance(analysis_json_data, dict) else 'Not a dict'}")
                
                if 'analysis_data' in analysis_json_data:
                    analysis_data = analysis_json_data['analysis_data']
                    print(f"   ✅ 'analysis_data' field found")
                    print(f"   📄 Analysis data keys: {list(analysis_data.keys()) if isinstance(analysis_data, dict) else 'Not a dict'}")
                    
                    return {
                        "status": "success",
                        "analysis_data": analysis_data,
                        "message": "Step1の出力からanalysisJSONを取得しました"
                    }
                else:
                    print(f"   ❌ 'analysis_data' field not found in analysis_json")
                    return {
                        "status": "error",
                        "error_message": "Step1の出力にanalysis_dataが見つかりません"
                    }
            else:
                print(f"   ❌ 'analysis_json' field not found in step1_output")
                return {
                    "status": "error",
                    "error_message": "Step1の出力にanalysis_jsonが見つかりません"
                }
        else:
            print(f"   ❌ Document or 'step1_output' field not found")
            if doc:
                print(f"   🔍 Available fields: {list(doc.keys()) if isinstance(doc, dict) else 'Not a dict'}")
            return {
                "status": "error",
                "error_message": f"Firestoreドキュメントまたはstep1_outputフィールドが見つかりません。利用可能なフィールド: {list(doc.keys()) if doc and isinstance(doc, dict) else 'Not a dict'}"
            }
            
    except Exception as e:
        print(f"❌ ERROR in get_analysis_json_from_step1_output: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"Step1出力からのanalysisJSON取得中にエラーが発生しました: {str(e)}"
        }

def create_simple_analysis_description(analysis_data: dict) -> dict:
    """analysisJSONの内容をシンプルに説明します。

    Args:
        analysis_data (dict): 解析されたJSONデータ

    Returns:
        dict: シンプルな説明結果
    """
    try:
        # 基本的な情報を抽出
        summary = analysis_data.get("summary", "概要情報なし")
        annotation = analysis_data.get("annotation", "注釈情報なし")
        pages = analysis_data.get("pages", [])
        
        # ページ情報の整理
        page_count = len(pages)
        page_details = []
        for page in pages:
            page_info = f"ページ{page.get('pageCount', '不明')}: {page.get('summary', '内容不明')}"
            page_details.append(page_info)
        
        # 製作数量の抽出（annotationから）
        production_info = []
        if "Type C-2" in annotation:
            if "10台" in annotation:
                production_info.append("Type C-2（ロータイプ）: 10台")
        if "Type B-2" in annotation:
            if "4台" in annotation:
                production_info.append("Type B-2（ハイタイプ）: 4台")
            if "棚板" in annotation and "8枚" in annotation:
                production_info.append("Type B-2用棚板: 8枚（各2枚づつ）")
        
        # シンプルな説明文を生成
        description = f"""
        📋 【Step1で取得したAnalysis JSONの内容】
        
        📄 プロジェクト概要:
        {summary}
        
        📊 製作仕様・注釈:
        {annotation}
        
        📄 図面構成:
        • 総ページ数: {page_count}ページ
        • ページ詳細:"""
        
        for page_detail in page_details:
            description += f"\n  - {page_detail}"
        
        if production_info:
            description += f"\n\n🔢 製作数量:"
            for info in production_info:
                description += f"\n  • {info}"
        
        description += f"""
        
        ✅ Step1で取得したanalysisJSONの内容を確認しました。
        🔧 次のステップ: 製品一覧の詳細特定に進む準備が整いました。
        """
        
        return {
            "status": "success",
            "description": description,
            "summary": summary,
            "annotation": annotation,
            "page_count": page_count,
            "page_details": page_details,
            "production_info": production_info,
            "raw_data": analysis_data,
            "message": "Step1で取得したanalysisJSONの内容を確認しました"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"analysisJSONの説明生成中にエラーが発生しました: {str(e)}"
        }

def save_step2_output_to_firestore(analysis_data: dict, description: str, document_id: str = "adk", collection_name: str = "agent_job") -> dict:
    """Step2の結果をFirestoreに保存します。

    Args:
        analysis_data (dict): 解析されたJSONデータ
        description (str): 生成された説明
        document_id (str): FirestoreのドキュメントID
        collection_name (str): Firestoreのコレクション名

    Returns:
        dict: 保存結果
    """
    try:
        print(f"🔍 DEBUG: save_step2_output_to_firestore called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        
        # 保存用のデータを準備
        step2_output = {
            "analysis_data": analysis_data,
            "description": description,
            "source": "step1_output",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        print(f"📋 STEP 1: 保存データを準備中...")
        print(f"   📊 Analysis data keys: {list(analysis_data.keys()) if isinstance(analysis_data, dict) else 'Not a dict'}")
        
        # Firestoreに保存
        print(f"📋 STEP 2: Firestoreに保存中...")
        success = firestore_helper.update_document(
            collection_name=collection_name,
            document_id=document_id,
            update_data={
                "step2_output": step2_output
            }
        )
        
        print(f"   📊 Save result: {success}")
        
        if success:
            print(f"   ✅ Step2 output saved successfully")
            return {
                "status": "success",
                "message": "Step2の結果をFirestoreに保存しました"
            }
        else:
            print(f"   ❌ Firestore save failed")
            raise Exception("Firestoreへの保存に失敗しました")
            
    except Exception as e:
        print(f"❌ ERROR in save_step2_output_to_firestore: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"Step2結果保存中にエラーが発生しました: {str(e)}"
        }

