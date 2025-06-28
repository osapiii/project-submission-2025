// stores/counter.spec.ts
import { setActivePinia, createPinia } from "pinia";
import { beforeAll, describe, expect, test } from "vitest";
import setup from "../vitest.setup";
import { diagnosisConverter } from "@models/Diagnosis";
import { organizationConverter } from "@models/Organization";

describe("firestoreDocOperationのユニットテスト", () => {
  beforeAll(() => {
    setActivePinia(createPinia());
    setup();
  });

  test("getDocumentListByQuery 条件付きクエリで正しく複数のドキュメントを取得できること", async () => {
    const firestoreOps = useFirestoreDocOperation();
    const diagnosisDocs = await firestoreOps.getDocumentListByQuery({
      collectionName: "organizations/YuiNd6IW8QSv9fOKYqZq/diagnosiss",
      targetField: "status",
      operator: "==",
      targetValue: "published",
      converter: diagnosisConverter,
    });
    expect(diagnosisDocs.length).toEqual(1);
  });
  test("getAllDocumentListFromCollectionWithoutConverter 全取得クエリで正しく複数のドキュメントを取得できること(形無し)", async () => {
    const firestoreOps = useFirestoreDocOperation();
    const diagnosisDocs =
      await firestoreOps.getAllDocumentListFromCollectionWithoutConverter({
        collectionName:
          "organizations/YuiNd6IW8QSv9fOKYqZq/diagnosiss/xbTNUj6ggwBudy4ULCaU/draft",
      });
    expect(diagnosisDocs.length).toEqual(6);
  });
  test("getAllDocumentListFromCollectionWithConverter 全取得クエリで正しく複数のドキュメントを取得できること(型付き)", async () => {
    const firestoreOps = useFirestoreDocOperation();
    const diagnosisDocs =
      await firestoreOps.getAllDocumentListFromCollectionWithConverter({
        collectionName: "organizations/YuiNd6IW8QSv9fOKYqZq/diagnosiss",
        converter: diagnosisConverter,
      });
    expect(diagnosisDocs.length).toEqual(4);
  });
  test("getSingleDocumentById ID指定で単一のドキュメントを取得する", async () => {
    const firestoreOps = useFirestoreDocOperation();
    const organizationDoc = await firestoreOps.getSingleDocumentById({
      collectionName: "organizations",
      docId: "YuiNd6IW8QSv9fOKYqZq",
      converter: organizationConverter,
    });
    expect(organizationDoc).toBeTruthy();
  });
  test("getSingleDocumentByQuery クエリで単一のドキュメントを取得する", async () => {
    const firestoreOps = useFirestoreDocOperation();
    const organizationDoc = await firestoreOps.getSingleDocumentByQuery({
      collectionName: "organizations",
      converter: organizationConverter,
      targetField: "code",
      operator: "==",
      targetValue: "ENOSTECH",
    });
    expect(organizationDoc).toBeTruthy();
  });
  test("createDocument 単一のドキュメントを新規に生成する", async () => {
    const firestoreOps = useFirestoreDocOperation();
    const organizationDoc = await firestoreOps.createDocument({
      collectionName: "organizations",
      docId: "TEST",
      docData: {
        code: "TEST",
        name: "株式会社TEST",
      },
      converter: organizationConverter,
    });
    expect(organizationDoc).toBeTruthy();
  });
  test("updateDocument 単一のドキュメントの内容を更新→存在する場合は更新結果を返却", async () => {
    const firestoreOps = useFirestoreDocOperation();
    const organizationDoc = await firestoreOps.updateDocument({
      collectionName: "organizations",
      docId: "TEST",
      docData: {
        name: "株式会社TEST更新",
      },
      converter: organizationConverter,
    });
    if (organizationDoc) {
      expect(organizationDoc.name == "株式会社TEST更新").toBeTruthy();
    }
  });

  test("updateDocument 単一のドキュメントの内容を更新する→存在しない場合はnullを返却", async () => {
    const firestoreOps = useFirestoreDocOperation();
    try {
      await firestoreOps.updateDocument({
        collectionName: "organizations",
        docId: "DUMMY",
        docData: {
          name: "株式会社TEST更新",
        },
        converter: organizationConverter,
      });
    } catch (error) {
      expect(error).toBeInstanceOf(Error);
    }
  });

  test("deleteDocument 単一のドキュメントを削除する", async () => {
    const firestoreOps = useFirestoreDocOperation();
    const response = await firestoreOps.deleteDocument({
      collectionName: "organizations",
      docId: "TEST",
    });
    expect(response).toBe(true);
  });
});
