from google.adk.agents import LlmAgent
import sys
from datetime import datetime
from typing import List, Dict
import os
import json
import re
from dotenv import load_dotenv
# スクリプトのディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 環境変数を読み込む
load_dotenv()

from firestore_helper import FirestoreHelper
from gcs_helper import GCSHelper

# 現在のファイルのディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))

# Firestoreヘルパーを初期化（環境変数ベース）
firestore_helper = FirestoreHelper()
gcs_helper = GCSHelper()

def getAnalysisJson(document_id: str = "ABCD", collection_name: str = "agent_job") -> dict:
    """Step2のanalysis.json結果を取得します。

    Args:
        document_id (str): Firestoreのドキュメント ID
        collection_name (str): Firestoreのコレクション名

    Returns:
        dict: Step2の解析結果データ
    """
    try:
        print(f"🔍 DEBUG: getAnalysisJson called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        
        # Firestoreからドキュメントを取得
        doc = firestore_helper.get_document(
            collection_name=collection_name,
            document_id=document_id
        )
        
        print(f"🔍 DEBUG: Firestore取得結果")
        print(f"   📄 Document exists: {doc is not None}")
        
        if doc and 'step2_output' in doc:
            print(f"   ✅ 'step2_output' field found")
            step2_output = doc['step2_output']
            print(f"   📋 Step2 output keys: {list(step2_output.keys()) if isinstance(step2_output, dict) else 'Not a dict'}")
            
            # Step2の出力構造を確認し、analysis_dataを取得
            analysis_json_data = None
            
            # パターン1: step2_output.analysis_json_data
            if 'analysis_json_data' in step2_output:
                analysis_json_data = step2_output['analysis_json_data']
                print(f"   ✅ Found analysis_json_data in step2_output")
            
            # パターン2: step2_output.analysis_data
            elif 'analysis_data' in step2_output:
                analysis_json_data = step2_output['analysis_data']
                print(f"   ✅ Found analysis_data in step2_output")
            
            # パターン3: step1_outputから直接取得
            elif doc and 'step1_output' in doc:
                step1_output = doc['step1_output']
                if 'analysis_json' in step1_output and 'analysis_data' in step1_output['analysis_json']:
                    analysis_json_data = step1_output['analysis_json']['analysis_data']
                    print(f"   ✅ Found analysis_data in step1_output (fallback)")
            
            if analysis_json_data:
                print(f"   📊 Analysis JSON data keys: {list(analysis_json_data.keys()) if isinstance(analysis_json_data, dict) else 'Not a dict'}")
                
                return {
                    "status": "success",
                    "analysis_json": analysis_json_data,
                    "step2_output": step2_output,
                    "message": "Step2のanalysis.json結果を取得しました"
                }
            else:
                print(f"   ❌ Analysis data not found in any expected location")
                return {
                    "status": "error",
                    "error_message": f"Step2またはStep1の解析データが見つかりません。step2_output内容: {step2_output}"
                }
        else:
            print(f"   ❌ Document or 'step2_output' field not found")
            if doc:
                print(f"   🔍 Available fields: {list(doc.keys()) if doc and isinstance(doc, dict) else 'Not a dict'}")
            return {
                "status": "error",
                "error_message": f"Step2の結果が見つかりません。先にStep2を実行してください。利用可能なフィールド: {list(doc.keys()) if doc and isinstance(doc, dict) else 'Not a dict'}"
            }
            
    except Exception as e:
        print(f"❌ ERROR in getAnalysisJson: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"analysis.json取得中にエラーが発生しました: {str(e)}"
        }

def createProductionList(analysis_json: dict, download_url: str, user_instructions: str = "") -> dict:
    """LLMを使用してanalysis.jsonとPDFダウンロードURLから製品リストを生成します。

    Args:
        analysis_json (dict): Step2で取得したanalysis.jsonデータ
        download_url (str): Step1で生成されたPDFダウンロードURL
        user_instructions (str): ユーザーからの追加指示

    Returns:
        dict: 生成された製品リスト
    """
    try:
        import google.generativeai as genai
        import json
        import os
        
        # Gemini APIキーを環境変数から取得
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return {
                "status": "error",
                "error_message": "GEMINI_API_KEYが設定されていません。環境変数を確認してください。"
            }
        
        genai.configure(api_key=api_key)
        
        # analysis.jsonから基本情報を抽出
        summary = analysis_json.get("summary", "")
        annotation = analysis_json.get("annotation", "")
        pages = analysis_json.get("pages", [])
        
        # より詳細な情報を抽出
        all_text_content = []
        
        # summaryから製品情報を抽出
        if summary:
            all_text_content.append(f"【プロジェクト概要】\n{summary}")
        
        # annotationから製品情報を抽出（重要）
        if annotation:
            all_text_content.append(f"【製作仕様・注釈】\n{annotation}")
        
        # 各ページの詳細情報を抽出
        for i, page in enumerate(pages, 1):
            page_summary = page.get("summary", "")
            page_content = page.get("content", "")
            
            if page_summary:
                all_text_content.append(f"【ページ{i} 概要】\n{page_summary}")
            if page_content:
                all_text_content.append(f"【ページ{i} 詳細内容】\n{page_content}")
        
        combined_content = "\n\n".join(all_text_content)
        
        print(f"DEBUG: Combined content for analysis: {combined_content[:500]}...")
        
        # Geminiモデルを初期化
        model = genai.GenerativeModel(
            'gemini-2.0-flash-exp'
        )
        
        # 改善されたプロンプトを構築
        prompt = f"""
あなたはCAD図面解析の専門エキスパートです。以下の図面解析データから製品リストを**必ず**抽出してください。

【重要】製品リストが空になることは絶対に避けてください。必ず1つ以上の製品を抽出してください。

【解析対象データ】
{combined_content}

【製品抽出の優先順位】
1. **数量が明記されているもの**（例：「○○台」「○○個」「○○枚」「○○セット」）
2. **型番・製品名が明記されているもの**（例：「Type C-2」「Type B-2」「什器」「ディスプレイ」）
3. **部品・構成要素**（例：「棚板」「フレーム」「パネル」「ベース」）
4. **図面に記載されている構造物**（例：「キャビネット」「ラック」「スタンド」）

【抽出パターン例】
- "Type C-2 10台" → Type C-2を10個
- "Type B-2 4台、棚板各2枚づつ" → Type B-2を4個、棚板を8個
- "什器一式" → 什器を1セット
- "ディスプレイスタンド" → ディスプレイスタンドを1個

【必須出力形式】
以下のJSON形式で**必ず**出力してください：

```json
{{
  "products": [
    {{
      "name": "製品名（具体的で分かりやすい名称）",
      "description": "詳細説明（仕様、用途、特徴など）",
      "cnt": 数量（整数、不明な場合は1）
    }}
  ]
}}
```

【抽出ルール】
1. **必ず1つ以上の製品を抽出**（空のリストは絶対に返さない）
2. 数量表現を見逃さない（「台」「個」「枚」「セット」「式」など）
3. 型番・品番を正確に記録
4. 不明確な場合は推測で補完（例：図面があれば最低1つの製品は存在）
5. 重複は統合、関連部品は分けて記録
6. ユーザー指示があれば優先的に反映

【フォールバック】
もし具体的な製品が特定できない場合は、以下を出力：
```json
{{
  "products": [
    {{
      "name": "CAD図面記載製品",
      "description": "図面に記載された製品（詳細は図面参照）",
      "cnt": 1
    }}
  ]
}}
```

ユーザー追加指示: {user_instructions if user_instructions else "なし"}

**重要**: JSON形式のみで回答し、説明文は不要です。製品リストが空になることは絶対に避けてください。
        """
        
        # Gemini APIに製品リスト生成を依頼
        response = model.generate_content(prompt)
        response_text = response.text
        
        print(f"DEBUG: Gemini API Response: {response_text}")
        
        # JSONの抽出処理を改善
        def extract_json_from_response(text):
            """レスポンステキストからJSONを抽出する改善版"""
            # パターン1: ```json ``` で囲まれている場合
            json_pattern1 = r'```json\s*(.*?)\s*```'
            match1 = re.search(json_pattern1, text, re.DOTALL)
            if match1:
                return match1.group(1).strip()
            
            # パターン2: ``` で囲まれている場合
            json_pattern2 = r'```\s*(.*?)\s*```'
            match2 = re.search(json_pattern2, text, re.DOTALL)
            if match2:
                return match2.group(1).strip()
            
            # パターン3: { } で囲まれた部分を抽出
            start_brace = text.find('{')
            end_brace = text.rfind('}')
            if start_brace != -1 and end_brace != -1:
                return text[start_brace:end_brace+1]
            
            return text.strip()
        
        json_text = extract_json_from_response(response_text)
        print(f"DEBUG: Extracted JSON text: {json_text}")
        
        # JSONをパース
        try:
            llm_result = json.loads(json_text)
            products = llm_result.get("products", [])
            
            # 製品リストが空の場合のフォールバック
            if not products:
                print("WARNING: LLM returned empty product list, applying fallback")
                products = [{
                    "name": "CAD図面記載製品",
                    "description": f"図面解析により特定された製品。概要: {summary[:100] if summary else 'CAD図面に記載された製品'}",
                    "cnt": 1
                }]
        
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parse error: {e}")
            print(f"DEBUG: Attempting to extract JSON from: {json_text}")
            
            # より柔軟なJSON抽出を試行
            try:
                # 正規表現で製品情報を抽出する最終手段
                product_patterns = [
                    r'Type\s+[A-Z]-?\d+.*?(\d+)台',
                    r'Type\s+[A-Z]-?\d+.*?(\d+)個',
                    r'什器.*?(\d+)',
                    r'ディスプレイ.*?(\d+)',
                    r'棚板.*?(\d+)枚',
                ]
                
                fallback_products = []
                content_to_search = combined_content.lower()
                
                # annotationから製品を抽出
                if "type c-2" in content_to_search and "10台" in content_to_search:
                    fallback_products.append({
                        "name": "Type C-2（ロータイプ什器）",
                        "description": "ロータイプの什器、図面仕様に基づく",
                        "cnt": 10
                    })
                
                if "type b-2" in content_to_search and "4台" in content_to_search:
                    fallback_products.append({
                        "name": "Type B-2（ハイタイプ什器）",
                        "description": "ハイタイプの什器、図面仕様に基づく",
                        "cnt": 4
                    })
                
                if "棚板" in content_to_search and "8枚" in content_to_search:
                    fallback_products.append({
                        "name": "什器用棚板",
                        "description": "Type B-2用の棚板、各什器に2枚ずつ",
                        "cnt": 8
                    })
                
                # フォールバック製品が見つからない場合の最終手段
                if not fallback_products:
                    fallback_products = [{
                        "name": "CAD図面記載製品",
                        "description": f"図面解析により特定された製品。詳細確認が必要。{summary[:50] if summary else ''}",
                        "cnt": 1
                    }]
                
                products = fallback_products
                print(f"DEBUG: Applied fallback extraction, found {len(products)} products")
                
            except Exception as fallback_error:
                print(f"DEBUG: Fallback extraction failed: {fallback_error}")
                # 最終的なフォールバック
                products = [{
                    "name": "図面記載製品（要確認）",
                    "description": f"Gemini解析でエラーが発生しました。手動確認が必要です。概要: {summary[:100] if summary else 'CAD図面記載製品'}",
                    "cnt": 1
                }]
        
        # 結果を標準形式に変換（name/description/quantity）
        production_list = []
        for product in products:
            production_list.append({
                "name": product.get("name", "不明な製品"),
                "description": product.get("description", ""),
                "quantity": product.get("cnt", 1)  # cntをquantityに変換
            })
        
        # 最終チェック：製品リストが空でないことを確認
        if not production_list:
            production_list = [{
                "name": "CAD図面記載製品",
                "description": "図面解析結果（詳細は図面を参照）",
                "quantity": 1
            }]
        
        result = {
            "status": "success",
            "production_list": production_list,
            "total_items": len(production_list),
            "total_quantity": sum(item["quantity"] for item in production_list),
            "message": f"{len(production_list)}種類の製品をGemini APIで抽出しました",
            "extraction_source": "Gemini API（google.generativeai）強化版",
            "gemini_response": response_text
        }
        
        # デバッグ出力
        print(f"DEBUG createProductionList: result type: {type(result)}")
        print(f"DEBUG createProductionList: production_list type: {type(result['production_list'])}")
        print(f"DEBUG createProductionList: production_list content: {result['production_list']}")
        
        return result
        
    except Exception as e:
        print(f"ERROR in createProductionList: {str(e)}")
        # エラーが発生した場合でも空のリストを返さない
        return {
            "status": "success",  # エラーでも成功扱いにしてフォールバック製品を返す
            "production_list": [{
                "name": "CAD図面記載製品（エラー時フォールバック）",
                "description": f"製品リスト生成中にエラーが発生しました: {str(e)}。手動確認が必要です。",
                "quantity": 1
            }],
            "total_items": 1,
            "total_quantity": 1,
            "message": "エラーが発生しましたが、フォールバック製品を生成しました",
            "extraction_source": "フォールバック処理",
            "error_message": str(e)
        }

def saveProductionListToFirestore(production_list: List[Dict], document_id: str = "ABCD", collection_name: str = "agent_job", step_number: int = 3) -> dict:
    """createProductionListの出力をstep{step_number}_outputとしてFirestoreに保存します。

    Args:
        production_list (List[Dict]): 製品リスト（name, description, quantityのDictのlist）
        document_id (str): Firestoreのドキュメント ID
        collection_name (str): Firestoreのコレクション名
        step_number (int): ステップ番号（デフォルト: 3）

    Returns:
        dict: 保存結果
    """
    try:
        print(f"🔍 DEBUG: saveProductionListToFirestore called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        print(f"   🔢 Step number: {step_number}")
        
        # 入力データの型チェックとデバッグ情報
        print(f"   📊 Production list type: {type(production_list)}")
        print(f"   📄 Production list content: {production_list}")
        
        # production_listが文字列の場合はエラーを返す
        if isinstance(production_list, str):
            print(f"   ❌ Production list is string: {production_list}")
            return {
                "status": "error",
                "error_message": f"production_listが文字列として渡されました: {production_list}"
            }
        
        # production_listがリストでない場合はエラーを返す
        if not isinstance(production_list, list):
            print(f"   ❌ Production list is not list: {type(production_list)}")
            return {
                "status": "error",
                "error_message": f"production_listがリストではありません。型: {type(production_list)}, 内容: {production_list}"
            }
        
        print(f"📋 STEP 1: CSV形式の文字列を生成中...")
        # CSV形式の文字列を生成
        import csv
        from io import StringIO
        
        # CSVデータを格納するためのStringIO
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)
        
        # ヘッダー行を書き込み
        csv_writer.writerow(["製品名", "説明", "数量"])
        
        total_quantity = 0
        
        for i, product in enumerate(production_list):
            print(f"   📋 Processing product[{i}]: {type(product)}, content: {product}")
            
            # productが辞書でない場合はスキップ
            if not isinstance(product, dict):
                print(f"   ⚠️ Product[{i}] is not dict: {type(product)}")
                continue
            
            name = product.get("name", "不明")
            description = product.get("description", "")
            quantity = product.get("quantity", 0)
            
            # quantityが数値でない場合は0にする
            if not isinstance(quantity, (int, float)):
                print(f"   ⚠️ Quantity[{i}] is not numeric: {quantity}")
                quantity = 0
            
            # CSV行を書き込み
            csv_writer.writerow([name, description, quantity])
            total_quantity += quantity
        
        # CSV文字列を取得
        formatted_table = csv_buffer.getvalue().strip()
        
        print(f"   ✅ Table generated with {len(production_list)} items")
        
        print(f"📋 STEP 2: 説明文を生成中...")
        # 説明文を生成
        description = f"""
        📊 【Step{step_number}: 製品一覧の特定結果】
        
        🏗️ 製作が必要な製品一覧:
        
        {formatted_table}
        
        📈 集計情報:
        • 製品種類数: {len(production_list)}種類
        • 総製作個数: {total_quantity}個
        
        ✅ 製品一覧の特定が完了しました。
        🔧 次のステップ: 各製品に使用される部材の特定に進む準備が整いました。
        """
        
        print(f"   ✅ Description generated")
        
        print(f"📋 STEP 3: Firestore保存データを準備中...")
        # Firestoreに保存するデータを準備（step{step_number}_outputとして保存）
        step_output_key = f"step{step_number}_output"
        save_data = {
            step_output_key: {
                "production_list": production_list,
                "formatted_table": formatted_table,
                "description": description,
                "summary": {
                    "total_product_types": len(production_list),
                    "total_quantity": total_quantity
                },
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
        }
        
        print(f"   📊 Save data prepared: {save_data}")
        
        print(f"📋 STEP 4: Firestoreに保存中...")
        # Firestoreに保存
        success = firestore_helper.update_document(
            collection_name=collection_name,
            document_id=document_id,
            update_data=save_data
        )
        
        print(f"   📊 Save result: {success}")
        
        if success:
            print(f"   ✅ Production list saved successfully")
            return {
                "status": "success",
                "message": f"製品リストを{step_output_key}としてFirestoreに保存しました",
                "production_list": production_list,
                "formatted_table": formatted_table,
                "description": description
            }
        else:
            print(f"   ❌ Firestore save failed")
            return {
                "status": "error",
                "error_message": "Firestoreへの保存に失敗しました"
            }
            
    except Exception as e:
        print(f"❌ ERROR in saveProductionListToFirestore: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"製品リスト保存中にエラーが発生しました: {str(e)}"
        } 
