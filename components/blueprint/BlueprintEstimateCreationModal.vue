<template>
  <UModal
    :open="open"
    fullscreen
    class="m-4 overflow-y-scroll"
    @update:open="(val) => $emit('update:open', val)"
  >
    <template #content>
      <UCard
        :ui="{
          header:
            'bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 text-white font-bold shadow-lg',
          body: 'p-0',
        }"
        class="rounded-2xl shadow-2xl border-0 overflow-hidden"
      >
        <template #header>
          <div class="flex justify-between items-center p-1.5">
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm"
              >
                <UIcon name="i-heroicons-sparkles" class="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 class="text-xl font-bold">AI見積もりアシスタント</h2>
                <p class="text-white/80 text-sm">
                  図面分析を基にした見積もり作成
                </p>
              </div>
            </div>
            <div class="flex gap-3 items-center">
              <!-- セッションID表示 -->
              <div
                v-if="
                  blueprintEstimateCreateProcessController.selectedEstimateProcessSessionId
                "
                class="hidden md:flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-3 py-1"
              >
                <UIcon
                  name="i-heroicons-signal"
                  class="w-3 h-3 text-green-300"
                />
                <span class="text-xs text-white/90 font-mono">
                  セッション:{{ googleAiAgent.currentSessionId }}
                </span>
              </div>
              <UButton
                color="neutral"
                variant="ghost"
                size="lg"
                icon="i-heroicons-x-mark"
                class="rounded-full hover:bg-white/10 transition-all duration-200 text-white hover:text-gray-200"
                @click="emit('update:open', false)"
              />
            </div>
          </div>
        </template>

        <div
          class="bg-gradient-to-br from-gray-50 to-blue-50/30 flex overflow-y-scroll relative"
        >
          <!-- 左側: ステップカード -->
          <div
            class="w-80 min-w-80 bg-white/80 backdrop-blur-sm border-r border-gray-200 p-4 flex-shrink-0 relative"
          >
            <!-- 進捗サマリー -->
            <div
              class="mb-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100"
            >
              <div class="flex items-center gap-2 mb-2">
                <UIcon
                  name="i-heroicons-chart-pie"
                  class="w-4 h-4 text-blue-600"
                />
                <span class="text-sm font-medium text-blue-800">全体進捗</span>
                <span class="text-xs text-gray-600 ml-auto"
                  >{{ completedStepsCount }}/{{ estimateSteps.length }}</span
                >
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2 mb-1">
                <div
                  class="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                  :style="{ width: `${progressPercentage}%` }"
                />
              </div>
              <div class="text-xs text-gray-600 text-center">
                {{ progressPercentage }}% 完了
              </div>
            </div>

            <div class="mb-3">
              <h3 class="text-lg font-bold text-gray-800">
                見積もり作成ステップ
              </h3>
            </div>

            <!-- ステップカード一覧 -->
            <div class="space-y-2 pb-32">
              <div
                v-for="(step, index) in estimateSteps"
                :key="step.id"
                class="relative"
              >
                <!-- ステップカード -->
                <div
                  class="rounded-lg p-3 border-2 transition-all duration-300 cursor-pointer hover:shadow-md"
                  :class="[
                    step.status === 'completed'
                      ? 'bg-green-50 border-green-200 hover:border-green-300'
                      : step.status === 'in-progress'
                      ? 'bg-blue-50 border-blue-200 hover:border-blue-300'
                      : 'bg-gray-50 border-gray-200 hover:border-gray-300',
                  ]"
                  @click="selectStep(step)"
                >
                  <!-- ステップヘッダー -->
                  <div class="flex items-center gap-3">
                    <!-- ステップ番号 -->
                    <div
                      class="w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0"
                      :class="[
                        step.status === 'completed'
                          ? 'bg-green-500 text-white'
                          : step.status === 'in-progress'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-300 text-gray-600',
                      ]"
                    >
                      <UIcon
                        v-if="step.status === 'completed'"
                        name="i-heroicons-check"
                        class="w-3 h-3"
                      />
                      <UIcon
                        v-else-if="step.status === 'in-progress'"
                        name="i-heroicons-arrow-path"
                        class="w-3 h-3 animate-spin"
                      />
                      <span v-else class="text-xs">{{ index + 1 }}</span>
                    </div>

                    <!-- ステップタイトル -->
                    <div class="flex-1 min-w-0">
                      <h4 class="font-semibold text-gray-800 text-sm truncate">
                        {{ step.title }}
                      </h4>
                      <!-- 進捗詳細 -->
                      <div
                        v-if="step.details"
                        class="text-xs text-gray-500 mt-1 truncate"
                      >
                        {{ step.details }}
                      </div>
                    </div>

                    <!-- ステータスバッジ -->
                    <UBadge
                      :color="getBadgeColor(step.status)"
                      variant="soft"
                      size="xs"
                      class="flex-shrink-0"
                    >
                      {{ getStatusText(step.status) }}
                    </UBadge>
                  </div>
                </div>

                <!-- 接続線 -->
                <div
                  v-if="index < estimateSteps.length - 1"
                  class="absolute left-6 top-full w-0.5 h-2 bg-gray-300 transform -translate-x-1/2"
                />
              </div>
            </div>

            <!-- ダウンロードエリア（左下固定） -->
            <div
              v-if="
                blueprintEstimateCreateProcessController.pdfFileIsDownloaded
              "
              class="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm border-t border-gray-200 p-4"
            >
              <div class="space-y-3">
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-sm font-medium text-gray-700">
                    📁ドキュメントダウンロード
                  </span>
                </div>

                <!-- step4完了前のプレースホルダー -->
                <div
                  v-if="
                    !blueprintEstimateCreateProcessController.isStep5Completed
                  "
                  class="space-y-2"
                >
                  <div
                    class="flex items-center justify-between p-2 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div class="flex items-center gap-2">
                      <UIcon
                        name="i-heroicons-document-text"
                        class="w-4 h-4 text-gray-400"
                      />
                      <span class="text-xs text-gray-500">見積書PDF</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <div
                        class="w-2 h-2 bg-gray-300 rounded-full animate-pulse"
                      />
                      <span class="text-xs text-gray-400">生成中...</span>
                    </div>
                  </div>
                  <div
                    class="flex items-center justify-between p-2 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div class="flex items-center gap-2">
                      <UIcon
                        name="i-heroicons-clipboard-document-list"
                        class="w-4 h-4 text-gray-400"
                      />
                      <span class="text-xs text-gray-500">明細書PDF</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <div
                        class="w-2 h-2 bg-gray-300 rounded-full animate-pulse"
                      />
                      <span class="text-xs text-gray-400">生成中...</span>
                    </div>
                  </div>
                </div>

                <!-- step5完了後のダウンロードボタン -->
                <div v-else class="space-y-2">
                  <!-- ファイル準備中の表示 -->
                  <div
                    v-if="
                      !blueprintEstimateCreateProcessController.areOutputFilesReady &&
                      blueprintEstimateCreateProcessController.isDownloadingOutputFiles
                    "
                    class="text-center py-2"
                  >
                    <div class="flex items-center gap-2 justify-center">
                      <UIcon
                        name="i-heroicons-arrow-path"
                        class="w-4 h-4 text-blue-500 animate-spin"
                      />
                      <span class="text-xs text-gray-600"
                        >ファイル準備中...</span
                      >
                    </div>
                  </div>

                  <!-- ダウンロードボタン -->
                  <template
                    v-else-if="
                      blueprintEstimateCreateProcessController.areOutputFilesReady
                    "
                  >
                    <!-- 見積書ダウンロードボタン -->
                    <UButton
                      v-if="
                        blueprintEstimateCreateProcessController.isEstimationFileReady
                      "
                      color="error"
                      variant="soft"
                      size="sm"
                      class="w-full justify-start"
                      @click="
                        blueprintEstimateCreateProcessController.downloadEstimationFile()
                      "
                    >
                      <template #leading>
                        <UIcon
                          name="i-heroicons-document-text"
                          class="w-4 h-4"
                        />
                      </template>
                      <span class="text-xs">見積書をダウンロード</span>
                      <template #trailing>
                        <UIcon
                          name="i-heroicons-arrow-down-tray"
                          class="w-3 h-3"
                        />
                      </template>
                    </UButton>

                    <!-- 明細書ダウンロードボタン -->
                    <UButton
                      v-if="
                        blueprintEstimateCreateProcessController.isPartsBreakdownFileReady
                      "
                      color="error"
                      variant="soft"
                      size="sm"
                      class="w-full justify-start"
                      @click="
                        blueprintEstimateCreateProcessController.downloadPartsBreakdownFile()
                      "
                    >
                      <template #leading>
                        <UIcon
                          name="i-heroicons-clipboard-document-list"
                          class="w-4 h-4"
                        />
                      </template>
                      <span class="text-xs">明細書をダウンロード</span>
                      <template #trailing>
                        <UIcon
                          name="i-heroicons-arrow-down-tray"
                          class="w-3 h-3"
                        />
                      </template>
                    </UButton>

                    <!-- ファイルが部分的に準備されていない場合の表示 -->
                    <div
                      v-if="
                        !blueprintEstimateCreateProcessController.isEstimationFileReady ||
                        !blueprintEstimateCreateProcessController.isPartsBreakdownFileReady
                      "
                      class="text-center py-1"
                    >
                      <div class="flex items-center gap-2 justify-center">
                        <UIcon
                          name="i-heroicons-exclamation-triangle"
                          class="w-3 h-3 text-amber-500"
                        />
                        <span class="text-xs text-amber-600">
                          一部のファイルの準備中です...
                        </span>
                      </div>
                    </div>
                  </template>

                  <!-- ファイル準備失敗時 -->
                  <div v-else class="text-center py-2">
                    <div class="flex items-center gap-2 justify-center mb-2">
                      <UIcon
                        name="i-heroicons-exclamation-triangle"
                        class="w-4 h-4 text-red-500"
                      />
                      <span class="text-xs text-red-600"
                        >ファイル準備に失敗しました</span
                      >
                    </div>
                    <UButton
                      color="neutral"
                      variant="soft"
                      size="xs"
                      @click="
                        blueprintEstimateCreateProcessController.downloadOutputFiles()
                      "
                    >
                      再試行
                    </UButton>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右側: チャット部分 -->
          <div class="flex-1 flex flex-col">
            <!-- UTabs for チャット/図面/解析結果 -->
            <UTabs v-model="currentActiveTab" :items="tabItems">
              <!-- チャットタブ -->
              <template #chat>
                <div class="h-[75vh] flex flex-col overflow-hidden">
                  <!-- 会話画面 -->
                  <div class="h-full flex flex-col overflow-hidden">
                    <!-- セッション情報エリア -->
                    <div
                      class="bg-white/80 backdrop-blur-sm border-b border-blue-100 p-4 flex-shrink-0"
                    >
                      <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                          <div
                            class="w-3 h-3 bg-green-400 rounded-full animate-pulse"
                          />
                          <span class="text-sm font-medium text-gray-700"
                            >接続中</span
                          >
                          <span
                            class="text-xs text-gray-500 font-mono bg-gray-100 px-2 py-1 rounded-full"
                          >
                            {{ googleAiAgent.currentSessionId.slice(-12) }}
                          </span>
                        </div>

                        <!-- 現在のステップ表示エリア（中央） -->
                        <div class="flex-1 flex justify-center">
                          <div
                            class="flex items-center gap-2 md:gap-3 bg-gradient-to-r from-blue-50 to-purple-50 px-3 md:px-4 py-2 rounded-full border border-blue-200 shadow-sm hover:shadow-md transition-shadow duration-200"
                          >
                            <!-- ステップアイコン -->
                            <div
                              class="w-7 h-7 md:w-8 md:h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0"
                              :class="[
                                updateStepsBasedOnCurrentStep >
                                estimateSteps.length
                                  ? 'bg-green-500 text-white shadow-md'
                                  : updateStepsBasedOnCurrentStep > 0
                                  ? 'bg-blue-500 text-white shadow-md'
                                  : 'bg-gray-400 text-white shadow-md',
                              ]"
                            >
                              <UIcon
                                v-if="
                                  updateStepsBasedOnCurrentStep >
                                  estimateSteps.length
                                "
                                name="i-heroicons-check-circle"
                                class="w-3 h-3 md:w-4 md:h-4"
                              />
                              <UIcon
                                v-else-if="updateStepsBasedOnCurrentStep > 0"
                                name="i-heroicons-arrow-path"
                                class="w-3 h-3 md:w-4 md:h-4 animate-spin"
                              />
                              <UIcon
                                v-else
                                name="i-heroicons-play"
                                class="w-3 h-3 md:w-4 md:h-4"
                              />
                            </div>

                            <!-- ステップ情報 -->
                            <div class="text-center min-w-0 flex-1">
                              <div
                                class="text-xs md:text-sm font-bold text-gray-800"
                              >
                                {{
                                  updateStepsBasedOnCurrentStep > 0
                                    ? `STEP ${updateStepsBasedOnCurrentStep}`
                                    : "開始前"
                                }}
                              </div>
                              <div
                                class="text-xs text-gray-600 truncate max-w-32 md:max-w-48"
                              >
                                {{
                                  updateStepsBasedOnCurrentStep > 0 &&
                                  updateStepsBasedOnCurrentStep <=
                                    estimateSteps.length
                                    ? estimateSteps[
                                        updateStepsBasedOnCurrentStep - 1
                                      ]?.title
                                    : updateStepsBasedOnCurrentStep >
                                      estimateSteps.length
                                    ? "全ステップ完了"
                                    : "処理開始を待機中"
                                }}
                              </div>
                            </div>

                            <!-- ステータスバッジ（デスクトップのみ表示） -->
                            <UBadge
                              :color="
                                updateStepsBasedOnCurrentStep >
                                estimateSteps.length
                                  ? 'success'
                                  : updateStepsBasedOnCurrentStep > 0
                                  ? 'primary'
                                  : 'neutral'
                              "
                              variant="soft"
                              size="xs"
                              class="hidden md:inline-flex flex-shrink-0"
                            >
                              {{
                                updateStepsBasedOnCurrentStep >
                                estimateSteps.length
                                  ? "完了"
                                  : updateStepsBasedOnCurrentStep > 0
                                  ? "進行中"
                                  : "待機中"
                              }}
                            </UBadge>
                          </div>
                        </div>

                        <div class="text-xs text-gray-500">
                          {{ googleAiAgent.conversationHistory.length }}
                          メッセージ
                        </div>
                      </div>
                    </div>

                    <!-- 会話履歴エリア -->
                    <div
                      ref="conversationArea"
                      class="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-transparent to-blue-50/20"
                    >
                      <!-- 会話メッセージ -->
                      <template
                        v-for="(
                          message, index
                        ) in googleAiAgent.conversationHistoryForView"
                        :key="message.id"
                      >
                        <div
                          v-if="message.type === 'text'"
                          class="flex animate-fade-in"
                          :class="
                            message.role === 'user'
                              ? 'justify-end'
                              : 'justify-start'
                          "
                          :style="{ animationDelay: `${index * 0.1}s` }"
                        >
                          <div
                            class="max-w-[calc(100%-2rem)] md:max-w-[70%] group"
                            :class="
                              message.role === 'user'
                                ? 'flex flex-col items-end'
                                : 'flex flex-col items-start'
                            "
                          >
                            <!-- メッセージバブル -->
                            <div
                              class="rounded-3xl px-5 py-3 shadow-md transform transition-all duration-200 hover:scale-[1.02] hover:shadow-lg"
                              :class="[
                                message.role === 'user'
                                  ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-br-lg'
                                  : 'bg-white border border-gray-100 text-gray-800 rounded-bl-lg',
                              ]"
                            >
                              <!-- 通常のテキストメッセージ -->
                              <div
                                class="whitespace-pre-wrap leading-relaxed break-words word-break overflow-wrap-anywhere github-markdown"
                                v-html="convertMarkdownToHtml(message.content)"
                              />
                            </div>

                            <!-- タイムスタンプとステータス -->
                            <div
                              class="flex items-center gap-1 mt-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                              :class="
                                message.role === 'user'
                                  ? 'flex-row-reverse'
                                  : 'flex-row'
                              "
                            >
                              <span class="text-xs text-gray-500">
                                {{ formatTime(message.timestamp) }}
                              </span>
                              <UIcon
                                v-if="message.role === 'user'"
                                name="i-heroicons-check-circle"
                                class="w-3 h-3 text-blue-500"
                              />
                            </div>
                          </div>
                        </div>
                      </template>

                      <!-- ローディング表示 -->
                      <div
                        v-if="googleAiAgent.isProcessing"
                        class="flex justify-start animate-fade-in"
                      >
                        <div class="flex flex-col items-start">
                          <div
                            class="bg-white border border-gray-100 rounded-3xl rounded-bl-lg px-5 py-3 shadow-md"
                          >
                            <div class="flex items-center gap-3">
                              <div class="flex gap-1">
                                <div
                                  class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                  style="animation-delay: 0ms"
                                />
                                <div
                                  class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                  style="animation-delay: 150ms"
                                />
                                <div
                                  class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                  style="animation-delay: 300ms"
                                />
                              </div>
                              <span class="text-gray-600 text-sm"
                                >AIエージェントが業務を実行中...</span
                              >
                            </div>
                          </div>
                          <div class="text-xs text-gray-500 mt-1 px-2">
                            {{ formatTime(new Date()) }}
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- メッセージ入力エリア -->
                    <div
                      class="bg-white/90 backdrop-blur-sm border-t border-gray-100 p-4 flex-shrink-0"
                    >
                      <div class="flex gap-3 items-center justify-center">
                        <UInput
                          v-model="userInput"
                          placeholder="メッセージを入力してください..."
                          size="xl"
                          class="focus:border-blue-400 focus:ring-blue-400 transition-all duration-200 w-2/3"
                          :ui="{
                            base: 'rounded-2xl  focus:border-blue-400 transition-all duration-200',
                          }"
                          :disabled="googleAiAgent.isProcessing"
                          @keydown.enter.prevent="handleEnterKey"
                        />
                        <UButton
                          color="primary"
                          variant="solid"
                          size="lg"
                          class="rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
                          :disabled="
                            !userInput.trim() || googleAiAgent.isProcessing
                          "
                          :loading="googleAiAgent.isProcessing"
                          @click="sendMessage"
                        >
                          <div class="flex items-center gap-1">
                            <UIcon
                              name="i-heroicons-paper-airplane"
                              class="w-5 h-5 transform rotate-45"
                            />
                            <div>送信</div>
                          </div>
                        </UButton>
                        <div class="text-xs text-gray-500">
                          <UIcon
                            name="i-heroicons-command-line"
                            class="w-3 h-3 inline mr-1"
                          />
                          Ctrl+Enterで送信
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </template>

              <!-- 図面タブ -->
              <template #blueprint>
                <div class="h-[75vh] overflow-y-auto p-4">
                  <BlueprintPreview :preview-url="blueprint.pdfPreviewUrl" />
                </div>
              </template>

              <!-- 解析結果タブ -->
              <template #analysis>
                <div class="h-[75vh] overflow-y-auto p-4">
                  <BlueprintFormInput
                    :blueprint="blueprint.selectedBlueprint"
                    :disabled="true"
                  />
                </div>
              </template>

              <!-- アウトプットタブ -->
              <template #output>
                <div class="h-[75vh] overflow-y-auto p-4">
                  <div class="space-y-6">
                    <!-- ステップ選択ガイド -->
                    <div v-if="!selectedStep" class="text-center py-8">
                      <UIcon
                        name="i-heroicons-cursor-arrow-rays"
                        class="w-12 h-12 text-gray-400 mx-auto mb-4"
                      />
                      <div v-if="updateStepsBasedOnCurrentStep === 0">
                        <p class="text-gray-500 text-lg font-medium mb-2">
                          まだ処理が開始されていません
                        </p>
                        <p class="text-gray-400 text-sm">
                          チャットタブで処理を開始してください
                        </p>
                      </div>
                      <div v-else-if="updateStepsBasedOnCurrentStep === 1">
                        <p class="text-gray-500 text-lg font-medium mb-2">
                          Step1を実行中です
                        </p>
                        <p class="text-gray-400 text-sm">
                          Step1が完了したら、その結果が自動的に表示されます
                        </p>
                      </div>
                      <div v-else>
                        <p class="text-gray-500 text-lg font-medium mb-2">
                          ステップを選択してください
                        </p>
                        <p class="text-gray-400 text-sm mb-3">
                          左側のステップカードをクリックすると、そのステップの結果が表示されます
                        </p>
                        <UBadge variant="soft" color="primary" size="sm">
                          💡 現在Step{{
                            updateStepsBasedOnCurrentStep
                          }}を実行中のため、Step{{
                            Math.max(1, updateStepsBasedOnCurrentStep - 1)
                          }}の結果をお勧めします
                        </UBadge>
                      </div>
                    </div>

                    <!-- STEP2の製品リスト -->
                    <div v-if="selectedStep?.id === 2" class="space-y-4">
                      <Step2EstimateOutputPreview />
                      <div class="text-center">
                        <p class="text-sm text-gray-600 mb-2">
                          💡
                          製品の数量を編集して「更新保存」ボタンを押すと、見積もりデータが更新されます
                        </p>
                      </div>
                    </div>

                    <!-- STEP3の部材分解リスト -->
                    <div v-if="selectedStep?.id === 3" class="space-y-4">
                      <Step3EstimateOutputPreview />
                      <div class="text-center">
                        <p class="text-sm text-gray-600 mb-2">
                          💡
                          部品の数量や単価を編集して「更新保存」ボタンを押すと、見積もりデータが更新されます
                        </p>
                      </div>
                    </div>

                    <!-- STEP4の見積書・明細書プレビュー -->
                    <div v-if="selectedStep?.id === 4" class="space-y-6">
                      <!-- ヘッダー -->
                      <div class="text-center">
                        <h3 class="text-xl font-bold text-gray-800 mb-2">
                          📋 見積書・明細書プレビュー
                        </h3>
                      </div>

                      <!-- step4未完了時のメッセージ -->
                      <div
                        v-if="
                          !blueprintEstimateCreateProcessController.isStep5Completed
                        "
                        class="text-center py-12"
                      >
                        <UIcon
                          name="i-heroicons-cog-6-tooth"
                          class="w-16 h-16 text-gray-300 mx-auto mb-4 animate-spin"
                        />
                        <p class="text-lg font-medium text-gray-500 mb-2">
                          見積書を生成中です...
                        </p>
                        <p class="text-sm text-gray-400">
                          しばらくお待ちください
                        </p>
                      </div>

                      <!-- step5完了時のタブ表示 -->
                      <div v-else>
                        <!-- ファイル準備中の表示 -->
                        <div
                          v-if="
                            !blueprintEstimateCreateProcessController.areOutputFilesReady
                          "
                          class="text-center py-12"
                        >
                          <UIcon
                            name="i-heroicons-arrow-path"
                            class="w-16 h-16 text-blue-500 mx-auto mb-4 animate-spin"
                          />
                          <p class="text-lg font-medium text-gray-500 mb-2">
                            ファイルを準備中です...
                          </p>
                          <p class="text-sm text-gray-400">
                            プレビューの準備をしています
                          </p>
                        </div>

                        <!-- ファイル準備完了時のプレビュー -->
                        <UTabs
                          v-else
                          :items="step4PreviewTabs"
                          :default-index="0"
                          class="w-full"
                        >
                          <!-- 見積書プレビュー -->
                          <template #estimate>
                            <div class="mt-4">
                              <div v-if="estimatePdfUrl" class="h-[60vh]">
                                <iframe
                                  :src="estimatePdfUrl"
                                  class="w-full h-full border border-gray-200 rounded-lg"
                                  title="見積書プレビュー"
                                />
                              </div>
                              <div
                                v-else
                                class="h-[60vh] flex items-center justify-center"
                              >
                                <div class="text-center">
                                  <UIcon
                                    name="i-heroicons-exclamation-triangle"
                                    class="w-8 h-8 text-red-500 mx-auto mb-2"
                                  />
                                  <p class="text-red-600">
                                    見積書の読み込みに失敗しました
                                  </p>
                                </div>
                              </div>
                            </div>
                          </template>

                          <!-- 明細書プレビュー -->
                          <template #inner>
                            <div class="mt-4">
                              <div v-if="innerPdfUrl" class="h-[60vh]">
                                <iframe
                                  :src="innerPdfUrl"
                                  class="w-full h-full border border-gray-200 rounded-lg"
                                  title="明細書プレビュー"
                                />
                              </div>
                              <div
                                v-else
                                class="h-[60vh] flex items-center justify-center"
                              >
                                <div class="text-center">
                                  <UIcon
                                    name="i-heroicons-exclamation-triangle"
                                    class="w-8 h-8 text-red-500 mx-auto mb-2"
                                  />
                                  <p class="text-red-600">
                                    明細書の読み込みに失敗しました
                                  </p>
                                </div>
                              </div>
                            </div>
                          </template>
                        </UTabs>
                      </div>
                    </div>

                    <!-- 他のステップの結果表示エリア（将来的に追加） -->
                    <div
                      v-if="
                        selectedStep && ![2, 3, 4].includes(selectedStep.id)
                      "
                      class="text-center py-8"
                    >
                      <UIcon
                        name="i-heroicons-cog-6-tooth"
                        class="w-12 h-12 text-gray-400 mx-auto mb-4"
                      />
                      <p class="text-lg font-medium text-gray-500 mb-2">
                        STEP{{ selectedStep.id }}の結果
                      </p>
                      <p class="text-sm text-gray-400">
                        このステップの結果表示は準備中です
                      </p>
                    </div>
                  </div>
                </div>
              </template>
            </UTabs>
          </div>
        </div>
      </UCard>
    </template>
  </UModal>
