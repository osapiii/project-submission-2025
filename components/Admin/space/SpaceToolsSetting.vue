<template>
  <!-- 保存ボタン -->
  <div class="flex justify-end">
    <UButton color="primary" :loading="isSaving" @click="saveSpace">
      スペース設定を保存
    </UButton>
  </div>
  <div class="space-y-6">
    <!-- エージェントセクション -->
    <UCard
      :ui="{
        header: 'bg-slate-700',
      }"
    >
      <template #header>
        <div class="flex items-center gap-2 text-white">
          <UIcon name="i-heroicons-user-circle" class="w-5 h-5" />
          <h3 class="text-lg font-semibold">エージェント</h3>
        </div>
      </template>

      <div class="grid grid-cols-2 gap-4">
        <!-- 左側：利用可能なエージェント一覧 -->
        <UCard class="bg-white shadow-sm">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <UBadge
                color="neutral"
                size="lg"
                variant="soft"
                class="font-bold px-3 py-1"
                >追加候補</UBadge
              >
            </div>
            <div class="flex gap-2">
              <UInput
                v-model="searchQuery.agent"
                icon="i-heroicons-magnifying-glass"
                placeholder="検索..."
                class="flex-1"
                :ui="{ base: 'bg-gray-50' }"
              />
            </div>
            <div
              class="space-y-3 overflow-y-auto h-[300px] pr-2"
              @dragover.prevent
              @drop="handleDrop($event, null, 'agent')"
            >
              <div
                v-for="agent in filteredAvailableAgents"
                :key="agent.id"
                class="p-4 rounded-lg cursor-move hover:bg-gray-50/80 hover:shadow-sm transition-all duration-200 border border-gray-200 bg-white"
                draggable="true"
                @dragstart="handleDragStart($event, agent, 'agent')"
              >
                <div class="flex items-center gap-3">
                  <div>
                    <NuxtImg
                      :src="
                        spaceStore.returnDefaultImageURl({
                          toolCategory: 'agent',
                        })
                      "
                      class="w-10 h-10 rounded-xl"
                    />
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <h4 class="font-medium text-gray-900">
                        {{ agent.name }}
                      </h4>
                      <UBadge
                        color="neutral"
                        variant="soft"
                        size="xs"
                        class="bg-gray-100 text-gray-600"
                        >{{ agent.id }}</UBadge
                      >
                    </div>
                    <p class="text-sm text-gray-600 mt-1">
                      {{ agent.description }}
                    </p>
                  </div>
                  <div class="flex items-center gap-2">
                    <UButton
                      v-if="!selectedTools.agent.some((t) => t.id === agent.id)"
                      color="primary"
                      variant="ghost"
                      icon="i-heroicons-plus"
                      class="hover:bg-primary-50"
                      @click="addTool(agent, 'agent')"
                    />
                    <UButton
                      color="gray"
                      variant="ghost"
                      icon="i-heroicons-play"
                      class="hover:bg-gray-50"
                      @click="testTool(agent, 'agent')"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </UCard>
        <!-- 右側：選択済みエージェント一覧 -->
        <UCard class="bg-white shadow-sm">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <UBadge
                color="neutral"
                size="lg"
                variant="soft"
                class="font-bold px-3 py-1"
                >連携済み</UBadge
              >
            </div>
            <div
              class="space-y-3 overflow-y-auto h-[300px] pr-2"
              @dragover.prevent
              @drop="handleDrop($event, null, 'agent')"
            >
              <div
                v-for="agent in selectedTools.agent"
                :key="agent.id"
                class="p-4 rounded-lg hover:bg-gray-50/80 hover:shadow-sm transition-all duration-200 border border-gray-200 bg-white"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="w-12 h-12 bg-green-50 rounded-full flex items-center justify-center"
                  >
                    <UIcon
                      name="i-heroicons-user-circle"
                      class="w-6 h-6 text-green-500"
                    />
                  </div>
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900">{{ agent.name }}</h4>
                    <p class="text-sm text-gray-600 mt-1">
                      {{ agent.description }}
                    </p>
                  </div>
                  <div class="flex items-center gap-2">
                    <UButton
                      color="error"
                      variant="ghost"
                      icon="i-heroicons-trash"
                      class="hover:bg-red-50"
                      @click="removeTool(agent, 'agent')"
                    />
                    <UButton
                      color="neutral"
                      variant="ghost"
                      icon="i-heroicons-play"
                      class="hover:bg-gray-50"
                      @click="testTool(agent, 'agent')"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </UCard>
    <!-- Difyセクション -->
    <UCard
      :ui="{
        header: 'bg-slate-700',
      }"
    >
      <template #header>
        <div class="flex items-center gap-2 text-white">
          <UIcon name="i-heroicons-cube" class="w-5 h-5" />
          <h3 class="text-lg font-semibold">Dify</h3>
        </div>
      </template>

      <div class="grid grid-cols-2 gap-4">
        <!-- 左側：利用可能なDify一覧 -->
        <UCard class="bg-white shadow-sm">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <UBadge
                color="neutral"
                size="lg"
                variant="soft"
                class="font-bold px-3 py-1"
                >追加候補</UBadge
              >
            </div>
            <div class="flex gap-2">
              <UInput
                v-model="searchQuery.dify"
                icon="i-heroicons-magnifying-glass"
                placeholder="検索..."
                class="flex-1"
                :ui="{ base: 'bg-gray-50' }"
              />
            </div>
            <div
              class="space-y-3 overflow-y-auto h-[300px] pr-2"
              @dragover.prevent
              @drop="handleDrop($event, null, 'dify')"
            >
              <div
                v-for="dify in filteredAvailableDify"
                :key="dify.id"
                class="p-4 rounded-lg cursor-move hover:bg-gray-50/80 hover:shadow-sm transition-all duration-200 border border-gray-200 bg-white"
                draggable="true"
                @dragstart="handleDragStart($event, dify, 'dify')"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="w-12 h-12 bg-primary-50 rounded-full flex items-center justify-center"
                  >
                    <UIcon
                      name="i-heroicons-cube"
                      class="w-6 h-6 text-primary-500"
                    />
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <h4 class="font-medium text-gray-900">
                        {{ dify.name }}
                      </h4>
                      <UBadge
                        color="neutral"
                        variant="soft"
                        size="xs"
                        class="bg-gray-100 text-gray-600"
                        >{{ dify.id }}</UBadge
                      >
                    </div>
                    <p class="text-sm text-gray-600 mt-1">
                      {{ dify.description }}
                    </p>
                  </div>
                  <div class="flex items-center gap-2">
                    <UButton
                      v-if="!selectedTools.dify.some((t) => t.id === dify.id)"
                      color="primary"
                      variant="ghost"
                      icon="i-heroicons-plus"
                      class="hover:bg-primary-50"
                      @click="addTool(dify, 'dify')"
                    />
                    <UButton
                      color="neutral"
                      variant="ghost"
                      icon="i-heroicons-play"
                      class="hover:bg-gray-50"
                      @click="testTool(dify, 'dify')"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </UCard>
        <!-- 右側：選択済みDify一覧 -->
        <UCard class="bg-white shadow-sm">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <UBadge
                color="neutral"
                size="lg"
                variant="soft"
                class="font-bold px-3 py-1"
                >連携済み</UBadge
              >
            </div>
            <div
              class="space-y-3 overflow-y-auto h-[300px] pr-2"
              @dragover.prevent
              @drop="handleDrop($event, null, 'dify')"
            >
              <div
                v-for="dify in selectedTools.dify"
                :key="dify.id"
                class="p-4 rounded-lg hover:bg-gray-50/80 hover:shadow-sm transition-all duration-200 border border-gray-200 bg-white"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="w-12 h-12 bg-green-50 rounded-full flex items-center justify-center"
                  >
                    <UIcon
                      name="i-heroicons-cube"
                      class="w-6 h-6 text-green-500"
                    />
                  </div>
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900">{{ dify.name }}</h4>
                    <p class="text-sm text-gray-600 mt-1">
                      {{ dify.description }}
                    </p>
                  </div>
                  <div class="flex items-center gap-2">
                    <UButton
                      color="error"
                      variant="ghost"
                      icon="i-heroicons-trash"
                      class="hover:bg-red-50"
                      @click="removeTool(dify, 'dify')"
                    />
                    <UButton
                      color="neutral"
                      variant="ghost"
                      icon="i-heroicons-play"
                      class="hover:bg-gray-50"
                      @click="testTool(dify, 'dify')"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </UCard>
    <!-- プロンプトセクション -->
    <UCard
      :ui="{
        header: 'bg-slate-700',
      }"
    >
      <template #header>
        <div class="flex items-center gap-2 text-white">
          <UIcon name="i-heroicons-chat-bubble-left-right" class="w-5 h-5" />
          <h3 class="text-lg font-semibold">プロンプト</h3>
        </div>
      </template>

      <div class="grid grid-cols-2 gap-4">
        <!-- 左側：利用可能なプロンプト一覧 -->
        <UCard class="bg-white shadow-sm">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <UBadge
                color="neutral"
                size="lg"
                variant="soft"
                class="font-bold px-3 py-1"
                >追加候補</UBadge
              >
            </div>
            <div class="flex gap-2">
              <UInput
                v-model="searchQuery.prompt"
                icon="i-heroicons-magnifying-glass"
                placeholder="検索..."
                class="flex-1"
                :ui="{ base: 'bg-gray-50' }"
              />
            </div>
            <div
              class="space-y-3 overflow-y-auto h-[300px] pr-2"
              @dragover.prevent
              @drop="handleDrop($event, null, 'prompt')"
            >
              <div
                v-for="prompt in _filteredAvailablePrompts"
                :key="prompt.id"
                class="p-4 rounded-lg cursor-move hover:bg-gray-50/80 hover:shadow-sm transition-all duration-200 border border-gray-200 bg-white"
                draggable="true"
                @dragstart="handleDragStart($event, prompt, 'prompt')"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="w-12 h-12 bg-primary-50 rounded-full flex items-center justify-center"
                  >
                    <UIcon
                      name="i-heroicons-chat-bubble-left-right"
                      class="w-6 h-6 text-primary-500"
                    />
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <h4 class="font-medium text-gray-900">
                        {{ prompt.name }}
                      </h4>
                      <UBadge
                        color="neutral"
                        variant="soft"
                        size="xs"
                        class="bg-gray-100 text-gray-600"
                        >{{ prompt.id }}</UBadge
                      >
                    </div>
                    <p class="text-sm text-gray-600 mt-1">
                      {{ prompt.description }}
                    </p>
                  </div>
                  <div class="flex items-center gap-2">
                    <UButton
                      v-if="
                        !selectedTools.prompt.some((t) => t.id === prompt.id)
                      "
                      color="primary"
                      variant="ghost"
                      icon="i-heroicons-plus"
                      class="hover:bg-primary-50"
                      @click="addTool(prompt, 'prompt')"
                    />
                    <UButton
                      color="neutral"
                      variant="ghost"
                      icon="i-heroicons-play"
                      class="hover:bg-gray-50"
                      @click="testTool(prompt, 'prompt')"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </UCard>
        <!-- 右側：選択済みプロンプト一覧 -->
        <UCard class="bg-white shadow-sm">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <UBadge
                color="neutral"
                size="lg"
                variant="soft"
                class="font-bold px-3 py-1"
                >連携済み</UBadge
              >
            </div>
            <div
              class="space-y-3 overflow-y-auto h-[300px] pr-2"
              @dragover.prevent
              @drop="handleDrop($event, null, 'prompt')"
            >
              <div
                v-for="prompt in selectedTools.prompt"
                :key="prompt.id"
                class="p-4 rounded-lg hover:bg-gray-50/80 hover:shadow-sm transition-all duration-200 border border-gray-200 bg-white"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="w-12 h-12 bg-green-50 rounded-full flex items-center justify-center"
                  >
                    <UIcon
                      name="i-heroicons-chat-bubble-left-right"
                      class="w-6 h-6 text-green-500"
                    />
                  </div>
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900">{{ prompt.name }}</h4>
                    <p class="text-sm text-gray-600 mt-1">
                      {{ prompt.description }}
                    </p>
                  </div>
                  <div class="flex items-center gap-2">
                    <UButton
                      color="error"
                      variant="ghost"
                      icon="i-heroicons-trash"
                      class="hover:bg-red-50"
                      @click="removeTool(prompt, 'prompt')"
                    />
                    <UButton
                      color="neutral"
                      variant="ghost"
                      icon="i-heroicons-play"
                      class="hover:bg-gray-50"
                      @click="testTool(prompt, 'prompt')"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
