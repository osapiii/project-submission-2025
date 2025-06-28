<template>
  <div>
    <!-- Register Modal -->
    <BlueprintEstimateCreationModal
      v-model:open="blueprintModalIsOpen"
      :model-value="blueprintStore.selectedBlueprint"
      :loading="globalLoading.isLoading"
    />
    <!-- Breadcrumb -->
    <UBreadcrumb
      class="mb-2"
      :items="[
        {
          label: '図面一覧',
          to: '/admin/report/blueprint/list',
        },
        {
          label: blueprintStore.selectedBlueprint?.name || '図面詳細',
          to: '#',
        },
      ]"
    />

    <!-- Header -->
    <EPageCommonHeader>
      <template #left>
        <div class="flex items-center gap-2">
          <div class="text-xl font-bold mb-1">
            {{ blueprintStore.selectedBlueprint?.name }}
            <span class="text-sm text-gray-500">
              ID: {{ blueprintStore.selectedBlueprint?.id }}
            </span>
          </div>
        </div>
        <div class="text-sm text-gray-500">
          {{ blueprintStore.selectedBlueprint?.description.slice(0, 100) }}
        </div>
      </template>
      <template #right>
        <div class="flex gap-2">
          <!-- 魔法的な見積もり自動作成ボタン -->
          <button
            class="magic-estimate-btn group relative px-4 py-2 text-lg font-bold text-white rounded-2xl transform transition-all duration-300 hover:scale-105 hover:shadow-2xl focus:outline-none focus:ring-4 focus:ring-purple-300 active:scale-95 hover:cursor-pointer mb-2"
            @click="startEstimateProcess"
          >
            <!-- グラデーション背景 -->
            <div
              class="absolute inset-0 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 rounded-2xl opacity-100 group-hover:opacity-90 transition-opacity duration-300"
            />

            <!-- アニメーション効果のオーバーレイ -->
            <div
              class="absolute inset-0 bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 rounded-2xl opacity-0 group-hover:opacity-30 transition-opacity duration-300 animate-pulse"
            />

            <!-- 光る効果 -->
            <div
              class="absolute inset-0 rounded-2xl shadow-lg group-hover:shadow-purple-500/50 transition-shadow duration-300"
            />

            <!-- ボタンの内容 -->
            <div class="relative flex items-center gap-3 z-10">
              <!-- 魔法の杖アイコン -->
              <svg
                class="w-6 h-6 transform group-hover:rotate-12 transition-transform duration-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                />
                <!-- 魔法のキラキラエフェクト -->
                <circle cx="18" cy="6" r="1" fill="currentColor" opacity="0.8">
                  <animate
                    attributeName="opacity"
                    values="0.8;0.2;0.8"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                </circle>
                <circle
                  cx="20"
                  cy="8"
                  r="0.5"
                  fill="currentColor"
                  opacity="0.6"
                >
                  <animate
                    attributeName="opacity"
                    values="0.6;0.1;0.6"
                    dur="1.5s"
                    repeatCount="indefinite"
                  />
                </circle>
                <circle
                  cx="16"
                  cy="4"
                  r="0.5"
                  fill="currentColor"
                  opacity="0.7"
                >
                  <animate
                    attributeName="opacity"
                    values="0.7;0.2;0.7"
                    dur="1.8s"
                    repeatCount="indefinite"
                  />
                </circle>
              </svg>

              <span class="relative">
                見積もり自動作成
                <!-- テキストの光る効果 -->
                <div
                  class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                >
                  <span
                    class="bg-gradient-to-r from-white via-yellow-200 to-white bg-clip-text text-transparent animate-pulse"
                  >
                    見積もり自動作成
                  </span>
                </div>
              </span>
            </div>

            <!-- 魔法のパーティクル効果 -->
            <div
              class="absolute -top-1 -right-1 w-3 h-3 bg-yellow-300 rounded-full opacity-0 group-hover:opacity-100 animate-ping"
            />
            <div
              class="absolute -bottom-1 -left-1 w-2 h-2 bg-pink-300 rounded-full opacity-0 group-hover:opacity-100 animate-ping"
              style="animation-delay: 0.5s"
            />
            <div
              class="absolute top-1/2 -right-2 w-1.5 h-1.5 bg-purple-300 rounded-full opacity-0 group-hover:opacity-100 animate-ping"
              style="animation-delay: 1s"
            />
          </button>
        </div>
      </template>
    </EPageCommonHeader>

    <!-- Content -->
    <!-- 表示モード切り替えボタン -->
    <div class="mb-6 flex justify-center">
      <div
        class="inline-flex items-center bg-gray-100 rounded-full p-1 shadow-inner gap-x-2"
      >
        <button
          v-for="mode in viewModes"
          :key="mode.value"
          class="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ease-in-out cursor-pointer"
          :class="[
            selectedViewMode === mode.value
              ? 'bg-white text-blue-600 shadow-md transform scale-105'
              : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50',
          ]"
          :aria-pressed="selectedViewMode === mode.value"
          @click="selectedViewMode = mode.value"
        >
          {{ mode.label }}
        </button>
      </div>
    </div>

    <!-- コンテンツエリア -->
    <div :class="getContentGridClass()">
      <!-- 読み取り情報フォーム -->
      <div v-if="showSettings" :class="getContentItemClass()">
        <div class="bg-white rounded-lg border shadow-sm">
          <div class="p-4 border-b border-gray-200">
            <h3
              class="text-lg font-semibold text-gray-900 flex items-center gap-2"
            >
              <svg
                class="w-5 h-5 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              読み取り情報
            </h3>
          </div>
          <div class="p-4">
            <BlueprintFormInput
              :blueprint="blueprintStore.selectedBlueprint"
              :disabled="true"
            />
          </div>
        </div>
      </div>

      <!-- プレビュー -->
      <div v-if="showPreview" :class="getContentItemClass()">
        <div class="bg-white rounded-lg border shadow-sm">
          <div class="p-4 border-b border-gray-200">
            <h3
              class="text-lg font-semibold text-gray-900 flex items-center gap-2"
            >
              <svg
                class="w-5 h-5 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
              プレビュー
            </h3>
          </div>
          <div class="p-4">
            <BlueprintPreview :preview-url="pdfPreviewUrl" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
