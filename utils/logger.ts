/**
 * アプリケーション全体で使用するロガーユーティリティ
 * consolaライブラリを使用してログレベル別に出力
 */
import { consola } from "consola";

/**
 * ログレベル定義
 */
export enum LogLevel {
  ERROR = "error",
  WARN = "warn",
  INFO = "info",
  DEBUG = "debug",
}

/**
 * ログ出力関数
 * @param level ログレベル
 * @param messages ログメッセージ（可変長引数）
 */
export default function log(
  level: "ERROR" | "WARN" | "INFO" | "DEBUG",
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ...messages: any[]
) {
  // if (import.meta.env.MODE !== "development") {
  //   return;
  // }

  switch (level) {
    case "ERROR":
      consola.error("", ...messages);
      break;
    case "WARN":
      consola.warn("", ...messages);
      break;
    case "INFO":
      consola.info("", ...messages);
      break;
    case "DEBUG":
      consola.debug("", ...messages);
      break;
    default:
      consola.log("", ...messages);
      break;
  }
}
