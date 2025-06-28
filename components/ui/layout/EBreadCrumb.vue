<template><UBreadcrumb :links="links" :ui="{ li: 'text-xs' }" /></template>

<script setup lang="ts">
import type { BreadcrumbLink } from "node_modules/@nuxt/ui/dist/runtime/types";

export interface Props {
  links: BreadcrumbLink[];
}

defineProps<Props>();
</script>
