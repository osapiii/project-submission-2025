<script setup lang="ts">
const formValue = defineModel<
  | string
  | { label: string; id: string }
  | { name: string; id: string }
  | { value: string; label: string }
  | string[]
>();
const emit = defineEmits(["changeFormValue"]);

watch(formValue, (newValue) => {
  emit("changeFormValue", newValue);
});

export interface Props {
  label?: string;
  options:
    | string[]
    | {
        id: string;
        label: string;
        href?: string;
        target?: string;
        avatar?: { src: string };
      }[]
    | {
        id: string;
        name: string;
      }[]
    | {
        value: string;
        label: string;
      }[];
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  icon?: string;
  disabled?: boolean;
  placeholder?: string;
  formTopLabel?: string;
}

withDefaults(defineProps<Props>(), {
  size: "md",
  options: () => ["Option 1", "Option 2", "Option 3"],
  icon: "",
  label: "選択フォーム",
  disabled: false,
  placeholder: "選択してください",
  formTopLabel: "",
});
</script>

<template>
  <span v-if="formTopLabel" class="text-xs font-bold text-slate-400">{{
    formTopLabel
  }}</span>
  <USelectMenu
    v-model="formValue"
    :options="options"
    :size="size"
    :icon="icon"
    :disabled="disabled"
    :ui="{
      input:
        'bg-red-100 border-red-500 text-red-900 placeholder-red-500 focus:ring-red-500 focus:border-red-500',
    }"
  />
</template>
