import { z } from "zod";
// import { firestoreFieldValueOrTimestampSchema } from "./firestoreFieldValueOrTimestampSchema";
import { firestoreTypeConverter } from "./firestoreTypeConverter";
import { Timestamp } from "firebase/firestore";

// スキーマを定義
export const firestoreQueryRequestSchema = z.object({
  // キーが文字列で値は任意の型のオブジェクト
  requestParams: z.record(z.unknown()),
  status: z.union([
    z.literal("pending"),
    z.literal("success"),
    z.literal("failed"),
  ]),
  error: z.string().optional(),
});

// id, createdAt, updatedAtの3つのフィールドを追加した新しいスキーマを定義
export const decodedFirestoreQueryRequestSchema =
  firestoreQueryRequestSchema.extend({
    id: z.string(),
    createdAt: z.instanceof(Timestamp),
    updatedAt: z.instanceof(Timestamp),
  });

// スキーマをもとに型を作成
export type FirestoreQueryRequest = z.infer<
  typeof decodedFirestoreQueryRequestSchema
>;

// スキーマをもとにコンバーターを作成
export const firestoreQueryRequestConverter = firestoreTypeConverter(
  decodedFirestoreQueryRequestSchema
);
