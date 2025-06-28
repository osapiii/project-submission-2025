<template>
  <UAlert
    v-model="alertIsOpen"
    :title="title"
    :icon="icon"
    :color="color"
    :variant="variant"
    :duration="duration"
  />
</template>

<script setup lang="ts">
const alertIsOpen = defineModel<boolean>("alertIsOpen");

export interface Props {
  title: string;
  description: string;
  variant?: "solid" | "outline" | "soft" | "subtle";
  color?: "primary" | "warning" | "success" | "info" | "error" | "background";
  icon?: string;
  duration?: number; // 追加: アラートが表示されてから消えるまでの時間（秒）
}

withDefaults(defineProps<Props>(), {
  title: "タイトルを入力します",
  description: "アラートで表示したい文言を入力します",
  color: "primary",
  variant: "solid",
  icon: "i-heroicons-command-line",
  duration: 5,
});
</script>
