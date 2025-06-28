<template>
  <UCard>
    <template #header>
      <div class="text-sm font-bold">プレビュー</div>
    </template>
    <div v-if="previewUrl" class="sticky top-4">
      <iframe
        :src="previewUrl"
        class="w-full h-[100vh] border border-gray-200 rounded-lg"
      />
    </div>
    <div v-else>
      <USkeleton class="h-full w-full bg-slate-100" />
      <USkeleton class="h-full w-full bg-slate-100" />
    </div>
  </UCard>
</template>

<script setup lang="ts">
defineProps<{
  previewUrl: string | null;
}>();
</script>
