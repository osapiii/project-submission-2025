import log from "@utils/logger";

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.config.errorHandler = (error, instance, info) => {
    // handle error, e.g. report to a service
    log("ERROR", error, instance, info);
  };

  // Also possible
  nuxtApp.hook("vue:error", (error, instance, info) => {
    // handle error, e.g. report to a service

    log("ERROR", error, instance, info);
  });
});
