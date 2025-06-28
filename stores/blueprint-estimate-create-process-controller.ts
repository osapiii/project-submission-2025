import { defineStore } from "pinia";
import log from "@utils/logger";
import { ZodError } from "zod";
import type { decodedCreateNewSessionWithGoogleAgentRequest } from "@models/createNewSessionWithGoogleAgentRequest";
import {
  doc,
  getFirestore,
  onSnapshot,
  type Unsubscribe,
} from "firebase/firestore";
import { useGoogleAiAgentStore } from "./google-ai-agent";
import {
  blueprintCostEstimationCreateJobConverter,
  type DecodedBlueprintCostEstimationCreateJob,
} from "@models/blueprintCostEstimationCreateJob";

export const useBlueprintEstimateCreateProcessControllerStore = defineStore(
  "blueprintEstimateCreateProcessController",
  {
    state: () => ({
      selectedEstimateProcessSessionId: "",
      selectedBlueprintCostEstimationCreateJob:
        {} as DecodedBlueprintCostEstimationCreateJob,
      outputEstimationFile: null as Blob | null,
      outputPartsBreakdownFile: null as Blob | null,
      isDownloadingOutputFiles: false,
      pdfFileIsDownloaded: false,
    }),

    getters: {
      // step4のresponse_dataを取得
      step4ResponseData: (state) => {
        const step4Output =
          state.selectedBlueprintCostEstimationCreateJob?.step4_output;
        if (step4Output && step4Output.api_result?.response_data) {
          return step4Output.api_result.response_data;
        }
        return null;
      },

      // currentStepが5かどうか
      isStep5Completed: (state) => {
        return (
          state.selectedBlueprintCostEstimationCreateJob?.currentStep === 5
        );
      },

      // 出力ファイルが両方とも準備できているかどうか（より厳密なチェック）
      areOutputFilesReady: (state) => {
        return !!(
          state.outputEstimationFile &&
          state.outputPartsBreakdownFile &&
          state.outputEstimationFile instanceof Blob &&
          state.outputPartsBreakdownFile instanceof Blob &&
          state.outputEstimationFile.size > 0 &&
          state.outputPartsBreakdownFile.size > 0
        );
      },

      // 見積書ファイルが準備できているかどうか
      isEstimationFileReady: (state) => {
        return !!(
          state.outputEstimationFile &&
          state.outputEstimationFile instanceof Blob &&
          state.outputEstimationFile.size > 0
        );
      },

      // 明細書ファイルが準備できているかどうか
      isPartsBreakdownFileReady: (state) => {
        return !!(
          state.outputPartsBreakdownFile &&
          state.outputPartsBreakdownFile instanceof Blob &&
          state.outputPartsBreakdownFile.size > 0
        );
      },
    },

    actions: {
      async createNewBlueprintCostEstimationCreateJob() {
        const organization = useOrganizationStore();
        const blueprint = useBlueprintStore();
        const firestoreDocOps = useFirestoreDocOperation();

        try {
          await firestoreDocOps.createDocument({
            collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/blueprintCostEstimationCreateJobs`,
            docId: this.selectedEstimateProcessSessionId,
            docData: {
              currentStep: 1,
              metadata: {
                blueprintId: blueprint.selectedBlueprintId,
              },
              input: {
                pdfFilePath: blueprint.returnBlueprintPdfGCSfilePath({
                  blueprintId: blueprint.selectedBlueprintId,
                }),
                preAnalysisJson: blueprint.selectedBlueprint.preAnalysisOutput,
              },
              output: {
                costEstimation: "",
              },
              stepIsCompleted: {
                step1: false,
                step2: false,
                step3: false,
                step4: false,
                step5: false,
              },
            },
            converter: blueprintCostEstimationCreateJobConverter,
          });
        } catch (error) {
          if (error instanceof ZodError) {
            error.errors.forEach((err) => {
              log("ERROR", "Zod validation error:", err);
            });
          } else {
            log("ERROR", "Unexpected error:", error);
          }
        }
      },

      /**
       * セッション生成と会話開始を統合したメソッド
       * セッション作成完了後に自動的に会話を開始する
       */
      async startEstimateProcessWithConversation() {
        const organization = useOrganizationStore();
        const blueprint = useBlueprintStore();
        const googleAiAgent = useGoogleAiAgentStore();
        const globalError = useGlobalErrorStore();
        const toast = useToast();

        try {
          log("INFO", "🚀 見積もりプロセス会話を開始します");

          // セッションIDを生成
          const sessionId = googleAiAgent.generateSessionId();
          this.selectedEstimateProcessSessionId = sessionId;

          log("INFO", `📋 生成されたセッションID: ${sessionId}`);

          // 1. セッション作成を待機
          log("INFO", "🔄 STEP1: セッション作成中...");
          const sessionSuccess = await googleAiAgent.createNewAgentSession(
            sessionId,
            "firestore_test_connect",
            blueprint.selectedBlueprintId
          );

          if (!sessionSuccess) {
            throw new Error("セッション作成に失敗しました");
          }

          log("INFO", "✅ STEP1: セッション作成完了");

          // 2. 見積もりジョブドキュメント作成を待機
          log("INFO", "🔄 STEP2: 見積もりジョブ作成中...");
          await this.createNewBlueprintCostEstimationCreateJob();
          log("INFO", "✅ STEP2: 見積もりジョブ作成完了");

          // 3. Firestoreドキュメント監視を設定
          log("INFO", "🔄 STEP3: ドキュメント監視設定中...");
          const db = getFirestore();
          const docRef = doc(
            db,
            `organizations/${organization.loggedInOrganizationInfo.id}/blueprintCostEstimationCreateJobs`,
            sessionId
          );

          // リアルタイムリスナーを設定
          onSnapshot(
            docRef,
            (doc) => {
              if (doc.exists()) {
                const data = doc.data();
                this.selectedBlueprintCostEstimationCreateJob =
                  data as DecodedBlueprintCostEstimationCreateJob;
                log("INFO", "📊 見積もりジョブデータが更新されました");
              }
            },
            (error) => {
              log("ERROR", "ドキュメント監視エラー:", error);
            }
          );
          log("INFO", "✅ STEP3: ドキュメント監視設定完了");

          // 4. 会話開始メッセージを送信（セッション作成完了後）
          log("INFO", "🔄 STEP4: 会話開始メッセージ送信中...");
          await googleAiAgent.sendQueryToAgent(
            `コレクション名: organizations/${organization.loggedInOrganizationInfo.id}/blueprintCostEstimationCreateJobs ID: ${sessionId} でジョブを開始`
          );
          log("INFO", "✅ STEP4: 会話開始メッセージ送信完了");

          // 5. 成功通知
          toast.add({
            title: "見積もりプロセスセッションが作成されました",
            description: "AIアシスタントとの会話が始まりました",
            color: "success",
          });

          log("INFO", "🎉 見積もりプロセス会話開始が完了しました");
          return true;
        } catch (error) {
          log(
            "ERROR",
            "見積もりプロセス会話開始でエラーが発生しました:",
            error
          );

          if (error instanceof ZodError) {
            error.errors.forEach((err) => {
              log("ERROR", "Zod validation error:", err);
            });
          }

          globalError.createNewGlobalError({
            selectedErrorMessage:
              globalError.errorCodeList.estimateProcess.E4300,
          });

          toast.add({
            title: "エラー",
            description: "見積もりプロセスの開始に失敗しました",
            color: "error",
          });
          return false;
        }
      },

      async createStartEstimateProcessRequest() {
        const organization = useOrganizationStore();
        const blueprint = useBlueprintStore();
        const googleAiAgent = useGoogleAiAgentStore();
        const globalError = useGlobalErrorStore();
        const toast = useToast();

        try {
          // google-ai-agentストアの汎用メソッドを使用してセッション作成
          const success = await googleAiAgent.createNewAgentSession(
            this.selectedEstimateProcessSessionId,
            "firestore_test_connect",
            blueprint.selectedBlueprintId
          );
          // firestoreに見積もりジョブ本体のDocを生成
          await this.createNewBlueprintCostEstimationCreateJob();

          if (!success) {
            return false;
          }

          log("INFO", "見積もりプロセスリクエストが正常に作成されました ✨");

          // Firestoreのドキュメント参照を取得
          const db = getFirestore();
          const docRef = doc(
            db,
            `organizations/${organization.loggedInOrganizationInfo.id}/requests/startEstimateCreateProcessRequests/logs`,
            this.selectedEstimateProcessSessionId
          );

          // リアルタイムリスナーを設定
          const unsubscribe: Unsubscribe = onSnapshot(
            docRef,
            (docSnapshot) => {
              if (docSnapshot.exists()) {
                log(
                  "INFO",
                  "見積もりプロセスドキュメントが更新されました:",
                  docSnapshot.data()
                );
                const data =
                  docSnapshot.data() as decodedCreateNewSessionWithGoogleAgentRequest;

                if (data && data.status === "completed") {
                  toast.add({
                    title: "見積もりプロセスセッションが作成されました",
                    description: "見積もりプロセスセッションが作成されました",
                    color: "success",
                  });
                  log("INFO", "セッション作成完了、監視を停止します");
                  // 監視を停止
                  unsubscribe();
                }
              }
            },
            (error: Error) => {
              log(
                "ERROR",
                "スナップショット監視でエラーが発生しました:",
                error
              );
              globalError.createNewGlobalError({
                selectedErrorMessage:
                  globalError.errorCodeList.estimateProcess.E4303,
              });
              // エラー時も監視を停止
              unsubscribe();
            }
          );

          return true;
        } catch (error) {
          log(
            "ERROR",
            "見積もりプロセスリクエストの作成でエラーが発生しました:",
            error
          );
          if (error instanceof ZodError) {
            error.errors.forEach((err) => {
              log("ERROR", "Zod validation error:", err);
            });
          }
          globalError.createNewGlobalError({
            selectedErrorMessage:
              globalError.errorCodeList.estimateProcess.E4302,
          });
          return false;
        }
      },
      /**
       * step4のPDFファイルをダウンロードしてstateに格納
       */
      async downloadOutputFiles() {
        if (this.isDownloadingOutputFiles) {
          log("INFO", "すでにダウンロード中です");
          return;
        }

        const responseData = this.step4ResponseData;
        if (!responseData?.estimate_gcs_path || !responseData?.inner_gcs_path) {
          log("ERROR", "PDFファイルのパスが見つかりません", responseData);
          return;
        }

        this.isDownloadingOutputFiles = true;
        const storageOps = useFirebaseStorageOperations();
        const toast = useToast();

        try {
          log("INFO", "出力ファイルのダウンロードを開始します", {
            estimatePath: responseData.estimate_gcs_path,
            innerPath: responseData.inner_gcs_path,
          });

          // 見積書PDFのダウンロード
          const estimationBlob = await storageOps.downloadPdfFile({
            bucketName: "knockai-106a4.firebasestorage.app",
            filePath: responseData.estimate_gcs_path,
          });

          // 明細書PDFのダウンロード
          const partsBreakdownBlob = await storageOps.downloadPdfFile({
            bucketName: "knockai-106a4.firebasestorage.app",
            filePath: responseData.inner_gcs_path,
          });

          if (estimationBlob && partsBreakdownBlob) {
            // stateに格納
            this.outputEstimationFile = estimationBlob;
            this.outputPartsBreakdownFile = partsBreakdownBlob;

            log("INFO", "出力ファイルのダウンロードが完了しました ✅");

            toast.add({
              title: "📄 ドキュメント準備完了",
              description: "見積書と明細書のプレビューが利用可能になりました",
              color: "success",
            });
          } else {
            throw new Error("ファイルのダウンロードに失敗しました");
          }
        } catch (error) {
          log(
            "ERROR",
            "出力ファイルのダウンロードでエラーが発生しました:",
            error
          );

          toast.add({
            title: "ダウンロードエラー",
            description: "見積書・明細書のダウンロードに失敗しました",
            color: "error",
          });
        } finally {
          this.isDownloadingOutputFiles = false;
        }
      },

      /**
       * stateをリセット
       */
      resetOutputFiles() {
        this.outputEstimationFile = null;
        this.outputPartsBreakdownFile = null;
        this.isDownloadingOutputFiles = false;
      },

      /**
       * 見積書をダウンロード
       */
      downloadEstimationFile() {
        if (!this.isEstimationFileReady) {
          log("ERROR", "見積書ファイルが準備されていません", {
            exists: !!this.outputEstimationFile,
            isBlob: this.outputEstimationFile instanceof Blob,
            size: this.outputEstimationFile?.size || 0,
          });

          const toast = useToast();
          toast.add({
            title: "ダウンロードエラー",
            description: "見積書ファイルが準備されていません",
            color: "error",
          });
          return;
        }

        try {
          const url = URL.createObjectURL(this.outputEstimationFile!);
          const link = document.createElement("a");
          link.href = url;
          link.download = "見積書.pdf";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);

          const toast = useToast();
          toast.add({
            title: "ダウンロード完了",
            description: "見積書.pdfをダウンロードしました",
            color: "success",
          });
        } catch (error) {
          log("ERROR", "見積書ダウンロードでエラーが発生しました:", error);

          const toast = useToast();
          toast.add({
            title: "ダウンロードエラー",
            description: "見積書のダウンロードに失敗しました",
            color: "error",
          });
        }
      },

      /**
       * 明細書をダウンロード
       */
      downloadPartsBreakdownFile() {
        if (!this.isPartsBreakdownFileReady) {
          log("ERROR", "明細書ファイルが準備されていません", {
            exists: !!this.outputPartsBreakdownFile,
            isBlob: this.outputPartsBreakdownFile instanceof Blob,
            size: this.outputPartsBreakdownFile?.size || 0,
          });

          const toast = useToast();
          toast.add({
            title: "ダウンロードエラー",
            description: "明細書ファイルが準備されていません",
            color: "error",
          });
          return;
        }

        try {
          const url = URL.createObjectURL(this.outputPartsBreakdownFile!);
          const link = document.createElement("a");
          link.href = url;
          link.download = "明細書.pdf";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);

          const toast = useToast();
          toast.add({
            title: "ダウンロード完了",
            description: "明細書.pdfをダウンロードしました",
            color: "success",
          });
        } catch (error) {
          log("ERROR", "明細書ダウンロードでエラーが発生しました:", error);

          const toast = useToast();
          toast.add({
            title: "ダウンロードエラー",
            description: "明細書のダウンロードに失敗しました",
            color: "error",
          });
        }
      },

      /**
       * 現在のstateをFirestoreに同期する
       */
      async updateSelectedBlueprintCostEstimationCreateJob() {
        const organization = useOrganizationStore();
        const firestoreDocOps = useFirestoreDocOperation();
        const toast = useToast();

        if (!this.selectedEstimateProcessSessionId) {
          log("ERROR", "セッションIDが設定されていません");
          toast.add({
            title: "更新エラー",
            description: "セッションIDが設定されていません",
            color: "error",
          });
          return false;
        }

        try {
          // createdAt、updatedAt、idを除外したデータを作成
          const { id, createdAt, updatedAt, ...updateData } =
            this.selectedBlueprintCostEstimationCreateJob;

          log("INFO", "Firestoreへの更新を開始します", {
            sessionId: this.selectedEstimateProcessSessionId,
            updateData,
          });

          await firestoreDocOps.updateDocument({
            collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/blueprintCostEstimationCreateJobs`,
            docId: this.selectedEstimateProcessSessionId,
            docData: updateData,
            converter: blueprintCostEstimationCreateJobConverter,
          });

          toast.add({
            title: "更新完了",
            description: "見積もりデータがFirestoreに保存されました",
            color: "success",
          });

          log("INFO", "Firestoreへの更新が完了しました ✅");
          return true;
        } catch (error) {
          log("ERROR", "Firestoreへの更新でエラーが発生しました:", error);

          if (error instanceof ZodError) {
            error.errors.forEach((err) => {
              log("ERROR", "Zod validation error:", err);
            });
          }

          toast.add({
            title: "更新エラー",
            description: "見積もりデータの保存に失敗しました",
            color: "error",
          });
          return false;
        }
      },
    },
  }
);
