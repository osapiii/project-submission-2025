<template>
  <UCard>
    <div class="space-y-2">
      <!-- スコアカード -->
      <div>
        <div class="grid grid-cols-4 gap-x-3">
          <UCard class="p-4 border-l-4 border-primary">
            <div class="flex flex-col">
              <div class="text-sm text-gray-500 mb-1">総会話数</div>
              <div class="text-2xl font-bold">
                {{ stats?.totalConversations || 0 }}
              </div>
              <div class="text-xs text-green-500 mt-2 flex items-center">
                <UIcon name="i-heroicons-arrow-up" class="mr-1" />
                <span>前月比 12%増</span>
              </div>
            </div>
          </UCard>
          <UCard class="p-4 border-l-4 border-indigo-500">
            <div class="flex flex-col">
              <div class="text-sm text-gray-500 mb-1">平均応答時間</div>
              <div class="text-2xl font-bold">
                {{ stats?.avgResponseTime || "0.0" }}秒
              </div>
              <div class="text-xs text-red-500 mt-2 flex items-center">
                <UIcon name="i-heroicons-arrow-down" class="mr-1" />
                <span>前月比 3%減</span>
              </div>
            </div>
          </UCard>
          <UCard class="p-4 border-l-4 border-amber-500">
            <div class="flex flex-col">
              <div class="text-sm text-gray-500 mb-1">ユニークユーザー</div>
              <div class="text-2xl font-bold">
                {{ stats?.uniqueUsers || 0 }}
              </div>
              <div class="text-xs text-green-500 mt-2 flex items-center">
                <UIcon name="i-heroicons-arrow-up" class="mr-1" />
                <span>前月比 8%増</span>
              </div>
            </div>
          </UCard>
          <UCard class="p-4 border-l-4 border-emerald-500">
            <div class="flex flex-col">
              <div class="text-sm text-gray-500 mb-1">満足度</div>
              <div class="text-2xl font-bold">
                {{ stats?.satisfactionRate || "0" }}%
              </div>
              <div class="text-xs text-green-500 mt-2 flex items-center">
                <UIcon name="i-heroicons-arrow-up" class="mr-1" />
                <span>前月比 5%増</span>
              </div>
            </div>
          </UCard>
        </div>
      </div>

      <!-- 日々の利用数グラフ -->
      <div>
        <h3 class="text-lg font-bold mb-4">日々の利用数</h3>
        <div class="h-80 w-full">
          <v-chart class="chart" :option="chartOption" autoresize />
        </div>
      </div>

      <!-- 使用ログテーブル -->
      <div>
        <h3 class="text-lg font-bold mb-4">使用ログ</h3>
        <UTable
          :columns="usageLogColumns"
          :data="usageLogs"
          :loading="isLoading"
          class="w-full"
        >
          <template #timestamp-cell="{ row }">
            {{ formatDate(row.original.timestamp) }}
          </template>
          <template #user-cell="{ row }">
            <div class="flex items-center">
              <UAvatar
                :src="row.original.user.avatar"
                :alt="row.original.user.name"
                size="sm"
                class="mr-2"
              />
              <span>{{ row.original.user.name }}</span>
            </div>
          </template>
          <template #message-cell="{ row }">
            <div class="max-w-md truncate">{{ row.original.message }}</div>
          </template>
          <template #response-cell="{ row }">
            <div class="max-w-md truncate">{{ row.original.response }}</div>
          </template>
          <template #actions-cell="{ row }">
            <UButton
              icon="i-heroicons-eye"
              color="primary"
              variant="ghost"
              size="xs"
              @click="viewLogDetail(row.original.id)"
            />
          </template>
        </UTable>
        <div class="flex justify-end mt-4">
          <UPagination
            v-model="currentPage"
            :total="totalLogs"
            :per-page="perPage"
            @update:model-value="fetchUsageLogs"
          />
        </div>
      </div>
    </div>
  </UCard>
</template>

<script lang="ts" setup>
//#region import
import log from "@utils/logger";
import { format } from "date-fns";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart, BarChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
} from "echarts/components";
import VChart from "vue-echarts";

// EChartsコンポーネントの登録
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
]);
//#endregion import

//#region props
const props = defineProps<{
  resourceId: string;
  resourceType: "dify" | "agent" | "prompt" | "space";
}>();
//#endregion props

//#region initializeStores
const toast = useToast();
//#endregion initializeStores

//#region reactive-data
// 使用ログ関連のデータ
const isLoading = ref(false);
const usageLogs = ref([]);
const currentPage = ref(1);
const perPage = ref(10);
const totalLogs = ref(0);
const stats = ref({
  totalConversations: 0,
  avgResponseTime: "0.0",
  uniqueUsers: 0,
  satisfactionRate: "0",
});

// 使用ログテーブルのカラム定義
const usageLogColumns = [
  {
    accessorKey: "timestamp",
    header: "日時",
  },
  {
    accessorKey: "user",
    header: "ユーザー",
  },
  {
    accessorKey: "message",
    header: "メッセージ",
  },
  {
    accessorKey: "response",
    header: "レスポンス",
  },
  {
    accessorKey: "actions",
    header: "操作",
  },
];

