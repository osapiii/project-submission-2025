import { defineStore } from "pinia";
import log from "@utils/logger";
import { ZodError } from "zod";
import { sendQueryToGoogleAgentRequestConverter } from "@models/sendQueryToGoogleAgentRequest";
import {
  doc,
  getFirestore,
  onSnapshot,
  type Unsubscribe,
} from "firebase/firestore";
import type { decodedSendQueryToGoogleAgentRequest } from "@models/sendQueryToGoogleAgentRequest";
import { createNewSessionWithGoogleAgentRequestConverter } from "@models/createNewSessionWithGoogleAgentRequest";

// 会話履歴の型定義
interface ConversationMessage {
  id: string;
  role: "user" | "model";
  content: string | Part[];
  timestamp: Date;
}

interface Part {
  text?: string;
  functionCall?: {
    name: string;
    args: Record<string, unknown>;
  };
  functionResponse?: {
    name: string;
    response: Record<string, unknown>;
  };
}

// チャット表示用の会話履歴の型定義
interface ConversationMessageForView {
  id: string;
  role: "user" | "model";
  type: "text" | "functionCall" | "functionResponse";
  content: string;
  functionCall?: {
    name: string;
    args: Record<string, unknown>;
  };
  functionResponse?: {
    name: string;
    response: Record<string, unknown>;
  };
  timestamp: Date;
}

