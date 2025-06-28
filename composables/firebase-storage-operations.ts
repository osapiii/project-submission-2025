import {
  getBytes,
  getDownloadURL,
  getStorage,
  ref as storageRef,
  uploadBytes,
} from "firebase/storage";
import log from "@utils/logger";
import { ZodError, type z } from "zod";
import Papa, { parse } from "papaparse";
import type { errorCodeKeys } from "@models/errorCode";
import { getAuth, onAuthStateChanged } from "firebase/auth";
import { onMounted, onUnmounted, ref } from "vue";

export function useFirebaseStorageOperations() {
  const isAuthenticated = ref(false);

  // 認証状態の監視を設定
  onMounted(() => {
    const auth = getAuth();
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      isAuthenticated.value = !!user;
    });

    // コンポーネントのアンマウント時に監視を解除
    onUnmounted(() => {
      unsubscribe();
    });
  });

  /**
   * 指定したバケット名とファイルパスからCSVファイルをダウンロードする
   */
  async function downloadCsvFileByBlobPath(params: {
    bucketName: string;
    filePath: string;
  }): Promise<string | undefined> {
    log(
      "INFO",
      "downloadCsvFileByBlobPath triggered🔥",
      "params is....",
      params
    );
    try {
      const storage = getStorage();
      const gerUrl = `gs://${params.bucketName}/${params.filePath}`;
      const gsReference = storageRef(storage, gerUrl);
      const url = await getDownloadURL(gsReference);

      log("INFO", "downloadCsvFileByBlobPath result📗 is...", url);
      return url;
    } catch (e) {
      log("ERROR", "downloadCsvFileByBlobPath error", e);
    }
  }

  async function downloadCsvFileWithParse<T extends z.AnyZodObject>(params: {
    bucketName: string;
    filePath: string;
    zodObject: T;
    parseErrorCode: z.infer<typeof errorCodeKeys>;
  }): Promise<z.infer<T>[] | undefined> {
    log(
      "INFO",
      "downloadCsvFileWithParse triggered🔥",
      "params is....",
      params
    );
    const storage = getStorage();
    const globalError = useGlobalErrorStore();
    const gerUrl = `gs://${params.bucketName}/${params.filePath}`;
    const gsReference = storageRef(storage, gerUrl);
    try {
      const url = await getDownloadURL(gsReference);

      log("INFO", "downloadUrl result📗 is...", url);

      const response = await fetch(url);
      const textData = await response.text();
      const parsedData = parse(textData, { header: true }).data;

      const parsedObjects = [];
      for (const row of parsedData) {
        const parsedObject = params.zodObject.parse(row);
        parsedObjects.push(parsedObject);
      }
      log("INFO", "downloaded parsed object is...", parsedObjects);
      return parsedObjects;
    } catch (error) {
      if (error instanceof ZodError) {
        error.errors.forEach((err) => {
          log("ERROR", "Zod validation error:", err);
        });
      } else {
        log("ERROR", "Unexpected error:", error);
      }
      globalError.createNewGlobalError({
        selectedErrorMessage: globalError.errorCodeList.firebaseStorage.E4401,
      });
    }
  }

  /**
   * 指定したバケット名とファイルパスのPdfファイルをダウンロードする
   * @returns PDFファイルのBlobとURL
   */
  async function downloadPdfFile(params: {
    bucketName: string;
    filePath: string;
  }): Promise<Blob | null> {
    log("INFO", "downloadPdfFile triggered🔥", "params is....", params);
    try {
      const storage = getStorage();
      const gerUrl = `gs://${params.bucketName}/${params.filePath}`;
      const gsReference = storageRef(storage, gerUrl);
      const url = await getDownloadURL(gsReference);
      log("INFO", "downloadPdfFile url result📗 is...", url);
      // URLからBlobを取得
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const blob = await response.blob();

      log("INFO", "PDF file downloaded successfully as blob");
      return blob;
    } catch (error) {
      log("ERROR", "Error downloading PDF file:", error);
      return null;
    }
  }

  /**
   * 指定したバケット名とファイルパスにPdfファイルをアップロードする
   */
  async function uploadFileBySelectedType(params: {
    bucketName: string;
    filePath: string;
    rawData: Blob;
    fileType:
      | "application/pdf"
      | "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
  }): Promise<boolean> {
    log(
      "INFO",
      "uploadFileBySelectedType triggered🔥",
      "params is....",
      params
    );
    const globalError = useGlobalErrorStore();
    try {
      // Firebase認証のチェック
      const auth = getAuth();
      if (!auth.currentUser) {
        log("ERROR", "User is not authenticated");
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.firebaseStorage.E4404,
        });
        return false;
      }

      // Blobを作成
      const blob = new Blob([params.rawData], { type: params.fileType });

      const storage = getStorage();
      const storageReference = storageRef(storage, params.filePath);

      // Blobをアップロード
      await uploadBytes(storageReference, blob);

      log("INFO", "uploadPdfFile success🎉");
      return true;
    } catch (e) {
      log("ERROR", "uploadPdfFile error", e);
      globalError.createNewGlobalError({
        selectedErrorMessage: globalError.errorCodeList.firebaseStorage.E4400,
      });
      return false;
    }
  }

  /**
   * 指定したバケット名とファイルパスにCSVファイルをアップロードする
   */
  async function uploadCsvFile(params: {
    bucketName: string;
    filePath: string;
    rawData: object[];
  }): Promise<boolean> {
    log("INFO", "uploadCsvFile triggered🔥", "params is....", params);
    const globalError = useGlobalErrorStore();
    try {
      // rawDataをCSV形式に変換
      const csv = Papa.unparse(params.rawData);

      // Blobを作成
      const blob = new Blob([csv], { type: "text/csv" });

      const storage = getStorage();
      const gsUrl = `gs://${params.bucketName}/${params.filePath}`;
      const gsReference = storageRef(storage, gsUrl);

      // Blobをアップロード
      await uploadBytes(gsReference, blob);

      log("INFO", "uploadCsvFile success🎉");
      return true;
    } catch (e) {
      log("ERROR", "uploadCsvFile error", e);
      globalError.createNewGlobalError({
        selectedErrorMessage: globalError.errorCodeList.firebaseStorage.E4400,
      });
      return false;
    }
  }

  /**
   * 指定したバケット名とファイルパスにJSONファイルをアップロードする
   */
  async function uploadJsonFile(params: {
    bucketName: string;
    filePath: string;
    rawData: object[] | object;
  }): Promise<boolean> {
    log("INFO", "uploadJsonFile triggered🔥", "params is....", params);
    const globalError = useGlobalErrorStore();
    try {
      // rawDataをJSON形式に変換
      const json = JSON.stringify(params.rawData);

      // Blobを作成
      const blob = new Blob([json], { type: "application/json" });

      const storage = getStorage();
      const gsUrl = `gs://${params.bucketName}/${params.filePath}`;
      const gsReference = storageRef(storage, gsUrl);

      // Blobをアップロード
      await uploadBytes(gsReference, blob);

      log("INFO", "uploadJsonFile success🎉");
      return true;
    } catch (e) {
      log("ERROR", "uploadJsonFile error", e);
      globalError.createNewGlobalError({
        selectedErrorMessage: globalError.errorCodeList.firebaseStorage.E4400,
      });
      return false;
    }
  }

  /**
   * 指定したバケット名とファイルパスにJSONファイルを型付けしてアップロードする
   */
  async function uploadJsonFileWithParse(params: {
    bucketName: string;
    filePath: string;
    zodObject: z.AnyZodObject;
    parseErrorCode: z.infer<typeof errorCodeKeys>;
    rawData: object[] | object;
  }): Promise<boolean> {
    log("INFO", "uploadJsonFile triggered🔥", "params is....", params);
    const globalError = useGlobalErrorStore();
    try {
      // JSONをZodObjectによるParse
      try {
        // zod parseする処理を記述
        const zodParsedJson = params.zodObject.parse(params.rawData);
        log("INFO", "zodParsedJson result📗 is...", zodParsedJson);

        // Blobを作成
        const blob = new Blob([JSON.stringify(zodParsedJson)], {
          type: "application/json",
        });

        const storage = getStorage();
        const gsUrl = `gs://${params.bucketName}/${params.filePath}`;
        const gsReference = storageRef(storage, gsUrl);

        // Blobをアップロード
        await uploadBytes(gsReference, blob);

        log("INFO", "uploadJsonFile success🎉");
        return true;
      } catch (error) {
        if (error instanceof ZodError) {
          error.errors.forEach((err) => {
            log("ERROR", "Zod validation error:", err);
          });
        } else {
          log("ERROR", "Unexpected error:", error);
        }
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.firebaseStorage.E4400,
        });
        return false;
      }
    } catch (e) {
      log("ERROR", "uploadJsonFile error", e);
      globalError.createNewGlobalError({
        selectedErrorMessage: globalError.errorCodeList.firebaseStorage.E4400,
      });
      return false;
    }
  }

  /**
   * 指定したバケット名とファイルパスからJSONファイルを受け取って、引数の任意のzodObjectによるParseを実行→成功したら返却する
   */
  async function fetchJsonFileByBlobPathWithParse<
    T extends z.AnyZodObject
  >(params: {
    bucketName: string;
    filePath: string;
    zodObject: T;
    parseErrorCode: z.infer<typeof errorCodeKeys>;
  }): Promise<z.infer<T> | undefined> {
    log(
      "INFO",
      "fetchJsonFileByBlobPathWithParse triggered🔥",
      "params is....",
      params
    );

    const storage = getStorage();
    const globalError = useGlobalErrorStore();
    try {
      // Blobを取得
      const gerUrl = `gs://${params.bucketName}/${params.filePath}`;
      const gsReference = storageRef(storage, gerUrl);
      log("INFO", "file fetch by getBytes🔥");
      const blob = await getBytes(gsReference);
      log("INFO", "file fetch completed!");

      // BlobをJSONに変換
      const json = new TextDecoder("utf-8").decode(blob);
      const parsedJson = JSON.parse(json);
      log("INFO", "parsedJson result📗 is...", parsedJson);

      // JSONをZodObjectによるParse
      try {
        // zod parseする処理を記述
        const zodParsedJson = params.zodObject.parse(parsedJson);
        log("INFO", "zodParsedJson result📗 is...", zodParsedJson);
        return zodParsedJson;
      } catch (error) {
        if (error instanceof ZodError) {
          error.errors.forEach((err) => {
            log("ERROR", "Zod validation error:", err);
          });
        } else {
          log("ERROR", "Unexpected error:", error);
        }
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.firebaseStorage.E4401,
        });
      }
    } catch (e) {
      log("ERROR", "downloadJsonFileByBlobPath error", e);
      globalError.createNewGlobalError({
        selectedErrorMessage: globalError.errorCodeList.firebaseStorage.E4401,
      });
    }
  }

  async function downloadJsonFile(params: {
    bucketName: string;
    filePath: string;
  }) {
    log("INFO", "downloadJsonFile triggered🔥", "params is....", params);
    try {
      const storage = getStorage();
      const gsReference = storageRef(storage, params.filePath);
      let url;
      try {
        url = await getDownloadURL(gsReference);
      } catch (error) {
        log("ERROR", "getDownloadURL error:", error);
        const storageError = error as { code?: string };
        switch (storageError.code) {
          case "storage/object-not-found":
            log("ERROR", "ファイルが存在しません");
            break;
          case "storage/unauthorized":
            log("ERROR", "ユーザーにオブジェクトへのアクセス権限がありません");
            break;
          case "storage/canceled":
            log("ERROR", "ユーザーがアップロードをキャンセルしました");
            break;
          case "storage/unknown":
            log(
              "ERROR",
              "不明なエラーが発生しました。サーバーレスポンスを確認してください"
            );
            break;
          default:
            log("ERROR", `ストレージエラー: ${storageError.code || "unknown"}`);
            break;
        }
        throw error;
      }
      log("INFO", "Downloading JSON file via URL...", url);
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const jsonData = await response.json();
      log("INFO", "JSON file downloaded successfully", jsonData);
      return jsonData;
    } catch (error) {
      log("ERROR", "Error downloading JSON file:", error);
    }
  }

  return {
    downloadCsvFileByBlobPath,
    downloadCsvFileWithParse,
    downloadJsonFile,
    downloadPdfFile,
    uploadCsvFile,
    uploadFileBySelectedType,
    uploadJsonFile,
    uploadJsonFileWithParse,
    fetchJsonFileByBlobPathWithParse,
  };
}