// EChartsのオプション設定
const chartOption = ref({
  title: {
    text: "日々の利用統計",
    left: "center",
    textStyle: {
      fontSize: 16,
      fontWeight: "bold",
    },
  },
  tooltip: {
    trigger: "axis",
    axisPointer: {
      type: "shadow",
    },
  },
  legend: {
    data: ["利用回数"],
    bottom: 0,
  },
  grid: {
    left: "3%",
    right: "4%",
    bottom: "10%",
    top: "15%",
    containLabel: true,
  },
  xAxis: {
    type: "category",
    data: [],
    axisLine: {
      lineStyle: {
        color: "#ddd",
      },
    },
    axisLabel: {
      color: "#666",
    },
  },
  yAxis: {
    type: "value",
    splitLine: {
      lineStyle: {
        color: "#eee",
      },
    },
    axisLabel: {
      color: "#666",
    },
  },
  series: [
    {
      name: "利用回数",
      type: "bar",
      data: [],
      itemStyle: {
        color: new Function(
          "params",
          `
          const colorList = ['#83bff6', '#188df0', '#005eaa', '#0a3a68', '#00cfdd'];
          return colorList[params.dataIndex % colorList.length];
        `
        ),
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: "rgba(0, 0, 0, 0.5)",
        },
      },
      barWidth: "60%",
      showBackground: true,
      backgroundStyle: {
        color: "rgba(220, 220, 220, 0.2)",
      },
    },
  ],
});
//#endregion reactive-data

//#region methods
/**
 * 日付をフォーマットする
 */
const formatDate = (timestamp: string): string => {
  return format(new Date(timestamp), "yyyy/MM/dd HH:mm:ss");
};

/**
 * 使用ログを取得する
 */
const fetchUsageLogs = async () => {
  isLoading.value = true;
  try {
    log(
      "INFO",
      "fetchUsageLogs called",
      props.resourceId,
      props.resourceType,
      currentPage.value,
      perPage.value
    );
    // ここで実際のAPIからデータを取得する処理を実装
    // 仮のデータを生成
    const mockData = generateMockUsageLogs();
    usageLogs.value = mockData.logs;
    totalLogs.value = mockData.total;

    // 統計情報を設定
    stats.value = {
      totalConversations: Math.floor(Math.random() * 1000) + 100,
      avgResponseTime: (Math.random() * 2 + 0.5).toFixed(1),
      uniqueUsers: Math.floor(Math.random() * 500) + 50,
      satisfactionRate: (Math.random() * 30 + 70).toFixed(0),
    };

    // 使用数グラフのデータを更新
    updateUsageChartData();
  } catch (error) {
    log("ERROR", "使用ログの取得に失敗しました", error);
    toast.add({
      title: "使用ログの取得に失敗しました",
      color: "error",
    });
  } finally {
    isLoading.value = false;
  }
};

/**
 * 使用ログの詳細を表示する
 */
const viewLogDetail = (logId: string) => {
  log("INFO", "viewLogDetail called", logId);
  // ログ詳細表示の処理を実装
  toast.add({
    title: `ログID: ${logId} の詳細を表示します`,
    color: "info",
  });
};

/**
 * モックの使用ログデータを生成する
 */
const generateMockUsageLogs = () => {
  const logs = [];
  const total = 100;

  for (let i = 0; i < perPage.value; i++) {
    const index = (currentPage.value - 1) * perPage.value + i;
    if (index >= total) break;

    logs.push({
      id: `log-${index}`,
      timestamp: new Date(Date.now() - index * 3600000).toISOString(),
      user: {
        name: `ユーザー${(index % 10) + 1}`,
        avatar: `https://i.pravatar.cc/150?u=${index}`,
      },
      message: `これは${
        index + 1
      }番目のユーザーメッセージです。長いメッセージの場合は省略表示されます。`,
      response: `これは${
        index + 1
      }番目のAIレスポンスです。こちらも長い場合は省略表示されます。`,
    });
  }

  return { logs, total };
};

/**
 * 使用数グラフのデータを更新する
 */
const updateUsageChartData = () => {
  // 過去7日間のデータを生成
  const labels = [];
  const data = [];

  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    labels.push(format(date, "MM/dd"));
    // ランダムな使用回数を生成（実際はAPIから取得）
    data.push(Math.floor(Math.random() * 50) + 10);
  }

  // EChartsのデータを更新
  chartOption.value.xAxis.data = labels;
  chartOption.value.series[0].data = data;
};
//#endregion methods

//#region lifecycle-hooks
onMounted(async () => {
  log("INFO", "UsageLog component mounted");
  await fetchUsageLogs();
});
//#endregion lifecycle-hooks

defineOptions({
  name: "AdminUsageLog",
});
</script>

<style scoped>
.chart {
  height: 100%;
  width: 100%;
}
</style>
