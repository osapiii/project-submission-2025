import { initializeApp, getApps } from "firebase/app";
import log from "@utils/logger";
import { initializeAppCheck, ReCaptchaV3Provider } from "firebase/app-check";

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();
  const firebaseConfig = config.public.firebaseConfig;
  const recaptchaSiteKey = config.public.firebaseConfig.appCheckSiteKey;

  log("INFO", "🔥 firebaseConfig is...", firebaseConfig);

  if (!getApps().length) {
    const app = initializeApp(firebaseConfig);

    // AppCheck初期化（環境変数からSiteKeyを取得）
    if (recaptchaSiteKey && typeof recaptchaSiteKey === "string") {
      try {
        initializeAppCheck(app, {
          provider: new ReCaptchaV3Provider(recaptchaSiteKey),
          isTokenAutoRefreshEnabled: true,
        });
        log("INFO", "✅ Firebase AppCheck initialized successfully");
      } catch (error) {
        log("ERROR", "❌ Firebase AppCheck initialization failed:", error);
      }
    } else {
      log(
        "ERROR",
        "❌ NUXT_PUBLIC_RECAPTCHA_SITE_KEY is not set or invalid. AppCheck will not be initialized."
      );
    }

    log("INFO", "🚀 app is...", app);
  }

  // Emulator接続
  const emulator = config.public.firebaseEmulator;
  log("INFO", "⚙️ Firebase Emulator設定:", emulator);

  if (emulator && emulator.enabled) {
    log("INFO", "🔌 Firebase Emulatorに接続します");

    // Auth Emulator
    // const auth = getAuth();
    // const authEmulatorUrl = `http://${emulator.auth.host}:${emulator.auth.port}`;
    // log("INFO", "🔐 Auth Emulatorに接続:", authEmulatorUrl);
    // connectAuthEmulator(auth, authEmulatorUrl);

    // Firestore Emulator
    // const firestore = getFirestore();
    // log(
    //   "INFO",
    //   "📊 Firestore Emulatorに接続:",
    //   `${emulator.firestore.host}:${emulator.firestore.port}`
    // );
    // connectFirestoreEmulator(
    //   firestore,
    //   emulator.firestore.host,
    //   Number(emulator.firestore.port)
    // );

    log("INFO", "✅ すべてのFirebase Emulatorへの接続が完了しました");
  } else {
    log(
      "ERROR",
      "❌ Firebase Emulatorが無効です。本番環境のFirebaseサービスに接続します。注意: 本番環境のデータが変更される可能性があります。"
    );
  }
});
