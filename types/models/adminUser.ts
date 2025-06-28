import { z } from "zod";
import { firestoreTypeConverter } from "./firestoreTypeConverter";
import { Timestamp } from "firebase/firestore";

// スキーマを定義
export const adminUserSchema = z.object({
  email: z.string(),
  role: z.string(),
  organizationId: z.string(),
});

// id, createdAt, updatedAtの3つのフィールドを追加した新しいスキーマを定義
export const decodedAdminUserSchema = adminUserSchema.extend({
  id: z.string(),
  createdAt: z.instanceof(Timestamp),
  updatedAt: z.instanceof(Timestamp),
});

// スキーマをもとに型を作成
export type decodedAdminUser = z.infer<typeof decodedAdminUserSchema>;

// スキーマをもとにコンバーターを作成
export const adminUserConverter = firestoreTypeConverter(
  decodedAdminUserSchema
);
