#!/usr/bin/env python3
"""
ローカル環境での見積書生成テスト用スクリプト

使用方法:
1. requirements.txtのパッケージをインストール
2. GEMINI_API_KEYを環境変数に設定
3. このスクリプトを実行

このスクリプトはGCSを使わずに、ローカルファイルシステムで動作確認を行います。
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# パスを追加してapp.pyをインポート
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_html_generation():
    """HTML生成機能のテスト"""
    
    print("🚀 HTML生成機能のテストを開始します...")
    
    # テスト用の見積書データ
    estimate_data = {
        "totalPrice": 150000,
        "products": [
            {
                "productName": "Type C-2 ロータイプディスプレイ什器",
                "quantity": 10,
                "price": 15000
            }
        ]
    }
    
    # テスト用の部品明細データ
    parts_breakdown = [
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
    ]
    
    print("\n📋 見積書テストデータ:")
    print(json.dumps(estimate_data, ensure_ascii=False, indent=2))
    
    print("\n🔧 部品明細テストデータ:")
    print(json.dumps(parts_breakdown, ensure_ascii=False, indent=2))
    
    try:
        # app.pyから関数をインポート
        from app import generate_html_with_gemini, generate_html_fallback
        from app import generate_parts_breakdown_html_with_gemini, generate_parts_breakdown_html_fallback
        
        success_count = 0
        total_tests = 2
        
        # 1. 見積書HTML生成テスト
        print("\n📄 見積書HTML生成テスト...")
        try:
            estimate_html = generate_html_with_gemini(estimate_data)
            print("✅ Gemini APIでの見積書HTML生成が成功しました！")
            generation_method = "Gemini API"
        except Exception as e:
            print(f"⚠️  Gemini APIでの生成に失敗: {e}")
            print("🔄 フォールバック処理で見積書HTML生成を試行...")
            estimate_html = generate_html_fallback(estimate_data)
            print("✅ フォールバック処理での見積書HTML生成が成功しました！")
            generation_method = "Fallback"
        
        # 見積書HTMLをファイルに保存
        estimate_filename = f"test_estimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        estimate_path = os.path.join(os.path.dirname(__file__), estimate_filename)
        
        with open(estimate_path, 'w', encoding='utf-8') as f:
            f.write(estimate_html)
        
        print(f"📄 見積書HTMLを保存しました: {estimate_path}")
        
        if "見積書" in estimate_html and "Type C-2" in estimate_html:
            print("✅ 見積書HTMLの内容が正しく生成されています")
            success_count += 1
        else:
            print("❌ 見積書HTMLの内容に問題があります")
        
        # 2. 部品明細書HTML生成テスト
        print("\n🔧 部品明細書HTML生成テスト...")
        try:
            parts_html = generate_parts_breakdown_html_with_gemini(parts_breakdown)
            print("✅ Gemini APIでの部品明細書HTML生成が成功しました！")
            parts_generation_method = "Gemini API"
        except Exception as e:
            print(f"⚠️  Gemini APIでの生成に失敗: {e}")
            print("🔄 フォールバック処理で部品明細書HTML生成を試行...")
            parts_html = generate_parts_breakdown_html_fallback(parts_breakdown)
            print("✅ フォールバック処理での部品明細書HTML生成が成功しました！")
            parts_generation_method = "Fallback"
        
        # 部品明細書HTMLをファイルに保存
        parts_filename = f"test_parts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        parts_path = os.path.join(os.path.dirname(__file__), parts_filename)
        
        with open(parts_path, 'w', encoding='utf-8') as f:
            f.write(parts_html)
        
        print(f"🔧 部品明細書HTMLを保存しました: {parts_path}")
        print(f"📄 見積書生成方法: {generation_method}")
        print(f"🔧 部品明細書生成方法: {parts_generation_method}")
        
        if "部品明細書" in parts_html and "フレーム" in parts_html:
            print("✅ 部品明細書HTMLの内容が正しく生成されています")
            success_count += 1
        else:
            print("❌ 部品明細書HTMLの内容に問題があります")
        
        return success_count == total_tests
            
    except ImportError as e:
        print(f"❌ app.pyのインポートに失敗: {e}")
        print("   requirements.txtのパッケージがインストールされているか確認してください")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False


def test_template_loading():
    """テンプレートファイルの読み込みテスト"""
    
    print("\n📄 テンプレートファイルの読み込みテスト...")
    
    template1_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template.html')
    template2_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template2.html')
    
    success_count = 0
    total_templates = 2
    
    # template.htmlのテスト
    try:
        with open(template1_path, 'r', encoding='utf-8') as f:
            template1_content = f.read()
        
        if len(template1_content) > 0 and "見積書" in template1_content:
            print("✅ template.htmlの読み込みが成功しました")
            print(f"   ファイルサイズ: {len(template1_content)} 文字")
            success_count += 1
        else:
            print("❌ template.htmlの内容に問題があります")
            
    except FileNotFoundError:
        print(f"❌ template.htmlが見つかりません: {template1_path}")
    except Exception as e:
        print(f"❌ template.htmlの読み込みでエラー: {e}")
    
    # template2.htmlのテスト
    try:
        with open(template2_path, 'r', encoding='utf-8') as f:
            template2_content = f.read()
        
        if len(template2_content) > 0 and "部品明細書" in template2_content:
            print("✅ template2.htmlの読み込みが成功しました")
            print(f"   ファイルサイズ: {len(template2_content)} 文字")
            success_count += 1
        else:
            print("❌ template2.htmlの内容に問題があります")
            
    except FileNotFoundError:
        print(f"❌ template2.htmlが見つかりません: {template2_path}")
    except Exception as e:
        print(f"❌ template2.htmlの読み込みでエラー: {e}")
    
    return success_count == total_templates

def main():
    """メイン処理"""
    
    print("=" * 60)
    print("🧪 ローカル環境テストスイート")
    print("=" * 60)
    
    # 環境変数のチェック
    if not os.environ.get('GEMINI_API_KEY'):
        print("⚠️  GEMINI_API_KEY環境変数が設定されていません")
        print("   Gemini APIを使った生成はスキップし、フォールバック処理のみテストします")
        print("   export GEMINI_API_KEY=your_api_key")
    
    # テスト実行
    success_count = 0
    total_tests = 2
    
    # 1. テンプレートファイルの読み込みテスト
    if test_template_loading():
        success_count += 1
    
    # 2. HTML生成機能のテスト
    if test_html_generation():
        success_count += 1
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    print(f"成功: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 すべてのテストが成功しました！")
        print("\n📋 次のステップ:")
        print("1. Cloud Runにデプロイ")
        print("2. test_estimate_generation.pyでフルテストを実行")
        sys.exit(0)
    else:
        print("⚠️  一部のテストが失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main() 