# 見積書・部品明細書生成 Cloud Run API

この API は、見積書の内訳情報と部品明細情報を受け取り、見積書と部品明細書の HTML ドキュメントを動的生成して PDF に変換し、Google Cloud Storage に保存する機能を提供します。

## 🚀 機能

- **見積書生成**: 商品情報から見積書 HTML を動的生成
- **部品明細書生成**: 部品構成情報から詳細な明細書を生成
- **AI 支援**: Gemini 2.5 Pro を使用したインテリジェントな HTML 生成
- **PDF 変換**: HTML から PDF への高品質変換
- **GCS 統合**: 生成された PDF の自動アップロード
- **フォールバック**: AI 生成が失敗した場合の代替処理

## 📋 API 仕様

### エンドポイント

#### 1. 見積書・部品明細書生成 - `/create-estimate-document`

**メソッド:** POST

**リクエスト形式:**

```json
{
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
  "bucket_name": "your-gcs-bucket-name",
  "parentFolderPath": "estimates/project_001"
}
```

**レスポンス形式:**

```json
{
  "status": "success",
  "estimate_gcs_path": "estimates/project_001/estimation.pdf",
  "inner_gcs_path": "estimates/project_001/inner.pdf",
  "message": "Both estimate and parts breakdown documents successfully generated and uploaded to GCS."
}
```

#### 2. PDF 変換 - `/convert-pdf-to-png` (既存機能)

**メソッド:** POST

**リクエスト形式:**

```json
{
  "bucket_name": "your-gcs-bucket-name",
  "gcsInputPdfFilePath": "input/document.pdf",
  "gcsOutputPreviewPngFilePath": "output/preview.png"
}
```

## 🛠️ セットアップ

### 1. 環境変数の設定

#### 方法 1: .env ファイルを使用（推奨）

カレントディレクトリに`.env`ファイルを作成し、以下の内容を記述してください：

```bash
# .env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json
```

⚠️ **重要**: `.env`ファイルは機密情報を含むため、Git にコミットしないでください。

#### 方法 2: 環境変数で直接設定

```bash
export GEMINI_API_KEY="your_gemini_api_key"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account.json"
```

### 2. ローカル開発

```bash
# 依存関係のインストール
pip install -r requirements.txt

# .envファイルを作成（必要に応じて）
cp .env.example .env
# .envファイルを編集してAPIキーを設定

# ローカルテストの実行
cd sandbox
python local_test.py
```

### 3. Cloud Run へのデプロイ

```bash
# Dockerイメージのビルド
docker build -t gcr.io/your-project/estimate-generator .

# イメージのプッシュ
docker push gcr.io/your-project/estimate-generator

# Cloud Runサービスのデプロイ
gcloud run deploy estimate-generator \
  --image gcr.io/your-project/estimate-generator \
  --platform managed \
  --region asia-northeast1 \
  --set-env-vars GEMINI_API_KEY=your_api_key \
  --allow-unauthenticated
```

## 🧪 テスト

### ローカルテスト

```bash
cd sandbox
python local_test.py
```

### フルテスト（Cloud Run）

```bash
export CLOUD_RUN_URL="https://your-service-url.run.app"
export GCS_BUCKET_NAME="your-test-bucket"
export GEMINI_API_KEY="your_api_key"

cd sandbox
python test_estimate_generation.py
```

## 📁 ファイル構成

```
cloudRun/createEstimationDocument/
├── app.py                    # メインアプリケーション
├── template.html            # 見積書HTMLテンプレート
├── template2.html           # 部品明細書HTMLテンプレート
├── requirements.txt         # Python依存関係
├── dockerfile              # Dockerコンテナ設定
├── README.md               # このファイル
└── sandbox/
    ├── local_test.py       # ローカル環境テスト
    └── test_estimate_generation.py  # フルテスト
```

## 🎨 テンプレート

### 見積書テンプレート（template.html）

日本語の見積書形式で設計されており、以下の要素を含みます：

- **ヘッダー情報**: 発行者・顧客情報
- **見積詳細**: 発行日、伝票番号、支払条件
- **商品明細**: 商品名、数量、単価、金額
- **合計金額**: 小計、消費税、総額
- **備考欄**: 追加情報

