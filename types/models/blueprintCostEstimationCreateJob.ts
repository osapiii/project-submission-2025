import { z } from "zod";
import { firestoreTypeConverter } from "./firestoreTypeConverter";
import { Timestamp } from "firebase/firestore";
import { preAnalysisOutputZodObject } from "./blueprint";

// データソースの基本スキーマ
export const blueprintCostEstimationCreateJobZodObject = z.object({
  metadata: z.object({
    blueprintId: z.string(),
  }),
  input: z.object({
    pdfFilePath: z.string(),
    preAnalysisJson: preAnalysisOutputZodObject,
  }),
  output: z.object({
    costEstimation: z.string(),
  }),
  updated_at: z.any().optional(),
  allProcessCompleted: z.boolean().optional(),
  step1_output: z.any().optional(),
  step2_output: z.any().optional(),
  step3_output: z.any().optional(),
  step4_output: z.any().optional(),
  step5_output: z.any().optional(),
  currentStep: z.number().optional(),
  tmpPdfBlueprintDlUrl: z.string().optional(),
  stepIsCompleted: z.object({
    step1: z.boolean(),
    step2: z.boolean(),
    step3: z.boolean(),
    step4: z.boolean(),
    step5: z.boolean(),
  }),
});

// Firestoreから受け取る際のスキーマ（id, createdAt, updatedAt付き）
export const decodedBlueprintCostEstimationCreateJobZodObject =
  blueprintCostEstimationCreateJobZodObject.extend({
    id: z.string(),
    createdAt: z.instanceof(Timestamp),
    updatedAt: z.instanceof(Timestamp),
  });

export type DecodedBlueprintCostEstimationCreateJob = z.infer<
  typeof decodedBlueprintCostEstimationCreateJobZodObject
>;

export const blueprintCostEstimationCreateJobConverter = firestoreTypeConverter(
  decodedBlueprintCostEstimationCreateJobZodObject
);
