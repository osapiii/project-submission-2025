<template>
  <div class="flex flex-col">
    <label :for="label" class="text-sm font-bold text-gray-700 mb-1">{{
      formTopLabel
    }}</label>
    <input
      :id="label"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      @input="
        $emit('update:modelValue', ($event.target as HTMLInputElement).value)
      "
      class="border border-gray-400 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  </div>
</template>

<script lang="ts" setup>
defineProps<{
  label: string;
  modelValue: string | undefined;
  type: string;
  placeholder: string;
  formTopLabel: string;
}>();

defineEmits<{
  (e: "update:modelValue", value: string): void;
}>();
</script>
