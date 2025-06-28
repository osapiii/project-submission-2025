<template>
  <div>
    <div v-html="parsedText" />
  </div>
</template>

<script setup lang="ts">
import markdownit from "markdown-it";
const md = markdownit({
  breaks: true, // ①\n もしくは ②<br> も改行して認識させる設定
});

export interface Props {
  markdownText: string;
}

const props = withDefaults(defineProps<Props>(), {
  markdownText: "マークダウンテキストを入力します",
});

const parsedText = computed(() => {
  return md.render(props.markdownText);
});
</script>

<style scoped></style>
