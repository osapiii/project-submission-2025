<template>
  <UApp :toaster="toastConfig">
    <NuxtErrorBoundary>
      <div v-if="globalErrorStore.globalErrorModalStatus == 'triggered'">
        <EPopUpModal v-model:open="globalErrorStore.isModalOpen">
          <template #main-content>
            <UContainer>
              <div class="text-center">
                <Icon
                  size="60"
                  name="i-heroicons-x-circle-16-solid"
                  color="red"
                />
              </div>
              <div class="mb-2 font-bold mt-2">
                <p>
                  エラーが発生しました。お手数ですが、担当者までご連絡ください。
                </p>
              </div>
              <EAlert
                class="mt-3 mb-3"
                :color="'error'"
                :variant="'outline'"
                :title="globalErrorStore.selectedErrorMessage.message"
                :duration="99999"
              />
            </UContainer>
          </template>
          <template #left-button>
            <EButton
              color="background"
              variant="outline"
              label="閉じる"
              @click="globalErrorStore.globalErrorModalStatus = 'none'"
            />
          </template>
          <template #right-button>
            <EButton
              label="問い合わせ"
              @click="globalErrorStore.globalErrorModalStatus = 'none'"
            />
          </template>
        </EPopUpModal>
      </div>
      <NuxtLayout>
        <NuxtPage />
      </NuxtLayout>
    </NuxtErrorBoundary>
  </UApp>
</template>

<script lang="ts" setup>
import type { ToasterProps } from "@nuxt/ui";

//#region store
const globalErrorStore = useGlobalErrorStore();
// For Nuxt 3
definePageMeta({
  colorMode: "light",
});
onMounted(async () => {
  const firebaseAILogicStore = useFirebaseAILogic();
  firebaseAILogicStore.initializeVertexAI();
});
//#endregion store

//#region ui-config
const toastConfig: ToasterProps = {
  position: "top-right",
  portal: true,
};
//#endregion ui-config
</script>
