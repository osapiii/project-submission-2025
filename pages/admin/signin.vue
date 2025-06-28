<template>
  <div class="flex h-screen">
    <!-- 左側: ログインフォーム -->
    <div class="flex flex-col justify-center items-center w-1/2 bg-white">
      <UCard class="w-[400px] pt-3 pb-8">
        <div class="flex-col gap-y-2 mb-4">
          <div class="mb-2">
            <UInput
              v-model="email"
              label="メールアドレス"
              placeholder="メールアドレス"
              type="email"
              size="xl"
              required
              class="mb-2 w-full"
            />
          </div>
          <div>
            <UInput
              v-model="password"
              size="xl"
              label="パスワード"
              placeholder="パスワード"
              type="password"
              class="w-full"
              required
            />
          </div>
          <div class="flex justify-center">
            <UButton
              type="submit"
              color="primary"
              label="ログイン"
              class="mt-4"
              :icon="iconSet.login"
              size="xl"
              @click="SignIn({ email, password })"
            />
          </div>
        </div>
      </UCard>
    </div>
    <!-- 右側: イラストとロゴ -->
    <div
      class="relative w-1/2 h-full flex items-center justify-center bg-blue-800"
    >
      <img
        src="https://storage.googleapis.com/knockai-public/logo.png"
        alt="login-visual"
      />
      <!-- ロゴの上に重ねる場合はabsoluteで調整可能 -->
    </div>
  </div>
</template>

<script setup lang="ts">
import log from "@utils/logger";
import iconSet from "@utils/icon";

//#region reactive-data
const email = ref("");
const password = ref("");
//#endregion reactive-data

//#region store
const userAuthStore = useAdminUserStore();
//#endregion store

// 表示させたいフォームのスキーマを登録（複数可）
async function SignIn(params: { email: string; password: string }) {
  log("INFO", "SignIn triggered!", params);
  await userAuthStore.signIn({
    email: params.email,
    password: params.password,
  });
}
</script>
