import { Timestamp } from "firebase/firestore";
import { defineStore } from "pinia";
import log from "@utils/logger";
import {
  organizationConverter,
  type decodedOrganizationSchema,
} from "@models/Organization";
import type { RouteLocationNormalizedGeneric } from "vue-router";

// *********STORE*********
export const useOrganizationStore = defineStore("organization", {
  state: () => ({
    loggedInOrganizationInfo: {} as decodedOrganizationSchema,
  }),
  getters: {
    getLoggedInOrganizationId(): string {
      if (!this.loggedInOrganizationInfo.id) {
        return "";
      }
      return this.loggedInOrganizationInfo.id;
    },
  },
  actions: {
    /**
     * クエリパラメータ==oの値を元に組織情報を更新する
     */
    async updateOrganizationFromQueryParameter(params: {
      to: RouteLocationNormalizedGeneric;
    }) {
      // 組織IDの初期化 ⇨ 組織IDが存在しない場合はクエリパラメータから新規に取得
      const organizationId =
        (params.to.query.o as string) != undefined
          ? (params.to.query.o as string)
          : this.loggedInOrganizationInfo.id;

      await this.updateLoggedInOrganizationInfo({
        filterKey: organizationId,
        searchType: "id",
      });
    },
    async updateLoggedInOrganizationInfo(params: {
      filterKey: string;
      searchType: "code" | "id";
    }) {
      log(
        "INFO",
        "updateLoggedInOrganizationInfo triggered with params...🔥",
        params
      );
      const firestoreOps = useFirestoreDocOperation();
      let organization = null;
      // 組織情報を取得
      if (params.searchType === "code") {
        organization = await firestoreOps.getSingleDocumentByQuery({
          collectionName: "organizations",
          targetField: "code",
          operator: "==",
          targetValue: params.filterKey,
          converter: organizationConverter,
        });
      }
      if (params.searchType === "id") {
        organization = await firestoreOps.getSingleDocumentById({
          collectionName: "organizations",
          docId: params.filterKey,
          converter: organizationConverter,
        });
      }

      // 取得した組織情報をstateにセットする
      if (organization) {
        this.loggedInOrganizationInfo = organization;
      } else {
        // 取得できなかった場合は、デフォルト値をセットする
        this.loggedInOrganizationInfo = {
          id: "",
          name: "",
          code: "",
          createdAt: Timestamp.fromDate(new Date()),
          updatedAt: Timestamp.fromDate(new Date()),
        };
      }
    },
  },
});
