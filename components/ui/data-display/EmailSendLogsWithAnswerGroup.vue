<template>
  <div>
    <!-- 新規質問票作成のモーダル -->
    <UModal
      v-model="requestDetailModalIsOpen"
      :ui="{
        width: 'md:max-w-screen-lg',
        height: 'md:min-h-[300px]',
      }"
    >
      <EmailSentInputModal @close-dialog="requestDetailModalIsOpen = false" />
    </UModal>
    <UTabs :items="items" class="w-full">
      <template #default="{ item, index, selected }">
        <!-- メニューの編集 -->
        <div class="flex items-center gap-2 relative truncate">
          <UIcon :name="item.icon" class="w-4 h-4 flex-shrink-0" />
          <span class="truncate font-bold"
            >{{ index + 1 }}. {{ item.label }}</span
          >
          <span v-if="selected">
            <UBadge color="background">選択中</UBadge>
          </span>
        </div>
      </template>
      <!-- 各タブアイテムの表示 -->
      <template #item="{ item }">
        <!-- 送信予約中 -->
        <div
          v-if="
            item.key == 'reserved' && reservedEmailSentRequestRow.length > 0
          "
        >
          <!-- ページネーション -->
          <div class="flex justify-end">
            <UPagination
              v-model="page"
              class="mb-2"
              :page-count="pageCount"
              :total="emailSendRequests.reservedEmailSendRequestsForView.length"
            />
          </div>
          <UTable
            :rows="reservedEmailSentRequestRow"
            :columns="reservedColumns"
          >
            <!-- 送信数-->
            <template #mailAddressListCount-data="{ row }">
              <EBadge color="background">
                {{ row.mailAddressListCount }}
              </EBadge>
            </template>
            <!-- 送信メールアドレス-->
            <template #senderEmail-data="{ row }">
              <EBadge color="background" variant="outline">
                {{ row.senderEmail }}
              </EBadge>
            </template>
            <!-- 送信ステータス-->
            <template #status-data="{ row }">
              <EBadge v-if="row.status == 'reserved'" color="warning">
                送信予約中
              </EBadge>
              <EBadge v-if="row.status == 'done'" color="primary">
                送信完了
              </EBadge>
              <EBadge v-if="row.status == 'failed'" color="error">
                送信失敗
              </EBadge>
            </template>
            <!-- 作成時刻-->
            <template #createdAt-data="{ row }">
              {{ formatTimestamp(row.createdAt.toDate()) }}
            </template>
            <!-- 詳細情報 -->
            <template #expand="{ row }">
              <div class="p-4">
                <JsonViewer
                  class="border max-h-[40vh] overflow-scroll"
                  aria-expanded
                  :copyable="true"
                  expand-depth="10"
                  :value="row"
                  theme="dark"
                />
              </div>
            </template>
          </UTable>
        </div>
        <!-- 送信済み -->
        <div
          v-if="
            item.key == 'done' &&
            emailSendRequests
              .finishedEmailSendRequestsForViewOnlyFromAnswerUserGroup.length >
              0
          "
        >
          <!-- ページネーション -->
          <div class="flex justify-end">
            <UPagination
              v-model="page"
              class="mb-2"
              :page-count="pageCount"
              :total="
                emailSendRequests
                  .finishedEmailSendRequestsForViewOnlyFromAnswerUserGroup
                  .length
              "
            />
          </div>
          <UTable
            :rows="finishedEmailSentRequestRow"
            :columns="finishedColumns"
          >
            <!-- 送信数-->
            <template #mailAddressListCount-data="{ row }">
              <EBadge color="background">
                {{ row.mailAddressListCount }}
              </EBadge>
            </template>
            <!-- 送信完了数-->
            <template #mailSendSuccessCount-data="{ row }">
              <EBadge color="primary">
                {{ countStatusCode202SendLog(row.sendResultList) }}
              </EBadge>
            </template>
            <!-- 送信未完了数-->
            <template #mailSendNotFinishedCount-data="{ row }">
              <div v-if="row.sendResultList">
                <EBadge
                  v-if="
                    row.mailAddressListCount -
                      countStatusCode202SendLog(row.sendResultList) >
                    0
                  "
                  color="error"
                >
                  {{
                    row.mailAddressListCount -
                    countStatusCode202SendLog(row.sendResultList)
                  }}
                </EBadge>
              </div>
            </template>
            <!-- 送信メールアドレス-->
            <template #senderEmail-data="{ row }">
              <EBadge color="background" variant="outline">
                {{ row.senderEmail }}
              </EBadge>
            </template>
            <!-- 作成時刻-->
            <template #createdAt-data="{ row }">
              {{ formatTimestamp(row.createdAt.toDate()) }}
            </template>
            <!-- 送信ステータス-->
            <template #status-data="{ row }">
              <EBadge v-if="row.status == 'reserved'" color="warning">
                送信予約中
              </EBadge>
              <EBadge v-if="row.status == 'done'" color="primary">
                送信完了
              </EBadge>
              <EBadge v-if="row.status == 'failed'" color="error">
                送信失敗
              </EBadge>
            </template>

            <!-- 詳細情報 -->
            <template #expand="{ row }">
              <!-- 送信ログ -->
              <UAccordion :items="logAccordion" class="mt-2">
                <template #mailSendLogs>
                  <!-- メール送信履歴DLボタン -->
                  <div class="flex justify-end">
                    <EButton
                      size="xs"
                      label="メール送信履歴"
                      icon="i-heroicons-arrow-up-tray"
                      color="background"
                      class="mr-3"
                      @click="
                        csv.downloadCSV({
                          data: row.sendResultList as object[],
                          filename:
                            'Qlavis回答ユーザーグループ_メール送信履歴' +
                            '(ID:' +
                            row.id +
                            ')_' +
                            date.getCurrentJstTime(),
                        })
                      "
                    />
                  </div>
                  <UTable
                    :rows="row.sendResultList"
                    :columns="perUserLogColumns"
                  >
                    <!-- ステータスコード-->
                    <template #statusCode-data="{ row }">
                      <!-- 送信成功時 -->
                      <EBadge
                        v-if="row.statusCode == 202"
                        color="primary"
                        variant="outline"
                      >
                        {{ row.statusCode }}
                      </EBadge>
                      <!-- それ以外 -->
                      <EBadge
                        v-if="row.statusCode != 202"
                        color="error"
                        variant="outline"
                      >
                        {{ row.statusCode }}
                      </EBadge>
                    </template>
                  </UTable>
                </template>
              </UAccordion>

              <div class="p-4">
                <JsonViewer
                  class="border max-h-[40vh] overflow-scroll"
                  aria-expanded
                  :copyable="true"
                  expand-depth="10"
                  :value="row"
                  theme="dark"
                />
              </div>
            </template>
          </UTable>
        </div>
      </template>
    </UTabs>
  </div>