</template>

<script setup lang="ts">
//#region import
import { ref, watch, nextTick, computed } from "vue";
import log from "@utils/logger";
// Firebase関連のインポートはストア側で処理されるため削除
import { convertMarkdownToHtml } from "@utils/markdown";
//#endregion

//#region types
interface EstimateStep {
  id: number;
  title: string;
  description: string;
  status: "pending" | "in-progress" | "completed";
  details: string;
}

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

//#region reactive-data
const selectedStep = ref<EstimateStep | null>(null);
const estimatePdfUrl = ref<string | null>(null);
const innerPdfUrl = ref<string | null>(null);
const currentActiveTab = ref("0"); // 現在のアクティブタブを追跡
//#endregion reactive-data

//#region store
const googleAiAgent = useGoogleAiAgentStore();
const blueprintEstimateCreateProcessController =
  useBlueprintEstimateCreateProcessControllerStore();
const blueprint = useBlueprintStore();
const toast = useToast();
//#endregion

//#region ui-config
const userInput = ref("");
const conversationArea = ref<HTMLElement | null>(null);

// タブ設定
const tabItems = [
  {
    label: "チャット",
    slot: "chat",
    icon: "i-heroicons-chat-bubble-left-right",
  },
  {
    label: "アウトプット確認",
    slot: "output",
    icon: "i-heroicons-clipboard-document-list",
  },
  {
    label: "図面",
    slot: "blueprint",
    icon: "i-heroicons-document-text",
  },
  {
    label: "解析結果",
    slot: "analysis",
    icon: "i-heroicons-chart-bar",
  },
];

