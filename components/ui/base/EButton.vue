<script setup lang="ts">
//#region store
const globalLoading = useGlobalLoadingStore();
//#endregion store

export interface Props {
  label: string;
  variant?: "solid" | "outline" | "soft" | "link" | "ghost";
  color?:
    | "primary"
    | "warning"
    | "success"
    | "info"
    | "error"
    | "background"
    | "orange"
    | "green";
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  icon?: string;
  disabled?: boolean;
  type?: "button" | "submit" | "reset" | "";
}

const {
  label = "Click me!",
  color = "primary",
  size = "md",
  disabled = false,
  variant = "solid",
  type = "",
  icon = "",
} = defineProps<Props>();
</script>

<template>
  <UButton
    class="justify-center"
    :label="label"
    :color="color"
    :variant="variant"
    :disabled="disabled"
    :size="size"
    :icon="icon"
    :type="type"
    :loading="globalLoading.isLoading"
  />
</template>
