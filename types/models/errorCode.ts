import { z } from "zod";

export const errorCodeItemZodObject = z.object({
  message: z.string(),
});

export const errorCodeKeys = z.union([
  z.literal("E101"),
  z.literal("E102"),
  z.literal("E103"),
  z.literal("E103"),
  z.literal("E200"),
  z.literal("E201"),
  z.literal("E202"),
  z.literal("E203"),
  z.literal("E204"),
  z.literal("E301"),
  z.literal("E302"),
  z.literal("E303"),
  z.literal("E304"),
  z.literal("E305"),
  z.literal("E306"),
  z.literal("E400"),
  z.literal("E401"),
  z.literal("E402"),
  z.literal("E403"),
  z.literal("E404"),
  z.literal("E500"),
  z.literal("E501"),
  z.literal("E600"),
  z.literal("E601"),
  // GCS関連のエラー
  z.literal("E700"),
  z.literal("E701"),
  // 回答ユーザーグループ関連のエラー
  z.literal("E800"),
  z.literal("E801"),
  z.literal("E802"),
  z.literal("E803"),
  z.literal("E804"),
  z.literal("E805"),
  // 診断回答関連のエラー
  z.literal("E900"),
  // 属性紐付けテーブル関連のエラー
  z.literal("E1000"),
  // メール送信関連のエラー
  z.literal("E1100"),
  z.literal("E1110"),
  z.literal("E1120"),
  // サーベイ取得のエラー
  z.literal("E1200"),
  z.literal("E1210"),
  z.literal("E1220"),
  z.literal("E1230"),
  // サーベイ回答時のエラー
  z.literal("E1300"),
  z.literal("E1310"),
  z.literal("E1320"),
  z.literal("E1330"),
  // 診断一覧取得時のエラー
  z.literal("E1400"),
  z.literal("E1401"),
  // Google連携関連のエラー
  z.literal("E1500"),
  z.literal("E1501"),
  // 送信元メールアドレス関連のエラー
  z.literal("E1600"),
  // 診断公開関連のエラー
  z.literal("E1700"),
  z.literal("E1701"),
  z.literal("E1702"),
  // Slack連携関連のエラー
  z.literal("E1800"),
  z.literal("E1801"),
  z.literal("E1802"),
  z.literal("E1803"),
  // 診断フロー編集関連のエラー
  z.literal("E1900"),
  z.literal("E1910"),
  // サーベイ公開関連のエラー
  z.literal("E2000"),
  // 診断ロジック表示・生成関連のエラー
  z.literal("E2100"),
  z.literal("E2110"),
  z.literal("E2120"),
  z.literal("E2230"),
  z.literal("E2240"),
  z.literal("E2310"),
  z.literal("E2320"),
  z.literal("E2330"),
  z.literal("E2340"),
  z.literal("E2350"),
  z.literal("E2360"),
  z.literal("E2370"),
  z.literal("E2380"),
  z.literal("E2390"),
  z.literal("E2391"),
  z.literal("E2392"),
  z.literal("E2393"),
  // サーベイ生成・表示関連のエラー
  z.literal("E2200"),
  z.literal("E2201"),
  z.literal("E2202"),
  z.literal("E2203"),
  z.literal("E2204"),
  // 診断ロジック保存履歴関連のエラー
  z.literal("E2400"),
  z.literal("E2410"),
  z.literal("E2420"),
  z.literal("E2430"),
  z.literal("E2440"),
  z.literal("E2450"),
  z.literal("E2460"),
  z.literal("E2470"),
  z.literal("E2480"),
  // 診断生成関連のエラー
  z.literal("E2500"),
  z.literal("E2510"),
  // 診断結果画面関連のエラー
  z.literal("E2600"),
  z.literal("E2700"),
  z.literal("E2800"),
  // 回答フロー関連のエラー
  z.literal("E2900"),
  z.literal("E2910"),
  // 回答ユーザーグループ関連のエラー
  z.literal("E3000"),
  z.literal("E3001"),
]);

export const errorCodeListZodObject = z
  .record(errorCodeItemZodObject)
  .refine(
    (record) =>
      Object.keys(record).every((key) => errorCodeKeys.safeParse(key).success),
    {
      message: "Invalid error code key",
      path: ["errorCodeListZodObject"],
    }
  );
