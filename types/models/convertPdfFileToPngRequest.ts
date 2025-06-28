import { Timestamp } from "firebase/firestore";
import { z } from "zod";
import { firestoreTypeConverter } from "./firestoreTypeConverter";
import { requestJobLogZodObject } from "@models/logTypes";
// *********Request Type*********
export const convertPdfFileToPngRequestZodObject = z.object({
  metadata: z.object({
    jobType: z.literal("registerBlueprint"),
  }),
  input: z.object({
    organizationId: z.string(),
    blueprintId: z.string().nullable(),
    inputPdfGcsFilePath: z.string(),
    outputPngGcsFilePath: z.string(),
  }),
  status: z.union([
    z.literal("start"),
    z.literal("completed"),
    z.literal("failed"),
  ]),
  logs: z.array(requestJobLogZodObject),
});

// id, createdAt, updatedAtの3つのフィールドを追加した新しいスキーマを定義
export const decodedConvertPdfFileToPngRequestZodObject =
  convertPdfFileToPngRequestZodObject.extend({
    id: z.string(),
    createdAt: z.instanceof(Timestamp),
    updatedAt: z.instanceof(Timestamp),
  });

// スキーマをもとに型を作成
export type decodedConvertPdfFileToPngRequest = z.infer<
  typeof decodedConvertPdfFileToPngRequestZodObject
>;

// FirestoreのTypeConverterを作成
export const convertPdfFileToPngRequestConverter = firestoreTypeConverter(
  decodedConvertPdfFileToPngRequestZodObject
);
