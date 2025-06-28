import { resolve } from "path"; // ここに追加

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  colorMode: {
    preference: "light",
  },
  css: ["~/assets/css/main.css"],
  ssr: false,
  googleFonts: {
    families: {
      "Noto+Sans+JP": true,
    },
  },
  // Auto import components
  components: [
    {
      path: "~/components",
      pathPrefix: false,
    },
  ],
  app: {
    head: {
      link: [
        {
          rel: "preconnect",
          href: "https://fonts.googleapis.com",
        },
      ],
      script: [],
    },
  },

  devtools: {
    enabled: false,
  },

  plugins: [
    "~/plugins/firebase.client.ts",
    "~/plugins/errorHandle.ts",
    "~/plugins/loader.ts",
  ],

  devServer: {
    https: {
      key: "./localhost.key",
      cert: "./localhost.crt",
    },
  },

  build: {
    // 自動インポート対象の指定
    transpile: ["@formkit/core", "@formkit/vue", "@formkit/drag-and-drop"],
  },

  vite: {
    resolve: {
      alias: {
        "@models": resolve(__dirname, "./types/models"),
        "@utils": resolve(__dirname, "./utils"),
        "@stores": resolve(__dirname, "./stores"),
        "@pages": resolve(__dirname, "./pages"),
        "@components": resolve(__dirname, "./components"),
        "@assets": resolve(__dirname, "./assets"),
      },
    },
    server: {
      watch: {
        ignored: [
          "**/node_modules/**",
          "**/backend/**",
          "**/venv/**",
          "**/dumps/**",
          "**/cloudRun/**",
          "**/*.log",
          "**/credential/**",
        ],
      },
    },
    vue: {
      script: {
        propsDestructure: true,
        defineModel: true,
      },
    },
  },

  ui: {
    theme: {
      colors: [
        "primary",
        "warning",
        "success",
        "info",
        "error",
        "background",
        "neutral",
        "accent",
        "excel",
        "purple",
      ],
    },
  },

  modules: [
    "@nuxt/ui",
    "@nuxt/test-utils/module",
    "@nuxt/eslint",
    "@pinia/nuxt",
    "@nuxt/image",
    "@nuxtjs/mdc",
    "nuxt-icon",
    "@nuxtjs/google-fonts",
    "@formkit/nuxt",
    "@vueuse/nuxt",
    "floating-vue/nuxt",
    // "nuxt-rating", // 一時的にコメントアウト
    "dayjs-nuxt",
    "@nuxtjs/mdc",
  ],
  formkit: {
    autoImport: true,
  },
  runtimeConfig: {
    public: {
      firebaseConfig: {
        apiKey: process.env.NUXT_PUBLIC_FIREBASECONFIG_APIKEY,
        authDomain: process.env.NUXT_PUBLIC_FIREBASECONFIG_AUTHDOMEIN,
        projectId: process.env.NUXT_PUBLIC_FIREBASECONFIG_PROJECTID,
        storageBucket: process.env.NUXT_PUBLIC_FIREBASECONFIG_STORAGEBUCKET,
        appId: process.env.NUXT_PUBLIC_FIREBASECONFIG_APPID,
        appCheckSiteKey: process.env.NUXT_PUBLIC_FIREBASECONFIG_APPCHECKSITEKEY,
      },
      datadog: {
        applicationId: process.env.NUXT_PUBLIC_DATADOG_APPLICATIONID,
        clientToken: process.env.NUXT_PUBLIC_DATADOG_CLIENTTOKEN,
      },
      node: {
        env: "",
      },
      firebaseEmulator: {
        enabled: process.env.USE_FIREBASE_EMULATOR === "true" || "true",
        auth: {
          host: process.env.FIREBASE_EMULATOR_AUTH_HOST || "localhost",
          port: process.env.FIREBASE_EMULATOR_AUTH_PORT || "9099",
        },
        firestore: {
          host: process.env.FIREBASE_EMULATOR_FIRESTORE_HOST || "localhost",
          port: process.env.FIREBASE_EMULATOR_FIRESTORE_PORT || "8080",
        },
        storage: {
          host: process.env.FIREBASE_EMULATOR_STORAGE_HOST || "localhost",
          port: process.env.FIREBASE_EMULATOR_STORAGE_PORT || "9000",
        },
      },
    },
  },
  nitro: {
    preset: "firebase",
    watchOptions: {
      ignored: [
        "**/venv/**",
        "**/python/**",
        "**/.venv/**",
        "**/node_modules/**",
        "**/backend/**",
        "**/dumps/**",
        "**/cloudRun/**",
        "**/*.log",
        "**/credential/**",
      ],
    },
    firebase: {
      gen: 2,
      nodeVersion: "20",
      httpsOptions: {
        region: "asia-northeast1",
      },
    },
  },

  compatibilityDate: "2024-09-28",

  typescript: {
    strict: true,
    typeCheck: false,
    shim: false,
    tsConfig: {
      outDir: ".nuxt/tsconfig",
    },
  },

  imports: {
    dirs: ["stores", "components"],
  },
});
