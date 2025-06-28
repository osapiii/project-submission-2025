import { z } from "zod";
import { firestoreTypeConverter } from "./firestoreTypeConverter";
import { Timestamp } from "firebase/firestore";

// スキーマを定義
export const organizationSchema = z.object({
  name: z.string(),
  code: z.string(),
});

// id, createdAt, updatedAtの3つのフィールドを追加した新しいスキーマを定義
export const decodedOrganizationSchema = organizationSchema.extend({
  id: z.string(),
  createdAt: z.instanceof(Timestamp),
  updatedAt: z.instanceof(Timestamp),
});

// スキーマをもとに型を作成
export type decodedOrganizationSchema = z.infer<
  typeof decodedOrganizationSchema
>;

// FirestoreのTypeConverterを作成
export const organizationConverter = firestoreTypeConverter(
  decodedOrganizationSchema
);
