import { z } from "zod";
import { firestoreTypeConverter } from "./firestoreTypeConverter";
import { Timestamp } from "firebase/firestore";

export const toolCategoryZodObject = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
});

// グローバル設定のスキーマを定義
export const globalConfigsZodObject = z.object({
  google: z.object({
    sheet: z.object({
      sheetId: z.string(),
      status: z.enum(["validated", "invalid"]),
    }),
    serviceAccount: z.object({
      email: z.string(),
    }),
    drive: z.object({
      folderId: z.string(),
      status: z.enum(["validated", "invalid"]),
    }),
  }),
  dify: z.object({
    domain: z.string(),
    status: z.enum(["validated", "invalid"]),
  }),
  tool: z.object({
    categories: z.array(toolCategoryZodObject),
  }),
});

// id, createdAt, updatedAtの3つのフィールドを追加した新しいスキーマを定義
export const decodedGlobalConfigsZodObject = globalConfigsZodObject.extend({
  id: z.string(),
  createdAt: z.instanceof(Timestamp),
  updatedAt: z.instanceof(Timestamp),
});

// スキーマをもとに型を作成
export type decodedGlobalConfigsZodObject = z.infer<
  typeof decodedGlobalConfigsZodObject
>;

// FirestoreのTypeConverterを作成
export const globalConfigsConverter = firestoreTypeConverter(
  decodedGlobalConfigsZodObject
);