//#region import
import { ref, computed, onMounted } from "vue";
// Firebase関連のインポートは統合メソッド内で処理されるため削除
import log from "@utils/logger";
//#endregion import

//#region store
const blueprintStore = useBlueprintStore();
const blueprintEstimateCreateProcessController =
  useBlueprintEstimateCreateProcessControllerStore();
const globalLoading = useGlobalLoadingStore();
//#endregion store

//#region ui-config
// 表示モードの定義
const viewModes = [
  {
    value: "settings",
    label: "読み取り情報のみ",
    icon: "svg", // 読み取り情報アイコン用のSVGコンポーネント
  },
  {
    value: "preview",
    label: "プレビューのみ",
    icon: "svg", // 目アイコン用のSVGコンポーネント
  },
  {
    value: "both",
    label: "両方表示",
    icon: "svg", // グリッドアイコン用のSVGコンポーネント
  },
];
//#endregion ui-config

//#region definePageMeta
definePageMeta({
  layout: "admin",
  middleware: ["admin-logged-in-check"],
});
//#endregion definePageMeta

//#region reactive-data
const blueprintModalIsOpen = ref(false);
const route = useRoute();
const pdfPreviewUrl = ref<string | null>(null);
const selectedViewMode = ref("both"); // デフォルトは両方表示
//#endregion reactive-data

//#region computed
const showSettings = computed(() => {
  return (
    selectedViewMode.value === "settings" || selectedViewMode.value === "both"
  );
});

const showPreview = computed(() => {
  return (
    selectedViewMode.value === "preview" || selectedViewMode.value === "both"
  );
});

const getContentGridClass = () => {
  switch (selectedViewMode.value) {
    case "settings":
    case "preview":
      return "w-full"; // max-w-4xl mx-auto から変更
    case "both":
      return "grid grid-cols-2 gap-6";
    default:
      return "grid grid-cols-2 gap-6";
  }
};

const getContentItemClass = () => {
  switch (selectedViewMode.value) {
    case "settings":
    case "preview":
      return "w-full"; // 全幅で表示
    case "both":
      return "w-full";
    default:
      return "w-full";
  }
};
//#endregion computed

//#region method
async function startEstimateProcess() {
  // 見積もりプロセス開始の統合メソッドを呼び出し
  const success =
    await blueprintEstimateCreateProcessController.startEstimateProcessWithConversation();

  if (success) {
    // 成功時のみモーダルを開く
    blueprintModalIsOpen.value = true;
    log("INFO", "見積もりプロセスが正常に開始され、モーダルを開きました 🎉");
  } else {
    log("ERROR", "見積もりプロセスの開始に失敗しました");
  }
}

onMounted(async () => {
  if (!blueprintStore.selectedBlueprintId) {
    const blueprintId = route.params.blueprintId as string;
    blueprintStore.selectedBlueprintId = blueprintId;
    await blueprintStore.fetchBlueprintById({
      blueprintId: blueprintStore.selectedBlueprintId,
    });
  }

  // PDFファイルのURLを取得
  if (blueprintStore.selectedBlueprintId) {
    const pdfUrl = await blueprintStore.getBlueprintPdfFileUrl({
      blueprintId: blueprintStore.selectedBlueprintId,
    });
    pdfPreviewUrl.value = pdfUrl;
  }
});

//#endregion method
</script>

<style scoped>
/* 魔法的なボタンのスタイル */
.magic-estimate-btn {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.magic-estimate-btn:hover {
  box-shadow: 0 15px 35px rgba(102, 126, 234, 0.6);
}

.magic-estimate-btn:active {
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

/* カスタムアニメーション */
.view-mode-transition {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ホバー効果の強化 */
button:hover {
  transform: translateY(-1px);
}

button:active {
  transform: translateY(0) scale(0.98);
}

/* フォーカス状態のスタイリング */
button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* キーフレームアニメーション */
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.magic-estimate-btn::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100px;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transition: left 0.5s;
}

.magic-estimate-btn:hover::before {
  left: 100%;
}
</style>