// step4プレビュー用のタブ設定
const step4PreviewTabs = [
  {
    label: "📄 見積書",
    slot: "estimate",
  },
  {
    label: "📊 明細書",
    slot: "inner",
  },
];

// ステップ定義
const estimateSteps = ref<EstimateStep[]>([
  {
    id: 1,
    title: "図面情報の取得",
    description: "アップロードされた図面から基本情報を抽出",
    status: "pending",
    details: "",
  },
  {
    id: 2,
    title: "対象製品の特定",
    description: "図面から製造対象となる製品を特定",
    status: "pending",
    details: "",
  },
  {
    id: 3,
    title: "明細の確定",
    description: "製品製造に必要な部品リストを確定",
    status: "pending",
    details: "",
  },
  {
    id: 4,
    title: "見積書の出力",
    description: "見積書を出力",
    status: "pending",
    details: "",
  },
]);
//#endregion ui-config

//#region computed
// currentStepに基づくステップ状態の更新
const updateStepsBasedOnCurrentStep = computed(() => {
  const currentStep =
    blueprintEstimateCreateProcessController
      .selectedBlueprintCostEstimationCreateJob?.currentStep || 0;

  // ステップごとの詳細メッセージ定義
  const stepMessages = {
    completed: [
      "図面情報の取得が完了しました",
      "対象製品の特定が完了しました",
      "使用部品の洗い出しが完了しました",
      "部品数量/金額の確定が完了しました",
      "見積書作成が完了しました",
    ],
    inProgress: [
      "図面から基本情報を抽出中...",
      "図面から製造対象製品を特定中...",
      "製品製造に必要な部品を洗い出し中...",
      "各部品の必要数量と単価を算出中...",
      "最終的な見積書を生成中...",
    ],
  };

  // ステップ状態を更新
  estimateSteps.value.forEach((step, index) => {
    const stepNumber = index + 1;
    if (stepNumber < currentStep) {
      // 現在ステップより前は完了
      step.status = "completed";
      step.details =
        stepMessages.completed[index] || `ステップ${stepNumber}が完了しました`;
    } else if (stepNumber === currentStep) {
      // 現在のステップは進行中
      step.status = "in-progress";
      step.details =
        stepMessages.inProgress[index] || `ステップ${stepNumber}を実行中...`;
    } else {
      // 現在ステップより後は未開始
      step.status = "pending";
      step.details = "";
    }
  });

  return currentStep;
});

