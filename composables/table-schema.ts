export const useTableSchema = () => {
  const tableSchema = {
    "admin-user-group-upload-preview": {
      columns: [
        {
          accessorKey: "userId",
          header: "ユーザーID",
          sortable: true,
        },
        {
          accessorKey: "email",
          header: "メールアドレス",
          sortable: true,
        },
        {
          accessorKey: "freeText",
          header: "フリーテキスト",
          sortable: true,
        },
      ],
    },
    "admin-user-group-user-list": {
      columns: [
        {
          accessorKey: "userId",
          header: "ユーザーID",
          sortable: true,
        },
        {
          accessorKey: "role",
          header: "ロール",
          sortable: true,
        },
        {
          accessorKey: "email",
          header: "メールアドレス",
          sortable: true,
        },
        {
          accessorKey: "freeText",
          header: "メモ",
          sortable: true,
        },

        {
          accessorKey: "createdAt",
          header: "登録日時",
          sortable: true,
        },
      ],
    },
    "admin-shipping-event-list": {
      columns: [
        {
          accessorKey: "start",
          header: "出荷日",
          sortable: true,
        },
        {
          accessorKey: "productInfo",
          header: "商品名",
          sortable: true,
        },
        {
          accessorKey: "quantity",
          header: "数量",
          sortable: true,
        },
      ],
    },
    "admin-master-set-calendar-event": {
      columns: [
        {
          accessorKey: "code",
          header: "コード",
          sortable: true,
        },
        {
          accessorKey: "name",
          header: "名称",
          sortable: true,
        },
        {
          accessorKey: "description",
          header: "説明",
          sortable: true,
        },
      ],
    },
    "admin-inventory-plan-product-stock-input": {
      columns: [
        {
          accessorKey: "code",
          header: "コード",
        },
        {
          accessorKey: "name",
          header: "名称",
        },
        {
          accessorKey: "currentStock",
          header: "本日時点の在庫",
        },
        {
          accessorKey: "maxInventory",
          header: "上限在庫数",
        },
        {
          accessorKey: "safetyStockLevel",
          header: "欠品判定ライン",
        },
      ],
    },
    "admin-material-event-for-analysis": {
      columns: [
        {
          accessorKey: "start",
          header: "開始日",
        },
        {
          accessorKey: "end",
          header: "終了日",
        },
        {
          accessorKey: "note",
          header: "備考",
        },
        {
          accessorKey: "quantity",
          header: "数量",
        },
        {
          accessorKey: "materialName",
          header: "原料名",
        },
        {
          accessorKey: "type",
          header: "タイプ",
        },
        {
          accessorKey: "tag1",
          header: "タグ1",
        },
        {
          accessorKey: "tag2",
          header: "タグ2",
        },
        {
          accessorKey: "tag3",
          header: "タグ3",
        },
        {
          accessorKey: "tag4",
          header: "タグ4",
        },
        {
          accessorKey: "tag5",
          header: "タグ5",
        },
        {
          accessorKey: "tag6",
          header: "タグ6",
        },
        {
          accessorKey: "tag7",
          header: "タグ7",
        },
        {
          accessorKey: "tag8",
          header: "タグ8",
        },
        {
          accessorKey: "tag9",
          header: "タグ9",
        },
        {
          accessorKey: "tag10",
          header: "タグ10",
        },
      ],
    },
    "admin-production-history-and-plan-event": {
      columns: [
        {
          accessorKey: "start",
          header: "開始日",
        },
        {
          accessorKey: "end",
          header: "終了日",
        },
        {
          accessorKey: "note",
          header: "備考",
        },
        {
          accessorKey: "quantity",
          header: "数量",
        },
        {
          accessorKey: "productName",
          header: "商品名",
        },
        {
          accessorKey: "tag1",
          header: "タグ1",
        },
        {
          accessorKey: "tag2",
          header: "タグ2",
        },
        {
          accessorKey: "tag3",
          header: "タグ3",
        },
        {
          accessorKey: "tag4",
          header: "タグ4",
        },
        {
          accessorKey: "tag5",
          header: "タグ5",
        },
        {
          accessorKey: "tag6",
          header: "タグ6",
        },
        {
          accessorKey: "tag7",
          header: "タグ7",
        },
        {
          accessorKey: "tag8",
          header: "タグ8",
        },
        {
          accessorKey: "tag9",
          header: "タグ9",
        },
        {
          accessorKey: "tag10",
          header: "タグ10",
        },
      ],
    },
    "admin-inventory-plan-shipping-event": {
      columns: [
        {
          accessorKey: "start",
          header: "開始日",
        },
        {
          accessorKey: "end",
          header: "終了日",
        },
        {
          accessorKey: "note",
          header: "備考",
        },
        {
          accessorKey: "quantity",
          header: "数量",
        },
        {
          accessorKey: "productName",
          header: "商品名",
        },
        {
          accessorKey: "tag1",
          header: "タグ1",
        },
        {
          accessorKey: "tag2",
          header: "タグ2",
        },
        {
          accessorKey: "tag3",
          header: "タグ3",
        },
        {
          accessorKey: "tag4",
          header: "タグ4",
        },
        {
          accessorKey: "tag5",
          header: "タグ5",
        },
        {
          accessorKey: "tag6",
          header: "タグ6",
        },
        {
          accessorKey: "tag7",
          header: "タグ7",
        },
        {
          accessorKey: "tag8",
          header: "タグ8",
        },
        {
          accessorKey: "tag9",
          header: "タグ9",
        },
        {
          accessorKey: "tag10",
          header: "タグ10",
        },
      ],
    },
    "admin-inventory-plan-shipping-event-for-analysis": {
      columns: [
        {
          accessorKey: "start",
          header: "開始日",
        },
        {
          accessorKey: "end",
          header: "終了日",
        },
        {
          accessorKey: "note",
          header: "備考",
        },

        {
          accessorKey: "productInfo",
          header: "商品",
        },
        {
          accessorKey: "materialInfo",
          header: "原料",
        },
        {
          accessorKey: "tag1",
          header: "タグ1",
        },
        {
          accessorKey: "tag2",
          header: "タグ2",
        },
        {
          accessorKey: "tag3",
          header: "タグ3",
        },
        {
          accessorKey: "tag4",
          header: "タグ4",
        },
        {
          accessorKey: "tag5",
          header: "タグ5",
        },
        {
          accessorKey: "tag6",
          header: "タグ6",
        },
        {
          accessorKey: "tag7",
          header: "タグ7",
        },
        {
          accessorKey: "tag8",
          header: "タグ8",
        },
        {
          accessorKey: "tag9",
          header: "タグ9",
        },
        {
          accessorKey: "tag10",
          header: "タグ10",
        },
        {
          accessorKey: "quantity",
          header: "数量",
        },
        {
          accessorKey: "productPrice",
          header: "単価",
        },
        {
          accessorKey: "totalSales",
          header: "販売価格",
        },

        {
          accessorKey: "materialQuantity",
          header: "原料数量(kg)",
        },
        {
          accessorKey: "materialCost",
          header: "原料価格",
        },

        {
          accessorKey: "grossProfit",
          header: "粗利",
        },
        {
          accessorKey: "grossProfitRate",
          header: "粗利率(%)",
        },
      ],
    },
    "admin-inventory-plan-product-master-simple": {
      columns: [
        {
          accessorKey: "code",
          header: "コード",
        },
        {
          accessorKey: "name",
          header: "名称",
        },
        {
          accessorKey: "note",
          header: "説明",
        },
        {
          accessorKey: "productCapacity",
          header: "商品容量(kg)",
        },
        {
          accessorKey: "currentStock",
          header: "本日時点の在庫",
        },
        {
          accessorKey: "price",
          header: "販売価格",
        },
        {
          accessorKey: "materialCode",
          header: "原料",
        },
        {
          accessorKey: "yieldRate",
          header: "歩留率",
        },
        {
          accessorKey: "maxProductionAmountPer1day",
          header: "1日あたりの最大製造数",
        },
        {
          accessorKey: "maxInventory",
          header: "上限在庫数",
        },
        {
          accessorKey: "safetyStockLevel",
          header: "安全在庫",
        },
      ],
    },
    "admin-inventory-plan-product-master": {
      columns: [
        {
          accessorKey: "expandIcon",
          header: "",
        },
        {
          accessorKey: "imageUrl",
          header: "画像",
          sortable: true,
        },

        {
          accessorKey: "code",
          header: "コード",
          sortable: true,
        },
        {
          accessorKey: "name",
          header: "名称",
          sortable: true,
        },
        {
          accessorKey: "totalProductionPriorityScore",
          header: "合計発注スコア",
          sortable: true,
        },
        {
          accessorKey: "currentStock",
          header: "本日時点の在庫",
          sortable: true,
        },
        {
          accessorKey: "maxProductionAmountPer1dayByMaterialInfo",
          header: "原料ベースの最大製造数",
          sortable: true,
        },
        {
          accessorKey: "maxInventory",
          header: "上限在庫数",
          sortable: true,
        },
        {
          accessorKey: "safetyStockLevel",
          header: "欠品判定ライン数",
          sortable: true,
        },
        {
          accessorKey: "diffValueCurrentStockAndMaxInventory",
          header: "本日時点の在庫と上限在庫の差分",
          sortable: true,
        },
        {
          accessorKey: "maxProductionCountPerDay",
          header: "最大生産量",
          sortable: true,
        },
        {
          accessorKey: "firstBelowSafetyStockDays",
          header: "初欠品までの日数",
          sortable: true,
        },
        {
          accessorKey: "next30DaysMaxShipment",
          header: "翌30日間の最大出荷数",
          sortable: true,
        },
        {
          accessorKey: "totalProduction",
          header: "総生産数",
          sortable: true,
        },
        {
          accessorKey: "totalOutStock",
          header: "総出庫数",
          sortable: true,
        },
        {
          accessorKey: "shortageDays",
          header: "欠品日数",
          sortable: true,
        },
      ],
    },
    "admin-master-set-master-calendar-mapping": {
      columns: [
        {
          accessorKey: "start",
          header: "日",
        },
        {
          accessorKey: "materialMasterTypeKey",
          header: "原料",
        },
        {
          accessorKey: "productMasterTypeKey",
          header: "製品",
        },
        {
          accessorKey: "rulesetTypeKey",
          header: "生産ルール",
        },
      ],
    },
    "admin-master-set-material-simple": {
      columns: [
        {
          accessorKey: "code",
          header: "コード",
        },
        {
          accessorKey: "name",
          header: "名称",
        },
        {
          accessorKey: "currentStock",
          header: "現在在庫",
        },
        {
          accessorKey: "minStock",
          header: "最小在庫",
        },
        {
          accessorKey: "maxStock",
          header: "最大在庫",
        },
        {
          accessorKey: "maxDailyInputKilogram",
          header: "1日あたりの最大投入量(kg)",
        },
        {
          accessorKey: "minInputUnitPerBatch",
          header: "1回あたりの最小投入量",
        },
        {
          accessorKey: "pricePerKilogram",
          header: "1gあたりの価格",
        },
        {
          accessorKey: "description",
          header: "説明",
        },
      ],
    },
    "admin-master-set-material": {
      columns: [
        {
          accessorKey: "imageUrl",
          header: "原料画像",
        },
        {
          accessorKey: "code",
          header: "コード",
        },

        {
          accessorKey: "name",
          header: "名称",
        },
        {
          accessorKey: "currentStock",
          header: "現在在庫",
        },
        {
          accessorKey: "minStock",
          header: "最小在庫",
        },
        {
          accessorKey: "maxStock",
          header: "最大在庫",
        },
        {
          accessorKey: "maxDailyInputKilogram",
          header: "1日あたりの最大投入量(kg)",
        },
        {
          accessorKey: "minInputUnitPerBatch",
          header: "1回あたりの最小投入量",
        },
        {
          accessorKey: "pricePerKilogram",
          header: "1gあたりの価格",
        },
        {
          accessorKey: "description",
          header: "説明",
        },
      ],
    },
    "admin-production-simulator-history": {
      columns: [
        {
          accessorKey: "executionId",
          header: "実行ID",
        },
        {
          accessorKey: "status",
          header: "ステータス",
        },
        {
          accessorKey: "createdAt",
          header: "実行日時",
        },
        {
          accessorKey: "reportDl",
          header: "レポートDL",
        },
        {
          accessorKey: "chatWithGemini",
          header: "",
        },
      ],
    },
    "admin-production-simulator-optimize-result-products": {
      columns: [
        {
          accessorKey: "product_name",
          header: "製品名",
        },
        {
          accessorKey: "production",
          header: "本日の製造個数",
        },
        {
          accessorKey: "priority",
          header: "優先度スコア",
        },
        {
          accessorKey: "capacity",
          header: "製品単位の製造上限",
        },
        {
          accessorKey: "production_rate",
          header: "製造率",
        },
      ],
    },
    "admin-production-simulator-optimize-result-materials": {
      columns: [
        {
          accessorKey: "material_code",
          header: "コード",
        },
        {
          accessorKey: "materialInfo",
          header: "原料",
        },
        {
          accessorKey: "total_consumption",
          header: "本日の投入量",
        },
        {
          accessorKey: "limit",
          header: "1日の投入上限",
        },
        {
          accessorKey: "consumption_rate",
          header: "原料の投入率",
        },
      ],
    },
    "admin-production-simulator-find-out-of-stock-products": {
      columns: [
        {
          accessorKey: "priority",
          header: "優先度",
        },
        {
          accessorKey: "date",
          header: "日付",
        },
        {
          accessorKey: "imageUrl",
          header: "",
        },
        {
          accessorKey: "code",
          header: "コード",
        },
        {
          accessorKey: "name",
          header: "商品名",
        },
        {
          accessorKey: "currentStock",
          header: "現在在庫",
        },
        {
          accessorKey: "outStock",
          header: "出庫数",
        },
        {
          accessorKey: "diffCurrentStockAndOutStock",
          header: "現在在庫-出庫数",
        },
        {
          accessorKey: "maxProductionAmountPer1day",
          header: "1日最大製造量",
        },
        {
          accessorKey: "productionRotationCount",
          header: "必要な生産回数",
        },
      ],
    },
    "admin-production-simulator-find-out-of-stock-materials": {
      columns: [
        {
          accessorKey: "code",
          header: "原料コード",
        },
        {
          accessorKey: "name",
          header: "原料名",
        },
        {
          accessorKey: "maxUsage",
          header: "本日の最大使用量",
        },
        {
          accessorKey: "used",
          header: "使用済み",
        },
        {
          accessorKey: "remaining",
          header: "残量",
        },
      ],
    },
    "admin-production-simulator-find-out-of-stock-products-add-result": {
      columns: [
        {
          accessorKey: "status",
          header: "ステータス",
        },
        {
          accessorKey: "priority",
          header: "優先度",
        },
        {
          accessorKey: "date",
          header: "日付",
        },
        {
          accessorKey: "imageUrl",
          header: "",
        },
        {
          accessorKey: "code",
          header: "コード",
        },
        {
          accessorKey: "name",
          header: "商品名",
        },
        {
          accessorKey: "productionResult",
          header: "製造結果",
        },
        {
          accessorKey: "currentStock",
          header: "現在在庫",
        },
        {
          accessorKey: "outStock",
          header: "出庫数",
        },
        {
          accessorKey: "diffCurrentStockAndOutStock",
          header: "現在在庫-出庫数",
        },
        {
          accessorKey: "maxProductionAmountPer1day",
          header: "1日最大製造量",
        },
        {
          accessorKey: "productionRotationCount",
          header: "必要な生産回数",
        },
      ],
    },
    "admin-production-simulator-fixed-product-master": {
      columns: [
        {
          accessorKey: "code",
          header: "コード",
        },
        {
          accessorKey: "productInfo",
          header: "商品",
        },
        {
          accessorKey: "materialInfo",
          header: "製造原料",
        },
        {
          accessorKey: "currentStock",
          header: "本日時点の在庫",
        },
        {
          accessorKey: "maxProductionAmountPer1day",
          header: "1日あたりの製造可能量",
        },

        {
          accessorKey: "maxProductionAmountPer1day",
          header: "1日あたりの製造可能量",
        },
        {
          accessorKey: "yieldRate",
          header: "製造効率",
        },
        {
          accessorKey: "productCapacity",
          header: "商品容量",
        },
        {
          accessorKey: "materialMaxDailyInputKilogram",
          header: "原料の最大投入量",
        },
      ],
    },
    "admin-production-simulator-available-resources": {
      productGroups: {
        columns: [
          {
            accessorKey: "code",
            header: "コード",
          },
          {
            accessorKey: "name",
            header: "名前",
          },
          {
            accessorKey: "isAllRulesPassed",
            header: "稼働判定",
          },
          {
            accessorKey: "production_group_used_today",
            header: "本日まだ使用されていない",
          },
          {
            accessorKey: "production_group_prohibited_by_event_calendar",
            header: "イベントカレンダーによって禁止されていない",
          },
        ],
      },
      products: {
        columns: [
          {
            accessorKey: "code",
            header: "コード",
          },
          {
            accessorKey: "name",
            header: "名前",
          },
          {
            accessorKey: "isAllRulesPassed",
            header: "稼働判定",
          },
          {
            accessorKey: "product_used_today",
            header: "本日まだ使用されていない",
          },
          {
            accessorKey:
              "product_used_today_is_prohibited_by_event_as_item_layer_rule",
            header: "イベントカレンダーによって禁止されていない",
          },
        ],
      },
      materials: {
        columns: [
          {
            accessorKey: "code",
            header: "コード",
          },
          {
            accessorKey: "name",
            header: "名前",
          },
          {
            accessorKey: "isAllRulesPassed",
            header: "稼働判定",
          },
          {
            accessorKey: "material_used_today",
            header: "本日まだ使用されていない",
          },
        ],
      },
      facilities: {
        columns: [
          {
            accessorKey: "code",
            header: "コード",
          },
          {
            accessorKey: "name",
            header: "名前",
          },
          {
            accessorKey: "isAllRulesPassed",
            header: "稼働判定",
          },
          {
            accessorKey: "facility_used_today",
            header: "本日既に使用されているか?",
          },
        ],
      },
    },
    "admin-master-set-product": {
      columns: [
        {
          accessorKey: "imageUrl",
          header: "",
        },
        {
          accessorKey: "code",
          header: "コード",
        },
        {
          accessorKey: "name",
          header: "名称",
        },
        {
          accessorKey: "currentStock",
          header: "現在在庫",
        },
        {
          accessorKey: "materialCode",
          header: "製品原料",
        },

        {
          accessorKey: "yieldRate",
          header: "製造率",
        },
        {
          accessorKey: "productCapacity",
          header: "商品容量",
        },
        {
          accessorKey: "price",
          header: "販売価格",
        },
        {
          accessorKey: "maxProductionAmountPer1dayByMaterialInfo",
          header: "原料ベースの最大製造数",
          sortable: true,
        },
        {
          accessorKey: "maxInventory",
          header: "上限在庫",
        },
        {
          accessorKey: "safetyStockLevel",
          header: "安全在庫",
        },
        {
          accessorKey: "note",
          header: "備考",
        },
      ],
    },
    "admin-master-set-product-group": {
      columns: [
        {
          accessorKey: "code",
          header: "コード",
        },
        {
          accessorKey: "name",
          header: "名称",
        },
        {
          accessorKey: "description",
          header: "説明",
        },
        {
          accessorKey: "priority",
          header: "優先度",
        },
        {
          accessorKey: "workerCode",
          header: "労働リソースID",
        },
        {
          accessorKey: "facilityCode",
          header: "設備コード",
        },
      ],
    },
    "admin-settings-google-users": {
      columns: [
        {
          accessorKey: "mailAddress",
          header: "Googleアカウント",
        },
        {
          accessorKey: "createdAt",
          header: "登録日時",
        },
        {
          accessorKey: "action",
          header: "",
        },
      ],
    },
    "admin-config-templates-email": {
      columns: [
        {
          accessorKey: "name",
          header: "名称",
        },
        {
          accessorKey: "description",
          header: "説明",
        },
        {
          accessorKey: "templateType",
          header: "タイプ",
        },
        {
          accessorKey: "createdAt",
          header: "登録時刻",
        },
        {
          accessorKey: "action",
          header: "",
        },
      ],
    },
    "admin-config-templates-html": {
      columns: [
        {
          accessorKey: "name",
          header: "名称",
        },
        {
          accessorKey: "description",
          header: "説明",
        },
        {
          accessorKey: "templateType",
          header: "タイプ",
        },
        {
          accessorKey: "createdAt",
          header: "登録時刻",
        },
        {
          accessorKey: "action",
          header: "",
        },
      ],
    },
    "admin-diagnosis-answer-summary": {
      columns: [
        {
          accessorKey: "created_at",
          header: "回答時刻",
        },
        {
          accessorKey: "diagnosis_name",
          header: "診断名",
        },
        {
          accessorKey: "answer_user_email",
          header: "メールアドレス",
        },
        {
          accessorKey: "answer_user_id",
          header: "回答者ID",
        },
        {
          accessorKey: "answer_user_group_name",
          header: "回答グループ名",
        },
        {
          accessorKey: "answer_history_count",
          header: "累計回答回数",
        },
        {
          accessorKey: "result_page_url",
          header: "回答ページURL",
        },
      ],
    },
    "admin-survey-answer-summary": {
      columns: [
        {
          accessorKey: "created_at",
          header: "回答時刻",
        },
        {
          accessorKey: "survey_name",
          header: "サーベイ名",
        },
        {
          accessorKey: "answer_user_email",
          header: "メールアドレス",
        },
        {
          accessorKey: "answer_user_id",
          header: "回答者ID",
        },
        {
          accessorKey: "answer_user_group_name",
          header: "回答グループ名",
        },
      ],
    },
    "admin-post-http-send-logs": {
      columns: [
        {
          accessorKey: "id",
          header: "ID",
        },
        {
          accessorKey: "requestUrl",
          header: "リクエスト先URL",
        },
        {
          accessorKey: "status",
          header: "実行結果",
        },
        {
          accessorKey: "statusCode",
          header: "ステータスコード",
        },
        {
          accessorKey: "responseBody",
          header: "レスポンスBody",
        },
        {
          accessorKey: "createdAt",
          header: "送信時刻",
        },
      ],
    },
    "admin-post-email-send-logs": {
      columns: [
        {
          accessorKey: "id",
          header: "ID",
        },
        {
          accessorKey: "senderEmail",
          header: "送信元",
        },
        {
          accessorKey: "mailTitle",
          header: "件名",
        },
        {
          accessorKey: "type",
          header: "モード",
        },
        // {
        //   accessorKey: "status",
        //   header: "ステータス",
        // },
        {
          accessorKey: "createdAt",
          header: "送信時刻",
        },
      ],
    },
    "admin-post-slack-message-send-logs": {
      columns: [
        {
          accessorKey: "id",
          header: "ID",
        },
        {
          accessorKey: "content",
          header: "送信コンテンツ",
        },
        {
          accessorKey: "channelName",
          header: "送信先チャンネル名",
        },
        // {
        //   accessorKey: "status",
        //   header: "ステータス",
        // },
        {
          accessorKey: "createdAt",
          header: "送信時刻",
        },
      ],
    },
    "admin-settings-sender-emails": {
      columns: [
        {
          accessorKey: "mailAddress",
          header: "送信元メールアドレス",
        },
        {
          accessorKey: "type",
          header: "タイプ",
        },
        {
          accessorKey: "createdAt",
          header: "登録日時",
        },
        {
          accessorKey: "action",
          header: "",
        },
      ],
    },
    "admin-logic-questionnaire-previews": [
      {
        accessorKey: "pageId",
        header: "ページID",
      },
      {
        accessorKey: "pageTitle",
        header: "ページタイトル",
      },
      {
        accessorKey: "questionId",
        header: "質問ID",
      },
      {
        accessorKey: "question",
        header: "質問文",
      },
      {
        accessorKey: "caption",
        header: "注釈",
      },
      {
        accessorKey: "choices",
        header: "選択肢",
      },
    ],
    "admin-logic-diagnosis-group-previews": [
      {
        accessorKey: "imageUrl",
        header: "画像",
      },
      {
        accessorKey: "id",
        header: "ID",
      },
      {
        accessorKey: "name",
        header: "名称",
      },
      {
        accessorKey: "description",
        header: "説明",
      },
    ],
    "admin-logic-chart-score-previews": [
      {
        accessorKey: "id",
        header: "ID",
      },
      {
        accessorKey: "name",
        header: "名称",
      },
      {
        accessorKey: "description",
        header: "説明",
      },
    ],
    "admin-logic-total-score-chart-selector": [
      {
        accessorKey: "chartId",
        header: "ID",
      },
      {
        accessorKey: "name",
        header: "スコア項目名",
      },
      {
        accessorKey: "scoreWeightSlider",
        header: "最大得点",
      },
    ],
    "admin-logic-diagnosis-group-recommend-item-mapping": [
      {
        accessorKey: "id",
        header: "ID",
      },
      {
        accessorKey: "image",
        header: "画像",
      },
      {
        accessorKey: "name",
        header: "アイテム名",
      },
      {
        accessorKey: "linkUrl",
        header: "遷移先",
      },
    ],
    "admin-logic-diagnosis-group-total-score-mapping": [
      {
        accessorKey: "id",
        header: "ID",
      },
      {
        accessorKey: "name",
        header: "診断グループ名",
      },
      {
        accessorKey: "imageUrl",
        header: "",
      },
      {
        accessorKey: "name",
        header: "診断グループ名",
      },
      {
        accessorKey: "activeTotalScoreRange",
        header: "総合スコア範囲",
      },
    ],
    "admin-logic-chart-score-groups": [
      {
        accessorKey: "imageUrl",
        header: "グループ画像",
      },
      {
        accessorKey: "description",
        header: "表示テキスト",
      },
      {
        accessorKey: "activeScoreRange",
        header: "マッチする得点範囲 (%)",
      },
    ],

    "admin-logic-idcore-previews": [
      {
        accessorKey: "id",
        header: "ID",
      },
      {
        accessorKey: "score",
        header: "最大得点",
      },
      {
        accessorKey: "name",
        header: "名称",
      },
      {
        accessorKey: "description",
        header: "説明",
      },
    ],
    "admin-logic-recommend-item-previews": [
      {
        accessorKey: "imageUrl",
        header: "画像",
      },
      {
        accessorKey: "id",
        header: "ID",
      },
      {
        accessorKey: "name",
        header: "名称",
      },
      {
        accessorKey: "description",
        header: "説明",
      },
      {
        accessorKey: "linkUrl",
        header: "リンクURL",
      },
    ],
    "admin-logic-group-answer-simulator-result": [
      {
        accessorKey: "imageUrl",
        header: "",
      },
      {
        accessorKey: "name",
        header: "グループ名",
      },
      {
        accessorKey: "totalScore",
        header: "総得点",
      },
      {
        accessorKey: "isSelected",
        header: "判定結果",
      },
    ],
    "admin-logic-chart-answer-simulator-result": [
      {
        accessorKey: "name",
        header: "チャートスコア",
      },
      {
        accessorKey: "maxTotalScore",
        header: "最大選択肢得点",
      },
      {
        accessorKey: "totalScore",
        header: "獲得得点",
      },
      {
        accessorKey: "scoreAcquisitionRate",
        header: "得点率",
      },
      {
        accessorKey: "totalScoreWeightRate",
        header: "総合スコア重み付け",
      },
      {
        accessorKey: "calculatedTotalScore",
        header: "計算済み総合得点",
      },
    ],
    "admin-logic-chart-groups-answer-simulator-result": [
      {
        accessorKey: "imageUrl",
        header: "",
      },
      {
        accessorKey: "chartId",
        header: "紐づくチャート項目",
      },
      {
        accessorKey: "description",
        header: "表示テキスト",
      },
      {
        accessorKey: "min",
        header: "得点率(%) 下限",
      },
      {
        accessorKey: "max",
        header: "得点率(%) 上限",
      },
    ],
    "admin-answer-user-group-users-preview": {
      columns: [
        {
          accessorKey: "userId",
          header: "回答者ID",
          sortable: false,
        },
        {
          accessorKey: "email",
          header: "メールアドレス",
          sortable: false,
        },
        {
          accessorKey: "freeText",
          header: "自由テキスト",
          sortable: false,
        },
      ],
    },
    "admin-answer-user-group-users": {
      columns: [
        {
          accessorKey: "uniqueUserId",
          header: "管理用ID",
          sortable: true,
        },
        {
          accessorKey: "userId",
          header: "回答者ID",
          sortable: true,
        },
        {
          accessorKey: "email",
          header: "メールアドレス",
          sortable: true,
        },
        {
          accessorKey: "freeText",
          header: "自由テキスト",
          sortable: false,
        },
        {
          accessorKey: "customTag",
          header: "属性",
          sortable: false,
        },
        {
          accessorKey: "mailSendStatus",
          header: "メール送信ステータス",
          sortable: false,
        },
        {
          accessorKey: "answerStatus",
          header: "回答ステータス",
          sortable: false,
        },
        {
          accessorKey: "answerUrl",
          header: "回答URL",
          sortable: false,
        },
      ],
    },
    "admin-logic-recommend-item-answer-simulator-result-for-score-add": [
      {
        accessorKey: "imageUrl",
        header: "画像",
      },
      {
        accessorKey: "name",
        header: "アイテム名",
      },
      {
        accessorKey: "totalScore",
        header: "総得点",
      },
      {
        accessorKey: "linkUrl",
        header: "遷移先",
      },
    ],
    "admin-logic-recommend-item-answer-simulator-result-for-diagnosis-group": [
      {
        accessorKey: "imageUrl",
        header: "画像",
      },
      {
        accessorKey: "name",
        header: "アイテム名",
      },
      {
        accessorKey: "linkUrl",
        header: "遷移先",
      },
    ],
    "admin-logic-answer-simulator-input": [
      {
        accessorKey: "choice",
        header: "選択肢",
      },
      {
        accessorKey: "groupMappedScores",
        header: "診断グループ配点",
      },
      {
        accessorKey: "chartMappedScore",
        header: "チャートスコア配点",
      },
      {
        accessorKey: "recommendItemMappedScore",
        header: "おすすめアイテム配点",
      },
    ],
    "admin-settings": {
      columns: [
        {
          accessorKey: "id",
          header: "id",
          sortable: true,
        },
        {
          accessorKey: "email",
          header: "Eメールアドレス",
          sortable: true,
        },

        {
          accessorKey: "role",
          header: "タイプ",
          sortable: true,
        },
        {
          accessorKey: "createdAt",
          header: "作成日",
          sortable: true,
        },
        {
          accessorKey: "actions",
        },
      ],
    },
    "diagnosis-create-modal-diagnosis-flow-modal": {
      columns: [
        {
          accessorKey: "id",
          header: "ID",
          sortable: false,
        },
        {
          accessorKey: "type",
          header: "タイプ",
          sortable: false,
        },

        {
          accessorKey: "title",
          header: "設問文",
          sortable: false,
        },
        {
          accessorKey: "choices",
          header: "選択肢",
          sortable: false,
        },
      ],
    },
    "admin-email-send-reservations-reserved": {
      columns: [
        {
          accessorKey: "id",
          header: "ID",
          sortable: false,
        },
        {
          accessorKey: "createdAt",
          header: "予約作成時刻",
          sortable: false,
        },
        {
          accessorKey: "reservedAt",
          header: "送信予定時刻",
          sortable: false,
        },
        {
          accessorKey: "mailTitle",
          header: "メール件名",
          sortable: false,
        },
        {
          accessorKey: "senderName",
          header: "送信者名",
          sortable: false,
        },
        {
          accessorKey: "senderEmail",
          header: "送信元メールアドレス",
          sortable: false,
        },
        {
          accessorKey: "mailAddressListCount",
          header: "送信予定数",
        },
      ],
    },
    "admin-email-send-reservations-finished": {
      columns: [
        {
          accessorKey: "id",
          header: "ID",
          sortable: false,
        },
        {
          accessorKey: "createdAt",
          header: "予約作成時刻",
          sortable: false,
        },
        {
          accessorKey: "reservedAt",
          header: "送信予定時刻",
          sortable: false,
        },
        {
          accessorKey: "mailTitle",
          header: "メール件名",
          sortable: false,
        },
        {
          accessorKey: "senderName",
          header: "送信者名",
          sortable: false,
        },
        {
          accessorKey: "senderEmail",
          header: "送信元メールアドレス",
          sortable: false,
        },
        {
          accessorKey: "mailAddressListCount",
          header: "送信予定数",
        },
        {
          accessorKey: "mailSendSuccessCount",
          header: "送信成功数",
        },
        {
          accessorKey: "mailSendNotFinishedCount",
          header: "送信未完了数",
        },
      ],
    },
    "admin-email-send-log-per-user": {
      columns: [
        {
          accessorKey: "userId",
          header: "ユーザーID",
          sortable: false,
        },
        {
          accessorKey: "mailAddress",
          header: "メールアドレス",
          sortable: false,
        },
        {
          accessorKey: "statusCode",
          header: "ステータスコード",
          sortable: false,
        },
        {
          accessorKey: "sendAt",
          header: "送信完了時刻",
          sortable: false,
        },
      ],
    },
    "admin-master-set-worker": {
      columns: [
        {
          accessorKey: "imageUrl",
          header: "画像URL",
          sortable: true,
        },
        {
          accessorKey: "code",
          header: "コード",
          sortable: true,
        },
        {
          accessorKey: "name",
          header: "名称",
          sortable: true,
        },
        {
          accessorKey: "description",
          header: "説明",
          sortable: true,
        },

        {
          accessorKey: "costPerHour",
          header: "1Hあたりの人件費総額",
          sortable: true,
        },
      ],
    },
    "admin-master-set-facility": {
      columns: [
        {
          accessorKey: "imageUrl",
          header: "画像URL",
          sortable: true,
        },
        {
          accessorKey: "id",
          header: "ID",
          sortable: true,
        },
        {
          accessorKey: "name",
          header: "名称",
          sortable: true,
        },
        {
          accessorKey: "description",
          header: "説明",
          sortable: true,
        },

        {
          accessorKey: "costPerHour",
          header: "1Hあたりの設備稼働費総額",
          sortable: true,
        },
      ],
    },
  };

  return ref(tableSchema);
};
