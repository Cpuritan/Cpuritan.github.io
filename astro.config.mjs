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
  },
  server: {
    // Proxy /api/* to the local schedule-editing server (see server/README.md)
    // so the dev server can read/write the live schedule.json.
    proxy: {
      "/api": {
        target: "http://localhost:3010",
        changeOrigin: true
      }
    }
  }
});
