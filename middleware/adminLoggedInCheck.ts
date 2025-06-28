import { getAuth, onAuthStateChanged } from "firebase/auth";
import log from "@utils/logger";

export default defineNuxtRouteMiddleware(async () => {
  log("INFO", "adminLoggedInCheck triggered!🔥");

  // クライアントのミドルウェアを実行
  const auth = getAuth();

  // Contextの更新
  const context = useContextStore();
  context.updateContextInfo();

  // 現在ユーザーの取得
  const user = await new Promise<boolean>((resolve) => {
    onAuthStateChanged(auth, async (user) => {
      if (user) {
        log("INFO", "user is..", user);

        log("INFO", "ユーザーが存在するので組織とClaimsの初期化");
        const adminUserStore = useAdminUserStore();
        await adminUserStore.updateAuthState({
          currentUser: user,
        });
        log(
          "INFO",
          "組織とClaimsの初期化完了 adminUserStore.currentUserClaimsInfo:",
          adminUserStore.currentUserClaimsInfo
        );
        // 組織情報を更新する
        const organizationStore = useOrganizationStore();
        // globalConfigsStoreを取得
        const globalConfigsStore = useGlobalConfigsStore();
        await organizationStore.updateLoggedInOrganizationInfo({
          filterKey: adminUserStore.currentUserClaimsInfo
            .organizationCode as string,
          searchType: "code",
        });
        await globalConfigsStore.fetchSelectedGlobalConfig();
        log("INFO", "update organization operation finished!🔥");
        resolve(true);
      } else {
        log("INFO", "ユーザーが見つからないのでサインインにリダイレクト");
        resolve(false);
      }
    });
  });
  log("INFO", "user is..", user);
  if (user) {
    log("INFO", "user is found, next()🔥");
  } else {
    log("INFO", "user is not found, redirect to admin-signin");
    // Redirectする時はreturnを使用(router.pushは使用しない)
    return { path: "/admin/signin" };
  }
});
