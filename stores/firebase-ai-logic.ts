import { defineStore } from "pinia";
import { getApp } from "firebase/app";
import {
  getVertexAI,
  getGenerativeModel,
  type GenerativeModel,
  type Schema,
} from "firebase/vertexai";
import log from "@utils/logger";
import type { preAnalysisOutputZodObject } from "@models/blueprint";
import type { z } from "zod";

export const useFirebaseAILogic = defineStore("firebaseAILogic", {
  state: () => ({
    vertexAIModel: null as GenerativeModel | null,
  }),

  actions: {
    /**
     * Vertex AIモデルを初期化する（structured output対応）
     */
    initializeVertexAI() {
      log("INFO", "initializeVertexAI triggered!");

      // 既に初期化されているFirebaseアプリを取得
      const firebaseApp = getApp();
      const vertexAI = getVertexAI(firebaseApp);

      // structured output用のスキーマ定義
      const responseSchema: Schema = {
        type: "object",
        properties: {
          summary: {
            type: "string",
            description: "図面全体の概要を簡潔に説明",
          },
          annotation: {
            type: "string",
            description: "見積もり作成時に注意すべき点を箇条書きで説明",
          },
          pages: {
            type: "array",
            description: "各ページの詳細情報",
            items: {
              type: "object",
              properties: {
                pageCount: {
                  type: "integer",
                  description: "ページ番号",
                },
                summary: {
                  type: "string",
                  description: "該当ページの内容を簡潔に説明",
                },
              },
              required: ["pageCount", "summary"],
            },
          },
        },
        required: ["summary", "annotation", "pages"],
      };

      this.vertexAIModel = getGenerativeModel(vertexAI, {
        model: "gemini-2.0-flash",
        generationConfig: {
          responseMimeType: "application/json",
          responseSchema: responseSchema,
        },
      });
    },

    /**
     * ArrayBufferをBase64文字列に変換する（スタックオーバーフロー対策版）
     */
    arrayBufferToBase64(buffer: ArrayBuffer): string {
      const bytes = new Uint8Array(buffer);
      let binary = "";
      const chunkSize = 8192; // 8KBに縮小（スタックオーバーフロー対策）

      for (let i = 0; i < bytes.length; i += chunkSize) {
        const chunk = bytes.slice(i, i + chunkSize);
        // より安全な方法でString.fromCharCodeを使用
        for (let j = 0; j < chunk.length; j++) {
          binary += String.fromCharCode(chunk[j]);
        }
      }

      return btoa(binary);
    },

    /**
     * より効率的なArrayBufferからBase64への変換（代替案）
     */
    arrayBufferToBase64Alternative(buffer: ArrayBuffer): Promise<string> {
      // FileReaderを使用した方法（非同期）
      return new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          const result = reader.result as string;
          // data:application/pdf;base64, の部分を除去
          const base64 = result.split(",")[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(new Blob([buffer]));
      });
    },

    /**
     * PDFファイルを解析してGemini APIで処理する（structured output対応）
     * @param params.pdfFileBlob - 解析対象のPDFファイルのBlob
     * @returns 構造化された解析結果
     */
    async analyzePdfFile(params: {
      pdfFileBlob: Blob;
    }): Promise<z.infer<typeof preAnalysisOutputZodObject>> {
      if (!this.vertexAIModel) {
        throw new Error(
          "Vertex AI model is not initialized. Please call initializeVertexAI() first."
        );
      }

      try {
        const arrayBuffer = await params.pdfFileBlob.arrayBuffer();
        const base64String = await this.arrayBufferToBase64Alternative(
          arrayBuffer
        );

        const prompt = `この図面を分析し、以下の形式で情報を抽出してください：
        
- summary: 図面全体の概要を簡潔に説明してください
- annotation: 見積もり作成時に注意すべき点を箇条書きで説明してください  
- pages: 各ページの情報を配列で提供してください
  - pageCount: ページ番号（1から開始）
  - summary: そのページの主要な内容を簡潔に説明

注意点：
- 見積もり作成時の注意点は、具体的な数値や仕様に関する重要な情報を含めてください
- 各ページのsummaryは、そのページの主要な内容を簡潔に説明してください
- 図面の詳細な寸法、材質、加工方法などの技術仕様に注目してください`;

        const result = await this.vertexAIModel.generateContent({
          contents: [
            {
              role: "user",
              parts: [
                {
                  inlineData: {
                    mimeType: "application/pdf",
                    data: base64String,
                  },
                },
                { text: prompt },
              ],
            },
          ],
        });

        const response = await result.response;
        const responseText = response.text();

        try {
          // structured outputにより、既にJSON形式で返される
          const parsedOutput = JSON.parse(responseText);

          // 基本的な構造チェック
          if (
            !parsedOutput.summary ||
            !parsedOutput.annotation ||
            !Array.isArray(parsedOutput.pages)
          ) {
            throw new Error("AIの応答が期待される構造と一致しません");
          }

          log("INFO", "PDF analysis completed successfully", parsedOutput);
          return parsedOutput as z.infer<typeof preAnalysisOutputZodObject>;
        } catch (parseError) {
          log("ERROR", "Failed to parse AI response as JSON:", parseError);
          log("ERROR", "Response text:", responseText);
          throw new Error("AIの応答をJSONとして解析できませんでした");
        }
      } catch (error) {
        log("ERROR", "PDF analysis error:", error);

        if (error instanceof Error) {
          if (error.message.includes("Service agents are being provisioned")) {
            throw new Error(
              "Firebase Vertex AIサービスが初期化中です。数分待ってから再度お試しください。"
            );
          }

          if (error.message.includes("vertexAI/fetch-error")) {
            throw new Error(
              "Vertex AI APIへのアクセスに失敗しました。プロジェクトの設定とAPIの有効化を確認してください。"
            );
          }

          if (error.message.includes("Invalid response schema")) {
            throw new Error(
              "AIの応答スキーマが無効です。モデルの設定を確認してください。"
            );
          }
        }

        throw new Error(
          `PDF analysis failed: ${
            error instanceof Error ? error.message : "Unknown error"
          }`
        );
      }
    },
  },
});