//#region import
import { ref, computed, watch } from "vue";

type ToolType = "agent" | "dify" | "prompt";

interface Tool {
  id: string;
  name: string;
  description: string;
  type: ToolType;
}

interface DragItem extends Tool {
  id: string;
  name: string;
  description: string;
  type: ToolType;
}
//#endregion import

//#region store
const spaceStore = useSpaceStore();
const agentStore = useAgentStore();
const difyStore = useDifyStore();
const promptStore = usePromptStore();
const organizationStore = useOrganizationStore();
const vectorStoreController = useVectorStoreControllerStore();
const toast = useToast();
//#endregion store

//#region reactive-data
const searchQuery = ref({
  agent: "",
  dify: "",
  prompt: "",
});
const isSaving = ref(false);
const selectedTools = ref<Record<ToolType, Tool[]>>({
  agent: [],
  dify: [],
  prompt: [],
});
//#endregion reactive-data

//#region computed
const filteredAvailableAgents = computed(() => {
  return agentStore.allAgentList
    .filter(
      (agent) =>
        agent.name
          .toLowerCase()
          .includes(searchQuery.value.agent.toLowerCase()) ||
        agent.description
          .toLowerCase()
          .includes(searchQuery.value.agent.toLowerCase())
    )
    .map((agent) => ({
      id: agent.id,
      name: agent.name,
      description: agent.description,
      type: "agent" as ToolType,
    }));
});

