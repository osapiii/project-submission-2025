<template>
  <UBadge :icon="icon" :color="color" :variant="variant">
    <slot />
  </UBadge>
</template>

<script setup lang="ts">
export interface Props {
  variant?: "solid" | "outline" | "soft" | "subtle";
  color?:
    | "primary"
    | "warning"
    | "success"
    | "info"
    | "error"
    | "background"
    | "orange";
  icon?: string;
}

withDefaults(defineProps<Props>(), {
  color: "primary",
  variant: "solid",
  icon: "i-heroicons-command-line",
});
</script>