### 部品明細書テンプレート（template2.html）

社内参照用の詳細な部品構成明細で、以下の要素を含みます：

- **ヘッダー情報**: 発行者情報、発行日、関連見積書番号
- **製品サマリー**: 製品数量、部品総数、総部品数量
- **部品明細テーブル**: カテゴリ、部品名、説明、材質、数量、単価、合計金額
- **カテゴリ別色分け**: 金属部品、樹脂部品、電子部品、その他
- **注意事項**: 価格情報の説明

## 🤖 AI 機能

### Gemini 2.5 Pro 統合

- **動的 HTML 生成**: 商品データから見積書 HTML を自動生成
- **部品明細書生成**: 部品構成データから詳細な明細書を自動生成
- **日本語対応**: 日本のビジネス慣習に適した文書形式
- **フォールバック**: AI 生成が失敗した場合の代替処理

### プロンプト設計

AI は以下の指示に従って HTML を生成します：

#### 見積書生成

1. テンプレートの Jinja2 変数を実際の値に置換
2. 商品配列の各要素を明細行として表示
3. 合計金額の正確な計算と表示
4. 日本語ビジネス文書の適切な形式

#### 部品明細書生成

1. 製品ごとの部品構成を明細テーブルとして表示
2. カテゴリ別の色分け表示
3. 部品数量と価格の正確な計算
4. 社内参照用の詳細情報を含む

## 📊 データ構造

### 部品明細データ（partsBreakdown）

```javascript
{
  "product_name": "製品名",
  "product_quantity": 10,           // 製品の数量
  "total_quantity": 20,            // 総部品数量
  "total_price": 50000,            // 製品の総部品費
  "parts": [
    {
      "category": "金属部品",        // カテゴリ（金属部品/樹脂部品/電子部品/その他）
      "part_name": "フレーム",       // 部品名
      "part_description": "本体フレーム（スチール製）", // 部品説明
      "material": "スチール",        // 材質
      "unit_quantity": 1,           // 製品1個あたりの部品数
      "total_quantity": 10,         // 総数量（製品数量×単位数量）
      "estimated_unit_price": 2000, // 推定単価
      "total_price": 20000,         // 合計金額
      "price_source": "gemini_estimated" // 価格ソース
    }
  ]
}
```

## 🧪 テスト

### ローカルテスト

```bash
cd sandbox
python local_test.py
```

### フルテスト（Cloud Run）

```bash
export CLOUD_RUN_URL="https://your-service-url.run.app"
export GCS_BUCKET_NAME="your-test-bucket"
export GEMINI_API_KEY="your_api_key"

cd sandbox
python test_estimate_generation.py
```

## 📊 エラーハンドリング

- **バリデーション**: 必須フィールドの検証
- **AI 生成失敗**: フォールバック処理への自動切り替え
- **PDF 変換エラー**: 詳細なエラーログと適切なレスポンス
- **GCS 操作エラー**: 接続・アップロード失敗の処理

## 🔧 技術スタック

- **Python 3.11**: ベースランタイム
- **Flask**: Web フレームワーク
- **Google Generative AI**: Gemini 2.5 Pro API
- **wkhtmltopdf**: HTML→PDF 変換
- **Google Cloud Storage**: ファイルストレージ
- **Jinja2**: テンプレートエンジン

## 📝 ライセンス

このプロジェクトは内部使用のためのものです。

## 🆘 トラブルシューティング

### よくある問題

1. **Gemini API エラー**

   - API キーが正しく設定されているか確認
   - API クォータの制限を確認

2. **PDF 変換エラー**

   - wkhtmltopdf の依存関係が正しくインストールされているか確認
   - 日本語フォントが利用可能か確認

3. **GCS アップロードエラー**

   - サービスアカウントの権限を確認
   - バケット名とパスが正しいか確認

4. **部品明細データエラー**
   - partsBreakdown 配列の構造が正しいか確認
   - 必須フィールドが全て含まれているか確認

### ログの確認

```bash
# Cloud Runのログを確認
gcloud logs read --service=estimate-generator --limit=50
```
