import type { materialCapacityZodObject } from "@models/productionSimulatorAvailableResources";
import type { resourceConsumptionLogZodObject } from "@models/productionSimulatorResourcesConsumptionLogs";
import type { z } from "zod";

/**
 * 指定された日付Indexに使用された原料のキャパシティを計算するメソッド
 * @param {number} params.dayIndex - 日付インデックス
 * @param {string} params.materialCode - 原料コード
 * @returns {number} その日に使用された原料のInputedAmount
 */
export function calculateMaterialCapacityAtSelectedDayIndex(params: {
  dayIndex: number;
  materialCode: string;
}): z.infer<typeof materialCapacityZodObject> {
  let inputedAmount = 0;
  const simulatorControllerStore = useProductionSimulatorController();
  simulatorControllerStore.resourceConsumptionLogs.value.forEach(
    (log: z.infer<typeof resourceConsumptionLogZodObject>) => {
      if (
        log.meta.dayIndex === params.dayIndex &&
        log.result.resouceItem.code === params.materialCode
      ) {
        inputedAmount += log.result.amount;
      }
    }
  );
  return {
    isUsedAtDay: true,
    meta: {
      materialItem:
        simulatorControllerStore.calcTargetInfo.meta.materialItems[0],
    },
    metrics: {
      // TODO: 各原料の最大使用量にアップデートする
      maxDailyInput: 100,
      inputedAmount: inputedAmount,
    },
  };
}

// TODO: Substep単位で更新する仕様にアップデートする
/**
 * 指定された日付Index / SubstepIndexまでに使用された原料のキャパシティを計算するメソッド
 * @param {number} params.dayIndex - 日付インデックス
 * @param {number} params.roundIndex - ラウンドインデックス
 * @param {number} params.substepIndex - サブステップインデックス
 * @param {string} params.materialCode - 原料コード
 * @returns {number} その日に使用された原料のInputedAmount
 */
export function calculateMaterialCapacityAtSelectedDayIndexAndSubstep(params: {
  dayIndex: number;
  roundIndex: number;
  substepIndex: number;
  materialCode: string;
}): z.infer<typeof materialCapacityZodObject> {
  let inputedAmount = 0;
  const simulatorControllerStore = useProductionSimulatorController();
  simulatorControllerStore.resourceConsumptionLogs.value.forEach(
    (log: z.infer<typeof resourceConsumptionLogZodObject>) => {
      if (
        log.meta.dayIndex === params.dayIndex &&
        log.result.resouceItem.code === params.materialCode
      ) {
        inputedAmount += log.result.amount;
      }
    }
  );
  return {
    isUsedAtDay: true,
    meta: {
      materialItem:
        simulatorControllerStore.calcTargetInfo.meta.materialItems[0],
    },
    metrics: {
      // TODO: 各原料の最大使用量にアップデートする
      maxDailyInput: 100,
      inputedAmount: inputedAmount,
    },
  };
}
