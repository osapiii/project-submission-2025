<script setup lang="ts">
import iconSet from "@utils/icon";
export interface Props {
  label: string;
  status?: "success" | "failed" | "copied";
  message?: string;
}

withDefaults(defineProps<Props>(), {
  status: "success",
  message: "",
});
</script>

<template>
  <UCard
    class="pl-10 pr-10 h-auto fixed top-10 right-10 z-50 border-1 shadow-md grid place-items-center bg-white place-content-center"
  >
    <div class="text-center">
      <Icon
        v-if="status == 'success'"
        name="i-heroicons-check-circle"
        color="green"
        size="32"
      />
      <Icon
        v-if="status == 'failed'"
        name="i-heroicons-exclamation-circle"
        color="red"
        size="32"
      />
      <Icon
        v-if="status == 'copied'"
        :name="iconSet.copy"
        size="32"
        color="green"
      />
    </div>
    <div class="font-bold mt-3 text-center">{{ label }}</div>
    <div v-if="status == 'failed'" class="text-xs text-error-500">
      {{ message }}
    </div>
    <div v-if="status != 'failed'" class="text-xs text-slate-700">
      {{ message }}
    </div>
  </UCard>
</template>
