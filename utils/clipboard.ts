export default async function copyToClipboard(params: { text: string }) {
  await navigator.clipboard.writeText(params.text);
}
