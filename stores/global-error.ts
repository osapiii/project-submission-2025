import { defineStore } from "pinia";
import log from "@utils/logger";

// *********STORE*********
export const useGlobalErrorStore = defineStore("globalError", {
  state: () => ({
    globalErrorModalStatus: "none" as "none" | "triggered",
    globalErrorCode: "" as string,
    globalErrorMessage: "" as string,
    selectedErrorMessage: {
      type: "error",
      errorCode: 0,
      message: "",
    } as {
      type: string;
      errorCode: number;
      message: string;
    },
    errorCodeList: {
      blueprint: {
        E4100: {
          type: "error",
          errorCode: 4100,
          message: "図面ファイルのアップロードに失敗しました",
        },
        E4101: {
          type: "error",
          errorCode: 4101,
          message: "図面のPDF変換リクエスト作成に失敗しました",
        },
        E4102: {
          type: "error",
          errorCode: 4102,
          message: "図面の登録に失敗しました",
        },
        E4103: {
          type: "error",
          errorCode: 4103,
          message: "図面の取得に失敗しました",
        },
        E4104: {
          type: "error",
          errorCode: 4104,
          message: "図面一覧の取得に失敗しました",
        },
      },
      googleAiAgent: {
        E4200: {
          type: "error",
          errorCode: 4200,
          message: "AIエージェントセッションの作成に失敗しました",
        },
        E4201: {
          type: "error",
          errorCode: 4201,
          message: "AIエージェントへのクエリ送信に失敗しました",
        },
        E4202: {
          type: "error",
          errorCode: 4202,
          message: "AIエージェントのレスポンス監視でエラーが発生しました",
        },
        E4205: {
          type: "error",
          errorCode: 4205,
          message: "AIエージェントの処理が失敗しました",
        },
      },
      estimateProcess: {
        E4300: {
          type: "error",
          errorCode: 4300,
          message: "見積もりプロセスの開始に失敗しました",
        },
        E4302: {
          type: "error",
          errorCode: 4302,
          message: "見積もりプロセスリクエストの作成に失敗しました",
        },
        E4303: {
          type: "error",
          errorCode: 4303,
          message: "見積もりプロセスの監視でエラーが発生しました",
        },
      },
      firebaseStorage: {
        E4400: {
          type: "error",
          errorCode: 4400,
          message: "ファイルのアップロードに失敗しました",
        },
        E4401: {
          type: "error",
          errorCode: 4401,
          message: "ファイルのダウンロードに失敗しました",
        },
        E4404: {
          type: "error",
          errorCode: 4404,
          message: "Firebase認証が必要です",
        },
      },
      email: {
        E1100: {
          type: "error",
          errorCode: 1100,
          message: "メール送信リクエストの取得に失敗しました",
        },
      },
      globalConfigs: {
        E3200: {
          type: "error",
          errorCode: 3200,
          message: "グローバル設定の取得に失敗しました",
        },
        E3201: {
          type: "error",
          errorCode: 3201,
          message: "グローバル設定一覧の取得に失敗しました",
        },
        E3204: {
          type: "error",
          errorCode: 3204,
          message: "グローバル設定の削除に失敗しました",
        },
      },
    },
  }),
  getters: {
    isModalOpen(): boolean {
      return this.globalErrorModalStatus === "triggered";
    },
  },
  actions: {
    /**
     * エラーを生成する
     */
    createNewGlobalError(params: {
      selectedErrorMessage: {
        type: string;
        errorCode: number;
        message: string;
      };
    }): void {
      const globalLoading = useGlobalLoadingStore();
      this.selectedErrorMessage = params.selectedErrorMessage;
      // loading中の場合は終了する
      if (globalLoading.isLoading) {
        globalLoading.stopLoading();
      }
      log("ERROR", "createNewGlobalError triggered!🚨 ", params);
      // Errorモーダルを表示
      this.globalErrorModalStatus = "triggered";
      // エラーをスローして処理をストップ
      createError(params.selectedErrorMessage.message);
    },
  },
});
