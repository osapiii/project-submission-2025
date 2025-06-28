<template>
  <div class="blueprint-analysis-result space-y-6">
    <!-- 全体制御ボタン -->
    <div class="flex justify-end gap-3 mb-4">
      <UButton variant="soft" color="neutral" @click="openAllSections">
        <svg
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 8V4a1 1 0 011-1h4M4 16v4a1 1 0 001 1h4m8-16h4a1 1 0 011 1v4m-4 12h4a1 1 0 001-1v-4"
          />
        </svg>
        全て開く
      </UButton>
      <UButton variant="soft" color="neutral" @click="closeAllSections">
        <svg
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
          />
        </svg>
        全て閉じる
      </UButton>
    </div>
    <!-- 全体概要セクション -->
    <div
      class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100 overflow-hidden"
    >
      <div
        class="flex items-center justify-between p-6 cursor-pointer hover:bg-blue-100/50 transition-colors duration-200"
        @click="toggleSection('summary')"
      >
        <div class="flex items-center gap-3">
          <h3 class="text-xl font-bold text-gray-800">📋 図面の全体像</h3>
        </div>
        <div
          class="transform transition-transform duration-200"
          :class="{ 'rotate-180': !sectionsOpen.summary }"
        >
          <svg
            class="w-5 h-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </div>

      <div
        class="transition-all duration-300 ease-in-out overflow-hidden"
        :class="
          sectionsOpen.summary ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        "
      >
        <div class="px-6">
          <UTextarea
            :value="blueprint.selectedBlueprint?.preAnalysisOutput?.summary"
            class="w-full p-4 border-0 rounded-lg resize-none focus:outline-none text-gray-700 leading-relaxed"
            rows="4"
            readonly
            placeholder="図面の概要が表示されます..."
          />
        </div>
      </div>
    </div>

    <!-- 注意事項セクション -->
    <div
      class="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl border border-amber-100 overflow-hidden"
    >
      <div
        class="flex items-center justify-between p-6 cursor-pointer hover:bg-amber-100/50 transition-colors duration-200"
        @click="toggleSection('annotation')"
      >
        <div class="flex items-center gap-3">
          <h3 class="text-xl font-bold text-gray-800">
            ⚠️ 見積時のチェックポイント
          </h3>
        </div>
        <div
          class="transform transition-transform duration-200"
          :class="{ 'rotate-180': !sectionsOpen.annotation }"
        >
          <svg
            class="w-5 h-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </div>

      <div
        class="transition-all duration-300 ease-in-out overflow-hidden"
        :class="
          sectionsOpen.annotation ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        "
      >
        <UTextarea
          :value="blueprint.selectedBlueprint?.preAnalysisOutput?.annotation"
          class="w-full p-4 border-0 rounded-lg resize-none focus:outline-none text-gray-700 leading-relaxed"
          :rows="10"
          readonly
          placeholder="見積もり作成時の注意点が表示されます..."
        />
      </div>
    </div>

    <!-- ページ別分析セクション -->
    <div
      class="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl border border-emerald-100 overflow-hidden"
    >
      <div
        class="flex items-center justify-between p-6 cursor-pointer hover:bg-emerald-100/50 transition-colors duration-200"
        @click="toggleSection('pages')"
      >
        <div class="flex items-center gap-3">
          <h3 class="text-xl font-bold text-gray-800">
            📄 ページごとの詳細分析
          </h3>
        </div>
        <div
          class="transform transition-transform duration-200"
          :class="{ 'rotate-180': !sectionsOpen.pages }"
        >
          <svg
            class="w-5 h-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </div>

      <div
        class="transition-all duration-300 ease-in-out overflow-hidden"
        :class="
          sectionsOpen.pages
            ? 'max-h-[1000px] opacity-100'
            : 'max-h-0 opacity-0'
        "
      >
        <div class="px-6 pb-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="page in blueprint.selectedBlueprint?.preAnalysisOutput
                ?.pages"
              :key="page.pageCount"
              class="bg-white rounded-lg p-5 border border-gray-100 hover:shadow-lg hover:border-emerald-200 transition-all duration-300 transform hover:-translate-y-1"
            >
              <div class="flex items-center gap-3 mb-3">
                <div
                  class="bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full w-8 h-8 flex items-center justify-center text-white font-bold text-sm"
                >
                  {{ page.pageCount }}
                </div>
                <h4 class="font-semibold text-gray-800">
                  ページ {{ page.pageCount }}
                </h4>
              </div>
              <div
                class="bg-gray-50 rounded-lg p-3 border-l-4 border-emerald-400"
              >
                <p class="text-gray-700 leading-relaxed text-sm">
                  {{ page.summary || "分析結果を準備中..." }}
                </p>
              </div>
            </div>
          </div>

          <!-- ページがない場合のメッセージ -->
          <div
            v-if="
              !blueprint.selectedBlueprint?.preAnalysisOutput?.pages?.length
            "
            class="text-center py-8"
          >
            <div class="text-gray-400 text-lg mb-2">📋</div>
            <p class="text-gray-500">ページ別の分析結果がまだありません</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const blueprint = useBlueprintStore();

// 各セクションの開閉状態を管理（最初は全て開いている）
const sectionsOpen = ref({
  summary: true,
  annotation: true,
  pages: true,
});

// セクションの開閉をトグルする関数
const toggleSection = (section: keyof typeof sectionsOpen.value) => {
  sectionsOpen.value[section] = !sectionsOpen.value[section];
};

// 全てのセクションを開く
const openAllSections = () => {
  sectionsOpen.value = {
    summary: true,
    annotation: true,
    pages: true,
  };
};

// 全てのセクションを閉じる
const closeAllSections = () => {
  sectionsOpen.value = {
    summary: false,
    annotation: false,
    pages: false,
  };
};
</script>

<style scoped>
.blueprint-analysis-result {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto",
    sans-serif;
}

/* ホバー時のアニメーション効果を強化 */
.blueprint-analysis-result .hover\:shadow-lg:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* スクロールバーのスタイリング（Webkit系ブラウザ用） */
textarea::-webkit-scrollbar {
  width: 6px;
}

textarea::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* アコーディオンのスムーズなアニメーション */
.transition-all {
  transition-property: max-height, opacity;
}
</style>
