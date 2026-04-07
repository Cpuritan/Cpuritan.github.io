import { defineConfig } from "astro/config";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";

export default defineConfig({
  site: "https://cpuritan.cn",
  output: "static",
  trailingSlash: "always",
  markdown: {
    remarkPlugins: [remarkGfm],
    rehypePlugins: [rehypeRaw],
    remarkRehype: {
      allowDangerousHtml: true
    }
  }
});
