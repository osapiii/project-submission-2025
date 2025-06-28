export function createCustomGroupObject(params: {
  n: number;
  groupName: string;
}): Record<string, null> {
  const result: Record<string, null> = {};
  for (let i = 1; i <= params.n; i++) {
    result[`${params.groupName}${i}`] = null;
  }
  return result;
}

export function filterKeysByKeyword<T extends object>(params: {
  object: T;
  keyword: string;
}): (keyof T)[] {
  return Object.keys(params.object).filter((key) =>
    key.includes(params.keyword)
  ) as (keyof T)[];
}

export function pickProperties<T extends Record<string, unknown>>(params: {
  object: T;
  groupKeys: (keyof T)[];
}) {
  const groupObj: Partial<T> = {};
  params.groupKeys.forEach((key) => {
    groupObj[key] = params.object[key];
  });
  return groupObj;
}

export function cloneObject(params: { object: object }) {
  return JSON.parse(JSON.stringify(params.object));
}

/**
 * オブジェクトの配列でKeyを指定してソートする
 */
export function sortArrayByObjectKey(params: {
  array: object[];
  sortKey1: string;
  sortKey2: string;
  order: "asc" | "desc";
}) {
  return params.array.sort((a, b) => {
    // 各々Keyに型をつける (サバイバルTypeScript: https://typescriptbook.jp/reference/type-reuse/keyof-type-operator)
    const typedSortKey1 = params.sortKey1 as keyof typeof a;
    const typedSortKey2 = params.sortKey2 as keyof typeof b;
    // 先に key1 で比較
    if (a[typedSortKey1] < b[typedSortKey1])
      return params.order === "asc" ? -1 : 1;
    if (a[typedSortKey1] > b[typedSortKey1])
      return params.order === "asc" ? 1 : -1;

    // key1 が同じ場合は key2 で比較
    if (a[typedSortKey2] < b[typedSortKey2])
      return params.order === "asc" ? -1 : 1;
    if (a[typedSortKey2] > b[typedSortKey2])
      return params.order === "asc" ? 1 : -1;

    // key1 と key2 が両方とも同じ場合は同じとみなす
    return 0;
  });
}

// eslint-disable-next-line
export function restructureData(data: any, key: any) {
  // eslint-disable-next-line
  return data.reduce((acc: any, cur: any) => {
    if (!acc[cur[key]]) {
      acc[cur[key]] = [];
    }
    // eslint-disable-next-line
    const obj = {} as any;
    for (const prop in cur) {
      if (prop !== key) {
        obj[prop] = cur[prop];
      }
    }
    acc[cur[key]].push(obj);
    return acc;
  }, {});
}