export const useGoogleAiAgentStore = defineStore("googleAiAgent", {
  state: () => ({
    // 生の会話履歴
    conversationHistory: [] as ConversationMessage[],
    // チャット表示用の会話履歴
    conversationHistoryForView: [] as ConversationMessageForView[],
    // 現在処理中のリクエスト
    isProcessing: false,
    // 現在のセッションID
    currentSessionId: "",
    currentUserId: "",
    currentAppName: "",
    // リアルタイム監視のunsubscribe関数
    currentUnsubscribe: null as Unsubscribe | null,
  }),

  getters: {
    // 最新の会話メッセージを取得
    latestMessage: (state) => {
      return (
        state.conversationHistory[state.conversationHistory.length - 1] || null
      );
    },
    // ユーザーメッセージのみを取得
    userMessages: (state) => {
      return state.conversationHistory.filter((msg) => msg.role === "user");
    },
    // Agentメッセージのみを取得
    agentMessages: (state) => {
      return state.conversationHistory.filter((msg) => msg.role === "model");
    },
  },

  actions: {
    // 会話履歴にメッセージを追加
    addMessage(role: "user" | "model", content: string | Part[]) {
      const message: ConversationMessage = {
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role,
        content,
        timestamp: new Date(),
      };
      this.conversationHistory.push(message);
      log("INFO", `${role}メッセージを追加しました:`, content);

      // 表示用の会話履歴も更新
      this.updateConversationHistoryForView();
    },

    // 表示用の会話履歴を更新する
    updateConversationHistoryForView() {
      this.conversationHistoryForView = this.conversationHistory
        .map(
          (msg): ConversationMessageForView | ConversationMessageForView[] => {
            // ユーザーからの単純なテキストメッセージ
            if (msg.role === "user" && typeof msg.content === "string") {
              return {
                id: msg.id,
                role: "user",
                type: "text",
                content: msg.content,
                timestamp: msg.timestamp,
              };
            }

            // modelからの返信、もしくはfunction_response
            try {
              const parts = Array.isArray(msg.content) ? msg.content : [];
              const messages: ConversationMessageForView[] = [];

              for (const part of parts) {
                // テキスト部分
                if (part.text && part.text.trim()) {
                  messages.push({
                    id: `${msg.id}-text-${messages.length}`,
                    role: msg.role,
                    type: "text",
                    content: part.text,
                    timestamp: msg.timestamp,
                  });
                }
                // Function Call部分
                if (part.functionCall) {
                  messages.push({
                    id: `${msg.id}-functioncall`,
                    role: "model",
                    type: "functionCall",
                    content: "Function Callを実行しました",
                    functionCall: part.functionCall,
                    timestamp: msg.timestamp,
                  });
                }
                // Function Response部分
                if (part.functionResponse) {
                  messages.push({
                    id: `${msg.id}-functionresponse`,
                    role: "user", // function responseはuser roleとして扱う
                    type: "functionResponse",
                    content: `Function [${part.functionResponse.name}] の実行結果`,
                    functionResponse: part.functionResponse,
                    timestamp: msg.timestamp,
                  });
                }
              }

              if (messages.length > 0) {
                return messages;
              }

              // フォールバック
              return {
                id: msg.id,
                role: msg.role,
                type: "text",
                content:
                  typeof msg.content === "string"
                    ? msg.content
                    : JSON.stringify(msg.content),
                timestamp: msg.timestamp,
              };
            } catch (error) {
              log("ERROR", "メッセージの解析に失敗しました。", error);
              return {
                id: msg.id,
                role: "model",
                type: "text",
                content: "エラーが発生しました",
                timestamp: msg.timestamp,
              };
            }
          }
        )
        .flat();
    },

    // 会話履歴をクリア
    clearConversation() {
      this.conversationHistory = [];
      this.conversationHistoryForView = [];
      log("INFO", "会話履歴をクリアしました");
    },

    // セッションIDを生成・設定
    generateSessionId() {
      this.currentSessionId = `session-${Date.now()}-${Math.random()
        .toString(36)
        .substr(2, 9)}`;
      log("INFO", "新しいセッションIDを生成しました:", this.currentSessionId);
      return this.currentSessionId;
    },

    // 新しいAIエージェントセッションを作成（汎用版）
    async createNewAgentSession(
      sessionId: string,
      appName: string,
      userId?: string
    ) {
      const organization = useOrganizationStore();
      const firestoreOps = useFirestoreDocOperation();
      const globalError = useGlobalErrorStore();

      try {
        // デフォルトのuserIdを設定
        const targetUserId = userId || organization.loggedInOrganizationInfo.id;

        // セッション作成リクエストをFirestoreに登録
        await firestoreOps.createDocument({
          collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/requests/startEstimateCreateProcessRequests/logs`,
          docId: sessionId,
          docData: {
            input: {
              appName,
              organizationId: organization.loggedInOrganizationInfo.id,
              userId: targetUserId,
              sessionId,
            },
            status: "pending",
          },
          converter: createNewSessionWithGoogleAgentRequestConverter,
        });

        log(
          "INFO",
          `AIエージェントセッション作成リクエストが正常に作成されました ✨ SessionID: ${sessionId}`
        );

        // 現在のセッション情報を更新
        this.currentSessionId = sessionId;
        this.currentAppName = appName;
        this.currentUserId = targetUserId;

        return true;
      } catch (error) {
        log(
          "ERROR",
          "AIエージェントセッション作成リクエストでエラーが発生しました:",
          error
        );
        if (error instanceof ZodError) {
          error.errors.forEach((err) => {
            log("ERROR", "Zod validation error:", err);
          });
        }
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.googleAiAgent.E4200,
        });
        return false;
      }
    },

    // Google AI Agentにクエリを送信
    async sendQueryToAgent(query: string) {
      const organization = useOrganizationStore();
      const firestoreOps = useFirestoreDocOperation();
      const globalError = useGlobalErrorStore();
      const toast = useToast();

      try {
        this.isProcessing = true;

        // stateから必要な値を取得
        if (
          !this.currentSessionId ||
          !this.currentAppName ||
          !this.currentUserId
        ) {
          throw new Error(
            "セッション情報が不足しています。先にセッションを作成してください。"
          );
        }

        // ユーザーメッセージを会話履歴に追加
        this.addMessage("user", query);

        // リクエストIDを生成
        const requestId = `request-${Date.now()}-${Math.random()
          .toString(36)
          .substr(2, 9)}`;

        // Google AgentリクエストをFirestoreに登録
        await firestoreOps.createDocument({
          collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/requests/sendQueryToGoogleAgentRequests/logs`,
          docId: requestId,
          docData: {
            input: {
              appName: this.currentAppName,
              userId: this.currentUserId,
              organizationId: organization.loggedInOrganizationInfo.id,
              sessionId: this.currentSessionId,
              query,
            },
            status: "pending",
          },
          converter: sendQueryToGoogleAgentRequestConverter,
        });

        log("INFO", "Google Agentリクエストが正常に作成されました ✨");

        // Firestoreのドキュメント参照を取得
        const db = getFirestore();
        const docRef = doc(
          db,
          `organizations/${organization.loggedInOrganizationInfo.id}/requests/sendQueryToGoogleAgentRequests/logs`,
          requestId
        );

        // 既存の監視があれば停止
        if (this.currentUnsubscribe) {
          this.currentUnsubscribe();
        }

        // リアルタイムリスナーを設定
        this.currentUnsubscribe = onSnapshot(
          docRef,
          (docSnapshot) => {
            if (docSnapshot.exists()) {
              log(
                "INFO",
                "Google Agentレスポンスが更新されました:",
                docSnapshot.data()
              );
              const data =
                docSnapshot.data() as decodedSendQueryToGoogleAgentRequest;

              if (data && data.status === "completed" && data.output?.parts) {
                // Agentのレスポンスを会話履歴に追加
                const agentResponse = data.output.parts;

                this.addMessage("model", agentResponse);

                toast.add({
                  title: "AI Agentからレスポンスを受信しました",
                  description: "新しいメッセージが届きました",
                  color: "success",
                });

                this.isProcessing = false;
                log("INFO", "レスポンス受信完了、監視を停止します");

                // 監視を停止
                if (this.currentUnsubscribe) {
                  this.currentUnsubscribe();
                  this.currentUnsubscribe = null;
                }
              } else if (data && data.status === "failed") {
                this.isProcessing = false;
                globalError.createNewGlobalError({
                  selectedErrorMessage:
                    globalError.errorCodeList.googleAiAgent.E4205,
                });

                // 監視を停止
                if (this.currentUnsubscribe) {
                  this.currentUnsubscribe();
                  this.currentUnsubscribe = null;
                }
              }
            }
          },
          (error: Error) => {
            log(
              "ERROR",
              "Google Agentスナップショット監視でエラーが発生しました:",
              error
            );
            this.isProcessing = false;
            globalError.createNewGlobalError({
              selectedErrorMessage:
                globalError.errorCodeList.googleAiAgent.E4202,
            });

            // エラー時も監視を停止
            if (this.currentUnsubscribe) {
              this.currentUnsubscribe();
              this.currentUnsubscribe = null;
            }
          }
        );

        return true;
      } catch (error) {
        log(
          "ERROR",
          "Google Agentリクエストの作成でエラーが発生しました:",
          error
        );
        this.isProcessing = false;

        if (error instanceof ZodError) {
          error.errors.forEach((err) => {
            log("ERROR", "Zod validation error:", err);
          });
        }

        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.googleAiAgent.E4201,
        });
        return false;
      }
    },

    // 監視を手動で停止
    stopListening() {
      if (this.currentUnsubscribe) {
        this.currentUnsubscribe();
        this.currentUnsubscribe = null;
        log("INFO", "Google Agent監視を手動で停止しました");
      }
    },

    // ストアをリセット
    resetStore() {
      this.clearConversation();
      this.isProcessing = false;
      this.currentSessionId = "";
      this.currentUserId = "";
      this.currentAppName = "";
      if (this.currentUnsubscribe) {
        this.currentUnsubscribe();
        this.currentUnsubscribe = null;
      }
      log("INFO", "googleAiAgentストアをリセットしました");
    },
  },
});
