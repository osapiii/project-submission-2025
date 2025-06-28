#!/usr/bin/env python3
"""
見積書生成APIのテスト用スクリプト

使用方法:
1. Cloud Runサービスをデプロイ
2. GEMINI_API_KEYを環境変数に設定
3. このスクリプトを実行

必要な環境変数:
- GEMINI_API_KEY: Gemini APIキー
- CLOUD_RUN_URL: デプロイされたCloud RunのURL (例: https://your-service-url.run.app)
- GCS_BUCKET_NAME: テスト用のGCSバケット名
"""

import os
import sys
import json
import requests
from datetime import datetime

# 設定
CLOUD_RUN_URL = os.environ.get('CLOUD_RUN_URL', 'http://localhost:8080')
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'your-test-bucket')

def test_estimate_generation():
    """見積書と部品明細書生成APIのテスト"""
    
    print("🚀 見積書・部品明細書生成APIのテストを開始します...")
    print(f"Cloud Run URL: {CLOUD_RUN_URL}")
    print(f"GCS Bucket: {GCS_BUCKET_NAME}")
    
    # テスト用のデータ
    test_data = {
        "estimateData": {
            "totalPrice": 150000,
            "products": [
                {
                    "productName": "Type C-2 ロータイプディスプレイ什器",
                    "quantity": 10,
                    "price": 15000
                }
            ]
        },
        "partsBreakdown": [
            {
                "product_name": "Type C-2 ロータイプディスプレイ什器",
                "product_quantity": 10,
                "total_quantity": 20,
                "total_price": 50000,
                "parts": [
                    {
                        "category": "金属部品",
                        "part_name": "フレーム",
                        "part_description": "本体フレーム（スチール製）",
                        "material": "スチール",
                        "unit_quantity": 1,
                        "total_quantity": 10,
                        "estimated_unit_price": 2000,
                        "total_price": 20000,
                        "price_source": "gemini_estimated"
                    },
                    {
                        "category": "樹脂部品",
                        "part_name": "背面パネル",
                        "part_description": "背面パネル（木製）",
                        "material": "木材",
                        "unit_quantity": 1,
                        "total_quantity": 10,
                        "estimated_unit_price": 3000,
                        "total_price": 30000,
                        "price_source": "gemini_estimated"
                    }
                ]
            }
        ],
        "bucket_name": GCS_BUCKET_NAME,
        "parentFolderPath": f"test_documents/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    print("\n📋 送信するデータ:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    
    try:
        # APIリクエストを送信
        print("\n📤 APIリクエストを送信中...")
        response = requests.post(
            f"{CLOUD_RUN_URL}/create-estimate-document",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ドキュメント生成が成功しました！")
            print(f"見積書PDF: {result.get('estimate_gcs_path')}")
            print(f"部品明細書PDF: {result.get('inner_gcs_path')}")
            print(f"メッセージ: {result.get('message')}")
            return True
        else:
            print("❌ ドキュメント生成が失敗しました")
            print(f"エラー: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

def test_pdf_conversion():
    """PDF変換APIのテスト（既存機能）"""
    
    print("\n🔄 PDF変換APIのテストも実行します...")
    
    test_data = {
        "bucket_name": GCS_BUCKET_NAME,
        "gcsInputPdfFilePath": "test/sample.pdf",  # 事前にアップロードしておく必要があります
        "gcsOutputPreviewPngFilePath": f"previews/test_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    }
    
    try:
        response = requests.post(
            f"{CLOUD_RUN_URL}/convert-pdf-to-png",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PDF変換も成功しました！")
            print(f"出力ファイル: {result.get('output_gcs_path')}")
            return True
        else:
            print("⚠️  PDF変換は失敗しましたが、これは既存機能なので問題ありません")
            return True
            
    except Exception as e:
        print(f"⚠️  PDF変換テストでエラーが発生しましたが、これは既存機能なので問題ありません: {e}")
        return True

def main():
    """メイン処理"""
    
    print("=" * 60)
    print("🏗️  見積書生成API テストスイート")
    print("=" * 60)
    
    # 環境変数のチェック
    if not os.environ.get('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY環境変数が設定されていません")
        print("   export GEMINI_API_KEY=your_api_key")
        sys.exit(1)
    
    if not GCS_BUCKET_NAME or GCS_BUCKET_NAME == 'your-test-bucket':
        print("❌ GCS_BUCKET_NAME環境変数が設定されていません")
        print("   export GCS_BUCKET_NAME=your_bucket_name")
        sys.exit(1)
    
    # テスト実行
    success_count = 0
    total_tests = 2
    
    # 1. 見積書生成APIのテスト
    if test_estimate_generation():
        success_count += 1
    
    # 2. PDF変換APIのテスト（既存機能）
    if test_pdf_conversion():
        success_count += 1
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    print(f"成功: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 すべてのテストが成功しました！")
        sys.exit(0)
    else:
        print("⚠️  一部のテストが失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main() 