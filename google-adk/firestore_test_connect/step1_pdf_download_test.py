import os
import sys
import json
from datetime import datetime
from google.cloud import storage
from typing import Dict, Any
# スクリプトのディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
from firestore_helper import FirestoreHelper
from gcs_helper import GCSHelper

# 現在のファイルのディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))

# Firestoreヘルパーを初期化（環境変数ベース）
firestore_helper = FirestoreHelper()
gcs_helper = GCSHelper()

def get_pdf_file_path_from_firestore(document_id: str = "adk",collection_name: str = "agent_job") -> dict:
    """FirestoreからPDFファイルのパス情報を取得します。

    Args:
        document_id (str): Firestoreのドキュメント ID

    Returns:
        dict: PDFファイルパス情報
    """
    try:
        print(f"🔍 DEBUG: Firestoreからドキュメントを取得開始")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        
        # Firestoreからドキュメントを取得
        doc = firestore_helper.get_document(
            collection_name=collection_name,
            document_id=document_id
        )
        
        print(f"🔍 DEBUG: Firestore取得結果")
        print(f"   📄 Document exists: {doc is not None}")
        
        if doc:
            print(f"   📋 Document keys: {list(doc.keys()) if isinstance(doc, dict) else 'Not a dict'}")
            print(f"   📊 Document type: {type(doc)}")
            print(f"   📝 Document content preview: {str(doc)[:200]}...")
            
            # inputフィールドの存在確認
            if 'input' in doc:
                print(f"   ✅ 'input' field found")
                input_data = doc['input']
                print(f"   📋 Input data keys: {list(input_data.keys()) if isinstance(input_data, dict) else 'Not a dict'}")
                print(f"   📊 Input data type: {type(input_data)}")
                
                pdf_file_path = input_data.get('pdfFilePath', '')
                print(f"   📁 PDF file path: {pdf_file_path}")
                
                if pdf_file_path:
                    print(f"   ✅ PDF file path found: {pdf_file_path}")
                    return {
                        "status": "success",
                        "pdf_file_path": pdf_file_path,
                        "message": f"PDFファイルパスを取得しました: {pdf_file_path}"
                    }
                else:
                    print(f"   ❌ PDF file path is empty")
                    return {
                        "status": "error",
                        "error_message": "PDFファイルパスが見つかりません"
                    }
            else:
                print(f"   ❌ 'input' field not found in document")
                print(f"   🔍 Available fields: {list(doc.keys()) if isinstance(doc, dict) else 'Not a dict'}")
                return {
                    "status": "error",
                    "error_message": f"ドキュメントまたはinputフィールドが見つかりません。利用可能なフィールド: {list(doc.keys()) if isinstance(doc, dict) else 'Not a dict'}"
                }
        else:
            print(f"   ❌ Document not found")
            return {
                "status": "error",
                "error_message": "ドキュメントまたはinputフィールドが見つかりません"
            }
            
    except Exception as e:
        print(f"❌ ERROR in get_pdf_file_path_from_firestore: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"PDFファイルパス取得中にエラーが発生しました: {str(e)}"
        }

