<template>
  <div class="mb-10">
    <EPageCommonHeader>
      <template #right>
        <UButton
          color="accent"
          icon="i-heroicons-plus"
          variant="soft"
          size="xl"
          class="hover:scale-110 transition-all duration-200"
          @click="openBlueprintRegisterModal"
        >
          図面アップロード
        </UButton>
      </template>
    </EPageCommonHeader>
    <!-- search area -->
    <div class="mb-6">
      <UInput
        v-model="searchQuery"
        label="検索"
        class="w-1/3"
        size="xl"
        placeholder="図面名で検索"
        :icon="
          searchQuery ? 'i-heroicons-x-circle' : 'i-heroicons-magnifying-glass'
        "
      />
    </div>

    <!-- 図面一覧 -->
    <UCard :ui="{ header: 'bg-slate-500 text-white font-bold' }">
      <template #header>
        <div class="flex items-center justify-between">
          <div class="font-bold text-lg flex items-center gap-2">
            <UIcon name="i-heroicons-document" class="w-6 h-6 text-primary" />
            図面一覧
          </div>
          <!-- Sort Button -->
          <UButton
            color="neutral"
            variant="outline"
            size="sm"
            :icon="iconSet.colorSearch"
            :label="`登録順に並び替え`"
          />
        </div>
      </template>
      <div
        class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-4"
      >
        <div
          v-for="blueprint in filteredBlueprints"
          :key="blueprint.id"
          class="group bg-white rounded-2xl border border-gray-200 hover:border-primary/40 shadow-sm hover:shadow-lg transition-all duration-200 cursor-pointer overflow-hidden flex flex-col hover:scale-105"
          @click="goToDetail(blueprint.id)"
        >
          <!-- ここをaspect-squareから長方形に変更 -->
          <div class="relative w-full" style="aspect-ratio: 4/3">
            <div
              class="w-full h-full flex items-center justify-center bg-gray-50"
            >
              <NuxtImg
                v-if="
                  blueprintStore.allBlueprintPreviewImages.find(
                    (img) => img.blueprintId === blueprint.id
                  )?.previewImageUrl
                "
                :src="
                  blueprintStore.allBlueprintPreviewImages.find(
                    (img) => img.blueprintId === blueprint.id
                  )?.previewImageUrl
                "
                class="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105"
                loading="lazy"
                placeholder
              />
              <UIcon
                v-else
                name="i-heroicons-arrow-path"
                class="w-8 h-8 text-gray-400 animate-spin"
              />
            </div>
            <div class="absolute top-2 right-2">
              <UBadge color="neutral" variant="soft" size="sm">
                {{ blueprint.fileFormat }}
              </UBadge>
            </div>
          </div>
          <div class="flex-1 flex flex-col justify-between p-4 gap-2">
            <div>
              <div class="font-semibold text-gray-900 text-base line-clamp-1">
                {{ blueprint.name }}
              </div>
              <div class="text-xs text-gray-500 line-clamp-2 mt-1 min-h-[2em]">
                {{ blueprint.description }}
              </div>
              <div class="flex items-center gap-4 mt-2 text-xs text-gray-500">
                <div class="flex items-center gap-1">
                  <UIcon name="i-heroicons-calendar" class="w-4 h-4" />
                  {{
                    new Date(
                      blueprint.createdAt.seconds * 1000
                    ).toLocaleDateString("ja-JP")
                  }}
                </div>
                <div class="flex items-center gap-1">
                  <UIcon name="i-heroicons-document-text" class="w-4 h-4" />
                  {{ blueprint.pageCount || 0 }}ページ
                </div>
              </div>
            </div>
            <div class="flex justify-end pt-2 gap-1">
              <UButton
                color="error"
                variant="outline"
                size="sm"
                icon="i-heroicons-trash"
                @click="handleDeleteClick(blueprint, $event)"
              >
                削除
              </UButton>
              <UButton
                color="primary"
                variant="outline"
                size="sm"
                icon="i-heroicons-pencil-square"
              >
                編集
              </UButton>
            </div>
          </div>
        </div>
        <div
          v-if="!filteredBlueprints || filteredBlueprints.length === 0"
          class="text-gray-400 col-span-4 text-center py-8"
        >
          図面がありません
        </div>
      </div>
    </UCard>

    <!-- 作成・編集モーダル -->
    <UModal v-model:open="blueprintRegisterModalOpen">
      <template #title>
        <div class="text-lg font-bold">図面登録</div>
      </template>
      <template #content>
        <BlueprintRegisterModal
          v-model:open="blueprintRegisterModalOpen"
          mode="blueprintRegister"
          :model-value="newBlueprint"
          :loading="globalLoading.isLoading"
          @register="registerBlueprint"
        />
      </template>
      <template #footer />
    </UModal>

    <!-- 削除確認モーダルを追加 -->
    <UModal v-model:open="deleteModalIsOpen">
      <template #title>
        <div class="text-lg font-bold text-red-600">図面の削除</div>
      </template>
      <template #content>
        <UCard :ui="{ header: 'bg-red-600 text-white font-bold' }">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" />
              削除の確認
            </div>
          </template>
          <div class="p-4">
            <p class="mb-4">以下の図面を削除してもよろしいですか？</p>
            <div class="bg-gray-50 p-3 rounded-lg">
              <p class="font-semibold">{{ blueprintToDelete?.name }}</p>
              <p class="text-sm text-gray-600">
                {{ blueprintToDelete?.description.slice(0, 100) }}
              </p>
            </div>
          </div>
          <template #footer>
            <div class="flex justify-end gap-2">
              <UButton
                color="neutral"
                variant="soft"
                @click="deleteModalIsOpen = false"
              >
                キャンセル
              </UButton>
              <UButton
                color="error"
                variant="solid"
                :loading="globalLoading.isLoading"
                @click="deleteBlueprint"
              >
                削除する
              </UButton>
            </div>
          </template>
        </UCard>
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import iconSet from "@utils/icon";
import log from "@utils/logger";
import type { DecodedBlueprint } from "@models/blueprint";

