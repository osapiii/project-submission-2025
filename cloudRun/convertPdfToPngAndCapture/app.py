import os
import sys
import tempfile
import subprocess
import logging
# Google Cloud Storage クライアント
from google.cloud import storage
# Flask ウェブフレームワーク
from flask import Flask, request, jsonify
from pdf2image import convert_from_path

# ロガーの設定
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Flask アプリケーションを作成します
app = Flask(__name__)

# GCS クライアントはアプリケーション起動時に一度だけ作成します
storage_client = storage.Client()

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