def generate_download_url_and_analyze(pdf_file_path: str) -> dict:
    """GCSファイルパスからダウンロード可能なURLを生成し、ファイル内容を解析してコメントします。

    Args:
        pdf_file_path (str): GCS上のPDFファイルパス

    Returns:
        dict: URL生成とファイル解析結果
    """
    try:
        print(f"DEBUG: Starting URL generation and analysis for: {pdf_file_path}")
        
        # GCSからダウンロード可能なURLを生成
        download_url = gcs_helper.generate_download_url(pdf_file_path)
        
        if not download_url:
            return {
                "status": "error",
                "error_message": "ダウンロードURLの生成に失敗しました"
            }
        
        print(f"DEBUG: Generated download URL: {download_url}")
        
        # URLから直接ファイル内容を取得
        import requests
        response = requests.get(download_url)
        response.raise_for_status()
        
        pdf_blob = response.content
        file_size = len(pdf_blob)
        
        # PDFファイルの基本情報を取得
        pdf_info = {
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "blob_length": len(pdf_blob),
            "is_valid_pdf": pdf_blob.startswith(b'%PDF'),
            "download_url": download_url,
            "access_method": "direct_url"
        }
        
        # ファイル内容の解析とコメント生成
        analysis_comment = analyze_and_comment_on_file(pdf_blob, pdf_file_path)
        
        print(f"DEBUG: File analysis completed. Size: {pdf_info['file_size_mb']}MB")
        
        return {
            "status": "success",
            "download_url": download_url,
            "pdf_info": pdf_info,
            "analysis_comment": analysis_comment,
            "message": f"ファイルURL生成と解析が完了しました（{pdf_info['file_size_mb']}MB）"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"URL生成・ファイル解析中にエラーが発生しました: {str(e)}"
        }

def analyze_and_comment_on_file(file_blob: bytes, file_path: str) -> str:
    """ファイル内容を解析してコメントを生成します。

    Args:
        file_blob (bytes): ファイルのバイナリデータ
        file_path (str): ファイルパス

    Returns:
        str: ファイル内容に関するコメント
    """
    try:
        # ファイル形式の判定
        file_extension = file_path.lower().split('.')[-1] if '.' in file_path else 'unknown'
        file_size_mb = round(len(file_blob) / (1024 * 1024), 2)
        
        # 基本的なファイル解析
        analysis_parts = []
        
        # ファイル形式別の解析
        if file_blob.startswith(b'%PDF'):
            analysis_parts.append("📄 **PDFファイル**として認識されました")
            
            # PDFの簡易解析
            content_str = str(file_blob)
            page_count = content_str.count('/Type /Page')
            if page_count == 0:
                page_count = content_str.count('endobj') // 10  # 大まかな推定
            
            analysis_parts.append(f"📊 推定ページ数: {max(1, page_count)}ページ")
            
            # PDFの内容キーワード検索
            keywords_found = []
            keywords_to_check = ['図面', '設計', 'CAD', 'blueprint', 'drawing', 'specification', '仕様']
            for keyword in keywords_to_check:
                if keyword.encode() in file_blob or keyword in content_str:
                    keywords_found.append(keyword)
            
            if keywords_found:
                analysis_parts.append(f"🔍 検出されたキーワード: {', '.join(keywords_found)}")
            
        elif file_blob.startswith(b'\x89PNG'):
            analysis_parts.append("🖼️ **PNGファイル**として認識されました")
        elif file_blob.startswith(b'\xff\xd8\xff'):
            analysis_parts.append("📸 **JPEGファイル**として認識されました")
        elif file_blob.startswith(b'PK'):
            analysis_parts.append("📦 **ZIPアーカイブ**または**Office文書**として認識されました")
        else:
            analysis_parts.append(f"📁 **{file_extension.upper()}ファイル**として推定されます")
        
        # ファイルサイズの評価
        if file_size_mb < 1:
            size_comment = "軽量なファイル"
        elif file_size_mb < 10:
            size_comment = "標準的なサイズ"
        elif file_size_mb < 50:
            size_comment = "やや大きなファイル"
        else:
            size_comment = "大容量ファイル"
        
        analysis_parts.append(f"💾 ファイルサイズ: {file_size_mb}MB ({size_comment})")
        
        # 内容の品質評価
        if len(file_blob) > 10240:  # 10KB以上
            analysis_parts.append("✅ 十分な内容を含んでいると推定されます")
        else:
            analysis_parts.append("⚠️ 内容が少ない可能性があります")
        
        # 最終コメント
        final_comment = f"""
🔍 **ファイル解析結果**

{chr(10).join(analysis_parts)}

📋 **総合評価**: 
このファイルは{size_comment}で、解析に適した形式です。
{'CADや設計図面関連の可能性が高いです。' if any(kw in keywords_found for kw in ['図面', '設計', 'CAD', 'blueprint', 'drawing']) else '一般的な文書ファイルと推定されます。'}

🔧 **次のステップ**: 
このファイルは後続の処理（analysisJSON解析、製品一覧特定）で活用できます。
        """
        
        return final_comment.strip()
        
    except Exception as e:
        return f"ファイル解析中にエラーが発生しました: {str(e)}"

