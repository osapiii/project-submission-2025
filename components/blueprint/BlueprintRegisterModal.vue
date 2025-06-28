<template>
  <UModal
    :open="open"
    fullscreen
    class="m-8 rounded-lg"
    @update:open="(val) => $emit('update:open', val)"
  >
    <template #content>
      <UCard :ui="{ header: 'bg-sky-800 text-white font-bold' }">
        <template #header>
          <div class="flex justify-between items-center">
            <div>AIと会話して見積書作成を進めましょう</div>
            <div class="flex gap-2 items-center">
              <UButton
                v-if="registerIsAvailable"
                color="accent"
                variant="solid"
                size="xl"
                class="hover:scale-105 transition-all duration-300"
                :disabled="!registerIsAvailable || globalLoading.isLoading"
                :loading="globalLoading.isLoading"
                @click="registerFile"
              >
                <template v-if="globalLoading.isLoading"> 登録中... </template>
                <template v-else-if="registerIsAvailable">
                  図面を登録✏️
                </template>
              </UButton>

              <UButton
                color="neutral"
                variant="soft"
                size="xl"
                icon="i-heroicons-x-mark"
                @click="emit('update:open', false)"
              >
                閉じる
              </UButton>
            </div>
          </div>
        </template>

        <div class="pr-6 pl-6">
          <!-- STEP 0: 分析結果取得 -->
          <div v-if="activatedStepIndex === 0" class="relative">
            <div class="grid grid-cols-2 gap-6">
              <!-- 左カラム: 入力フォーム -->
              <div class="flex flex-col gap-4">
                <!-- ファイル選択済み時のヘッダー -->
                <div
                  v-if="uploadFile"
                  class="flex items-center justify-between"
                >
                  <div class="flex items-center gap-2">
                    <UIcon
                      name="i-heroicons-document"
                      class="w-6 h-6 text-primary"
                    />
                    <span class="font-medium">{{ uploadFile.name }}</span>
                    <span class="text-sm text-gray-500">
                      ({{ ((uploadFile.size ?? 0) / 1024 / 1024).toFixed(2) }}
                      MB)
                    </span>
                  </div>
                  <UButton
                    color="neutral"
                    variant="soft"
                    icon="i-heroicons-arrow-path"
                    @click="resetUploadFile"
                  >
                    リセット
                  </UButton>
                </div>

                <BlueprintFormInput
                  v-if="uploadFile"
                  :blueprint="blueprintStore.selectedBlueprint"
                  :is-generating-description="isGeneratingDescription"
                />
                <!-- ファイルアップロードエリア -->
                <div class="mt-4">
                  <!-- ファイル未選択時 -->
                  <div
                    v-if="!uploadFile"
                    class="border-2 border-dashed border-gray-300 rounded-lg p-8 flex flex-col items-center justify-center min-h-[200px] hover:border-primary transition-colors cursor-pointer"
                    @click="fileInputRef?.click()"
                  >
                    <input
                      ref="fileInputRef"
                      type="file"
                      accept=".pdf"
                      class="hidden"
                      @change="handleFileSelect"
                    />
                    <div
                      class="text-center w-full h-full flex flex-col items-center justify-center"
                    >
                      <UIcon
                        name="i-heroicons-cloud-arrow-up"
                        class="w-12 h-12 text-gray-400 mb-4"
                      />
                      <div class="text-gray-600 mb-2 font-bold">
                        ここをクリックしてファイルを選択
                      </div>
                      <div class="text-sm text-gray-500">
                        PDFファイルのみ対応しています
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 次のステップボタン -->
                <div v-if="canProceedToNextStep" class="flex justify-end mt-4">
                  <UButton
                    color="primary"
                    variant="solid"
                    @click="goToNextStep"
                  >
                    次のステップへ
                  </UButton>
                </div>
              </div>

              <!-- 右カラム: プレビュー -->
              <BlueprintPreview :preview-url="previewUrl" />
            </div>
          </div>

          <!-- STEP 1: 見積もり製品決定 -->
          <div v-else-if="activatedStepIndex === 1" class="relative">
            <div class="text-center py-12">
              <UIcon
                name="i-heroicons-cube"
                class="w-16 h-16 text-primary mx-auto mb-4"
              />
              <h3 class="text-xl font-bold mb-2">見積もり製品決定</h3>
              <p class="text-gray-600 mb-6">
                分析結果を基に、適切な製品を選択してください
              </p>
              <!-- ここに製品選択のUIを追加予定 -->
              <div class="flex justify-between">
                <UButton
                  color="neutral"
                  variant="soft"
                  @click="goToPreviousStep"
                >
                  前のステップへ
                </UButton>
                <UButton color="primary" variant="solid" @click="goToNextStep">
                  次のステップへ
                </UButton>
              </div>
            </div>
          </div>

          <!-- STEP 2: 使用部品決定 -->
          <div v-else-if="activatedStepIndex === 2" class="relative">
            <div class="text-center py-12">
              <UIcon
                name="i-heroicons-cog-6-tooth"
                class="w-16 h-16 text-primary mx-auto mb-4"
              />
              <h3 class="text-xl font-bold mb-2">使用部品決定</h3>
              <p class="text-gray-600 mb-6">
                製品に必要な部品を選択・設定してください
              </p>
              <!-- ここに部品選択のUIを追加予定 -->
              <div class="flex justify-between">
                <UButton
                  color="neutral"
                  variant="soft"
                  @click="goToPreviousStep"
                >
                  前のステップへ
                </UButton>
                <UButton color="primary" variant="solid" @click="goToNextStep">
                  次のステップへ
                </UButton>
              </div>
            </div>
          </div>

          <!-- STEP 3: 見積もり完了 -->
          <div v-else-if="activatedStepIndex === 3" class="relative">
            <div class="text-center py-12">
              <UIcon
                name="i-heroicons-check-circle"
                class="w-16 h-16 text-green-500 mx-auto mb-4"
              />
              <h3 class="text-xl font-bold mb-2">見積もり完了</h3>
              <p class="text-gray-600 mb-6">
                見積もりが完了しました。内容を確認してください
              </p>
              <!-- ここに見積もり結果のUIを追加予定 -->
              <div class="flex justify-between">
                <UButton
                  color="neutral"
                  variant="soft"
                  @click="goToPreviousStep"
                >
                  前のステップへ
                </UButton>
                <UButton
                  color="success"
                  variant="solid"
                  :disabled="!registerIsAvailable || globalLoading.isLoading"
                  :loading="globalLoading.isLoading"
                  @click="registerFile"
                >
                  <template v-if="globalLoading.isLoading">
                    登録中...
                  </template>
                  <template v-else> 見積もりを完了する </template>
                </UButton>
              </div>
            </div>
          </div>
        </div>
      </UCard>
    </template>
  </UModal>
