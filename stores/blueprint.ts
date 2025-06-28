/**
 * 図面管理用のPiniaストア
 * 図面のCRUD操作、ファイルアップロード、プレビュー機能を提供
 */
import { defineStore } from "pinia";
import {
  type blueprintZodObject,
  blueprintConverter,
  type DecodedBlueprint,
  type preAnalysisOutputZodObject,
} from "@models/blueprint";
import log from "@utils/logger";
import type { z } from "zod";
import { ZodError } from "zod";
import {
  getStorage,
  ref as storageRef,
  getDownloadURL,
} from "firebase/storage";
import { convertPdfFileToPngRequestConverter } from "@models/convertPdfFileToPngRequest";

export const useBlueprintStore = defineStore("blueprint", {
  state: () => ({
    // 全図面リスト
    allBlueprints: [] as DecodedBlueprint[],
    // 図面プレビュー画像情報
    allBlueprintPreviewImages: [] as {
      blueprintId: string;
      previewImageUrl: string;
      pdfUrl: string;
    }[],
    // 選択中の図面ID
    selectedBlueprintId: "",
    // 選択中の図面データ
    selectedBlueprint: {
      name: "新しい図面",
      description: "新しい図面の説明",
      fileFormat: "pdf" as const,
      preAnalysisOutput: {
        summary: "",
        annotation: "",
        pages: [],
      } as z.infer<typeof preAnalysisOutputZodObject>,
    } as z.infer<typeof blueprintZodObject>,
    // PDFプレビューURL
    pdfPreviewUrl: null as string | null,
  }),

  actions: {
    /**
     * 図面PDFのGCSファイルパスを生成
     * @param params.blueprintId 図面ID
     * @returns GCSファイルパス
     */
    returnBlueprintPdfGCSfilePath(params: { blueprintId: string }): string {
      const organization = useOrganizationStore();
      return `organizations/${organization.loggedInOrganizationInfo.id}/blueprints/${params.blueprintId}/pdf/blueprint.pdf`;
    },
    /**
     * 図面解析JSONのGCSファイルパスを生成
     * @param params.blueprintId 図面ID
     * @returns GCSファイルパス
     */
    returnBlueprintAnalysisJsonGCSfilePath(params: {
      blueprintId: string;
    }): string {
      const organization = useOrganizationStore();
      return `organizations/${organization.loggedInOrganizationInfo.id}/blueprints/${params.blueprintId}/pdf/analysis.json`;
    },
    /**
     * 新しい図面登録リクエストを作成
     * PDFアップロード、PNG変換、Firestore登録を実行
     * @param params.blueprintId 図面ID
     * @param params.fileBlob PDFファイルのBlob
     * @param params.fileInfo ファイル情報
     * @returns 成功時true、失敗時false
     */
    async createNewlyBlueprintRegisterRequest(params: {
      blueprintId: string;
      fileBlob: Blob;
      fileInfo: {
        name: string;
        type: string;
        size: number;
        lastModified: number;
      };
    }) {
      const { blueprintId, fileBlob } = params;
      const organization = useOrganizationStore();
      const firestoreOps = useFirestoreDocOperation();
      const globalError = useGlobalErrorStore();
      const storageOps = useFirebaseStorageOperations();

      try {
        // ①firebase storageにデータを保存
        const pdfFilePath = `organizations/${organization.loggedInOrganizationInfo.id}/blueprints/${blueprintId}/pdf/blueprint.pdf`;
        const convertedPngFilePath = `organizations/${organization.loggedInOrganizationInfo.id}/blueprints/${blueprintId}/png/blueprint.png`;
        try {
          await storageOps.uploadFileBySelectedType({
            bucketName: "knockai-106a4.firebasestorage.app",
            filePath: pdfFilePath,
            fileType: "application/pdf",
            rawData: fileBlob,
          });
        } catch (error) {
          log("ERROR", "Firebase Storage upload error:", error);
          globalError.createNewGlobalError({
            selectedErrorMessage: globalError.errorCodeList.blueprint.E4100,
          });
          return false;
        }

        // ②PDFをPNGに変換
        try {
          await firestoreOps.createDocument({
            collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/requests/convertPdfToPngAndCaptureRequests/logs`,
            docId: params.blueprintId,
            docData: {
              metadata: {
                jobType: "registerBlueprint",
              },
              input: {
                organizationId: organization.loggedInOrganizationInfo.id,
                blueprintId,
                inputPdfGcsFilePath: pdfFilePath,
                outputPngGcsFilePath: convertedPngFilePath,
              },
              status: "start",
              logs: [],
            },
            converter: convertPdfFileToPngRequestConverter,
          });
        } catch (error) {
          log("ERROR", "Firestore registration error:", error);
          if (error instanceof ZodError) {
            error.errors.forEach((err) => {
              log("ERROR", "Zod validation error:", err);
            });
          }
          globalError.createNewGlobalError({
            selectedErrorMessage: globalError.errorCodeList.blueprint.E4101,
          });
          return false;
        }

        // ③FirestoreにBlueprintのデータを保存
        try {
          this.registerBlueprint({
            blueprintId: params.blueprintId,
            name: this.selectedBlueprint.name,
            description: this.selectedBlueprint.description,
            fileFormat: "pdf",
            preAnalysisOutput: this.selectedBlueprint.preAnalysisOutput,
          });
        } catch (error) {
          log("ERROR", "Firestore registration error:", error);
          globalError.createNewGlobalError({
            selectedErrorMessage: globalError.errorCodeList.blueprint.E4102,
          });
        }
        return true;
      } catch (error) {
        log("ERROR", "Unexpected error in blueprint registration:", error);
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.blueprint.E4102,
        });
        return false;
      }
    },
    /**
     * 図面をFirestoreに登録
     * @param params 図面データ
     * @returns 成功時true、失敗時false
     */
    async registerBlueprint(params: {
      name: string;
      blueprintId: string;
      description: string;
      fileFormat: "pdf";
      preAnalysisOutput: {
        summary: string;
        annotation: string;
        pages: {
          pageCount: number;
          summary: string;
        }[];
      };
    }) {
      log("INFO", "registerBlueprint triggered! 図面を登録します🔥", params);
      const { name, blueprintId, description, fileFormat, preAnalysisOutput } =
        params;
      const organization = useOrganizationStore();
      const firestoreOps = useFirestoreDocOperation();
      const globalError = useGlobalErrorStore();

      try {
        await firestoreOps.createDocument({
          collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/blueprints`,
          docId: blueprintId,
          docData: {
            name,
            description,
            fileFormat,
            preAnalysisOutput,
          },
          converter: blueprintConverter,
        });
        return true;
      } catch (error) {
        log("ERROR", "Firestore registration error:", error);
        if (error instanceof ZodError) {
          error.errors.forEach((err) => {
            log("ERROR", "Zod validation error:", err);
          });
        } else {
          log("ERROR", "Unexpected error:", error);
        }
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.blueprint.E4102,
        });
        return false;
      }
    },
    async fetchBlueprintById(params: { blueprintId: string }) {
      const { blueprintId } = params;
      const firestoreOps = useFirestoreDocOperation();
      const globalError = useGlobalErrorStore();
      const organization = useOrganizationStore();
      try {
        // Blueprintドキュメントを取得
        const blueprintDoc = await firestoreOps.getSingleDocumentById({
          collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/blueprints`,
          docId: blueprintId,
          converter: blueprintConverter,
        });
        if (blueprintDoc) {
          this.selectedBlueprint = blueprintDoc;
          this.selectedBlueprintId = blueprintId;

          // PDFプレビューURLも一緒に取得・更新
          try {
            const pdfUrl = await this.getBlueprintPdfFileUrl({
              blueprintId: blueprintId,
            });
            this.pdfPreviewUrl = pdfUrl;
            log("INFO", "pdfPreviewUrlを更新しました", { blueprintId, pdfUrl });
          } catch (pdfError) {
            log("ERROR", "PDFプレビューURLの取得に失敗しました:", pdfError);
            this.pdfPreviewUrl = null;
          }
        }
      } catch (error) {
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.blueprint.E4103,
        });
        if (error instanceof ZodError) {
          error.errors.forEach((err) => {
            log("ERROR", "Zod validation error:", err);
          });
        } else {
          log("ERROR", "Unexpected error:", error);
        }
        return null;
      }
    },
    async fetchBlueprints() {
      log("INFO", "fetchBlueprints triggered! 図面一覧を取得します🔥");
      const firestoreOps = useFirestoreDocOperation();
      const globalError = useGlobalErrorStore();
      const organization = useOrganizationStore();

      this.allBlueprints = [];
      this.allBlueprintPreviewImages = [];
      try {
        const blueprintDocs =
          await firestoreOps.getAllDocumentListFromCollectionWithConverter({
            collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/blueprints`,
            converter: blueprintConverter,
          });
        blueprintDocs.forEach((blueprintDoc) => {
          this.allBlueprints.push(blueprintDoc);
        });

        // プレビュー画像とpdfのURLを取得
        for (const blueprint of this.allBlueprints) {
          try {
            const url = await this.getBlueprintPreviewImageAUrl(blueprint.id);
            const pdfUrl = await this.getBlueprintPdfFileUrl({
              blueprintId: blueprint.id,
            });
            if (url) {
              this.allBlueprintPreviewImages.push({
                blueprintId: blueprint.id,
                previewImageUrl: url,
                pdfUrl: pdfUrl || "",
              });
            }
          } catch (error) {
            log(
              "ERROR",
              `Failed to get preview image for blueprint ${blueprint.id}:`,
              error
            );
          }
        }
      } catch (error) {
        globalError.createNewGlobalError({
          selectedErrorMessage: globalError.errorCodeList.blueprint.E4104,
        });
        if (error instanceof ZodError) {
          error.errors.forEach((err) => {
            log("ERROR", "Zod validation error:", err);
          });
        } else {
          log("ERROR", "Unexpected error:", error);
        }
      }
    },
    async getBlueprintPreviewImageAUrl(
      blueprintId: string
    ): Promise<string | null> {
      try {
        const organization = useOrganizationStore();
        const storage = getStorage();
        const imagePath = `organizations/${organization.loggedInOrganizationInfo.id}/blueprints/${blueprintId}/png/blueprint.png`;
        const imageRef = storageRef(storage, imagePath);
        const url = await getDownloadURL(imageRef);
        return url;
      } catch (error) {
        log("ERROR", "Failed to get blueprint preview image URL:", error);
        return null;
      }
    },
    async getBlueprintPdfFileUrl(params: {
      blueprintId: string;
    }): Promise<string | null> {
      try {
        const organization = useOrganizationStore();
        const storage = getStorage();
        const pdfPath = `organizations/${organization.loggedInOrganizationInfo.id}/blueprints/${params.blueprintId}/pdf/blueprint.pdf`;
        const pdfRef = storageRef(storage, pdfPath);
        const url = await getDownloadURL(pdfRef);
        return url;
      } catch (error) {
        log("ERROR", "Failed to get blueprint pdf file URL:", error);
        return null;
      }
    },
  },
});
