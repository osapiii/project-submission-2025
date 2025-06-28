import log from "@utils/logger";
import {
  Timestamp,
  type FirestoreDataConverter,
  type QueryDocumentSnapshot,
} from "firebase/firestore";

import type { z } from "zod";

const getTokyoTimestamp = () => {
  const now = new Date();
  const tokyoOffset = 9 * 60; // Tokyo is UTC+9
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const tokyoTime = new Date(utc + tokyoOffset * 60000);
  return Timestamp.fromDate(tokyoTime);
};

export const firestoreTypeConverter = <T extends z.AnyZodObject>(
  schema: T
): FirestoreDataConverter<z.infer<T>> => ({
  toFirestore: (data: Partial<z.infer<T>>): z.infer<T> => {
    log("INFO", "conveter toFirestore🤖", "parsedDocData is....", data);
    let additionalData = {};

    if (!data.createdAt) {
      // 新規作成時はcreatedAtとupdatedAtに現在のタイムスタンプを設定
      additionalData = {
        createdAt: getTokyoTimestamp(),
        updatedAt: getTokyoTimestamp(),
      };
    } else {
      // 更新時はupdatedAtのみ現在のタイムスタンプを設定
      additionalData = {
        updatedAt: getTokyoTimestamp(),
      };
    }
    const mergedDoc = { ...data, ...additionalData };
    // 書き込み時はidを持たないのでスキーマから除外
    const withoutIdSchema = schema.omit({
      id: true,
    });
    const parsedDocData = withoutIdSchema.strict().parse(mergedDoc);
    return parsedDocData;
  },
  fromFirestore: (snapshot: QueryDocumentSnapshot<z.infer<T>>): z.infer<T> => {
    const parsedDocData = snapshot.data();
    log(
      "INFO",
      "conveter fromFirestore🤖",
      "parsedDocData is....",
      parsedDocData
    );
    const dataWithId = { ...parsedDocData, id: snapshot.id };
    const validatedDocData = schema.strict().parse(dataWithId);
    return validatedDocData;
  },
});