const filteredAvailableDify = computed(() => {
  return difyStore.allDifyList
    .filter(
      (dify) =>
        dify.name
          .toLowerCase()
          .includes(searchQuery.value.dify.toLowerCase()) ||
        dify.description
          .toLowerCase()
          .includes(searchQuery.value.dify.toLowerCase())
    )
    .map((dify) => ({
      id: dify.id,
      name: dify.name,
      description: dify.description,
      type: "dify" as ToolType,
    }));
});

const _filteredAvailablePrompts = computed(() => {
  return promptStore.allPromptList
    .filter(
      (prompt) =>
        prompt.name
          .toLowerCase()
          .includes(searchQuery.value.prompt.toLowerCase()) ||
        prompt.description
          .toLowerCase()
          .includes(searchQuery.value.prompt.toLowerCase())
    )
    .map((prompt) => ({
      id: prompt.id,
      name: prompt.name,
      description: prompt.description,
      type: "prompt" as ToolType,
    }));
});
//#endregion computed

//#region methods
const handleDragStart = (event: DragEvent, item: DragItem, type: ToolType) => {
  event.dataTransfer?.setData(
    "application/json",
    JSON.stringify({ tool: item, type })
  );
};

const handleDrop = (
  event: DragEvent,
  _targetTool: DragItem | null,
  type: ToolType
) => {
  const data = JSON.parse(
    event.dataTransfer?.getData("application/json") || "{}"
  );
  if (data.tool && data.type === type) {
    addTool(data.tool as Tool, type);
  }
};

