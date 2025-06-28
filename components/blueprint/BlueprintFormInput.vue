<template>
  <UCard>
    <template #header>
      <div class="text-sm font-bold">図面情報</div>
    </template>
    <div class="flex flex-col gap-4">
      <div>
        <div class="text-sm font-bold">図面名称</div>
        <UInput
          v-model="blueprint.selectedBlueprint.name"
          placeholder="アップロードしたファイル名が自動的に設定されます"
          class="w-full"
          size="xl"
          :disabled="disabled"
        />
      </div>
      <div v-if="blueprint.selectedBlueprint">
        <div
          v-if="isGeneratingDescription"
          class="flex flex-col items-center justify-center gap-4 p-8"
        >
          <EGoogleStyleLoading />
          <span class="text-lg font-bold text-gray-600"
            >🤖 AIが図面を読み取っています...</span
          >
        </div>
        <BlueprintAnalysisResult
          v-else-if="
            blueprint.selectedBlueprint.preAnalysisOutput?.pages.length
          "
        />
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
const blueprint = useBlueprintStore();

defineProps<{
  disabled?: boolean;
  isGeneratingDescription?: boolean;
}>();
</script>
