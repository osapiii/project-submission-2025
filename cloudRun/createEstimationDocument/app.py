import os
import sys
import tempfile
import subprocess
import logging
import json
from datetime import datetime
# Google Cloud Storage クライアント
from google.cloud import storage
# Flask ウェブフレームワーク
from flask import Flask, request, jsonify
from pdf2image import convert_from_path
# 新規追加
import google.generativeai as genai
from jinja2 import Template
import pdfkit
# 環境変数読み込み用
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# ロガーの設定
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Flask アプリケーションを作成します
app = Flask(__name__)

# GCS クライアントはアプリケーション起動時に一度だけ作成します
storage_client = storage.Client()

# Gemini APIの設定
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    logger.warning("GEMINI_API_KEY environment variable not set. Gemini API features will be disabled.")
    model = None
else:
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            location="us-central1"
        )
        logger.info("Gemini API configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        model = None

# LibreOfficeの実行可能ファイル名 (環境によって 'libreoffice' または 'soffice')

@app.route('/convert-pdf-to-png', methods=['POST'])
def convert_pdf_to_png_endpoint():
    """
    HTTP POSTリクエストを受け付け、指定されたGCS上のPDFファイルの1ページ目を
    PNGに変換し、結果をGCSに保存します。
    リクエストボディは以下のJSON形式を期待します:
    {
        "bucket_name": "your-gcs-bucket-name",
        "gcsInputPdfFilePath": "input/path/to/document.pdf",
        "gcsOutputPreviewPngFilePath": "output/path/to/preview.png"
    }
    """
    logger.info(f"Received request: {request.url} {request.method}")

    request_data = request.get_json()
    required_fields = ['bucket_name', 'gcsInputPdfFilePath', 'gcsOutputPreviewPngFilePath']
    
    if not request_data:
        logger.error("Error: Request body is empty or not valid JSON.")
        return jsonify({"status": "error", "message": "Request body must be valid JSON"}), 400
        
    for field in required_fields:
        if field not in request_data or not request_data[field]:
            logger.error(f"Error: Missing required field: {field}")
            return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400

    bucket_name = request_data['bucket_name']
    input_gcs_path = request_data['gcsInputPdfFilePath']
    output_gcs_path = request_data['gcsOutputPreviewPngFilePath']

    logger.info(f"Conversion task: bucket={bucket_name}, input={input_gcs_path}, output={output_gcs_path}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        logger.info(f"Created temporary directory: {tmp_dir}")
        
        input_local_path = None
        output_local_path = None
        
        try:
            bucket = storage_client.bucket(bucket_name)
            logger.info(f"Connected to GCS bucket: {bucket_name}")

            # 1. PDFファイルをGCSから一時ディレクトリにダウンロード
            input_blob = bucket.blob(input_gcs_path)
            if not input_blob.exists():
                logger.error(f"Error: Input file not found in GCS: {input_gcs_path}")
                return jsonify({"status": "error", "message": f"Input file not found in GCS: {input_gcs_path}"}), 404

            input_filename = os.path.basename(input_gcs_path)
            input_local_path = os.path.join(tmp_dir, input_filename)
            input_blob.download_to_filename(input_local_path)
            logger.info(f"Downloaded GCS file {input_gcs_path} to {input_local_path}")

            # 2. PDFの1ページ目をPNGに変換
            output_filename = os.path.basename(output_gcs_path)
            output_local_path = os.path.join(tmp_dir, output_filename)
            
            # PDFの1ページ目をPNGに変換
            images = convert_from_path(input_local_path, first_page=1, last_page=1)
            if not images:
                raise RuntimeError("Failed to convert PDF to PNG")
            
            # 変換された画像を保存
            images[0].save(output_local_path, 'PNG')
            logger.info(f"Converted PDF to PNG: {output_local_path}")

            # 3. 変換されたPNGファイルをGCSにアップロード
            output_blob = bucket.blob(output_gcs_path)
            output_blob.upload_from_filename(output_local_path)
            logger.info(f"Uploaded converted PNG {output_local_path} to GCS {output_gcs_path}")

            return jsonify({
                "status": "success",
                "input_gcs_path": input_gcs_path,
                "output_gcs_path": output_gcs_path,
                "message": "PDF successfully converted to PNG and uploaded to GCS."
            }), 200

        except Exception as e:
            logger.error(f"An error occurred during conversion: {e}")
            return jsonify({
                "status": "error",
                "message": f"Conversion failed: {str(e)}"
            }), 500

@app.route('/create-estimate-document', methods=['POST'])
def create_organizationIdt_endpoint():
    """
    見積書と部品明細書を生成し、PDFに変換してGCSに保存します。
    リクエストボディは以下のJSON形式を期待します:
    {
        "estimateData": {
            "totalPrice": 150000,
            "products": [
                {"productName": "商品A", "quantity": 2, "price": 50000}
            ]
        },
        "partsBreakdown": [
            {
                "product_name": "商品A",
                "product_quantity": 2,
                "parts": [
                    {
                        "category": "金属部品",
                        "part_name": "フレーム",
                        "part_description": "本体フレーム（スチール製）",
                        "material": "スチール",
                        "unit_quantity": 1,
                        "total_quantity": 2,
                        "estimated_unit_price": 2000,
                        "total_price": 4000,
                        "price_source": "gemini_estimated"
                    }
                ]
            }
        ],
        "bucket_name": "your-gcs-bucket-name",
        "parentFolderPath": "estimates/project_001/"
    }
    """
    logger.info(f"Received request: {request.url} {request.method}")

    request_data = request.get_json()
    required_fields = ['estimateData', 'partsBreakdown', 'bucket_name', 'parentFolderPath']
    
    if not request_data:
        logger.error("Error: Request body is empty or not valid JSON.")
        return jsonify({"status": "error", "message": "Request body must be valid JSON"}), 400
        
    for field in required_fields:
        if field not in request_data:
            logger.error(f"Error: Missing required field: {field}")
            return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400

    estimate_data = request_data['estimateData']
    parts_breakdown = request_data['partsBreakdown']
    bucket_name = request_data['bucket_name']
    parent_folder_path = request_data['parentFolderPath'].rstrip('/')

    # 出力ファイルパスを構築
    estimate_gcs_path = f"{parent_folder_path}/estimation.pdf"
    inner_gcs_path = f"{parent_folder_path}/inner.pdf"

    logger.info(f"Document generation task: bucket={bucket_name}, folder={parent_folder_path}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        logger.info(f"Created temporary directory: {tmp_dir}")
        
        try:
            bucket = storage_client.bucket(bucket_name)
            logger.info(f"Connected to GCS bucket: {bucket_name}")

            # 1. 見積書HTMLを生成
            estimate_html = generate_html_with_gemini(estimate_data)
            estimate_html_path = os.path.join(tmp_dir, "estimation.html")
            with open(estimate_html_path, 'w', encoding='utf-8') as f:
                f.write(estimate_html)
            logger.info("Generated estimate HTML")

            # 2. 部品明細書HTMLを生成
            inner_html = generate_parts_breakdown_html_with_gemini(parts_breakdown)
            inner_html_path = os.path.join(tmp_dir, "inner.html")
            with open(inner_html_path, 'w', encoding='utf-8') as f:
                f.write(inner_html)
            logger.info("Generated parts breakdown HTML")

            # 3. HTMLをPDFに変換
            pdf_options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }
            
            # 見積書PDF
            estimate_pdf_path = os.path.join(tmp_dir, "estimation.pdf")
            pdfkit.from_file(estimate_html_path, estimate_pdf_path, options=pdf_options)
            logger.info("Converted estimate HTML to PDF")

            # 部品明細書PDF
            inner_pdf_path = os.path.join(tmp_dir, "inner.pdf")
            pdfkit.from_file(inner_html_path, inner_pdf_path, options=pdf_options)
            logger.info("Converted parts breakdown HTML to PDF")

            # 4. PDFファイルをGCSにアップロード
            # 見積書PDF
            estimate_blob = bucket.blob(estimate_gcs_path)
            estimate_blob.upload_from_filename(estimate_pdf_path)
            logger.info(f"Uploaded estimate PDF to GCS: {estimate_gcs_path}")

            # 部品明細書PDF
            inner_blob = bucket.blob(inner_gcs_path)
            inner_blob.upload_from_filename(inner_pdf_path)
            logger.info(f"Uploaded parts breakdown PDF to GCS: {inner_gcs_path}")

            return jsonify({
                "status": "success",
                "estimate_gcs_path": estimate_gcs_path,
                "inner_gcs_path": inner_gcs_path,
                "message": "Both estimate and parts breakdown documents successfully generated and uploaded to GCS."
            }), 200

        except Exception as e:
            logger.error(f"An error occurred during document generation: {e}")
            return jsonify({
                "status": "error",
                "message": f"Document generation failed: {str(e)}"
            }), 500


def generate_html_with_gemini(estimate_data):
    """
    Gemini APIを使用して見積書のHTMLを動的生成する
    """
    logger.info("Starting HTML generation with Gemini API")
    
    # template.htmlを読み込み
    template_path = os.path.join(os.path.dirname(__file__), 'template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Gemini用のプロンプトを作成
    prompt = f"""
以下のHTMLテンプレートと見積書データを使用して、完全なHTMLドキュメントを生成してください。

【HTMLテンプレート】
{template_content}

【見積書データ】
{json.dumps(estimate_data, ensure_ascii=False, indent=2)}

【指示】
1. テンプレートのJinja2変数を実際の値に置き換えてください
2. estimate_data.products配列の各要素を明細行として表示してください
3. 合計金額はestimate_data.totalPriceを使用してください
4. 発行日は今日の日付を使用してください
5. 発行者情報は以下のデフォルト値を使用してください：
   - 会社名: "株式会社サンプル"
   - 住所: "〒100-0001 東京都千代田区千代田1-1-1"
   - 電話: "03-1234-5678"
   - メール: "info@sample.co.jp"
6. 顧客情報は以下のデフォルト値を使用してください：
   - 会社名: "お客様会社名"
   - 担当者: "ご担当者"
   - 住所: "〒000-0000 住所未設定"
7. 支払条件: "月末締め翌月末払い"
8. 有効期限: "発行日から30日間"
9. 備考: "ご不明な点がございましたらお気軽にお問い合わせください。"

完全なHTMLドキュメントのみを返してください。説明や追加のテキストは不要です。
"""

    try:
        response = model.generate_content(prompt)
        html_content = response.text
        
        # HTMLタグで囲まれていない場合の処理
        if not html_content.strip().startswith('<!DOCTYPE html>'):
            # コードブロックから抽出
            if '```html' in html_content:
                html_content = html_content.split('```html')[1].split('```')[0].strip()
            elif '```' in html_content:
                html_content = html_content.split('```')[1].split('```')[0].strip()
        
        logger.info("HTML generation completed successfully")
        return html_content
        
    except Exception as e:
        logger.error(f"Error generating HTML with Gemini: {e}")
        # フォールバック: 簡単なテンプレート処理
        return generate_html_fallback(estimate_data)


def generate_html_fallback(estimate_data):
    """
    Gemini APIが失敗した場合のフォールバック処理
    """
    logger.info("Using fallback HTML generation")
    
    # 現在の日付
    current_date = datetime.now().strftime('%Y年%m月%d日')
    
    # 明細行の生成
    items_html = ""
    for product in estimate_data['products']:
        items_html += f"""
        <tr>
            <td>{product['productName']}</td>
            <td class="text-right">{product['quantity']}</td>
            <td class="text-right">¥{product['price']:,}</td>
            <td class="text-right">¥{product['quantity'] * product['price']:,}</td>
        </tr>
        """
    
    # 空白行の追加（最大12行まで）
    for i in range(12 - len(estimate_data['products'])):
        items_html += """
        <tr>
            <td>&nbsp;</td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        """
    
    # 小計、消費税、合計の計算
    subtotal = estimate_data['totalPrice']
    tax = int(subtotal * 0.1)  # 10%の消費税
    total = subtotal + tax
    
    # HTMLテンプレートの読み込みと置換
    template_path = os.path.join(os.path.dirname(__file__), 'template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 簡単な文字列置換
    html_content = template_content.replace('{{ client.zip_code }}', '〒000-0000')
    html_content = html_content.replace('{{ client.address_line1 }}', '住所未設定')
    html_content = html_content.replace('{{ client.address_line2 }}', '')
    html_content = html_content.replace('{{ client.name }}', 'お客様会社名')
    html_content = html_content.replace('{{ client.contact_person }}', 'ご担当者')
    html_content = html_content.replace('{{ issue_date }}', current_date)
    html_content = html_content.replace('{{ quote_number }}', 'EST-001')
    html_content = html_content.replace('{{ issuer.name }}', '株式会社サンプル')
    html_content = html_content.replace('{{ issuer.zip_code }}', '〒100-0001')
    html_content = html_content.replace('{{ issuer.address }}', '東京都千代田区千代田1-1-1')
    html_content = html_content.replace('{{ issuer.tel }}', '03-1234-5678')
    html_content = html_content.replace('{{ issuer.email }}', 'info@sample.co.jp')
    html_content = html_content.replace('{{ calculations.total | currency }}', f'{total:,}')
    html_content = html_content.replace('{{ payment_terms }}', '月末締め翌月末払い')
    html_content = html_content.replace('{{ due_date }}', '発行日から30日間')
    html_content = html_content.replace('{{ calculations.subtotal | currency }}', f'{subtotal:,}')
    html_content = html_content.replace('{{ calculations.tax | currency }}', f'{tax:,}')
    html_content = html_content.replace('{{ notes }}', 'ご不明な点がございましたらお気軽にお問い合わせください。')
    
    # Jinja2のfor文を削除して明細行を直接挿入
    items_section_start = html_content.find('<!-- 明細行 -->')
    items_section_end = html_content.find('<!-- 空白行（テーブルの高さを一定に保つため） -->')
    
    if items_section_start != -1 and items_section_end != -1:
        before_items = html_content[:items_section_start]
        after_items = html_content[items_section_end:]
        
        # 空白行セクションの終了位置を見つける
        empty_rows_end = after_items.find('<!-- 合計欄 -->')
        if empty_rows_end != -1:
            after_items = after_items[empty_rows_end:]
        
        html_content = before_items + f"<!-- 明細行 -->\n{items_html}\n" + after_items
    
    return html_content

def generate_parts_breakdown_html_with_gemini(parts_breakdown):
    """
    Gemini APIを使用して部品明細書のHTMLを動的生成する
    """
    logger.info("Starting parts breakdown HTML generation with Gemini API")
    
    # template2.htmlを読み込み
    template_path = os.path.join(os.path.dirname(__file__), 'template2.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Gemini用のプロンプトを作成
    prompt = f"""
以下のHTMLテンプレートと部品明細データを使用して、完全なHTMLドキュメントを生成してください。

【HTMLテンプレート】
{template_content}

【部品明細データ】
{json.dumps(parts_breakdown, ensure_ascii=False, indent=2)}

【指示】
1. テンプレートのJinja2変数を実際の値に置き換えてください
2. parts_breakdown配列の各要素を製品セクションとして表示してください
3. 各製品の部品配列を明細テーブルとして表示してください
4. 発行日は今日の日付を使用してください
5. 発行者情報は以下のデフォルト値を使用してください：
   - 会社名: "株式会社サンプル"
   - 住所: "〒100-0001 東京都千代田区千代田1-1-1"
   - 電話: "03-1234-5678"
   - メール: "info@sample.co.jp"
6. 文書番号: "PARTS-001"
7. 関連見積書: "EST-001"
8. price_source: "AI推定価格"

完全なHTMLドキュメントのみを返してください。説明や追加のテキストは不要です。
"""

    try:
        response = model.generate_content(prompt)
        html_content = response.text
        
        # HTMLタグで囲まれていない場合の処理
        if not html_content.strip().startswith('<!DOCTYPE html>'):
            # コードブロックから抽出
            if '```html' in html_content:
                html_content = html_content.split('```html')[1].split('```')[0].strip()
            elif '```' in html_content:
                html_content = html_content.split('```')[1].split('```')[0].strip()
        
        logger.info("Parts breakdown HTML generation completed successfully")
        return html_content
        
    except Exception as e:
        logger.error(f"Error generating parts breakdown HTML with Gemini: {e}")
        # フォールバック: 簡単なテンプレート処理
        return generate_parts_breakdown_html_fallback(parts_breakdown)


def generate_parts_breakdown_html_fallback(parts_breakdown):
    """
    Gemini APIが失敗した場合の部品明細書フォールバック処理
    """
    logger.info("Using fallback parts breakdown HTML generation")
    
    # 現在の日付
    current_date = datetime.now().strftime('%Y年%m月%d日')
    
    # HTMLテンプレートの読み込み
    template_path = os.path.join(os.path.dirname(__file__), 'template2.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 製品セクションの生成
    products_html = ""
    for i, product in enumerate(parts_breakdown):
        page_break_class = "page-break" if i > 0 else ""
        
        # 部品テーブルの生成
        parts_rows = ""
        total_price = 0
        for part in product.get('parts', []):
            category_class = ""
            if part.get('category') == '金属部品':
                category_class = "category-metal"
            elif part.get('category') == '樹脂部品':
                category_class = "category-resin"
            elif part.get('category') == '電子部品':
                category_class = "category-electronic"
            else:
                category_class = "category-other"
            
            parts_rows += f"""
            <tr class="{category_class}">
              <td class="col-category">{part.get('category', '')}</td>
              <td class="col-name">{part.get('part_name', '')}</td>
              <td class="col-description">{part.get('part_description', '')}</td>
              <td class="col-material">{part.get('material', '')}</td>
              <td class="col-quantity">{part.get('total_quantity', 0)}</td>
              <td class="col-unit-price">¥{part.get('estimated_unit_price', 0):,}</td>
              <td class="col-total-price">¥{part.get('total_price', 0):,}</td>
            </tr>
            """
            total_price += part.get('total_price', 0)
        
        products_html += f"""
        <div class="product-section {page_break_class}">
          <div class="product-header">
            {product.get('product_name', '')} - 部品構成明細
          </div>

          <div class="product-summary">
            <div class="summary-item">
              <div class="summary-label">製品数量</div>
              <div class="summary-value">{product.get('product_quantity', 0)}個</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">部品総数</div>
              <div class="summary-value">{len(product.get('parts', []))}種類</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">総部品数量</div>
              <div class="summary-value">{sum(part.get('total_quantity', 0) for part in product.get('parts', []))}個</div>
            </div>
          </div>

          <table class="parts-table">
            <thead>
              <tr>
                <th class="col-category">カテゴリ</th>
                <th class="col-name">部品名</th>
                <th class="col-description">説明</th>
                <th class="col-material">材質</th>
                <th class="col-quantity">数量</th>
                <th class="col-unit-price">単価(円)</th>
                <th class="col-total-price">合計金額(円)</th>
              </tr>
            </thead>
            <tbody>
              {parts_rows}
              
              <!-- 製品合計行 -->
              <tr class="total-row">
                <td colspan="6" style="text-align: center;">{product.get('product_name', '')} 合計</td>
                <td class="col-total-price">¥{total_price:,}</td>
              </tr>
            </tbody>
          </table>
        </div>
        """
    
    # 変数の置換
    html_content = template_content.replace('{{ issuer.name }}', '株式会社サンプル')
    html_content = html_content.replace('{{ issuer.address }}', '〒100-0001 東京都千代田区千代田1-1-1')
    html_content = html_content.replace('{{ issuer.tel }}', '03-1234-5678')
    html_content = html_content.replace('{{ issuer.email }}', 'info@sample.co.jp')
    html_content = html_content.replace('{{ issue_date }}', current_date)
    html_content = html_content.replace('{{ document_number }}', 'PARTS-001')
    html_content = html_content.replace('{{ quote_number }}', 'EST-001')
    html_content = html_content.replace('{{ price_source }}', 'AI推定価格')
    
    # 製品セクションを挿入
    products_section_start = html_content.find('<!-- 各製品の部品明細 -->')
    products_section_end = html_content.find('<div class="footer-info">')
    
    if products_section_start != -1 and products_section_end != -1:
        before_products = html_content[:products_section_start]
        after_products = html_content[products_section_end:]
        html_content = before_products + f"<!-- 各製品の部品明細 -->\n{products_html}\n\n" + after_products
    
    return html_content