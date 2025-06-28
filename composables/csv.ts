// import log from "@utils/logger"; // 未使用のため削除
import JSZip from "jszip";
import { saveAs } from "file-saver";
import Papa from "papaparse";
import { getCurrentJstTime } from "@utils/date";

export const useCSV = () => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function parseCSVfile(file: File): Promise<any[]> {
    return new Promise((resolve, reject) => {
      Papa.parse(file, {
        header: true,

        complete: (results) => {
          resolve(results?.data);
        },
        error: () => {
          reject(new Error("csv parse err"));
        },
      });
    });
  }

  const downloadCSVWithHeaders = (params: {
    data: object[];
    headers: string[];
    filename: string;
  }) => {
    const toast = useToast();
    // ヘッダーの取得
    const headers = params.headers.join(",");

    const escapeCSVValue = (value: any): string => {
      if (Array.isArray(value)) {
        return `"${value.map((item) => escapeCSVValue(item)).join(",")}"`;
      } else if (typeof value === "string") {
        // ダブルクォートをエスケープし、カンマを含む場合は全体をダブルクォートで囲む
        const escapedValue = value.replace(/"/g, '""');
        return escapedValue.includes(",") || escapedValue.includes('"')
          ? `"${escapedValue}"`
          : escapedValue; // ダブルクォートがある場合も囲む
      } else if (value === null || value === undefined) {
        return "";
      } else {
        return String(value);
      }
    };

    const rows = params.data.map((row) => {
      return Object.values(row)
        .map((value) => escapeCSVValue(value))
        .join(",");
    });

    // UTF-8 BOMの追加
    const csvString = "\uFEFF" + headers + "\n" + rows.join("\n");

    // Blobの登録
    const blob = new Blob([csvString], { type: "text/csv;charset=utf-8;" });

    // ダウンロードリンクの登録
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = params.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.add({
      title: "CSVファイルをダウンロードしました",
      description: params.filename,
    });
  };

  const downloadCSV = (params: { data: object[]; filename: string }) => {
    // ログ出力 (必要に応じて実装してください)
    const log = (level: string, message: string, ...args: any[]) => {
      console.log(`[${level}] ${message}`, ...args);
    };

    log("INFO", "downloadCSV triggered🔥", "params is....", params);

    // ヘッダーの取得
    const headers = Object.keys(params.data[0]).join(",");

    const escapeCSVValue = (value: any): string => {
      if (Array.isArray(value)) {
        return `"${value.map((item) => escapeCSVValue(item)).join(",")}"`;
      } else if (typeof value === "string") {
        // ダブルクォートをエスケープし、カンマを含む場合は全体をダブルクォートで囲む
        const escapedValue = value.replace(/"/g, '""');
        return escapedValue.includes(",") || escapedValue.includes('"')
          ? `"${escapedValue}"`
          : escapedValue; // ダブルクォートがある場合も囲む
      } else if (value === null || value === undefined) {
        return "";
      } else {
        return String(value);
      }
    };

    const rows = params.data.map((row) => {
      return Object.values(row)
        .map((value) => escapeCSVValue(value))
        .join(",");
    });

    // UTF-8 BOMの追加
    const csvString = "\uFEFF" + headers + "\n" + rows.join("\n");

    // Blobの登録
    const blob = new Blob([csvString], { type: "text/csv;charset=utf-8;" });

    // ダウンロードリンクの登録
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = params.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadCSVsAsZip = async (params: {
    dataArray: object[][];
    fileNameArray: string[];
    filename: string;
  }) => {
    const zip = new JSZip();
    params.dataArray.forEach((data, index) => {
      const headers = Object.keys(data[0]).join(",");
      const rows = data.map((row) => {
        return Object.values(row)
          .map((value) => {
            if (typeof value === "string" && value.includes(",")) {
              return `"${value}"`;
            }
            return value;
          })
          .join(",");
      });
      const csvString = "\uFEFF" + headers + "\n" + rows.join("\n");
      zip.file(
        `${getCurrentJstTime()}_${params.fileNameArray[index]}.csv`,
        csvString
      );
    });

    const blob = await zip.generateAsync({ type: "blob" });
    saveAs(blob, params.filename);
  };

  return {
    parseCSVfile,
    downloadCSV,
    downloadCSVsAsZip,
    downloadCSVWithHeaders,
  };
};
