<script setup lang="ts">
import log from "@utils/logger";
import dropDownMenu from "@utils/dropDownMenus";
//#region reactive-data
const dropdownIsOpen = ref(false);
//#endregion reactive-data

//#region method
const openDropdown = () => {
  dropdownIsOpen.value = true;
};
//#endregion method

// #region emit
// emitsオプションを定義
const emits = defineEmits(["delete", "duplicate", "archive"]);

const emitDelete = () => {
  log("INFO", "emitDelete");
  emits("delete");
};

const emitArchive = () => {
  log("INFO", "emitArchive");
  emits("archive");
};

const emitDuplicate = () => {
  log("INFO", "emitDuplicate");
  emits("duplicate");
};
// #endregion emit

//#region component-props
export interface Props {
  title: string;
  description: string;
  imageUrl?: string | Promise<string>;
  menuItemType?:
    | "archiveAndDuplicate"
    | "duplicateOnly"
    | "deleteAndRollback"
    | "deleteOnly";
  menuItemIsActive?: boolean;
  tooltipIsActive?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  title: "カードのタイトル",
  description: "カードの説明",
  imageUrl:
    "https://storage.googleapis.com/facthub-dev-assets/agent-development-kit.png",
  menuItemType: "archiveAndDuplicate",
  menuItemIsActive: true,
  tooltipIsActive: true,
});
//#endregion component-props

//#region watch-computed
const dropdown = computed(() => {
  if (props.menuItemType === "archiveAndDuplicate") {
    return dropDownMenu.archiveAndDuplicate;
  } else if (props.menuItemType === "duplicateOnly") {
    return dropDownMenu.duplicateOnly;
  } else if (props.menuItemType === "deleteAndRollback") {
    return dropDownMenu.deleteAndRollback;
  } else if (props.menuItemType === "deleteOnly") {
    return dropDownMenu.deleteOnly;
  } else {
    return dropDownMenu.archiveAndDuplicate;
  }
});
//#endregion watch-computed
</script>

<template>
  <div
    class="grid max-w-[200px] bg-background-50 z-0 shadow-md rounded-xl hover:shadow-lg cursor-pointer relative hover:scale-105 transition-transform duration-300"
  >
    <!-- 左上カスタムスロット -->
    <div class="absolute top-2 left-2 p-1">
      <slot name="customLeftCorner" />
    </div>
    <!-- Dropdownメニュー -->
    <div v-if="menuItemIsActive" class="absolute top-2 right-2 p-1">
      <UDropdown
        v-model:open="dropdownIsOpen"
        class="z-50"
        :items="dropdown"
        :ui="{ item: { disabled: 'cursor-text select-text' } }"
        :popper="{ placement: 'top-start' }"
      >
        <div @click.stop="openDropdown">
          <UIcon name="i-heroicons-ellipsis-vertical-16-solid" />
        </div>
        <!-- アーカイブ操作 -->
        <template #archive="{ item }">
          <div
            class="text-error-600 text-left w-full h-full"
            @click.stop="emitArchive"
          >
            <UIcon :name="item.icon" class="flex-shrink-0 h-4 w-4 ms-auto" />
            <span class="text-xs"> アーカイブ </span>
          </div>
        </template>
        <!-- 削除操作 -->
        <template #delete="{ item }">
          <div
            class="text-error-600 text-left w-full h-full"
            @click.stop="emitDelete"
          >
            <UIcon :name="item.icon" class="flex-shrink-0 h-4 w-4 ms-auto" />
            <span class="text-xs"> 削除 </span>
          </div>
        </template>
        <!-- 複製操作 -->
        <template #duplicate="{ item }">
          <div class="text-left w-full h-full" @click.stop="emitDuplicate">
            <UIcon :name="item.icon" class="flex-shrink-0 h-4 w-4 ms-auto" />
            <span class="text-xs"> 複製 </span>
          </div>
        </template>
      </UDropdown>
    </div>

    <div class="grid-cols-12 max-h-[180px] overflow-hidden">
      <NuxtImg :src="imageUrl" width="300" height="169" fit="contains" />
    </div>
    <div class="p-4">
      <div class="text-xs grid-cols-12 text-gray-900 font-bold">
        <slot name="title" />
      </div>
      <div class="text-[10px] grid-cols-12 mt-1 text-gray-600 m-height-[200px]">
        <slot name="body" class="max-w-[80%]" />
      </div>
      <slot name="custom" class="max-w-[80%]" />
    </div>
  </div>
</template>
