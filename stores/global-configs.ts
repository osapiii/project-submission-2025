import { defineStore } from "pinia";
import type { z } from "zod";
import { ZodError } from "zod";
import log from "@utils/logger";
import type { decodedGlobalConfigsZodObject } from "@models/globalConfigs";
import { globalConfigsConverter } from "@models/globalConfigs";

// *********STORE*********
export const useGlobalConfigsStore = defineStore("globalConfigs", {
  state: () => ({
    selectedGlobalConfig: {} as z.infer<typeof decodedGlobalConfigsZodObject>,
    allGlobalConfigsList: [] as z.infer<typeof decodedGlobalConfigsZodObject>[],
  }),
  getters: {},
  actions: {
    /**
     * 現在のグローバル設定をFirestoreに保存する
     * @returns {Promise<boolean>} 保存が成功した場合はtrue、失敗した場合はfalseを返す
     */
    async saveGlobalConfig(): Promise<boolean> {
      const firestoreOps = useFirestoreDocOperation();
      const organization = useOrganizationStore();
      const globalError = useGlobalErrorStore();
      try {
        await firestoreOps.updateDocument({
          collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/globalConfigs`,
          docId: this.selectedGlobalConfig.id,
          docData: this.selectedGlobalConfig,
          converter: globalConfigsConverter,
        });
        return true;
      } catch (error) {
        if (error instanceof ZodError) {
          error.errors.forEach((err) => {
            log("ERROR", "Zod validation error:", err);
          });
        } else {
          log("ERROR", "Unexpected error:", error);
        }
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.globalConfigs.E3204,
        });
        return false;
      }
    },
    /**
     * グローバル設定を更新する
     * @param {Object} params - パラメータオブジェクト
     * @param {string} params.globalConfigId - 取得するグローバル設定のID
     * @returns {Promise<boolean>} 取得が成功した場合はtrue、失敗した場合はfalseを返す
     */
    async fetchSelectedGlobalConfig(): Promise<boolean> {
      const firestoreOps = useFirestoreDocOperation();
      const organization = useOrganizationStore();
      const globalError = useGlobalErrorStore();
      try {
        const globalConfigDoc = await firestoreOps.getSingleDocumentById({
          collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/globalConfigs`,
          docId: "latest",
          converter: globalConfigsConverter,
        });
        if (globalConfigDoc) {
          this.selectedGlobalConfig = globalConfigDoc;
          return true;
        } else {
          globalError.createNewGlobalError({
            selectedErrorMessage: globalError.errorCodeList.globalConfigs.E3200,
          });
          return false;
        }
      } catch (error) {
        if (error instanceof ZodError) {
          error.errors.forEach((err) => {
            log("ERROR", "Zod validation error:", err);
          });
        } else {
          log("ERROR", "Unexpected error:", error);
        }
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.globalConfigs.E3200,
        });
        return false;
      }
    },
    /**
     * 新しいグローバル設定を作成する
     * @param {Object} params - パラメータオブジェクト
     * @param {string} params.globalConfigId - 作成するグローバル設定のID
     * @param {string} params.sheetId - GoogleシートのID
     * @param {string} params.serviceAccount - サービスアカウント情報
     * @returns {Promise<boolean>} 作成が成功した場合はtrue、失敗した場合はfalseを返す
     */
    async createNewGlobalConfig(params: {
      globalConfigId: string;
      sheetId: string;
      serviceAccount: string;
    }): Promise<boolean> {
      log(
        "INFO",
        "createNewGlobalConfig triggered! 新しいグローバル設定を作成します🔥"
      );
      const firestoreOps = useFirestoreDocOperation();
      const globalError = useGlobalErrorStore();
      const organization = useOrganizationStore();

      try {
        // グローバル設定の登録
        await firestoreOps.createDocument({
          collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/globalConfigs`,
          docId: params.globalConfigId,
          docData: {
            google: {
              sheetId: params.sheetId,
              serviceAccount: params.serviceAccount,
            },
          },
          converter: globalConfigsConverter,
        });
        return true;
      } catch (error) {
        if (error instanceof ZodError) {
          error.errors.forEach((err) => {
            log("ERROR", "Zod validation error:", err);
          });
        } else {
          log("ERROR", "Unexpected error:", error);
        }
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.globalConfigs.E3201,
        });
        return false;
      }
    },

    /**
     * グローバル設定一覧を取得する
     * @param {Object} params - パラメータオブジェクト
     * @param {string} params.organizationId - 組織ID
     */
    async fetchGlobalConfigs(params: { organizationId: string }) {
      log(
        "INFO",
        "fetchGlobalConfigs triggered! グローバル設定一覧を取得します🔥"
      );
      const firestoreOps = useFirestoreDocOperation();
      const globalError = useGlobalErrorStore();
      this.allGlobalConfigsList = [];
      try {
        // zod parseする処理を記述
        const globalConfigDocs =
          await firestoreOps.getAllDocumentListFromCollectionWithConverter({
            collectionName: `organizations/${params.organizationId}/globalConfigs`,
            converter: globalConfigsConverter,
          });
        globalConfigDocs.forEach((globalConfigDoc) => {
          this.allGlobalConfigsList.push(globalConfigDoc);
        });
      } catch (error) {
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.globalConfigs.E3201,
        });
        if (error instanceof ZodError) {
          error.errors.forEach((err) => {
            log("ERROR", "Zod validation error:", err);
          });
        } else {
          log("ERROR", "Unexpected error:", error);
        }
      }
    },
  },
});