// 完了したステップ数（currentStepベース）
const completedStepsCount = computed(() => {
  const currentStep = updateStepsBasedOnCurrentStep.value;
  return Math.max(0, currentStep - 1); // currentStepより前のステップが完了済み
});

// 進捗パーセンテージ（currentStepベース）
const progressPercentage = computed(() => {
  const currentStep = updateStepsBasedOnCurrentStep.value;
  const totalSteps = estimateSteps.value.length;

  if (currentStep === 0) return 0;
  if (currentStep > totalSteps) return 100;

  // 現在のステップまでの進捗を計算（現在ステップは50%として計算）
  const completedProgress = Math.max(0, currentStep - 1) * (100 / totalSteps);
  const currentStepProgress = 0.5 * (100 / totalSteps); // 現在ステップは50%進行として計算

  return Math.round(completedProgress + currentStepProgress);
});

// currentStepに基づいて自動選択すべきステップを決定
const autoSelectedStep = computed(() => {
  const currentStep = updateStepsBasedOnCurrentStep.value;

  // currentStepが0の場合は何も選択しない
  if (currentStep === 0) return null;

  // currentStepが進行中の場合は、1つ前の完了済みステップを表示
  // (進行中のステップのアウトプットはまだ存在しないため)
  let targetStepId: number;

  if (currentStep === 1) {
    // Step1進行中の場合は表示するものがない
    return null;
  } else if (currentStep <= estimateSteps.value.length) {
    // Step2以降進行中の場合は、1つ前の完了済みステップを表示
    targetStepId = currentStep - 1;
  } else {
    // 全ステップ完了の場合は、最後のステップ(Step4)を表示
    targetStepId = estimateSteps.value.length;
  }

  // 対象のステップIDに該当するステップオブジェクトを返す
  return estimateSteps.value.find((step) => step.id === targetStepId) || null;
});