</template>

<script setup lang="ts">
//#region import
import type { Ref } from "vue";
import { ref, watch, onBeforeUnmount, computed, onMounted } from "vue";
import log from "@utils/logger";
//#endregion

//#region props & emits
const props = defineProps({
  open: Boolean,
  mode: { type: String, default: "blueprintRegister" },
  modelValue: { type: Object, required: true },
  loading: { type: Boolean, default: false },
});
const emit = defineEmits<{
  (e: "update:open", value: boolean): void;
  (e: "register"): void;
}>();
//#endregion

//#region store
const blueprintStore = useBlueprintStore();
const globalLoading = useGlobalLoadingStore();
const toast = useToast();
//#endregion

//#region ui-config
const activatedStepIndex: Ref<number> = ref(0);
const uploadFile = ref<File | null>(null);
const previewUrl = ref<string | null>(null);
const isGeneratingDescription = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);

// ステッパーの設定
const stepperItems = [
  {
    label: "分析結果取得",
    description: "図面をアップロードして分析",
    icon: "i-heroicons-document-magnifying-glass",
  },
  {
    label: "見積もり製品決定",
    description: "適切な製品を選択",
    icon: "i-heroicons-cube",
  },
  {
    label: "使用部品決定",
    description: "必要な部品を設定",
    icon: "i-heroicons-cog-6-tooth",
  },
  {
    label: "見積もり完了",
    description: "見積もりを確定",
    icon: "i-heroicons-check-circle",
  },
];
//#endregion ui-config

