import { defineStore } from "pinia";
// import type { z } from "zod"; // 未使用のため削除

// *********STORE*********
export const useContextStore = defineStore("context", {
  state: () => ({
    runtimeConfig: {},
    environmentType: "local" as "local" | "dev" | "stg" | "prod",
    bucketName: "enostech-sandbox.appspot.com",
    productType: "report" as "ai-management" | "report",
    isMobile: false,
    helpTextIsActive: true,
    firebaseToken: "",
  }),
  actions: {
    updateContextInfo(): void {
      const runtimeConfig = useRuntimeConfig();
      this.runtimeConfig = runtimeConfig;
      // 環境情報の更新
      if (window.location.host.includes("localhost")) {
        this.environmentType = "local";
        this.bucketName = "enostech-sandbox.appspot.com";
      } else if (window.location.host.includes("enostech-sandbox")) {
        this.environmentType = "dev";
        this.bucketName = "enostech-sandbox.appspot.com";
      } else if (window.location.host.includes("qravis")) {
        this.environmentType = "prod";
        this.bucketName = "qlavisprod.appspot.com";
      } else {
        this.environmentType = "dev";
        this.bucketName = "enostech-sandbox.appspot.com";
      }
      // モバイル判定
      this.isMobile = window.innerWidth <= 768;
    },
    returnDebutInfoIsActive(): boolean {
      return (
        (this.environmentType == "local" || this.environmentType == "dev") &&
        !this.isMobile
      );
    },
  },
});