const addTool = (tool: Tool, type: ToolType) => {
  if (!selectedTools.value[type].some((t) => t.id === tool.id)) {
    selectedTools.value[type].push(tool);
    updateSpaceTools();
  }
};

const removeTool = (tool: Tool, type: ToolType) => {
  selectedTools.value[type] = selectedTools.value[type].filter(
    (t) => t.id !== tool.id
  );
  updateSpaceTools();
};

const testTool = async (tool: Tool, _type: ToolType) => {
  try {
    // テスト実行のロジックをここに実装
    toast.add({
      title: `${tool.name}のテストを実行しました`,
      color: "success",
    });
  } catch {
    toast.add({
      title: `${tool.name}のテスト実行に失敗しました`,
      color: "error",
    });
  }
};

const updateSpaceTools = () => {
  spaceStore.selectedSpace.configs.tools = {
    agent: selectedTools.value.agent.map((t) => ({
      id: t.id,
      status: "active" as const,
    })),
    dify: selectedTools.value.dify.map((t) => ({
      id: t.id,
      status: "active" as const,
    })),
    prompt: selectedTools.value.prompt.map((t) => ({
      id: t.id,
      status: "active" as const,
    })),
  };
};

const saveSpace = async () => {
  isSaving.value = true;
  try {
    await spaceStore.saveSpace();
    const isPointRegisterSuccess =
      await vectorStoreController.createNewQdrantToolPointsCreateRequest({
        spaceId: spaceStore.selectedSpace.id,
        tools: spaceStore.getToolPointsForQdrantFromSelectedTools(),
      });
    if (isPointRegisterSuccess) {
      toast.add({
        title: "スペース設定を保存しました",
        color: "success",
      });
    } else {
      toast.add({
        title: "ツールポイントの登録に失敗しました",
        color: "error",
      });
    }
  } catch {
    toast.add({
      title: "スペース設定の保存に失敗しました",
      color: "error",
    });
  } finally {
    isSaving.value = false;
  }
};
//#endregion methods

