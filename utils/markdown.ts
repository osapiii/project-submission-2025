import markdownit from "markdown-it";

const md = markdownit({ breaks: true });

export function convertMarkdownToHtml(markdownText: string): string {
  return md.render(markdownText);
}
