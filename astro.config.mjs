import { defineConfig } from "astro/config";
import rehypeMathjax from "rehype-mathjax";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

export default defineConfig({
  site: "https://cpuritan.cn",
  output: "static",
  trailingSlash: "always",
  markdown: {
    remarkPlugins: [remarkGfm, remarkMath],
    rehypePlugins: [rehypeRaw, rehypeMathjax],
    remarkRehype: {
      allowDangerousHtml: true
    }
  }
});