const handleFileSelect = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (!input.files || input.files.length === 0) return;

  const file = input.files[0];
  if (file.type !== "application/pdf") {
    toast.add({
      title: "エラー",
      description: "PDFファイルのみアップロード可能です",
      color: "error",
    });
    return;
  }

  uploadFile.value = file;
  // ファイル名から拡張子を除去して図面名称として設定
  blueprintStore.selectedBlueprint.name = file.name.replace(/\.[^/.]+$/, "");
  // プレビュー用のURLを生成
  previewUrl.value = URL.createObjectURL(file);
  // ②fileBlobをGeminiで解析してdescriptionを更新
  isGeneratingDescription.value = true;
  const aiLogic = useFirebaseAILogic();
  try {
    const analysisOutput = await aiLogic.analyzePdfFile({
      pdfFileBlob: file,
    });
    blueprintStore.selectedBlueprint.preAnalysisOutput = analysisOutput;
  } catch (error) {
    log("ERROR", "Failed to analyze PDF file", error);
    toast.add({
      title: "エラー",
      description: "図面説明の生成に失敗しました",
      color: "error",
    });
  } finally {
    isGeneratingDescription.value = false;
  }
};

const registerFile = async () => {
  if (!uploadFile.value) {
    toast.add({
      title: "エラー",
      description: "ファイルを選択してください",
      color: "error",
    });
    return;
  }

  globalLoading.startLoading();
  try {
    const blueprintId = createRandomDocId();
    const isSuccess = await blueprintStore.createNewlyBlueprintRegisterRequest({
      blueprintId: blueprintId,
      fileBlob: uploadFile.value,
      fileInfo: {
        name: uploadFile.value.name,
        type: uploadFile.value.type,
        size: uploadFile.value.size,
        lastModified: uploadFile.value.lastModified,
      },
    });
    if (isSuccess) {
      await blueprintStore.fetchBlueprints();
      // pop up toast
      toast.add({
        title: "ファイルをアップロードしました",
        description: "問題がない場合は「完了」ボタンを押してください",
        color: "success",
      });
    } else {
      toast.add({
        title: "エラー",
        description: "ファイルのアップロードに失敗しました",
        color: "error",
      });
    }
    // close modal
    emit("update:open", false);
    // create request
  } catch (error) {
    console.error("Upload error:", error);
    toast.add({
      title: "エラー",
      description: "ファイルのアップロードに失敗しました",
      color: "error",
    });
    activatedStepIndex.value = 0;
  } finally {
    globalLoading.stopLoading();
  }
};

const resetUploadFile = () => {
  uploadFile.value = null;
  previewUrl.value = null;
  blueprintStore.selectedBlueprint.name = "";
  blueprintStore.selectedBlueprint.preAnalysisOutput = {
    summary: "",
    annotation: "",
    pages: [],
  };
  // ステップを最初に戻す
  activatedStepIndex.value = 0;
};

// ステップ遷移の関数
const goToNextStep = () => {
  if (activatedStepIndex.value < stepperItems.length - 1) {
    activatedStepIndex.value++;
  }
};

const goToPreviousStep = () => {
  if (activatedStepIndex.value > 0) {
    activatedStepIndex.value--;
  }
};

// 次のステップに進めるかどうかの判定
const canProceedToNextStep = computed(() => {
  return (
    uploadFile.value &&
    blueprintStore.selectedBlueprint.name &&
    blueprintStore.selectedBlueprint.preAnalysisOutput?.summary &&
    blueprintStore.selectedBlueprint.preAnalysisOutput?.annotation &&
    blueprintStore.selectedBlueprint.preAnalysisOutput?.pages &&
    !isGeneratingDescription.value
  );
});

// モーダルが閉じられたときにクリーンアップ
watch(
  () => props.open,
  (open) => {
    if (!open) {
      uploadFile.value = null;
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value);
        previewUrl.value = null;
      }
      // ステップを最初に戻す
      activatedStepIndex.value = 0;
    }
  }
);

const registerIsAvailable = computed(() => {
  return (
    uploadFile.value &&
    blueprintStore.selectedBlueprint.name &&
    blueprintStore.selectedBlueprint.preAnalysisOutput?.summary &&
    blueprintStore.selectedBlueprint.preAnalysisOutput?.annotation &&
    blueprintStore.selectedBlueprint.preAnalysisOutput?.pages
  );
});

onBeforeUnmount(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
});

onMounted(async () => {
  const aiLogic = useFirebaseAILogic();
  await aiLogic.initializeVertexAI();
});
</script>

<style scoped>
.dropzone {
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  background-color: #f8fafc;
  transition: border-color 0.2s;
}
.dropzone:hover {
  border-color: #3b82f6; /* primary hover */
}
</style>