</template>

<script lang="ts" setup>
import { JsonViewer } from "vue3-json-viewer";
import "vue3-json-viewer/dist/index.css";
import iconSet from "@utils/icon";
import date from "@utils/date";
import log from "@utils/logger";

//#region store
const emailSendRequests = useEmailSendRequestStore();
const globalError = useGlobalErrorStore();
const csv = useCSV();
//#endregion store

//#region ui-config
const tableSchema = useTableSchema();
const reservedColumns =
  tableSchema.value["admin-email-send-reservations-reserved"].columns;
const finishedColumns =
  tableSchema.value["admin-email-send-reservations-finished"].columns;
const perUserLogColumns =
  tableSchema.value["admin-email-send-log-per-user"].columns;
const page = ref(1);
const pageCount = 50;
//#endregion ui-config

//#region middleware
definePageMeta({
  layout: "admin",
  middleware: ["admin-logged-in-check"],
});
//#endregion middleware

//#region reactive-data
const requestDetailModalIsOpen = ref(false);
//#endregion reactive-data

//#region lifecycle-hooks
onMounted(async () => {
  try {
    // メール送信予約の一覧を取得
    await emailSendRequests.fetchEmailSendRequestList();
    // Tab Indexの一律初期化
    const tabControllerStore = useTabControllerStore();
    tabControllerStore.selectedTabIndex = 0;
  } catch (error) {
    log("ERROR", error);
    globalError.createNewGlobalError({
      selectedErrorMessage: globalError.errorCodeList.email.E1100,
    });
  }
});
//#endregion lifecycle-hooks

//#region watch-computed
const reservedEmailSentRequestRow = computed(() => {
  // 回答グループ起点のみに絞る
  return emailSendRequests.reservedEmailSendRequestsForViewOnlyFromAnswerUserGroup.slice(
    (page.value - 1) * pageCount,
    page.value * pageCount
  );
});
const finishedEmailSentRequestRow = computed(() => {
  // 回答グループ起点のみに絞る
  return emailSendRequests.finishedEmailSendRequestsForViewOnlyFromAnswerUserGroup.slice(
    (page.value - 1) * pageCount,
    page.value * pageCount
  );
});
//#endregion watch-computed

//#region ui-config
const logAccordion = [
  {
    label: "メール送信履歴",
    icon: iconSet.mail,
    defaultOpen: false,
    slot: "mailSendLogs",
  },
];

const countStatusCode202SendLog = (sendResultList: any): number => {
  log("INFO", "sendResultList is...", sendResultList);
  if (!sendResultList) {
    return 0;
  }
  return sendResultList.filter((sendLog: any) => sendLog.statusCode === 202)
    .length;
};
/**
 * メニューの一覧
 */
const items = [
  {
    key: "reserved",
    label: "送信予約中",
  },
  {
    key: "done",
    label: "送信済み",
  },
];
//#endregion ui-config
</script>
<style scoped>
.data-is-checked {
  background-color: black;
}
</style>
