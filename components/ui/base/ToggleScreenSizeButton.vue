<template>
  <div>
    <FormKit id="screenSizeToggle" type="group" @input="emitScreenSizeChange">
      <FormKitSchema :schema="toggleButtonFormkitSchema" />
    </FormKit>
  </div>
</template>

<script lang="ts" setup>
import { FormKitSchema } from "@formkit/vue";

const context = useFormKitContextById("screenSizeSwitcher");
const toggleButtonFormkitSchema = ref({
  $formkit: "togglebuttons",
  id: "screenSizeSwitcher",
  name: "screenSizeSwitcher",
  label: "",
  value: "mobile",
  enforced: true,
  options: {
    mobile: "モバイル",
    pc: "PC",
  },
});

// ***********************
// * スクリーンサイズの変更を親コンポーネントに通知
// ***********************
const emit = defineEmits(["screen-size-changed"]);
const emitScreenSizeChange = () => {
  emit("screen-size-changed", context.value?.value);
};
</script>