//#endregion

//#region methods
// 削除: startEstimateConversationメソッドはストア側に移動されました

// メッセージを送信する
const sendMessage = async () => {
  if (!userInput.value.trim() || googleAiAgent.isProcessing) return;

  const message = userInput.value.trim();
  userInput.value = "";

  try {
    await googleAiAgent.sendQueryToAgent(message);
    // 会話エリアを最下部にスクロール
    await scrollToBottom();
  } catch (error) {
    log("ERROR", "メッセージ送信でエラーが発生しました:", error);
    toast.add({
      title: "エラー",
      description: "メッセージの送信に失敗しました",
      color: "error",
    });
  }
};

// ステップを選択
const selectStep = (step: EstimateStep) => {
  log("INFO", "ステップが選択されました:", step);
  selectedStep.value = step;
};

// ステータステキストを取得
const getStatusText = (status: string) => {
  switch (status) {
    case "completed":
      return "完了";
    case "in-progress":
      return "進行中";
    case "pending":
    default:
      return "未開始";
  }
};

// ステータスに応じたバッジカラーを取得
const getBadgeColor = (status: string) => {
  switch (status) {
    case "completed":
      return "success";
    case "in-progress":
      return "primary";
    case "pending":
    default:
      return "neutral";
  }
};

// Enterキーの処理
const handleEnterKey = (event: KeyboardEvent) => {
  if (event.ctrlKey || event.metaKey) {
    // Ctrl+Enter または Cmd+Enter で送信
    sendMessage();
  }
  // 通常のEnterは改行（デフォルト動作）
};

