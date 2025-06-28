import { Timestamp } from "firebase/firestore";
import { z } from "zod";
import { firestoreTypeConverter } from "./firestoreTypeConverter";

export const adminUserCreateRequestZodObject = z.object({
  email: z.string(),
  role: z.string(),
  organizationId: z.string(),
  organizationCode: z.string(),
  status: z.union([
    z.literal("pending"),
    z.literal("done"),
    z.literal("failed"),
  ]),
});

// id, createdAt, updatedAtの3つのフィールドを追加した新しいスキーマを定義
export const decodedAdminUserCreateRequestZodObject =
  adminUserCreateRequestZodObject.extend({
    id: z.string(),
    createdAt: z.instanceof(Timestamp),
    updatedAt: z.instanceof(Timestamp),
  });

// スキーマをもとに型を作成
export type decodedAdminUserCreateRequest = z.infer<
  typeof decodedAdminUserCreateRequestZodObject
>;

// FirestoreのTypeConverterを作成
export const adminUserCreateRequestConverter = firestoreTypeConverter(
  decodedAdminUserCreateRequestZodObject
);
