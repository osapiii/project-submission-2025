export default function buildUrl(params: {
  base: string;
  path: string;
  params: Record<string, string>;
}) {
  const url = new URL(params.path, params.base);
  url.search = new URLSearchParams(params.params).toString();
  return url.toString();
}

export function openRecommendItemUrlWithAnotherTab(url: string) {
  window.open(url, "_blank");
}

export function returnCurrentHostUrl() {
  let hostUrl = "";
  if (window.location.host.includes("localhost")) {
    hostUrl = "https://localhost:3000";
  } else if (window.location.host.includes("sandbox")) {
    hostUrl = "https://enostech-sandbox.firebaseapp.com";
  } else if (window.location.host.includes("qravis")) {
    hostUrl = "https://qravis.com";
  }

  return hostUrl;
}
