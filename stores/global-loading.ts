import { defineStore } from "pinia";

// *********STORE*********
export const useGlobalLoadingStore = defineStore("globalLoading", {
  state: () => ({
    isLoading: false,
    loadingText: "",
  }),
  actions: {
    /**
     * loading開始
     */
    startLoading() {
      this.isLoading = true;
    },
    /**
     * loading終了
     */
    stopLoading() {
      this.isLoading = false;
    },
  },
});