def validate_pdf_content(pdf_blob: bytes) -> dict:
    """PDFファイルの内容を検証します。

    Args:
        pdf_blob (bytes): PDFファイルのバイナリデータ

    Returns:
        dict: 検証結果
    """
    try:
        validation_results = {
            "is_pdf_format": False,
            "has_content": False,
            "estimated_pages": 0,
            "file_size_mb": 0,
            "validation_status": "unknown"
        }
        
        # 基本的なPDFフォーマット検証
        if pdf_blob.startswith(b'%PDF'):
            validation_results["is_pdf_format"] = True
        
        # ファイルサイズ
        file_size = len(pdf_blob)
        validation_results["file_size_mb"] = round(file_size / (1024 * 1024), 2)
        
        # 内容の有無（簡易チェック）
        if file_size > 1024:  # 1KB以上
            validation_results["has_content"] = True
        
        # ページ数の推定（簡易的）
        page_count = pdf_blob.count(b'/Type /Page')
        if page_count == 0:
            # 別のパターンを試行
            page_count = pdf_blob.count(b'endobj')
        validation_results["estimated_pages"] = max(1, page_count // 10)  # 大まかな推定
        
        # 総合的な検証ステータス
        if validation_results["is_pdf_format"] and validation_results["has_content"]:
            validation_results["validation_status"] = "valid"
        elif validation_results["is_pdf_format"]:
            validation_results["validation_status"] = "format_ok_but_small"
        else:
            validation_results["validation_status"] = "invalid"
        
        return {
            "status": "success",
            "validation_results": validation_results,
            "message": f"PDF検証完了: {validation_results['validation_status']}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"PDF検証中にエラーが発生しました: {str(e)}"
        }

def save_step1_output_to_firestore(pdf_info: dict, validation_results: dict, pdf_file_path: str, download_url: str, analysis_data: dict, document_id: str = "adk",collection_name: str = "agent_job") -> dict:
    """Step1の結果をFirestoreに保存します。

    Args:
        pdf_info (dict): PDFファイル情報
        validation_results (dict): PDF検証結果
        pdf_file_path (str): PDFファイルパス
        download_url (str): ダウンロード可能なURL
        analysis_data (dict): 解析されたanalysisJSONデータ
        document_id (str): Firestoreのドキュメント ID

    Returns:
        dict: 保存結果
    """
    try:
        # 保存用のデータを準備
        step1_output = {
            "pdf_download_test": {
                "pdf_file_path": pdf_file_path,
                "pdf_info": pdf_info,
                "validation_results": validation_results,
                "download_status": "success",
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            },
            "analysis_json": {
                "analysis_data": analysis_data,
                "download_status": "success",
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
        }
        
        # Firestoreに保存（step1_outputとtmpPdfBlueprintDlUrlの両方を保存）
        update_data = {
            "step1_output": step1_output,
            "tmpPdfBlueprintDlUrl": download_url
        }
        
        success = firestore_helper.update_document(
            collection_name=collection_name,
            document_id=document_id,
            update_data=update_data
        )
        
        if success:
            return {
                "status": "success",
                "message": "Step1の結果とダウンロードURLをFirestoreに保存しました",
                "step1_output": step1_output,
                "tmpPdfBlueprintDlUrl": download_url
            }
        else:
            raise Exception("Firestoreへの保存に失敗しました")
            
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Step1結果保存中にエラーが発生しました: {str(e)}"
        }

def execute_pdf_download_test(document_id: str = "adk",collection_name: str = "agent_job") -> dict:
    """Step1のPDFダウンロードテストを実行します。

    Args:
        document_id (str): Firestoreのドキュメント ID

    Returns:
        dict: 実行結果
    """
    try:
        print(f"🚀 DEBUG: Starting Step1 PDF download test")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        print(f"   ⏰ Timestamp: {datetime.now().isoformat()}")
        
        # 1. PDFファイルパスを取得
        print(f"📋 STEP 1: PDFファイルパスを取得中...")
        path_result = get_pdf_file_path_from_firestore(document_id,collection_name)
        print(f"   📊 Path result status: {path_result.get('status', 'unknown')}")
        
        if path_result["status"] != "success":
            print(f"   ❌ Path retrieval failed: {path_result.get('error_message', 'Unknown error')}")
            return path_result
        
        pdf_file_path = path_result["pdf_file_path"]
        print(f"   ✅ PDF file path retrieved: {pdf_file_path}")
        
        # 2. ダウンロードURL生成とファイル解析
        print(f"📋 STEP 2: ダウンロードURL生成とファイル解析中...")
        analysis_result = generate_download_url_and_analyze(pdf_file_path)
        print(f"   📊 Analysis result status: {analysis_result.get('status', 'unknown')}")
        
        if analysis_result["status"] != "success":
            print(f"   ❌ Analysis failed: {analysis_result.get('error_message', 'Unknown error')}")
            return analysis_result
        
        download_url = analysis_result["download_url"]
        pdf_info = analysis_result["pdf_info"]
        analysis_comment = analysis_result["analysis_comment"]
        print(f"   ✅ Analysis completed successfully")
        print(f"   📁 Download URL: {download_url}")
        print(f"   📊 File size: {pdf_info.get('file_size_mb', 'unknown')}MB")
        
        # 3. FirestoreからanalysisJSONを取得
        print(f"📋 STEP 3: FirestoreからanalysisJSONを取得中...")
        json_result = get_analysis_json_from_firestore(collection_name, document_id)
        print(f"   📊 JSON result status: {json_result.get('status', 'unknown')}")
        
        if json_result["status"] != "success":
            print(f"   ❌ JSON retrieval failed: {json_result.get('error_message', 'Unknown error')}")
            return json_result
        
        analysis_data = json_result["analysis_data"]
        print(f"   ✅ Analysis JSON retrieved successfully from Firestore")
        print(f"   📊 Analysis data keys: {list(analysis_data.keys()) if isinstance(analysis_data, dict) else 'Not a dict'}")
        
        # 4. 簡易的な検証（URLアクセスベース）
        print(f"📋 STEP 4: ファイル検証中...")
        validation_results = {
            "is_pdf_format": pdf_info["is_valid_pdf"],
            "has_content": pdf_info["file_size_mb"] > 0.01,  # 10KB以上
            "estimated_pages": 1,  # 簡易推定
            "file_size_mb": pdf_info["file_size_mb"],
            "validation_status": "valid" if pdf_info["is_valid_pdf"] else "unknown",
            "access_method": "direct_url"
        }
        print(f"   ✅ Validation completed")
        print(f"   📊 Validation status: {validation_results['validation_status']}")
        
        # 5. 結果をFirestoreに保存
        print(f"📋 STEP 5: Firestoreに結果を保存中...")
        save_result = save_step1_output_to_firestore(
            pdf_info=pdf_info,
            validation_results=validation_results,
            pdf_file_path=pdf_file_path,
            download_url=download_url,
            analysis_data=analysis_data,
            document_id=document_id,
            collection_name=collection_name
        )
        print(f"   📊 Save result status: {save_result.get('status', 'unknown')}")
        
        if save_result["status"] != "success":
            print(f"   ❌ Save failed: {save_result.get('error_message', 'Unknown error')}")
            return save_result
        
        print(f"   ✅ Save completed successfully")
        
        # 6. 結果の要約を生成
        print(f"📋 STEP 6: 結果要約を生成中...")
        summary = f"""
        📄 【Step1: ファイルURL生成と解析結果】
        
        📁 ファイル情報:
        • PDFパス: {pdf_file_path}
        • ダウンロードURL: {download_url}
        • サイズ: {pdf_info['file_size_mb']}MB
        • アクセス方法: 直接URL
        
        🔍 ファイル解析:
        {analysis_comment}
        
        📊 Analysis JSON解析:
        • 取得元: Firestore (input.preAnalysisJson)
        • 解析ステータス: ✅ 完了
        • データキー: {list(analysis_data.keys()) if isinstance(analysis_data, dict) else 'Not a dict'}
        
        💾 Firestore保存:
        • step1_output: ✅ 保存完了（PDF + Analysis JSON）
        • tmpPdfBlueprintDlUrl: ✅ 保存完了
        
        ✅ ファイルURL生成と解析が完了しました。
        🔧 次のステップ: analysisJSONの内容出力に進む準備が整いました。
        """
        
        print(f"✅ Step1 completed successfully!")
        print(f"   📊 Summary generated")
        print(f"   🔧 Next step: Step2 ready")
        
        return {
            "status": "success",
            "message": f"Step1: ファイルURL生成と解析が完了しました\n{summary}",
            "summary": summary,
            "download_url": download_url,
            "pdf_info": pdf_info,
            "validation_results": validation_results,
            "analysis_comment": analysis_comment,
            "analysis_data": analysis_data,
            "next_step": "Step2: analysisJSONの内容出力に進む準備が整いました"
        }
        
    except Exception as e:
        print(f"❌ ERROR in execute_pdf_download_test: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"Step1実行中にエラーが発生しました: {str(e)}"
        }

def get_analysis_json_from_firestore(collection_name: str, document_id: str) -> dict:
    """FirestoreからanalysisJSONを取得します。

    Args:
        collection_name (str): Firestoreのコレクション名
        document_id (str): FirestoreのドキュメントID

    Returns:
        dict: input.preAnalysisJsonの内容
    """
    try:
        print(f"🔍 DEBUG: get_analysis_json_from_firestore called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   📄 Document ID: {document_id}")
        
        # Firestoreからドキュメントを取得
        print(f"📋 STEP 1: Firestoreからドキュメントを取得中...")
        doc = firestore_helper.get_document(collection_name, document_id)
        
        if not doc:
            raise Exception(f"Document not found: {collection_name}/{document_id}")
        
        doc_data = doc
        print(f"   ✅ Document retrieved successfully")
        
        # input.preAnalysisJsonを取得
        print(f"📋 STEP 2: input.preAnalysisJsonを取得中...")
        if 'input' not in doc_data:
            raise Exception("Document does not contain 'input' field")
        
        input_data = doc_data['input']
        if 'preAnalysisJson' not in input_data:
            raise Exception("Document does not contain 'input.preAnalysisJson' field")
        
        analysis_data = input_data['preAnalysisJson']
        print(f"   ✅ preAnalysisJson retrieved successfully")
        print(f"   📊 JSON keys: {list(analysis_data.keys()) if isinstance(analysis_data, dict) else 'Not a dict'}")
        print(f"   📄 JSON content preview: {str(analysis_data)[:200]}...")
        
        print(f"✅ Analysis JSON retrieval completed successfully")
        return {
            "status": "success",
            "analysis_data": analysis_data,
            "message": "FirestoreからanalysisJSONの取得が完了しました"
        }
        
    except Exception as e:
        print(f"❌ ERROR in get_analysis_json_from_firestore: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"FirestoreからのanalysisJSON取得中にエラーが発生しました: {str(e)}"
        }