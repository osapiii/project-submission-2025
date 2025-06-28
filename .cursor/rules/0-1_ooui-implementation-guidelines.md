---
title: OOUI実装ガイドライン
description: オブジェクト指向UIの実装ガイドラインと具体例
---

# オブジェクト指向UI (OOUI) 実装ガイドライン

## 1. 概要

オブジェクト指向UI (OOUI) は、ユーザーが操作対象とするオブジェクト（データや機能）を中心に据えた設計手法です。この文書では、Nuxt3とNuxtUIを使用したOOUI実装のためのガイドラインと具体例を提供します。

## 2. 基本原則

### オブジェクト指向UIの4つの基本原則

1. **オブジェクト中心設計**: ユーザーが操作したいオブジェクトを明確に特定し、UIの中心に据える
2. **直接操作**: オブジェクトに対する操作は、できるだけ直接的に行えるようにする
3. **視覚的フィードバック**: オブジェクトの状態変化は視覚的に明確に表現する
4. **一貫性**: 同じタイプのオブジェクトに対する操作は一貫した方法で提供する

## 3. 実装ガイドライン

### 3.1 コンポーネント設計

- オブジェクトごとにコンポーネントを作成し、そのオブジェクトに関連する操作をすべて含める
- コンポーネント内部でオブジェクトの状態を適切に管理する
- オブジェクト間の関係性は、コンポーネント間の階層構造で表現する

例:
```vue
<!-- ProductCard.vue - 商品オブジェクトを表現するコンポーネント -->
<template>
  <div class="product-card">
    <img :src="product.image" :alt="product.name" />
    <h3>{{ product.name }}</h3>
    <p>{{ product.price }}円</p>
    <!-- 商品に対する操作（アクション）をカード内に直接配置 -->
    <div class="actions">
      <UButton @click="addToCart">カートに追加</UButton>
      <UButton variant="outline" @click="viewDetails">詳細を見る</UButton>
    </div>
  </div>
</template>
```

### 3.2 状態管理

- オブジェクトの状態はPiniaストアで管理し、コンポーネント間で共有する
- オブジェクトに対する操作（アクション）はストア内のメソッドとして実装する
- オブジェクトの関係性はストア間の参照で表現する

例:
```ts
// stores/productStore.ts
export const useProductStore = defineStore('products', () => {
  // オブジェクトのコレクション
  const products = ref<Product[]>([])
  
  // オブジェクトに対する操作
  function fetchProducts() { /* ... */ }
  function addProduct(product: Product) { /* ... */ }
  function updateProduct(id: string, data: Partial<Product>) { /* ... */ }
  function deleteProduct(id: string) { /* ... */ }
  
  return { 
    products, 
    fetchProducts,
    addProduct,
    updateProduct,
    deleteProduct
  }
})
```

### 3.3 ナビゲーション設計

- オブジェクト階層に基づいたナビゲーション構造を設計する
- 関連するオブジェクト間の移動を自然にする
- ブレッドクラムなどでオブジェクト階層を視覚化する

例:
```vue
<template>
  <div>
    <!-- オブジェクト階層を示すブレッドクラム -->
    <UBreadcrumb :items="breadcrumbItems" />
    
    <!-- メインコンテンツ -->
    <NuxtPage />
  </div>
</template>

<script setup>
const route = useRoute()
const breadcrumbItems = computed(() => {
  const items = [{ label: '製品カテゴリ', to: '/categories' }]
  
  if (route.params.categoryId) {
    items.push({ 
      label: getCategoryName(route.params.categoryId), 
      to: `/categories/${route.params.categoryId}` 
    })
  }
  
  if (route.params.productId) {
    items.push({ 
      label: getProductName(route.params.productId),
      to: `/categories/${route.params.categoryId}/products/${route.params.productId}` 
    })
  }
  
  return items
})
</script>
```

### 3.4 視覚的表現

- オブジェクトの視覚的表現は、その性質と重要性を反映させる
- 関連するオブジェクトは視覚的にグループ化する
- オブジェクトの状態変化は適切なアニメーションで表現する

