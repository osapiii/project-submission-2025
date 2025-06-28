import json
import os
import sys
import re
from datetime import datetime
from typing import Dict, Any, List
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

# 部品カテゴリ別の単価データベース（円/個）
PARTS_UNIT_PRICE_DATABASE = {
    "金属部品": {
        "フレーム": {"small": 800, "medium": 1500, "large": 2500},
        "支柱": {"small": 600, "medium": 1200, "large": 2000},
        "ブラケット": {"small": 300, "medium": 600, "large": 1000},
        "ネジ": {"small": 50, "medium": 80, "large": 120},
        "ボルト": {"small": 80, "medium": 150, "large": 250},
        "ナット": {"small": 30, "medium": 50, "large": 80},
        "ワッシャー": {"small": 20, "medium": 30, "large": 50},
        "アングル": {"small": 400, "medium": 800, "large": 1400},
        "プレート": {"small": 500, "medium": 1000, "large": 1800},
        "パイプ": {"small": 300, "medium": 600, "large": 1200},
        "default": 500
    },
    "樹脂部品": {
        "パネル": {"small": 1200, "medium": 2500, "large": 4500},
        "カバー": {"small": 800, "medium": 1600, "large": 2800},
        "棚板": {"small": 1500, "medium": 3000, "large": 5500},
        "装飾部品": {"small": 600, "medium": 1200, "large": 2200},
        "キャップ": {"small": 100, "medium": 200, "large": 350},
        "ガイド": {"small": 300, "medium": 600, "large": 1100},
        "ストッパー": {"small": 200, "medium": 400, "large": 700},
        "default": 800
    },
    "電子部品": {
        "LED": {"small": 500, "medium": 1000, "large": 2000},
        "配線": {"small": 200, "medium": 400, "large": 800},
        "スイッチ": {"small": 800, "medium": 1500, "large": 2500},
        "コネクタ": {"small": 300, "medium": 600, "large": 1200},
        "基板": {"small": 2000, "medium": 4000, "large": 8000},
        "default": 1000
    },
    "ガラス・アクリル": {
        "ガラス板": {"small": 2000, "medium": 4000, "large": 8000},
        "アクリル板": {"small": 1500, "medium": 3000, "large": 6000},
        "透明パネル": {"small": 1800, "medium": 3600, "large": 7200},
        "default": 2500
    },
    "その他": {
        "ゴム部品": {"small": 150, "medium": 300, "large": 600},
        "シール": {"small": 100, "medium": 200, "large": 400},
        "クッション": {"small": 200, "medium": 400, "large": 800},
        "default": 300
    },
    "default": 500
}

def estimate_part_unit_price(part_name: str, category: str, material: str = "", description: str = "") -> int:
    """部品名、カテゴリ、材質から単価を推定します。
    
    Args:
        part_name (str): 部品名
        category (str): 部品カテゴリ
        material (str): 材質
        description (str): 部品説明
        
    Returns:
        int: 推定単価（円）
    """
    try:
        # カテゴリ別の価格データを取得
        category_prices = PARTS_UNIT_PRICE_DATABASE.get(category, PARTS_UNIT_PRICE_DATABASE["default"])
        
        if isinstance(category_prices, dict):
            # 部品名から具体的な価格を検索
            for part_type, prices in category_prices.items():
                if part_type.lower() in part_name.lower():
                    if isinstance(prices, dict):
                        # サイズ推定（説明文や部品名から）
                        text_to_check = f"{part_name} {description} {material}".lower()
                        if any(keyword in text_to_check for keyword in ["大", "large", "big", "長い", "厚い"]):
                            return prices.get("large", prices.get("default", category_prices.get("default", 500)))
                        elif any(keyword in text_to_check for keyword in ["小", "small", "mini", "短い", "薄い"]):
                            return prices.get("small", prices.get("default", category_prices.get("default", 500)))
                        else:
                            return prices.get("medium", prices.get("default", category_prices.get("default", 500)))
                    else:
                        return prices
            
            # 具体的な部品が見つからない場合はカテゴリのデフォルト価格
            return category_prices.get("default", PARTS_UNIT_PRICE_DATABASE["default"])
        else:
            return category_prices
            
    except Exception as e:
        print(f"DEBUG: 単価推定エラー: {e}")
        return PARTS_UNIT_PRICE_DATABASE["default"]