// 会話エリアを最下部にスクロール
const scrollToBottom = async () => {
  await nextTick();
  if (conversationArea.value) {
    conversationArea.value.scrollTop = conversationArea.value.scrollHeight;
  }
};

// 時刻をフォーマット
const formatTime = (date: Date) => {
  return date.toLocaleTimeString("ja-JP", {
    hour: "2-digit",
    minute: "2-digit",
  });
};

// アウトプット確認タブに移動したタイミングでcurrentStepに基づいてステップを自動選択
const handleOutputTabActivation = () => {
  log("INFO", "アウトプット確認タブがアクティブになりました");

  // 🎯 書類生成完了済みの場合はstep4を優先表示
  const allProcessCompleted =
    blueprintEstimateCreateProcessController
      .selectedBlueprintCostEstimationCreateJob.allProcessCompleted;

  if (allProcessCompleted) {
    const step4 = estimateSteps.value.find((step) => step.id === 4);
    if (step4) {
      selectedStep.value = step4;
      log("INFO", "書類生成完了済みのため、Step4を自動選択しました");
      return;
    }
  }

  // 書類生成完了前は従来のロジックを使用
  // 自動選択すべきステップが存在する場合
  if (autoSelectedStep.value) {
    log(
      "INFO",
      "currentStepベースでステップを自動選択します:",
      autoSelectedStep.value
    );
    selectedStep.value = autoSelectedStep.value;
  } else {
    log(
      "INFO",
      "自動選択可能なステップがありません（処理開始前またはStep1進行中）"
    );
    selectedStep.value = null;
  }
};

