import { defineStore } from "pinia";
import { getAuth, signInWithEmailAndPassword, type User } from "firebase/auth";
import { adminUserConverter, type decodedAdminUser } from "@models/adminUser";
import log from "@utils/logger";
import { adminUserCreateRequestConverter } from "@models/adminUserCreateRequest";

/**
 * サインインパラメータのインターフェース
 * @interface
 */
interface signInParams {
  email: string;
  password: string;
}

/**
 * 管理ユーザーストア
 */
export const useAdminUserStore = defineStore("adminUser", {
  state: () => ({
    currentUserClaimsInfo: {},
    adminUserList: [] as decodedAdminUser[],
  }),
  getters: {},
  actions: {
    /**
     * サインインの実行
     * @param {signInParams} params - サインインに必要なパラメータ
     */
    async signIn(params: signInParams) {
      const router = useRouter();
      const auth = getAuth();
      const context = useContextStore();
      try {
        await signInWithEmailAndPassword(auth, params.email, params.password);
        const user = auth.currentUser;
        if (user) {
          const idToken = await user.getIdToken();
          context.firebaseToken = idToken;
          if (context.productType == "ai-management") {
            router.push({ name: "admin-dashboard-top" });
          } else {
            router.push({ name: "admin-report-blueprint-list" });
          }
        }
      } catch (error) {
        return error;
      }
    },

    /**
     * サインアウトの実行
     */
    async signOut() {
      const router = useRouter();
      const auth = getAuth();
      await auth.signOut();
      router.push({ name: "admin-signin" });
    },

    /**
     * ユーザー認証ステータスの更新
     * @param {Object} params - パラメータオブジェクト
     * @param {User} params.currentUser - 現在のユーザー
     */
    async updateAuthState(params: { currentUser: User }) {
      log("INFO", "updateAuthState triggered🔥");
      const idTokenResult = await params.currentUser.getIdTokenResult();
      const customClaims = await idTokenResult.claims;
      this.currentUserClaimsInfo = {
        ...customClaims,
      };
    },

    /**
     * 管理ユーザー一覧の取得
     */
    async fetchAdminUserListWithCurrentLoggedInOrganization() {
      const firestoreOps = useFirestoreDocOperation();
      const organization = useOrganizationStore();
      const adminUsers = await firestoreOps.getDocumentListByQuery({
        collectionName: `organizations/${organization.getLoggedInOrganizationId}/adminUsers`,
        targetField: "organizationId",
        operator: "==",
        targetValue: organization.loggedInOrganizationInfo.id,
        converter: adminUserConverter,
      });
      this.adminUserList = adminUsers;
    },

    /**
     * 管理ユーザーの更新
     * @param {Object} params - パラメータオブジェクト
     * @param {string} params.adminUserId - 管理ユーザーID
     * @param {Partial<decodedAdminUser>} params.updateData - 更新データ
     */
    async updateAdminUser(params: {
      adminUserId: string;
      updateData: Partial<decodedAdminUser>;
    }) {
      params.updateData.role = String(params.updateData.role);
      const firestoreOps = useFirestoreDocOperation();
      firestoreOps.updateDocument({
        collectionName: "adminUsers",
        docId: params.adminUserId,
        docData: params.updateData,
        converter: adminUserConverter,
      });
    },

    /**
     * 管理ユーザーの削除
     * @param {Object} params - パラメータオブジェクト
     * @param {string} params.adminUserId - 管理ユーザーID
     */
    async deleteAdminUser(params: { adminUserId: string }) {
      const firestoreOps = useFirestoreDocOperation();
      firestoreOps.deleteDocument({
        collectionName: "adminUsers",
        docId: params.adminUserId,
      });
    },

    /**
     * ユーザー新規登録リクエストの実行
     * @param {Object} params - パラメータオブジェクト
     * @param {string} params.email - ユーザーのメールアドレス
     * @param {string} params.password - ユーザーのパスワード
     */
    async createNewAdminUser(params: { email: string; password: string }) {
      const firestoreOps = useFirestoreDocOperation();
      const organization = useOrganizationStore();
      firestoreOps.createDocument({
        collectionName: `organizations/${organization.getLoggedInOrganizationId}/requests/adminUserCreate/logs`,
        docId: createRandomDocId(),
        docData: {
          email: params.email,
          role: "2",
          organizationId: organization.loggedInOrganizationInfo.id,
          organizationCode: organization.loggedInOrganizationInfo.code,
          status: "pending",
        },
        converter: adminUserCreateRequestConverter,
      });
    },
  },
});
