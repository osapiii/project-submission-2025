import { z } from "zod";
import { firestoreTypeConverter } from "./firestoreTypeConverter";
import { Timestamp } from "firebase/firestore";

// ページ分析結果のスキーマ
export const pageAnalysisZodObject = z.object({
  pageCount: z.number(),
  summary: z.string(),
});

// 事前分析出力のスキーマ
export const preAnalysisOutputZodObject = z.object({
  summary: z.string(),
  annotation: z.string(),
  pages: z.array(pageAnalysisZodObject),
});

// データソースの基本スキーマ
export const blueprintZodObject = z.object({
  name: z.string(),
  description: z.string(),
  fileFormat: z.enum(["pdf"]),
  preAnalysisOutput: preAnalysisOutputZodObject,
});

// Firestoreから受け取る際のスキーマ（id, createdAt, updatedAt付き）
export const decodedBlueprintZodObject = blueprintZodObject.extend({
  id: z.string(),
  createdAt: z.instanceof(Timestamp),
  updatedAt: z.instanceof(Timestamp),
});

export type DecodedBlueprint = z.infer<typeof decodedBlueprintZodObject>;

export const blueprintConverter = firestoreTypeConverter(
  decodedBlueprintZodObject
);
