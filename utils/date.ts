import dayjs from "dayjs";
import log from "@utils/logger";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

// dayjsにUTCとタイムゾーンのプラグインを拡張
dayjs.extend(utc);
dayjs.extend(timezone);

// デフォルトのタイムゾーンを日本時間に設定
dayjs.tz.setDefault("Asia/Tokyo");

/**
 * 日付とIndexを受け取って、date + indexの日付を返す
 * @param {string} date - 日付
 * @param {number} index - インデックス
 * @returns {string} フォーマットされた日付 (YYYY-MM-DD)
 */
export function getDateWithIndexAdd(inputDate: string, index: number): string {
  log("INFO", "getDateWithIndexAdd is called!🔥");
  const date = dayjs(inputDate).add(index, "day").format("YYYY-MM-DD");
  log("INFO", "getDateWithIndexAdd result is...", date);
  return date;
}

/**
 * 今日の日付を取得します。
 * @returns {string} フォーマットされた日付 (YYYY-MM-DD)
 */
export function getToday(): string {
  return dayjs().format("YYYY-MM-DD");
}

/**
 * 現在の日本標準時を取得します。
 * @returns {string} フォーマットされた現在の日本標準時 (YYYY-MM-DD HH:mm:ss)
 */
export function getCurrentJstTime(): string {
  // 現在の日本時刻を取得
  const now = dayjs().tz("Asia/Tokyo");
  return now.format("YYYY-MM-DD HH:mm:ss");
}

/**
 * タイムスタンプを日本標準時にフォーマットします。
 * @param {dayjs.ConfigType} timestamp - フォーマットするタイムスタンプ
 * @returns {string} フォーマットされた日付 (YYYY-MM-DD HH:mm:ss)
 */
export function formatTimestamp(timestamp: dayjs.ConfigType): string {
  const date = dayjs(timestamp).tz("Asia/Tokyo");
  return date.format("YYYY-MM-DD HH:mm:ss");
}

/**
 * 日付文字列をYYYY-MM-DD形式にフォーマットします。
 * @param {string} dateString - フォーマットする日付文字列
 * @returns {string} フォーマットされた日付 (YYYY-MM-DD)
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const year = date.getFullYear();
  // 月と日を2桁にパディング
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
};

/**
 * UNIXタイムスタンプをYYYY-MM-DD形式にフォーマットします。
 * @param {string} timestamp - フォーマットするUNIXタイムスタンプ
 * @returns {string} フォーマットされた日付 (YYYY-MM-DD)
 */
export const formatUnixTimestamp = (timestamp: string): string => {
  const date = dayjs.unix(Number(timestamp)).tz("Asia/Tokyo");
  return date.format("YYYY-MM-DD");
};

export default { getCurrentJstTime, formatTimestamp, formatDate, getToday };
