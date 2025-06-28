export const useTsHelper = () => {
  const findIndexById = (params: {
    // eslint-disable-next-line
    array: any[];
    keyName: string;
    targetValue: string | number;
  }) => {
    return params.array.findIndex(
      (item) => item[params.keyName] === params.targetValue
    );
  };

  return { findIndexById };
};
