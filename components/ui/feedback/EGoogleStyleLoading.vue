<template>
  <div class="flex items-center justify-center space-x-2">
    <div
      class="dot w-4 h-4 rounded-full bg-primary-500"
      style="animation-delay: 0s"
    />
    <div
      class="dot w-4 h-4 rounded-full bg-red-500"
      style="animation-delay: 0.1s"
    />
    <div
      class="dot w-4 h-4 rounded-full bg-yellow-500"
      style="animation-delay: 0.2s"
    />
    <div
      class="dot w-4 h-4 rounded-full bg-green-500"
      style="animation-delay: 0.3s"
    />
  </div>
</template>

<style scoped>
@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.dot {
  animation: bounce 1.4s infinite ease-in-out both;
}
</style>
