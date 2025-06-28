<template>
  <transition name="fade">
    <div v-if="active" class="fullscreen-loading">
      <vue-loaders name="ball-scale-ripple" color="#34ebc0" scale="1" />
    </div>
  </transition>
</template>

<script setup lang="ts">
import "vue-loaders/dist/vue-loaders.css";

export interface Props {
  active: boolean;
  variant: "spinner" | "ring";
  color: string;
}

withDefaults(defineProps<Props>(), {
  active: false,
  variant: "spinner",
  color: "#008080",
});
</script>

<style scoped>
.fullscreen-loading {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.1);
  z-index: 9999;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>
