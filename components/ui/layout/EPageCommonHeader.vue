<script setup lang="ts"></script>

<template>
  <div class="grid-cols-2 grid">
    <div class="justify-self-start place-self-center">
      <!-- <div class="text-xl font-bold">診断の一覧</div> -->
      <slot name="left" />
    </div>

    <div class="mb-2 justify-self-end">
      <slot name="right" />
    </div>
  </div>
  <EDivider class="mb-3" />
</template>
