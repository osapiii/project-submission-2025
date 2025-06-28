const getBase64FromUrl = (params: { url: string }) => {
  return fetch(params.url)
    .then((response) => response.blob())
    .then(
      (blob) =>
        new Promise((resolve) => {
          const reader = new FileReader();
          reader.readAsDataURL(blob);
          reader.onloadend = () => resolve(reader.result);
        })
    );
};

export { getBase64FromUrl };