例:
```vue
<template>
  <div class="inventory-item" :class="{ 'low-stock': isLowStock }">
    <div class="item-header">
      <h3>{{ item.name }}</h3>
      <UBadge :color="stockStatusColor">{{ stockStatus }}</UBadge>
    </div>
    <div class="item-details">
      <p>在庫数: {{ item.quantity }}</p>
      <p>最終更新: {{ formatDate(item.updatedAt) }}</p>
    </div>
    <div class="item-actions">
      <UButton @click="increaseStock">入荷</UButton>
      <UButton @click="decreaseStock">出荷</UButton>
      <UButton variant="outline" @click="viewHistory">履歴を見る</UButton>
    </div>
  </div>
</template>

<script setup>
const isLowStock = computed(() => item.value.quantity < item.value.threshold)
const stockStatus = computed(() => isLowStock.value ? '在庫不足' : '在庫あり')
const stockStatusColor = computed(() => isLowStock.value ? 'red' : 'green')
</script>
```

## 4. OOUIパターン集

### 4.1 オブジェクトリスト + 詳細パターン

最も基本的なOOUIパターンで、オブジェクトの一覧と詳細表示を組み合わせたもの。

```vue
<template>
  <div class="ooui-list-detail">
    <!-- オブジェクトリスト -->
    <div class="object-list">
      <div
        v-for="obj in objects"
        :key="obj.id"
        class="object-item"
        :class="{ 'active': selectedId === obj.id }"
        @click="selectObject(obj.id)"
      >
        {{ obj.name }}
      </div>
    </div>
    
    <!-- 選択したオブジェクトの詳細 -->
    <div class="object-detail" v-if="selectedObject">
      <h2>{{ selectedObject.name }}</h2>
      <div class="object-properties">
        <!-- オブジェクトのプロパティ表示 -->
      </div>
      <div class="object-actions">
        <!-- オブジェクトに対するアクション -->
        <UButton @click="editObject">編集</UButton>
        <UButton variant="danger" @click="deleteObject">削除</UButton>
      </div>
    </div>
  </div>
</template>
```

### 4.2 ドラッグ&ドロップパターン

オブジェクトの直接操作性を高めるためのパターン。オブジェクト間の関係設定や並べ替えに効果的。

```vue
<template>
  <div class="drag-drop-container">
    <div class="source-objects">
      <div
        v-for="obj in availableObjects"
        :key="obj.id"
        draggable="true"
        @dragstart="dragStart($event, obj)"
        class="draggable-object"
      >
        {{ obj.name }}
      </div>
    </div>
    
    <div 
      class="target-container"
      @dragover.prevent
      @drop="handleDrop"
    >
      <div
        v-for="obj in selectedObjects"
        :key="obj.id"
        class="selected-object"
      >
        {{ obj.name }}
        <button @click="removeObject(obj.id)">×</button>
      </div>
    </div>
  </div>
</template>
```

### 4.3 インラインアクションパターン

オブジェクトに対する操作をインラインで提供するパターン。

```vue
<template>
  <UTable :columns="columns" :rows="objects">
    <template #actions-data="{ row }">
      <div class="inline-actions">
        <UButton icon="i-heroicons-eye" @click="viewObject(row.id)" />
        <UButton icon="i-heroicons-pencil" @click="editObject(row.id)" />
        <UButton icon="i-heroicons-trash" @click="confirmDelete(row.id)" />
      </div>
    </template>
  </UTable>
</template>
```

## 5. OOUI設計チェックリスト

新規UI設計時や既存UI改善時に以下のチェックリストを活用してください：

- [ ] ユーザーが操作対象とする主要なオブジェクトを特定できているか
- [ ] オブジェクトの視覚的表現は、その特性と重要性を適切に反映しているか
- [ ] オブジェクトに対する操作は直接的にアクセス可能か
- [ ] 関連オブジェクト間の関係性が自然に表現されているか
- [ ] オブジェクトの状態変化に対する視覚的フィードバックは明確か
- [ ] 同種のオブジェクトに対する操作方法は一貫しているか
- [ ] オブジェクト階層に基づいたナビゲーション構造になっているか

## 6. 参考

- [OOUI(オブジェクト指向UI)とは？デザイナーなら知っておきたいメリットや設計方法まで解説！](https://blog.nijibox.jp/article/ooui/)
- [About Face: The Essentials of Interaction Design](https://www.wiley.com/en-us/About+Face%3A+The+Essentials+of+Interaction+Design%2C+4th+Edition-p-9781118766576) - Alan Cooper著 