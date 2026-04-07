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
  - validates `src/content/blog` front matter and slug uniqueness.
- `.github/workflows/latex-publish.yml`
  - converts LaTeX to Astro content + PDF and commits generated artifacts.

## Domain

`public/CNAME` is set to:

`cpuritan.cn`

This preserves custom domain behavior on GitHub Pages.
