import { defineConfig } from "astro/config";
import rehypeMathjax from "rehype-mathjax";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

const BLOG_MARKDOWN_RE = /[\\/]src[\\/]content[\\/]blog[\\/].+\.md$/i;
const PLACEHOLDER_RE = /@@CPURITAN_BLOCK_(\d+)@@/g;

function normalizeSvgBlock(svgContent) {
  const fixed = svgContent.replace(/\?\/text>/gi, "</text>").trim();
  // Keep SVG as raw HTML, but collapse line breaks to avoid markdown->JS
  // serialization edge cases with very large multiline inline SVG blocks.
  const singleLine = fixed.replace(/\r?\n+/g, " ").replace(/\s{2,}/g, " ");
  return ` ${singleLine} `;
}

function normalizeMathArtifacts(markdownContent) {
  let fixed = markdownContent;

  fixed = fixed.replace(/\?\$\$/g, "$$");
  fixed = fixed.replace(/\$\$\?/g, "$$");
  fixed = fixed.replace(/\?\$/g, "$");
  fixed = fixed.replace(/\$\?/g, "$");

  fixed = fixed.replace(/\?\\\[/g, "\\[");
  fixed = fixed.replace(/\?\\\]/g, "\\]");
  fixed = fixed.replace(/\?\\\(/g, "\\(");
  fixed = fixed.replace(/\?\\\)/g, "\\)");
  fixed = fixed.replace(/\?\\([A-Za-z]+)/g, "\\$1");

  return fixed;
}

function normalizeBlogMarkdown(markdownSource) {
  const protectedBlocks = [];
  const protect = (content) => {
    const token = `@@CPURITAN_BLOCK_${protectedBlocks.length}@@`;
    protectedBlocks.push(content);
    return token;
  };

  let working = markdownSource;

  working = working.replace(/```[\s\S]*?```/g, (block) => protect(block));
  working = working.replace(/~~~[\s\S]*?~~~/g, (block) => protect(block));
  working = working.replace(/`[^`\r\n]+`/g, (block) => protect(block));
  working = working.replace(/<svg[\s\S]*?<\/svg>/gi, (block) =>
    protect(normalizeSvgBlock(block))
  );

  working = normalizeMathArtifacts(working);

  return working.replace(
    PLACEHOLDER_RE,
    (_, index) => protectedBlocks[Number(index)] ?? _
  );
}

function structuralMarkdownFixPlugin() {
  return {
    name: "cpuritan-structural-markdown-fix",
    enforce: "pre",
    transform(source, id) {
      const cleanId = id.split("?", 1)[0];
      if (!BLOG_MARKDOWN_RE.test(cleanId)) {
        return null;
      }

      // Vite also loads compiled virtual modules for markdown entries.
      // Those are JavaScript payloads and must not be rewritten.
      if (
        source.includes("export const frontmatter") ||
        source.includes("const html = ")
      ) {
        return null;
      }

      const fixed = normalizeBlogMarkdown(source);
      if (fixed === source) {
        return null;
      }
      return { code: fixed, map: null };
    }
  };
}

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
  vite: {
    plugins: [structuralMarkdownFixPlugin()]
  }
});
