// plugins/vue-loaders.js
import { defineNuxtPlugin } from "#app";
import VueLoaders from "vue-loaders";

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(VueLoaders);
});
