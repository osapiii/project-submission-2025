<script setup lang="ts">
const links = [
  [
    {
      label: "Profile",
      avatar: {
        src: "https://avatars.githubusercontent.com/u/739984?v=4",
      },
      badge: 100,
    },
    {
      label: "Installation",
      icon: "i-heroicons-home",
      to: "/getting-started/installation",
    },
    {
      label: "Vertical Navigation",
      icon: "i-heroicons-chart-bar",
      to: "/getting-started/installation",
    },
    {
      label: "Command Palette",
      icon: "i-heroicons-command-line",
      to: "/components/command-palette",
    },
  ],
  [
    {
      label: "Examples",
      icon: "i-heroicons-light-bulb",
    },
    {
      label: "Help",
      icon: "i-heroicons-question-mark-circle",
    },
  ],
];

const ui = /* ui */ {
  size: "text-2xl",
};
</script>

<template>
  <UVerticalNavigation :links="links" :ui="ui" />
</template>