// 図面データとPDFプレビューURLを取得
const loadBlueprintData = async () => {
  if (blueprint.selectedBlueprintId) {
    try {
      await blueprint.fetchBlueprintById({
        blueprintId: blueprint.selectedBlueprintId,
      });
      log("INFO", "図面データとPDFプレビューURLを取得しました");
    } catch (error) {
      log("ERROR", "図面データの取得に失敗しました:", error);
      toast.add({
        title: "エラー",
        description: "図面の読み込みに失敗しました",
        color: "error",
      });
    }
  }
};

// stateのBlobからプレビューURLを生成
const createPdfPreviewUrls = () => {
  // 見積書のプレビューURL生成
  if (blueprintEstimateCreateProcessController.isEstimationFileReady) {
    if (estimatePdfUrl.value) {
      URL.revokeObjectURL(estimatePdfUrl.value);
    }
    estimatePdfUrl.value = URL.createObjectURL(
      blueprintEstimateCreateProcessController.outputEstimationFile!
    );
    log("INFO", "見積書プレビューURLを生成しました");
  }

  // 明細書のプレビューURL生成
  if (blueprintEstimateCreateProcessController.isPartsBreakdownFileReady) {
    if (innerPdfUrl.value) {
      URL.revokeObjectURL(innerPdfUrl.value);
    }
    innerPdfUrl.value = URL.createObjectURL(
      blueprintEstimateCreateProcessController.outputPartsBreakdownFile!
    );
    log("INFO", "明細書プレビューURLを生成しました");
  }
};

//#endregion methods

// 会話履歴が更新されたら自動スクロール
watch(
  () => googleAiAgent.conversationHistoryForView,
  async () => {
    await scrollToBottom();
  },
  { deep: true }
);

// モーダルが閉じられたときにクリーンアップ
watch(
  () => props.open,
  (open) => {
    if (!open) {
      // ストアをリセット
      googleAiAgent.resetStore();
      userInput.value = "";
      selectedStep.value = null;

      // プレビューURLをクリーンアップ
      if (estimatePdfUrl.value) {
        URL.revokeObjectURL(estimatePdfUrl.value);
        estimatePdfUrl.value = null;
      }
      if (innerPdfUrl.value) {
        URL.revokeObjectURL(innerPdfUrl.value);
        innerPdfUrl.value = null;
      }

      // 出力ファイルのstateをリセット
      blueprintEstimateCreateProcessController.resetOutputFiles();
    } else {
      // モーダルが開かれた時に図面データを取得
      loadBlueprintData();
    }
  }
);

// 削除済み - step4プレビューはstateベースの実装に変更

// currentStep==5を監視してファイルを自動ダウンロード＋アウトプット確認タブに自動移動
watch(
  () =>
    blueprintEstimateCreateProcessController
      .selectedBlueprintCostEstimationCreateJob.allProcessCompleted,
  async (allProcessCompleted) => {
    if (allProcessCompleted) {
      log("INFO", "Step5完了を検知、出力ファイルのダウンロードを開始します");
      await blueprintEstimateCreateProcessController.downloadOutputFiles();
      // update state
      blueprintEstimateCreateProcessController.pdfFileIsDownloaded = true;

      // 🎯 書類生成完了時に自動的にアウトプット確認タブに移動＋step4を選択
      log("INFO", "書類生成完了により、アウトプット確認タブに自動移動します");
      currentActiveTab.value = "1"; // アウトプット確認タブ（配列の1番目）

      // step4を自動選択
      const step4 = estimateSteps.value.find((step) => step.id === 4);
      if (step4) {
        selectedStep.value = step4;
        log("INFO", "Step4を自動選択しました");
      }

      // ユーザーに通知
      toast.add({
        title: "🎉 見積書生成完了",
        description: "アウトプット確認タブで見積書と明細書をプレビューできます",
        color: "success",
      });
    }
  },
  { immediate: true }
);

// 出力ファイルが準備完了したらプレビューURLを生成
watch(
  () => [
    blueprintEstimateCreateProcessController.isEstimationFileReady,
    blueprintEstimateCreateProcessController.isPartsBreakdownFileReady,
  ],
  ([isEstimationReady, isPartsBreakdownReady]) => {
    if (isEstimationReady || isPartsBreakdownReady) {
      log("INFO", "出力ファイルが準備完了、プレビューURLを生成します", {
        estimationReady: isEstimationReady,
        partsBreakdownReady: isPartsBreakdownReady,
      });
      createPdfPreviewUrls();
    }
  },
  { immediate: true }
);

// アウトプット確認タブの変更を監視
watch(
  () => currentActiveTab.value,
  (newTab, oldTab) => {
    log("INFO", `タブが変更されました: ${oldTab} → ${newTab}`);

    // アウトプット確認タブに移動した場合
    if (newTab === "output") {
      handleOutputTabActivation();
    }
  }
);

//#region lifecycle-hooks
// blueprint storeのfetchBlueprintByIdでpdfPreviewUrlも更新されるため、
// 個別のマウント処理は不要

//#endregion lifecycle-hooks
</script>

<style scoped>
/* アニメーション定義 */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out forwards;
}

/* GitHub風Markdownスタイル */
.github-markdown {
  color: #24292f;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans",
    Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-words;
  overflow-wrap: anywhere;
  word-break: break-word;
  hyphens: auto;
  max-width: 100%;
}

