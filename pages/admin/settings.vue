<template>
  <UContainer>
    <div class="mb-6">
      <h1 class="text-2xl font-bold">設定</h1>
      <p class="text-gray-500">システム全体の設定を管理します</p>
    </div>

    <div class="flex">
      <div class="w-64 mr-6">
        <ul class="space-y-2">
          <li
            v-for="tab in tabs"
            :key="tab.name"
            class="flex items-center gap-2 p-3 rounded-lg cursor-pointer transition-colors duration-200 shadow-sm bg-white"
            :class="
              activeTab === tab.name
                ? 'bg-primary-50 text-primary-500 font-bold'
                : 'hover:bg-gray-100'
            "
            @click="activeTab = tab.name"
          >
            <UIcon :name="tab.icon" class="w-5 h-5" />
            <span>{{ tab.label }}</span>
          </li>
        </ul>
      </div>

      <div class="flex-1">
        <!-- 基本設定 -->
        <div v-if="activeTab === '基本設定'">
          <SettingsBasic />
        </div>

        <!-- 外部連携 -->
        <div v-if="activeTab === '外部連携'">
          <SettingsExternalIntegration />
        </div>

        <!-- LLMモデル設定 -->
        <div v-if="activeTab === 'LLMモデル設定'">
          <SettingsLLMModels />
        </div>

        <!-- データ出力 -->
        <div v-if="activeTab === 'データ出力'">
          <SettingsDataExport />
        </div>
      </div>
    </div>
  </UContainer>
</template>

<script lang="ts" setup>
//#region middleware
definePageMeta({
  layout: "admin",
  middleware: ["admin-logged-in-check"],
});
//#endregion middleware

//#region reactive-data
// タブ設定
const tabs = [
  { name: "基本設定", label: "基本設定", icon: "i-heroicons-cog-6-tooth" },
  { name: "外部連携", label: "外部連携", icon: "i-heroicons-link" },
  {
    name: "LLMモデル設定",
    label: "LLMモデル設定",
    icon: "i-heroicons-cpu-chip",
  },
  {
    name: "データ出力",
    label: "データ出力",
    icon: "i-heroicons-document-arrow-down",
  },
];

// アクティブなタブ
const activeTab = ref("基本設定");
//#endregion reactive-data
</script>
