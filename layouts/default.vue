<template>
  <div>
    <header />
    <main>
      <slot />
    </main>
  </div>
</template>
<script setup>
import log from "@utils/logger";
const route = useRoute();

// 特定のパスにマッチしない場合にメタ情報を更新
if (
  !route.path.startsWith("/survey/answer/") &&
  !route.path.startsWith("/diagnosis/answer/")
) {
  log("INFO", "デフォルトのメタ情報を設定します");
  useHead({
    title: "HAIFF | 管理画面",
    meta: [
      {
        name: "description",
        content: "HAIFFの管理画面です。",
      },
    ],
    link: [
      {
        rel: "icon",
        href: "https://www.qlavis.jp/favicon.ico",
        type: "image/x-icon",
      },
    ],
  });
} else {
  log("INFO", "特定のパスにマッチしたのでメタ情報を更新しません");
}
</script>

<style></style>
