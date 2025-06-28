<script setup lang="ts">
export interface Props {
  label?: string;
  orientation?: "horizontal" | "vertical";
  size?: "sm" | "md" | "lg";
}

withDefaults(defineProps<Props>(), {
  label: "",
  orientation: "horizontal",
  size: "sm",
});
</script>

<template>
  <UDivider :label="label" :orientation="orientation" :size="size" />
</template>
