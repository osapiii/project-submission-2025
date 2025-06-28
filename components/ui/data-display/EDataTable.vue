<script setup lang="ts">
// clumnsの型を定義
export interface TableColumns {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
  key: string;
  sortable?: boolean | undefined;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  sort?: ((a: any, b: any, direction: "asc" | "desc") => number) | undefined;
  direction?: "asc" | "desc" | undefined;
  class?: string | undefined;
}

export interface Props {
  rows: object[];
  columns: TableColumns[];
}

withDefaults(defineProps<Props>(), {});

const ui = /* ui */ {
  wrapper: "bg-white p-2 rounded-lg shadow-md",
};
</script>

<template>
  <UTable
    :rows="rows"
    :columns="columns"
    sort-asc-icon="i-heroicons-arrow-up-20-solid"
    sort-desc-icon="i-heroicons-arrow-down-20-solid"
    :ui="ui"
  >
    <slot />
  </UTable>
</template>
