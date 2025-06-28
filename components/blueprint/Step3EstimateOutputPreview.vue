<template>
  <div class="bg-white rounded-lg border border-blue-200 shadow-sm">
    <div class="p-4 border-b border-blue-100">
      <div class="flex justify-between items-center">
        <div>
          <h3
            class="text-lg font-semibold text-blue-800 flex items-center gap-2"
          >
            <UIcon name="i-heroicons-list-bullet" class="w-5 h-5" />
            STEP3: 明細の確定
          </h3>
          <p class="text-sm text-blue-600 mt-1">
            部材の使用個数/単価を確定します
          </p>
        </div>
        <UButton
          v-if="step3PartsBreakdown.length > 0"
          color="accent"
          variant="solid"
          size="xl"
          :loading="isUpdating"
          @click="updateStep3Output"
        >
          <template #leading>
            <UIcon name="i-heroicons-arrow-up-tray" class="w-4 h-4" />
          </template>
          更新
        </UButton>
      </div>
    </div>

    <div class="p-4">
      <div v-if="step3PartsBreakdown.length > 0">
        <!-- 製品単位でのテーブル表示 -->
        <div class="space-y-6">
          <div
            v-for="(product, productIndex) in editableStep3PartsBreakdown"
            :key="productIndex"
            class="border border-gray-200 rounded-lg overflow-hidden"
          >
            <!-- 製品ヘッダー -->
            <div
              class="bg-gradient-to-r from-gray-100 to-blue-100 px-4 py-3 border-b border-gray-200"
            >
              <div class="flex justify-between items-center">
                <div>
                  <h4 class="text-lg font-semibold text-gray-800">
                    {{ product.product_name }}
                  </h4>
                  <div class="flex items-center gap-2 mt-1">
                    <span class="text-sm text-gray-600">製造数量:</span>
                    <UInput
                      v-model.number="product.product_quantity"
                      type="number"
                      min="1"
                      size="sm"
                      class="max-w-20"
                      :ui="{ base: 'text-center' }"
                    />
                    <span class="text-sm text-gray-600">個</span>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm text-gray-600">総部材数</div>
                  <div class="text-lg font-bold text-blue-600">
                    {{ product.parts.length }}種類
                  </div>
                </div>
              </div>
            </div>

            <!-- 部材テーブル -->
            <div class="overflow-hidden">
              <!-- テーブルヘッダー -->
              <div class="bg-gray-50 px-4 py-3 border-b border-gray-200">
                <div
                  class="grid grid-cols-12 gap-4 text-xs font-semibold text-gray-700 uppercase tracking-wider"
                >
                  <div class="col-span-3">部材名</div>
                  <div class="col-span-2">カテゴリ</div>
                  <div class="col-span-1">単位数量</div>
                  <div class="col-span-1">総数量</div>
                  <div class="col-span-2">単価</div>
                  <div class="col-span-3">総額</div>
                </div>
              </div>

              <!-- テーブルボディ -->
              <div class="bg-white">
                <div
                  v-for="(part, partIndex) in product.parts"
                  :key="partIndex"
                  class="grid grid-cols-12 gap-4 px-4 py-3 text-sm border-b border-gray-100 hover:bg-gray-50 transition-colors duration-150"
                >
                  <div class="col-span-3 font-medium text-gray-900">
                    {{ part.part_name }}
                  </div>
                  <div class="col-span-2">
                    <UBadge variant="soft" color="secondary" size="xs">
                      {{ part.category }}
                    </UBadge>
                  </div>
                  <div class="col-span-1 flex justify-center">
                    <UInput
                      v-model.number="part.unit_quantity"
                      type="number"
                      min="1"
                      size="sm"
                      class="max-w-16"
                      :ui="{ base: 'text-center' }"
                    />
                  </div>
                  <div class="col-span-1 flex justify-center">
                    <UInput
                      v-model.number="part.total_quantity"
                      type="number"
                      min="1"
                      size="sm"
                      class="max-w-16"
                      :ui="{ base: 'text-center' }"
                    />
                  </div>
                  <div class="col-span-2 flex items-center gap-1">
                    <span class="text-xs text-gray-500">¥</span>
                    <UInput
                      v-model.number="part.estimated_unit_price"
                      type="number"
                      min="0"
                      size="sm"
                      class="flex-1"
                      :ui="{ base: 'text-right' }"
                      @input="updatePartTotalPrice(part)"
                    />
                  </div>
                  <div
                    class="col-span-3 text-right font-semibold text-blue-600 flex items-center justify-end"
                  >
                    ¥{{ part.total_price.toLocaleString() }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 製品別集計情報 -->
            <div
              class="bg-gradient-to-r from-gray-50 to-blue-50 px-4 py-3 border-t border-gray-200"
            >
              <div class="flex justify-between items-center">
                <div class="flex items-center gap-2">
                  <UIcon
                    name="i-heroicons-calculator"
                    class="w-4 h-4 text-blue-600"
                  />
                  <span class="text-sm font-medium text-gray-700"
                    >{{ product.product_name }} 集計</span
                  >
                </div>
                <div class="flex gap-6 text-sm">
                  <span class="flex items-center gap-1 text-gray-600">
                    部材種類:
                    <span class="font-semibold text-blue-600">{{
                      product.parts.length
                    }}</span
                    >種類
                  </span>
                  <span class="flex items-center gap-1 text-gray-600">
                    総部材費:
                    <span class="font-bold text-blue-600 text-lg"
                      >¥{{ getProductTotalCost(product) }}</span
                    >
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 全体集計情報 -->
        <div
          class="mt-6 p-4 bg-gradient-to-r from-blue-50 to-blue-50 rounded-lg border border-blue-200"
        >
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <UIcon
                name="i-heroicons-chart-pie"
                class="w-5 h-5 text-blue-600"
              />
              <span class="text-lg font-semibold text-gray-700">全体集計</span>
            </div>
            <div class="flex gap-8 text-sm">
              <span class="flex items-center gap-1 text-gray-600">
                <UIcon name="i-heroicons-cube" class="w-4 h-4" />
                製品数:
                <span class="font-semibold text-blue-600">{{
                  editableStep3PartsBreakdown.length
                }}</span
                >製品
              </span>
              <span class="flex items-center gap-1 text-gray-600">
                <UIcon name="i-heroicons-wrench-screwdriver" class="w-4 h-4" />
                総部材種類:
                <span class="font-semibold text-blue-600">{{
                  totalPartsCount
                }}</span
                >種類
              </span>
              <span class="flex items-center gap-1 text-gray-600">
                <UIcon name="i-heroicons-currency-yen" class="w-4 h-4" />
                総見積額:
                <span class="font-bold text-blue-600 text-xl"
                  >¥{{ totalEstimateAmount }}</span
                >
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
          STEP3の結果がありません
        </p>
        <p class="text-sm text-gray-400">
          STEP3が完了すると、部材分解結果がここに表示されます
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
interface PartItem {
  category: string;
  estimated_unit_price: number;
  part_name: string;
  total_price: number;
  total_quantity: number;
  unit_quantity: number;
}

interface ProductPartsBreakdown {
  product_name: string;
  product_quantity: number;
  parts: PartItem[];
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
// STEP3の部材分解データ（元データ）
const step3PartsBreakdown = computed((): ProductPartsBreakdown[] => {
  const step3Output =
    blueprintEstimateCreateProcessController
      .selectedBlueprintCostEstimationCreateJob?.step3_output;
  return (step3Output?.parts_breakdown || []) as ProductPartsBreakdown[];
});

// 編集可能な部材分解データ（reactive）
const editableStep3PartsBreakdown = ref<ProductPartsBreakdown[]>([]);

// 総部材種類数の計算（編集可能データベース）
const totalPartsCount = computed(() => {
  return editableStep3PartsBreakdown.value.reduce(
    (sum: number, product: ProductPartsBreakdown) => sum + product.parts.length,
    0
  );
});

// 総見積額の計算（編集可能データベース）
const totalEstimateAmount = computed(() => {
  const total = editableStep3PartsBreakdown.value.reduce(
    (sum: number, product: ProductPartsBreakdown) =>
      sum +
      product.parts.reduce(
        (partSum: number, part: PartItem) => partSum + (part.total_price || 0),
        0
      ),
    0
  );
  return total.toLocaleString();
});
//#endregion

//#region methods
// 製品別の総コスト計算
const getProductTotalCost = (product: ProductPartsBreakdown): string => {
  const total = product.parts.reduce(
    (sum: number, part: PartItem) => sum + (part.total_price || 0),
    0
  );
  return total.toLocaleString();
};

// 部品の総額を更新（単価が変更された時）
const updatePartTotalPrice = (part: PartItem) => {
  part.total_price =
    (part.estimated_unit_price || 0) * (part.total_quantity || 0);
};

// STEP3のoutputを更新
const updateStep3Output = async () => {
  if (isUpdating.value) return;

  isUpdating.value = true;

  try {
    // 全ての部品の総額を再計算
    editableStep3PartsBreakdown.value.forEach((product) => {
      product.parts.forEach((part) => {
        updatePartTotalPrice(part);
      });
    });

    // stateの更新
    if (
      blueprintEstimateCreateProcessController
        .selectedBlueprintCostEstimationCreateJob.step3_output
    ) {
      blueprintEstimateCreateProcessController.selectedBlueprintCostEstimationCreateJob.step3_output.parts_breakdown =
        editableStep3PartsBreakdown.value;
    }

    // Firestoreに保存
    await blueprintEstimateCreateProcessController.updateSelectedBlueprintCostEstimationCreateJob();
  } catch (error) {
    log("ERROR", "STEP3の更新でエラーが発生しました:", error);
  } finally {
    isUpdating.value = false;
  }
};

// 編集可能データを初期化
const initializeEditableData = () => {
  editableStep3PartsBreakdown.value = step3PartsBreakdown.value.map(
    (product) => ({
      ...product,
      product_quantity: product.product_quantity || 1,
      parts: product.parts.map((part) => ({
        ...part,
        unit_quantity: part.unit_quantity || 1,
        total_quantity: part.total_quantity || 1,
        estimated_unit_price: part.estimated_unit_price || 0,
        total_price: part.total_price || 0,
      })),
    })
  );
};
//#endregion

// step3PartsBreakdownが変更されたら編集可能データを初期化
watch(
  step3PartsBreakdown,
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
