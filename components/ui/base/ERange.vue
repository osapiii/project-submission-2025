<script setup lang="ts">
const rangeValue = defineModel<number>("rangeValue");

export interface Props {
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  color?: string;
}

withDefaults(defineProps<Props>(), {
  size: "md",
  color: "primary",
});
</script>

<template>
  <URange v-model="rangeValue" :size="size" />
</template>
