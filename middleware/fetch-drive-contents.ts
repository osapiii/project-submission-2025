import { doc, onSnapshot, getFirestore } from "firebase/firestore";
import log from "@utils/logger";

export default defineNuxtRouteMiddleware(async (to) => {
  // ミドルウェアはファイル関連ページでのみ実行
  if (!to.path.startsWith("/admin/file")) {
    return;
  }

  const googleDriveStore = useGoogleDriveStore();
  const organizationStore = useOrganizationStore();
  const globalConfigsStore = useGlobalConfigsStore();
  const globalLoading = useGlobalLoadingStore();

  // すでにデータが存在する場合はスキップ
  if (googleDriveStore.driveContents.length > 0) {
    return;
  }

  const requestId = createRandomDocId();
  globalLoading.startLoading();

  try {
    await googleDriveStore.createGoogleDriveDataFetchRequest({
      input: {
        organizationId: organizationStore.loggedInOrganizationInfo.id,
        connectedGDriveId:
          globalConfigsStore.selectedGlobalConfig.google.drive.folderId,
        response: [],
      },
      requestId: requestId,
    });

    // Firestoreのリスナー設定
    const db = getFirestore();
    const docRef = doc(
      db,
      `organizations/${organizationStore.getLoggedInOrganizationId}/requests/googleDriveDataFetchRequests/logs`,
      requestId
    );

    return new Promise((resolve) => {
      const unsubscribe = onSnapshot(
        docRef,
        (doc) => {
          if (doc.exists() && doc.data()?.status === "completed") {
            log(
              "INFO",
              "Google Drive Data Fetch Request completed:",
              doc.data()
            );
            const data = doc.data();
            googleDriveStore.driveContents = data.response.contents;
            globalLoading.stopLoading();
            unsubscribe();
            resolve();
          }
        },
        (error) => {
          log("ERROR", "Error getting document:", error);
          globalLoading.stopLoading();
          unsubscribe();
          resolve();
        }
      );
    });
  } catch (error) {
    log("ERROR", "Error in fetch-drive-contents middleware:", error);
    globalLoading.stopLoading();
    return;
  }
});