//#region middleware
definePageMeta({
  layout: "admin",
  middleware: ["admin-logged-in-check"],
});
//#endregion middleware

//#region reactive-data
const searchQuery = ref("");
const blueprintRegisterModalOpen = ref(false);
const deleteModalIsOpen = ref(false);
const blueprintToDelete = ref<DecodedBlueprint | null>(null);
//#endregion reactive-data

//#region store
const blueprintStore = useBlueprintStore();
const toast = useToast();
const globalLoading = useGlobalLoadingStore();
//#endregion store

const newBlueprint = ref({
  name: "新しい図面",
  description: "新しい図面の説明",
  fileFormat: "pdf" as const,
  originalFileGcsPath: "",
  filePreviewImageGcsPath: "",
  ocrStatus: "not_scanned" as const,
  ocrResult: {
    text: "",
    status: "not_scanned" as const,
  },
});

// 検索フィルター
const filteredBlueprints = computed(() => {
  if (!searchQuery.value) return blueprintStore.allBlueprints;
  return blueprintStore.allBlueprints.filter((blueprint) =>
    blueprint.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const registerBlueprint = async () => {
  // loading start
  globalLoading.startLoading();

  try {
    if (!blueprintStore.selectedBlueprint) {
      throw new Error("図面が選択されていません");
    }

    // register blueprint
    const registeredBlueprint = await blueprintStore.registerBlueprint({
      name: blueprintStore.selectedBlueprint.name,
      description: blueprintStore.selectedBlueprint.description,
      fileFormat: blueprintStore.selectedBlueprint.fileFormat,
      ocrStatus: blueprintStore.selectedBlueprint.ocrStatus,
      preAnalysisOutput: blueprintStore.selectedBlueprint.preAnalysisOutput,
    });
    await blueprintStore.fetchBlueprints();

    if (registeredBlueprint) {
      toast.add({
        title: "図面を登録しました",
        description: `図面名: ${blueprintStore.selectedBlueprint.name} (ID: ${blueprintStore.selectedBlueprintId})`,
        color: "success",
      });
    } else {
      toast.add({
        title: "図面の登録に失敗しました",
        color: "error",
      });
    }

    // フォームをリセット
    newBlueprint.value = {
      name: "新しい図面",
      description: "新しい図面の説明",
      fileFormat: "pdf" as const,
      originalFileGcsPath: "",
      filePreviewImageGcsPath: "",
      ocrStatus: "not_scanned" as const,
      ocrResult: {
        text: "",
        status: "not_scanned" as const,
      },
    };

    blueprintRegisterModalOpen.value = false;
    await blueprintStore.fetchBlueprints();
  } catch (error) {
    log("ERROR", error);
    toast.add({
      title: "エラー",
      description: "図面の登録に失敗しました",
      color: "error",
    });
  } finally {
    // loading end
    globalLoading.stopLoading();
  }
};

//#region method
const openBlueprintRegisterModal = () => {
  blueprintRegisterModalOpen.value = true;
};

const handleDeleteClick = (blueprint: DecodedBlueprint, event: Event) => {
  event.stopPropagation();
  blueprintToDelete.value = blueprint;
  deleteModalIsOpen.value = true;
};

const deleteBlueprint = async () => {
  if (!blueprintToDelete.value) return;

  globalLoading.startLoading();
  try {
    const organization = useOrganizationStore();
    const firestoreOps = useFirestoreDocOperation();

    await firestoreOps.deleteDocument({
      collectionName: `organizations/${organization.loggedInOrganizationInfo.id}/blueprints`,
      docId: blueprintToDelete.value.id,
    });
    await blueprintStore.fetchBlueprints();
    deleteModalIsOpen.value = false;
    toast.add({
      title: "図面を削除しました",
      description: `図面名: ${blueprintToDelete.value.name}`,
      color: "success",
    });
    blueprintToDelete.value = null;
  } catch (error) {
    log("ERROR", error);
    toast.add({
      title: "エラー",
      description: "図面の削除に失敗しました",
      color: "error",
    });
  } finally {
    globalLoading.stopLoading();
  }
};

const goToDetail = async (blueprintId: string) => {
  await blueprintStore.fetchBlueprintById({ blueprintId: blueprintId });
  navigateTo(`/admin/report/blueprint/detail/${blueprintId}`);
};

onMounted(async () => {
  await blueprintStore.fetchBlueprints();
});
</script>

<style scoped>
/* スタイルが必要な場合はここに追加 */
</style>