def getStep3Output(document_id: str = "ABCD", collection_name: str = "agent_job") -> dict:
    """Step3の製品リスト結果をFirestoreから取得します。

    Args:
        document_id (str): Firestoreのドキュメント ID
        collection_name (str): Firestoreのコレクション名

    Returns:
        dict: Step3の結果データ
    """
    try:
        print(f"🔍 DEBUG: getStep3Output called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        
        # Firestoreからドキュメントを取得
        doc = firestore_helper.get_document(
            collection_name=collection_name,
            document_id=document_id
        )
        
        print(f"🔍 DEBUG: Firestore取得結果")
        print(f"   📄 Document exists: {doc is not None}")
        
        if not doc or 'step3_output' not in doc:
            print(f"   ❌ Document or 'step3_output' field not found")
            if doc:
                print(f"   🔍 Available fields: {list(doc.keys()) if isinstance(doc, dict) else 'Not a dict'}")
            return {
                "status": "error",
                "error_message": f"Step3の結果が見つかりません。先にStep3を実行してください。利用可能なフィールド: {list(doc.keys()) if doc and isinstance(doc, dict) else 'Not a dict'}"
            }
        
        print(f"   ✅ 'step3_output' field found")
        step3_output = doc['step3_output']
        print(f"   📋 Step3 output keys: {list(step3_output.keys()) if isinstance(step3_output, dict) else 'Not a dict'}")
        
        production_list = step3_output.get('production_list', [])
        print(f"   📊 Production list length: {len(production_list)}")
        
        return {
            "status": "success",
            "step3_output": step3_output,
            "production_list": production_list,
            "message": f"Step3の結果を取得しました（{len(production_list)}製品）"
        }
        
    except Exception as e:
        print(f"❌ ERROR in getStep3Output: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"Step3結果取得中にエラーが発生しました: {str(e)}"
        }

def createPartsBreakdown(production_list: List[Dict], analysis_json: dict, download_url: str, user_instructions: str = "") -> dict:
    """Gemini APIを使用して製品リストから部品一覧を生成します。

    Args:
        production_list (List[Dict]): Step3で生成された製品リスト
        analysis_json (dict): Step2で取得したanalysis.jsonデータ
        download_url (str): Step1で生成されたPDFダウンロードURL
        user_instructions (str): ユーザーからの追加指示

    Returns:
        dict: 生成された部品一覧
    """
    try:
        import google.generativeai as genai
        
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
        
        # ページ情報を整理
        pages_info = []
        for i, page in enumerate(pages, 1):
            pages_info.append({
                "page_number": i,
                "summary": page.get("summary", ""),
                "content": page.get("content", "")
            })
        
        # 製品リストを整理
        products_info = []
        for product in production_list:
            products_info.append({
                "name": product.get("name", ""),
                "description": product.get("description", ""),
                "quantity": product.get("quantity", 0)
            })
        
        # Geminiモデルを初期化gemini-2.5
        model = genai.GenerativeModel(
            'gemini-2.0-flash-exp'
        )
        
        # プロンプトを構築
        prompt = f"""
あなたは製造業の部品設計・見積もりの専門家です。以下の情報から各製品に使用される部品一覧を詳細に分解し、単価と合計金額も算出してください：

【入力情報】
1. 製品リスト:
{json.dumps(products_info, ensure_ascii=False, indent=2)}

2. Analysis JSON データ:
   - 概要: {summary}
   - 注釈: {annotation}
   - ページ情報: {json.dumps(pages_info, ensure_ascii=False, indent=2)}

3. PDFダウンロードURL: {download_url}

4. ユーザー指示: {user_instructions if user_instructions else "なし"}

【出力要件】
以下の厳密なJSON形式で部品一覧を出力してください：

```json
{{
  "parts_breakdown": [
    {{
      "product_name": "製品名",
      "product_quantity": 製品数量,
      "parts": [
        {{
          "part_name": "部品名",
          "part_description": "部品の詳細説明",
          "unit_quantity": 1製品あたりの使用個数,
          "total_quantity": 総使用個数,
          "material": "材質・仕様",
          "category": "部品カテゴリ（例：金属部品、樹脂部品、電子部品等）",
          "estimated_unit_price": 推定単価（円）,
          "total_price": 総金額（円）
        }}
      ]
    }}
  ]
}}
```

【分解ルール】
1. 各製品を構成する主要部品に分解する
2. 金属部品（フレーム、ブラケット、ネジ等）、樹脂部品（パネル、カバー等）、その他部品を含める
3. 1製品あたりの使用個数と総使用個数を正確に計算する
4. 材質や仕様も可能な限り推定して記載する
5. 見積もり作成に必要な詳細レベルで分解する
6. 図面情報から読み取れる寸法や仕様も考慮する
7. ユーザー指示がある場合は優先的に反映する

【部品カテゴリ例】
- 金属部品: フレーム、支柱、ブラケット、ネジ、ボルト等
- 樹脂部品: パネル、カバー、棚板、装飾部品等
- 電子部品: LED、配線、スイッチ等（該当する場合）
- ガラス・アクリル: ガラス板、アクリル板、透明パネル等
- その他: ゴム部品、シール、クッション等

【単価推定ガイドライン】
- 金属部品: ネジ類50-120円、ブラケット300-1000円、フレーム800-2500円
- 樹脂部品: キャップ100-350円、パネル1200-4500円、棚板1500-5500円
- 電子部品: LED500-2000円、配線200-800円、基板2000-8000円
- ガラス・アクリル: 1500-8000円（サイズにより）
- その他: 100-800円程度

部品のサイズや複雑さを考慮して適切な単価を設定し、total_price = total_quantity × estimated_unit_priceで計算してください。

必ずJSON形式のみで回答してください。説明文は不要です。
        """
        
        # Gemini APIに部品分解を依頼
        response = model.generate_content(prompt)
        response_text = response.text
        
        print(f"DEBUG: Gemini API Response for parts breakdown: {response_text}")
        
        # JSONの抽出（```json ``` で囲まれている場合の処理）
        json_start = response_text.find('```json')
        json_end = response_text.find('```', json_start + 7)
        
        if json_start != -1 and json_end != -1:
            json_text = response_text[json_start + 7:json_end].strip()
        else:
            # 直接JSONが返された場合
            json_text = response_text.strip()
            # 先頭と末尾の```を除去
            if json_text.startswith('```'):
                json_text = json_text[3:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            json_text = json_text.strip()
        
        # JSONをパース
        try:
            llm_result = json.loads(json_text)
            parts_breakdown = llm_result.get("parts_breakdown", [])
            
            # 単価データベースを使用して単価を補正・検証
            for product in parts_breakdown:
                if isinstance(product, dict) and "parts" in product:
                    for part in product["parts"]:
                        if isinstance(part, dict):
                            # Geminiが単価を設定していない場合、またはデータベースで補正
                            part_name = part.get("part_name", "")
                            category = part.get("category", "その他")
                            material = part.get("material", "")
                            description = part.get("part_description", "")
                            total_quantity = part.get("total_quantity", 0)
                            
                            # データベースから推定単価を取得
                            estimated_price = estimate_part_unit_price(part_name, category, material, description)
                            
                            # Geminiの単価が設定されていない場合、またはデータベースの値で補正
                            gemini_price = part.get("estimated_unit_price", 0)
                            if gemini_price == 0 or abs(gemini_price - estimated_price) > estimated_price * 0.5:
                                # Geminiの価格が0または推定価格と50%以上乖離している場合は補正
                                part["estimated_unit_price"] = estimated_price
                                part["price_source"] = "database_corrected"
                            else:
                                part["estimated_unit_price"] = gemini_price
                                part["price_source"] = "gemini_estimated"
                            
                            # 総金額を再計算
                            part["total_price"] = part["estimated_unit_price"] * total_quantity
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parse error: {e}")
            print(f"DEBUG: Attempting to extract JSON from: {json_text}")
            
            # より柔軟なJSON抽出を試行
            try:
                # { で始まり } で終わる部分を抽出
                start_brace = json_text.find('{')
                end_brace = json_text.rfind('}')
                if start_brace != -1 and end_brace != -1:
                    json_text = json_text[start_brace:end_brace+1]
                    llm_result = json.loads(json_text)
                    parts_breakdown = llm_result.get("parts_breakdown", [])
                else:
                    raise json.JSONDecodeError("No valid JSON found", json_text, 0)
            except json.JSONDecodeError:
                # フォールバック: 基本的な部品リストを生成
                parts_breakdown = [{
                    "product_name": "部品分解エラー",
                    "product_quantity": 1,
                    "parts": [{
                        "part_name": "分解不可部品（Gemini解析エラー）",
                        "part_description": f"Gemini APIによる部品分解でエラーが発生しました。手動確認が必要です。",
                        "unit_quantity": 1,
                        "total_quantity": 1,
                        "material": "不明",
                        "category": "その他",
                        "estimated_unit_price": 500,
                        "total_price": 500,
                        "price_source": "fallback_default"
                    }]
                }]
        
        # 統計情報を計算
        total_products = len(parts_breakdown)
        total_parts_types = sum(len(product.get("parts", [])) for product in parts_breakdown)
        total_parts_quantity = sum(
            sum(part.get("total_quantity", 0) for part in product.get("parts", []))
            for product in parts_breakdown
        )
        total_estimated_cost = sum(
            sum(part.get("total_price", 0) for part in product.get("parts", []))
            for product in parts_breakdown
        )
        
        result = {
            "status": "success",
            "parts_breakdown": parts_breakdown,
            "total_products": total_products,
            "total_parts_types": total_parts_types,
            "total_parts_quantity": total_parts_quantity,
            "total_estimated_cost": total_estimated_cost,
            "message": f"{total_products}製品を{total_parts_types}種類の部品に分解しました（推定総額: ¥{total_estimated_cost:,}）",
            "extraction_source": "Gemini API（google.generativeai）+ 単価データベース補正",
            "gemini_response": response_text
        }
        
        # デバッグ出力
        print(f"DEBUG createPartsBreakdown: result type: {type(result)}")
        print(f"DEBUG createPartsBreakdown: parts_breakdown type: {type(result['parts_breakdown'])}")
        print(f"DEBUG createPartsBreakdown: parts_breakdown content: {result['parts_breakdown']}")
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"部品分解中にエラーが発生しました: {str(e)}"
        }

def savePartsBreakdownToFirestore(parts_breakdown: List[Dict], document_id: str = "ABCD", collection_name: str = "agent_job", step_number: int = 4) -> dict:
    """createPartsBreakdownの出力を動的なstep_outputとしてFirestoreに保存します。

    Args:
        parts_breakdown (List[Dict]): 部品分解リスト
        document_id (str): Firestoreのドキュメント ID
        collection_name (str): Firestoreのコレクション名
        step_number (int): ステップ番号（デフォルト: 4）

    Returns:
        dict: 保存結果
    """
    try:
        print(f"🔍 DEBUG: savePartsBreakdownToFirestore called")
        print(f"   📁 Collection: {collection_name}")
        print(f"   🆔 Document ID: {document_id}")
        
        # 入力データの型チェックとデバッグ情報
        print(f"   📊 Parts breakdown type: {type(parts_breakdown)}")
        print(f"   📄 Parts breakdown content: {parts_breakdown}")
        
        # parts_breakdownが文字列の場合はエラーを返す
        if isinstance(parts_breakdown, str):
            print(f"   ❌ Parts breakdown is string: {parts_breakdown}")
            return {
                "status": "error",
                "error_message": f"parts_breakdownが文字列として渡されました: {parts_breakdown}"
            }
        
        # parts_breakdownがリストでない場合はエラーを返す
        if not isinstance(parts_breakdown, list):
            print(f"   ❌ Parts breakdown is not list: {type(parts_breakdown)}")
            return {
                "status": "error",
                "error_message": f"parts_breakdownがリストではありません。型: {type(parts_breakdown)}, 内容: {parts_breakdown}"
            }
        
        print(f"📋 STEP 1: 表形式の文字列を生成中...")
        # 表形式の文字列を生成
        table_header = "| 製品名 | 部品名 | 部品説明 | 単位使用数 | 総使用数 | 単価(円) | 合計金額(円) | 材質 | カテゴリ |"
        table_separator = "|--------|--------|----------|------------|----------|----------|-------------|------|----------|"
        
        table_rows = []
        total_parts_types = 0
        total_parts_quantity = 0
        total_estimated_cost = 0
        
        for product in parts_breakdown:
            if not isinstance(product, dict):
                continue
                
            product_name = product.get("product_name", "不明製品")
            product_quantity = product.get("product_quantity", 0)
            parts = product.get("parts", [])
            
            for part in parts:
                if not isinstance(part, dict):
                    continue
                    
                part_name = part.get("part_name", "不明部品")
                part_description = part.get("part_description", "")
                unit_quantity = part.get("unit_quantity", 0)
                total_quantity = part.get("total_quantity", 0)
                unit_price = part.get("estimated_unit_price", 0)
                total_price = part.get("total_price", 0)
                material = part.get("material", "不明")
                category = part.get("category", "その他")
                
                table_rows.append(f"| {product_name} | {part_name} | {part_description} | {unit_quantity} | {total_quantity} | ¥{unit_price:,} | ¥{total_price:,} | {material} | {category} |")
                total_parts_types += 1
                total_parts_quantity += total_quantity
                total_estimated_cost += total_price
        
        # 完全な表を組み立て
        formatted_table = "\n".join([
            table_header,
            table_separator
        ] + table_rows)
        
        print(f"   ✅ Table generated with {len(table_rows)} rows")
        
        print(f"📋 STEP 2: 説明文を生成中...")
        # 説明文を生成
        description = f"""
        📊 【Step{step_number}: 部品一覧の分解結果（単価・合計金額付き）】
        
        🔧 各製品の部品内訳:
        
        {formatted_table}
        
        📈 集計情報:
        • 対象製品数: {len(parts_breakdown)}製品
        • 部品種類数: {total_parts_types}種類
        • 総部品個数: {total_parts_quantity}個
        • 推定総額: ¥{total_estimated_cost:,}
        
        💰 単価算出方法:
        • Gemini AIによる推定 + 部品データベースによる補正
        • 部品カテゴリ・サイズ・材質を考慮した価格設定
        
        ✅ 部品一覧の分解と見積もりが完了しました。
        📋 次のステップ: 見積書の作成に進む準備が整いました。
        """
        
        print(f"   ✅ Description generated")
        
        print(f"📋 STEP 3: Firestore保存データを準備中...")
        # Firestoreに保存するデータを準備（動的なstep_outputとして保存）
        step_output_key = f"step{step_number}_output"
        save_data = {
            step_output_key: {
                "parts_breakdown": parts_breakdown,
                "formatted_table": formatted_table,
                "description": description,
                "summary": {
                    "total_products": len(parts_breakdown),
                    "total_parts_types": total_parts_types,
                    "total_parts_quantity": total_parts_quantity,
                    "total_estimated_cost": total_estimated_cost
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
            print(f"   ✅ Parts breakdown saved successfully")
            return {
                "status": "success",
                "message": f"部品一覧を{step_output_key}としてFirestoreに保存しました",
                "parts_breakdown": parts_breakdown,
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
        print(f"❌ ERROR in savePartsBreakdownToFirestore: {str(e)}")
        print(f"   🔍 Exception type: {type(e)}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error_message": f"部品一覧保存中にエラーが発生しました: {str(e)}"
        } 