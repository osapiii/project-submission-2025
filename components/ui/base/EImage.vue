<script setup lang="ts">
// ***********************
// * Type of Props from Parent Component
// ***********************
export interface Props {
  imageUrl: string | undefined;
  width?: string;
}

// ***********************
// * Props Values
// ***********************
withDefaults(defineProps<Props>(), {
  width: "100%",
});
</script>

<template>
  <template v-if="imageUrl != undefined">
    <NuxtImg :src="imageUrl" alt="hero" :width="width" />
  </template>
  <template v-if="imageUrl == undefined">
    <NuxtImg src="/noImage.jpg" alt="hero" :width="width" fit="true" />
  </template>
</template>