.github-markdown h1,
.github-markdown h2,
.github-markdown h3,
.github-markdown h4,
.github-markdown h5,
.github-markdown h6 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
  color: #1f2328;
}

.github-markdown h1 {
  font-size: 2em;
  border-bottom: 1px solid #d0d7de;
  padding-bottom: 0.3em;
}

.github-markdown h2 {
  font-size: 1.5em;
  border-bottom: 1px solid #d0d7de;
  padding-bottom: 0.3em;
}

.github-markdown h3 {
  font-size: 1.25em;
  border-bottom: 1px solid #d0d7de;
  padding-bottom: 0.3em;
}

.github-markdown h4 {
  font-size: 1em;
  border-bottom: 1px solid #d0d7de;
  padding-bottom: 0.3em;
}

.github-markdown h5 {
  font-size: 0.875em;
  border-bottom: 1px solid #d0d7de;
  padding-bottom: 0.3em;
}

.github-markdown h6 {
  font-size: 0.85em;
  color: #656d76;
}

.github-markdown p {
  margin-top: 0;
  margin-bottom: 16px;
}

.github-markdown blockquote {
  margin: 0;
  padding: 0 1em;
  color: #656d76;
  border-left: 0.25em solid #d0d7de;
  margin-bottom: 16px;
}

.github-markdown ul,
.github-markdown ol {
  margin-top: 0;
  margin-bottom: 16px;
  padding-left: 2em;
}

.github-markdown li {
  margin-bottom: 0.25em;
}

.github-markdown li > p {
  margin-bottom: 0;
  margin-top: 16px;
}

.github-markdown li + li {
  margin-top: 0.25em;
}

.github-markdown code {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  white-space: break-spaces;
  background-color: rgba(175, 184, 193, 0.2);
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas,
    "Liberation Mono", Menlo, monospace;
}

.github-markdown pre {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 6px;
  margin-bottom: 16px;
  border: 1px solid #d0d7de;
}

.github-markdown pre code {
  display: inline;
  max-width: auto;
  padding: 0;
  margin: 0;
  overflow: visible;
  line-height: inherit;
  word-wrap: normal;
  background-color: transparent;
  border: 0;
}

.github-markdown table {
  border-spacing: 0;
  border-collapse: collapse;
  display: block;
  width: max-content;
  max-width: 100%;
  overflow: auto;
  margin-bottom: 16px;
}

.github-markdown table th,
.github-markdown table td {
  padding: 6px 13px;
  border: 1px solid #d0d7de;
}

.github-markdown table th {
  font-weight: 600;
  background-color: #f6f8fa;
}

.github-markdown table tr {
  background-color: #ffffff;
  border-top: 1px solid #c6cbd1;
}

.github-markdown table tr:nth-child(2n) {
  background-color: #f6f8fa;
}

.github-markdown a {
  color: #0969da;
  text-decoration: none;
}

.github-markdown a:hover {
  text-decoration: underline;
}

.github-markdown strong {
  font-weight: 600;
}

.github-markdown em {
  font-style: italic;
}

.github-markdown hr {
  height: 0.25em;
  padding: 0;
  margin: 24px 0;
  background-color: #d0d7de;
  border: 0;
}

/* ユーザーメッセージ（青いバブル）内のMarkdownスタイル調整 */
.bg-gradient-to-br.from-blue-500 .github-markdown,
.bg-gradient-to-br.from-blue-500 .github-markdown h1,
.bg-gradient-to-br.from-blue-500 .github-markdown h2,
.bg-gradient-to-br.from-blue-500 .github-markdown h3,
.bg-gradient-to-br.from-blue-500 .github-markdown h4,
.bg-gradient-to-br.from-blue-500 .github-markdown h5,
.bg-gradient-to-br.from-blue-500 .github-markdown h6 {
  color: #ffffff !important;
}

.bg-gradient-to-br.from-blue-500 .github-markdown h1,
.bg-gradient-to-br.from-blue-500 .github-markdown h2 {
  border-bottom-color: rgba(255, 255, 255, 0.3);
}

.bg-gradient-to-br.from-blue-500 .github-markdown h3 {
  border-bottom-color: rgba(255, 255, 255, 0.3);
}

.bg-gradient-to-br.from-blue-500 .github-markdown h4 {
  border-bottom-color: rgba(255, 255, 255, 0.3);
}

.bg-gradient-to-br.from-blue-500 .github-markdown h5 {
  border-bottom-color: rgba(255, 255, 255, 0.3);
}

.bg-gradient-to-br.from-blue-500 .github-markdown blockquote {
  color: rgba(255, 255, 255, 0.8);
  border-left-color: rgba(255, 255, 255, 0.3);
}

.bg-gradient-to-br.from-blue-500 .github-markdown code {
  background-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.bg-gradient-to-br.from-blue-500 .github-markdown pre {
  background-color: rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.bg-gradient-to-br.from-blue-500 .github-markdown a {
  color: #87ceeb;
}

.bg-gradient-to-br.from-blue-500 .github-markdown hr {
  background-color: rgba(255, 255, 255, 0.3);
}

/* スクロールバーのスタイリング - より洗練されたデザイン */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #cbd5e1, #94a3b8);
  border-radius: 10px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #94a3b8, #64748b);
}

/* ホバーエフェクトの改良 */
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .max-w-\[75\%\] {
    max-width: 85%;
  }

  .github-markdown {
    font-size: 13px;
  }

  .github-markdown h1 {
    font-size: 1.6em;
  }

  .github-markdown h2 {
    font-size: 1.3em;
  }

  .github-markdown pre {
    padding: 12px;
    font-size: 80%;
  }
}

/* グラデーション背景のアニメーション */
.bg-gradient-to-br {
  background-size: 200% 200%;
  animation: gradient-shift 3s ease infinite;
}

@keyframes gradient-shift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
</style>
