<script setup lang="ts">
const formValue = defineModel<string>();
const emit = defineEmits(["changeFormValue"]);
watch(formValue, (newValue) => {
  emit("changeFormValue", newValue);
});
export interface Props {
  label?: string;
  formTopLabel?: string;
  placeholder?: string;
  disabled?: boolean;
  width?: string;
}

withDefaults(defineProps<Props>(), {
  placeholder: "入力してください",
  label: "入力フォーム",
  disabled: false,
  formTopLabel: "",
  width: "w-full",
});
</script>

<template>
  <span v-if="formTopLabel" class="text-xs font-bold text-slate-400">{{
    formTopLabel
  }}</span>
  <UTextarea
    v-model="formValue"
    :placeholder="placeholder"
    :disabled="disabled"
  />
</template>
