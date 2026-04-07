# Cpuritan Personal Site (Astro)

This repository now uses Astro for `cpuritan.cn` with a minimal white theme:

- top navigation: `Home / Blog`
- `Home` page: personal profile only
- `Blog` page: post list (card style)
- post URLs: `/blog/YYYY/MM/DD/slug/` (legacy-compatible)

## Stack

- Astro static site
- Comic Shanns (self-hosted in `public/fonts/`)
- MathJax for markdown math rendering
- GitHub Pages via GitHub Actions

## Local development

Requirements:

- Node.js `>=18.17.1` (recommended `20.x`)

Commands:

```bash
npm install
npm run dev
npm run build
```

## Content authoring

### Legacy `_posts` workflow (recommended for your current files)

You can write directly in:

`_posts/**/*.md`

This includes nested folders such as:

- `_posts/crew schedule/crew scheduling CTS2025.md`
- `_posts/crew schedule/attachments/*`

`scripts/blog_pipeline.py` will automatically:

- sync markdown files into `src/content/blog/*.md`
- auto-fill minimal front matter (`title`, `date`) if missing
- convert Obsidian image embeds like `![[attachments/x.png|600]]`
- copy local assets to `public/assets/posts/<slug>/...`

The `blog-sync` GitHub Action runs this on every push that changes `_posts/**`.

### Markdown blog posts

Write posts in:

`src/content/blog/<slug>.md`

Minimal front matter:

```yaml
---
title: "Article Title"
date: 2026-04-03 20:00:00 +0800
---
```

Optional:

- `tags: [optimization, pricing]`
- `categories: [blog, reading]`

### LaTeX auto-publish

Write LaTeX sources in:

`latex/<slug>.tex`

Front matter must be commented at top:

```tex
% ---
% title: "Post title"
% date: "2026-04-03 20:30:00 +0800"
% tags: [latex, math]
% categories: [latex]
% ---
```

Pipeline outputs:

- `src/content/blog/<slug>.md` (auto-generated)
- `public/assets/papers/<slug>.pdf`

## Workflows

- `.github/workflows/deploy-astro.yml`
  - builds Astro and deploys `dist/` to GitHub Pages.
- `.github/workflows/blog-publish.yml`
  - syncs `_posts/**` (and attachments) into Astro content, then validates and auto-commits generated files.
- `.github/workflows/latex-publish.yml`
  - converts LaTeX to Astro content + PDF and commits generated artifacts.

## Domain

`public/CNAME` is set to:

`cpuritan.cn`

This preserves custom domain behavior on GitHub Pages.
