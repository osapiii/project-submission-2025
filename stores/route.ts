import { defineStore } from "pinia";
// import type { Route } from "vue-router"; // 未使用のため削除
import type { RouteRecordName } from "vue-router";

// *********INTERFACE*********
interface RouteInfo {
  path: RouteRecordName | null | undefined;
  name: RouteRecordName | null | undefined;
  fullPath: RouteRecordName | null | undefined;
  params: RouteParams | null | undefined;
  query: null | undefined;
}

interface RouteParams {
  diagnosisId?: string;
  contentId?: string;
  answerGroupId?: string;
  // other parameters...
}

// *********STORE*********
export const useRouteStore = defineStore("route", {
  state: () => ({
    currentRouteInfo: {} as RouteInfo,
    beforeRouteInfo: {} as RouteInfo,
  }),
});
