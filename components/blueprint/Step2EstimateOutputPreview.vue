<template>
  <div class="bg-white rounded-lg border border-blue-200 shadow-sm">
    <div class="p-4 border-b border-blue-100">
      <div class="flex justify-between items-center">
        <div>
          <h3
            class="text-lg font-semibold text-blue-800 flex items-center gap-2"
          >
            <UIcon name="i-heroicons-list-bullet" class="w-5 h-5" />
            STEP2: 対象製品一覧
          </h3>
          <p class="text-sm text-blue-600 mt-1">
            図面解析により特定された製造対象製品
          </p>
        </div>
        <UButton
          v-if="step2ProductionList.length > 0"
          color="accent"
          variant="solid"
          size="xl"
          :loading="isUpdating"
          @click="updateStep2Output"
        >
          <template #leading>
            <UIcon name="i-heroicons-arrow-up-tray" class="w-4 h-4" />
          </template>
          更新
        </UButton>
      </div>
    </div>

    <div class="p-4">
      <div v-if="step2ProductionList.length > 0">
        <!-- カスタムテーブル -->
        <div class="overflow-hidden border border-gray-200 rounded-lg">
          <!-- テーブルヘッダー -->
          <div class="bg-gray-50 px-4 py-3 border-b border-gray-200">
            <div
              class="grid grid-cols-12 gap-4 text-sm font-semibold text-gray-700 uppercase tracking-wider"
            >
              <div class="col-span-4">製品名</div>
              <div class="col-span-6">説明</div>
              <div class="col-span-2">数量</div>
            </div>
          </div>

          <!-- テーブルボディ -->
          <div class="bg-white">
            <div
              v-for="(item, index) in editableStep2ProductionList"
              :key="index"
              class="grid grid-cols-12 gap-4 px-4 py-3 text-sm border-b border-gray-100 hover:bg-gray-50 transition-colors duration-150"
            >
              <div class="col-span-4 font-medium text-gray-900">
                {{ item.name }}
              </div>
              <div class="col-span-6 text-gray-600" :title="item.description">
                {{ item.description }}
              </div>
              <div class="col-span-2 flex items-center gap-2">
                <UInput
                  v-model.number="item.quantity"
                  type="number"
                  min="1"
                  size="sm"
                  class="max-w-20"
                  :ui="{ base: 'text-center' }"
                />
                <span class="text-xs text-gray-500">個</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 集計情報 -->
        <div
          class="mt-4 p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg border border-gray-200"
        >
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <UIcon
                name="i-heroicons-chart-bar"
                class="w-4 h-4 text-blue-600"
              />
              <span class="text-sm font-medium text-gray-700">集計情報</span>
            </div>
            <div class="flex gap-6 text-sm text-gray-600">
              <span class="flex items-center gap-1">
                <UIcon name="i-heroicons-cube" class="w-4 h-4" />
                製品種類数:
                <span class="font-semibold text-blue-600">{{
                  editableStep2ProductionList.length
                }}</span
                >種類
              </span>
              <span class="flex items-center gap-1">
                <UIcon name="i-heroicons-calculator" class="w-4 h-4" />
                総数量:
                <span class="font-semibold text-blue-600">{{
                  totalQuantity
                }}</span
                >個
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-8">
        <UIcon
          name="i-heroicons-exclamation-triangle"
          class="w-12 h-12 text-gray-400 mx-auto mb-4"
        />
        <p class="text-lg font-medium text-gray-500 mb-2">
          STEP2の結果がありません
        </p>
        <p class="text-sm text-gray-400">
          STEP2が完了すると、製品一覧がここに表示されます
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
//#region import
import log from "@utils/logger";
//#endregion

//#region types
interface ProductionItem {
  name: string;
  description: string;
  quantity: number;
}
//#endregion

//#region reactive-data
const isUpdating = ref(false);
//#endregion

//#region store
const blueprintEstimateCreateProcessController =
  useBlueprintEstimateCreateProcessControllerStore();
//#endregion

//#region computed
// STEP2の製品リストデータ（元データ）
const step2ProductionList = computed((): ProductionItem[] => {
  const step2Output =
    blueprintEstimateCreateProcessController
      .selectedBlueprintCostEstimationCreateJob?.step2_output;
  return (step2Output?.production_list || []) as ProductionItem[];
});

// 編集可能な製品リスト（reactive）
const editableStep2ProductionList = ref<ProductionItem[]>([]);

// 総数量の計算（編集可能データベース）
const totalQuantity = computed(() => {
  return editableStep2ProductionList.value.reduce(
    (sum: number, item: ProductionItem) => sum + (item.quantity || 0),
    0
  );
});
//#endregion

//#region methods
// STEP2のoutputを更新
const updateStep2Output = async () => {
  if (isUpdating.value) return;

  isUpdating.value = true;

  try {
    // stateの更新
    if (
      blueprintEstimateCreateProcessController
        .selectedBlueprintCostEstimationCreateJob.step2_output
    ) {
      blueprintEstimateCreateProcessController.selectedBlueprintCostEstimationCreateJob.step2_output.production_list =
        editableStep2ProductionList.value;
    }

    // Firestoreに保存
    await blueprintEstimateCreateProcessController.updateSelectedBlueprintCostEstimationCreateJob();
  } catch (error) {
    log("ERROR", "STEP2の更新でエラーが発生しました:", error);
  } finally {
    isUpdating.value = false;
  }
};

// 編集可能データを初期化
const initializeEditableData = () => {
  editableStep2ProductionList.value = step2ProductionList.value.map((item) => ({
    ...item,
    quantity: item.quantity || 1, // デフォルト値を設定
  }));
};
//#endregion

// step2ProductionListが変更されたら編集可能データを初期化
watch(
  step2ProductionList,
  (newData) => {
    if (newData.length > 0) {
      initializeEditableData();
    }
  },
  { immediate: true, deep: true }
);

//#region lifecycle-hooks
onMounted(() => {
  initializeEditableData();
});
//#endregion
</script>
