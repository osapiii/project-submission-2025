<template>
  <div>
    <EFullScreenLoading :active="globalLoading.isLoading" />
    <!-- ヘッダー -->
    <header class="fixed top-0 left-0 w-full z-10 shadow-lg">
      <div
        class="flex justify-between bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900 backdrop-blur-sm border-b border-blue-700/50"
      >
        <!-- 左側 -->
        <div class="flex items-center">
          <!-- ロゴ画像 -->
          <div class="p-3">
            <div
              class="text-2xl text-white font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent"
            >
              KnockAI
            </div>
          </div>
        </div>
        <!-- 右側 -->
        <div class="flex items-center">
          <!-- ログイン情報 -->
          <div class="p-3">
            <div class="flex items-center text-xs">
              <div class="text-blue-100 mr-3 font-medium">
                {{ organization.loggedInOrganizationInfo.name }}
              </div>
              <div class="text-blue-100 mr-2">
                <EBadge
                  variant="outline"
                  color="background"
                  class="bg-blue-700/50 border-blue-600 text-blue-100"
                  ><span class="text-blue-100">{{
                    (adminUser.currentUserClaimsInfo as Record<string, any>)?.email || "未設定"
                  }}</span></EBadge
                >
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
    <!-- サイドバーとメインコンテンツ -->
    <div
      class="flex h-screen bg-gradient-to-br from-slate-50 to-slate-100 mt-12"
    >
      <!-- サイドバーWrapperの定義 -->
      <div
        class="min-h-screen bg-gradient-to-b from-blue-900 via-blue-800 to-blue-900 shadow-2xl border-r border-blue-700/50 transition-all duration-300 ease-in-out"
        :class="sidebarCollapsed ? 'w-16' : 'w-[6.5rem]'"
      >
        <!-- サイドバーのFlexbox -->
        <div
          class="sidebar min-h-screen pt-4 transition-all duration-300 ease-in-out"
          :class="sidebarCollapsed ? 'w-16' : 'w-[6.5rem]'"
        >
          <div class="flex h-screen flex-col justify-between pt-2 pb-6">
            <!-- 上方配置のメニュー -->
            <div>
              <!-- 折り畳みボタン -->
              <div class="px-2 mb-4">
                <button
                  class="w-full p-3 rounded-xl transition-all duration-300 ease-in-out transform hover:scale-105 hover:bg-blue-700/50 text-blue-100 hover:text-white"
                  @click="toggleSidebar"
                >
                  <div class="flex flex-col items-center justify-center">
                    <UIcon
                      :name="
                        sidebarCollapsed
                          ? 'i-heroicons-bars-3'
                          : 'i-heroicons-chevron-left'
                      "
                      class="w-6 h-6 mb-1"
                    />
                  </div>
                </button>
              </div>

              <!-- メニューアイテム -->
              <ul class="space-y-4 tracking-wide px-2">
                <template v-for="link in filteredLinks" :key="link.to">
                  <li
                    class="p-3 rounded-xl transition-all duration-300 ease-in-out transform hover:scale-105"
                    :class="{
                      'bg-white shadow-lg': isActiveRoute(link.target),
                      'hover:bg-blue-700/50': !isActiveRoute(link.target),
                    }"
                    @click="link.click"
                  >
                    <div
                      class="flex flex-col items-center justify-center cursor-pointer transition-colors duration-200"
                      :class="{
                        'text-blue-700': isActiveRoute(link.target),
                        'text-blue-100 hover:text-white': !isActiveRoute(
                          link.target
                        ),
                      }"
                    >
                      <UIcon :name="link.icon" class="w-8 h-8 mb-1" />
                      <div
                        v-if="!sidebarCollapsed"
                        class="text-[10px] text-center leading-tight whitespace-nowrap font-medium"
                      >
                        {{ link.label }}
                      </div>
                    </div>
                  </li>
                </template>
              </ul>
            </div>
            <!-- 下方配置のメニュー -->
            <div class="mb-12 px-2">
              <div
                class="flex flex-col items-center justify-center text-blue-100 hover:text-white cursor-pointer p-3 rounded-xl transition-all duration-300 hover:bg-blue-700/50 transform hover:scale-105"
                @click="auth.signOut"
              >
                <UIcon :name="iconSet.logout" class="w-8 h-8 mb-1" />
                <div
                  v-if="!sidebarCollapsed"
                  class="text-[10px] whitespace-nowrap font-medium"
                >
                  サインアウト
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <main
        class="flex-grow bg-gradient-to-br from-slate-50 to-slate-100 pt-[2%] pl-[6%] pr-[6%] overflow-y-auto transition-all duration-300 ease-in-out"
      >
        <!-- メインコンテンツはここに配置します -->
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import iconSet from "@utils/icon";