//#region lifecycle-hooks
onMounted(async () => {
  // 各Storeからツール一覧を取得
  await Promise.all([
    agentStore.fetchAgents({
      organizationId: organizationStore.loggedInOrganizationInfo.id,
    }),
    difyStore.fetchDifys({
      organizationId: organizationStore.loggedInOrganizationInfo.id,
    }),
    promptStore.fetchPrompts({
      organizationId: organizationStore.loggedInOrganizationInfo.id,
    }),
  ]);

  // 現在選択されているツールを設定
  const currentTools = spaceStore.selectedSpace.configs.tools || {};
  selectedTools.value = {
    agent: (currentTools.agent || []).map(({ id }) => {
      const agent = agentStore.allAgentList.find((a) => a.id === id);
      if (agent) {
        const tool: Tool = {
          id: agent.id,
          name: agent.name,
          description: agent.description,
          type: "agent" as ToolType,
        };
        return tool;
      }
      return { id, name: "", description: "", type: "agent" as ToolType };
    }),
    dify: (currentTools.dify || []).map(({ id }) => {
      const dify = difyStore.allDifyList.find((d) => d.id === id);
      if (dify) {
        const tool: Tool = {
          id: dify.id,
          name: dify.name,
          description: dify.description,
          type: "dify" as ToolType,
        };
        return tool;
      }
      return { id, name: "", description: "", type: "dify" as ToolType };
    }),
    prompt: (currentTools.prompt || []).map(({ id }) => {
      const prompt = promptStore.allPromptList.find((p) => p.id === id);
      if (prompt) {
        const tool: Tool = {
          id: prompt.id,
          name: prompt.name,
          description: prompt.description,
          type: "prompt" as ToolType,
        };
        return tool;
      }
      return { id, name: "", description: "", type: "prompt" as ToolType };
    }),
  };
});
//#endregion lifecycle-hooks
</script>
