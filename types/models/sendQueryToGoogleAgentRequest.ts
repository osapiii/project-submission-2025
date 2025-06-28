import { Timestamp } from "firebase/firestore";
import { z } from "zod";
import { firestoreTypeConverter } from "./firestoreTypeConverter";

// *********Send Query To Google Agent Request Type*********
export const sendQueryToGoogleAgentRequestZodObject = z.object({
  input: z.object({
    appName: z.string(),
    userId: z.string(),
    organizationId: z.string(),
    sessionId: z.string(),
    query: z.string(),
  }),
  output: z
    .object({
      rawResponse: z.string().optional(),
      parts: z.array(
        z.object({
          text: z.string().optional(),
          functionCall: z
            .object({
              id: z.string(),
              name: z.string(),
              args: z.record(z.any()),
            })
            .optional(),
          functionResponse: z
            .object({
              id: z.string(),
              name: z.string(),
              response: z.record(z.any()),
            })
            .optional(),
        })
      ),
    })
    .optional(),
  status: z.union([
    z.literal("pending"),
    z.literal("completed"),
    z.literal("failed"),
  ]),
});

// id, createdAt, updatedAtの3つのフィールドを追加した新しいスキーマを定義
export const decodedSendQueryToGoogleAgentRequestZodObject =
  sendQueryToGoogleAgentRequestZodObject.extend({
    id: z.string(),
    createdAt: z.instanceof(Timestamp),
    updatedAt: z.instanceof(Timestamp),
  });

// スキーマをもとに型を作成
export type decodedSendQueryToGoogleAgentRequest = z.infer<
  typeof decodedSendQueryToGoogleAgentRequestZodObject
>;

// FirestoreのTypeConverterを作成
export const sendQueryToGoogleAgentRequestConverter = firestoreTypeConverter(
  decodedSendQueryToGoogleAgentRequestZodObject
);