//#region store
const router = useRouter();
const route = useRoute();
const auth = useAdminUserStore();
const organization = useOrganizationStore();
const adminUser = useAdminUserStore();
const context = useContextStore();
const globalLoading = useGlobalLoadingStore();
//#endregion store

//#region sidebar-state
const sidebarCollapsed = ref(false);

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
};
//#endregion sidebar-state

//#region ui-config
const baseLinks = [
  {
    label: "図面",
    icon: iconSet.paper,
    target: "datasource",
    click: () =>
      router.push({
        name: "admin-report-blueprint-list",
      }),
    productType: "report",
  },
];

const filteredLinks = computed(() => {
  return baseLinks.filter((link) => {
    return link.productType == context.productType;
  });
});
//#endregion ui-config

//#region watch-computed
const isActiveRoute = (target: string) => {
  const routeName = route.name as string;

  if (target === "dashboard" && routeName?.startsWith("admin-dashboard")) {
    return true;
  } else if (target === "space" && routeName?.startsWith("admin-space")) {
    return true;
  } else if (target === "tool" && routeName?.startsWith("admin-tool")) {
    return true;
  } else if (
    target === "group" &&
    (routeName?.startsWith("admin-group") ||
      routeName === "admin-answerUserGroup-list")
  ) {
    return true;
  } else if (target === "file" && routeName?.startsWith("admin-file")) {
    return true;
  } else if (
    target === "datasource" &&
    (routeName?.startsWith("admin-datasource") ||
      routeName?.startsWith("admin-report-blueprint"))
  ) {
    return true;
  } else if (target === "capture" && routeName?.startsWith("admin-slide")) {
    return true;
  } else if (
    target === "template" &&
    (routeName?.startsWith("admin-files") ||
      routeName === "admin-template-list")
  ) {
    return true;
  } else if (target === "setting" && routeName === "admin-settings") {
    return true;
  } else if (target === "diagnosis" && routeName === "admin-diagnosis-list") {
    return true;
  } else if (target === "logic" && routeName === "admin-logic-list") {
    return true;
  } else if (target === "survey" && routeName === "admin-survey-list") {
    return true;
  }

  return false;
};

const forcusedMenuTargetName = computed(() => {
  if (route.name == "admin-diagnosis-list") {
    return "diagnosis";
  } else if (route.name == "admin-logic-list") {
    return "logic";
  } else if (route.name == "admin-survey-list") {
    return "survey";
  } else if (route.name == "admin-answerUserGroup-list") {
    return "group";
  } else if (route.name == "admin-template-list") {
    return "template";
  } else if (route.name == "admin-settings") {
    return "setting";
  } else {
    return "";
  }
});
//#endregion watch-computed

//#region event-handlers
onMounted(() => {
  window.addEventListener("keydown", (_event) => {
    // if (event.code === "Space") {
    //   event.preventDefault(); // スクロールを防ぐ
    //   toggleHelpText();
    // }
  });
});
//#endregion event-handlers
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-enter-to,
.slide-leave-from {
  transform: translateX(0);
}

.slide-leave-to {
  transform: translateX(-100%);
}
</style>
