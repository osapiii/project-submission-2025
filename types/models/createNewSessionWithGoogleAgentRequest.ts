import { Timestamp } from "firebase/firestore";
import { z } from "zod";
import { firestoreTypeConverter } from "./firestoreTypeConverter";

// *********Create New Session With Google Agent Request Type*********
export const createNewSessionWithGoogleAgentRequestZodObject = z.object({
  input: z.object({
    appName: z.string(),
    organizationId: z.string(),
    userId: z.string(),
    sessionId: z.string(),
  }),
  status: z.union([
    z.literal("pending"),
    z.literal("completed"),
    z.literal("failed"),
  ]),
});

// id, createdAt, updatedAtの3つのフィールドを追加した新しいスキーマを定義
export const decodedCreateNewSessionWithGoogleAgentRequestZodObject =
  createNewSessionWithGoogleAgentRequestZodObject.extend({
    id: z.string(),
    createdAt: z.instanceof(Timestamp),
    updatedAt: z.instanceof(Timestamp),
  });

// スキーマをもとに型を作成
export type decodedCreateNewSessionWithGoogleAgentRequest = z.infer<
  typeof decodedCreateNewSessionWithGoogleAgentRequestZodObject
>;

// FirestoreのTypeConverterを作成
export const createNewSessionWithGoogleAgentRequestConverter =
  firestoreTypeConverter(
    decodedCreateNewSessionWithGoogleAgentRequestZodObject
  );
