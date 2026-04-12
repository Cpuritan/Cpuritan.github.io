# Cpuritan Personal Site (Astro)

This repository uses Astro for `cpuritan.cn` with a minimal white layout:

- top navigation: `Home / Research / Blog / Musings`
- `Home`: profile content
- `Blog`: post list and article pages
- `Musings`: short-form notes and essays
- `Research`: research overview
- post URLs: `/blog/YYYY/MM/DD/slug/` (legacy-compatible)

## Stack

- Astro static site
- Comic Shanns (self-hosted in `public/fonts/`)
- MathJax (`remark-math + rehype-mathjax`)
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

### Home and Research pages

- Home body: `src/content/site/home.md`
- Research body: `src/content/site/research.md`
- Page wrappers:
`src/pages/index.astro`, `src/pages/research/index.astro`

### Blog posts (single source of truth)

Write posts only in:

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

### Blog assets

For local images used by blog posts, keep assets under:

`public/assets/posts/<slug>/...`

### LaTeX auto-publish

Write LaTeX sources in:

`latex/<slug>.tex`

Pipeline outputs:

- `src/content/blog/<slug>.md`
- `public/assets/papers/<slug>.pdf`

## Content guard and CI

- `scripts/checks/content_guard.py` validates:
  - UTF-8 decode (strict)
  - malformed SVG blocks
  - legacy bad marker: `AUTO-GENERATED: scripts/blog_pipeline.py`
  - common encoding-corruption signals
  - scans `blog`, `musings`, and `site` content collections
- `.github/workflows/blog-publish.yml` runs guard on content changes.
- `.github/workflows/deploy-astro.yml` runs guard before `npm run build`.

## Windows encoding safety

Use UTF-8 explicitly when writing files from scripts/terminal.

PowerShell examples:

```powershell
# Read as UTF-8
Get-Content -LiteralPath .\src\content\blog\post.md -Raw -Encoding UTF8

# Write UTF-8 without BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Resolve-Path .\src\content\blog\post.md), $content, $utf8NoBom)
```

Avoid writing markdown with default encoding commands that do not specify UTF-8.

## Workflows

- `.github/workflows/deploy-astro.yml`
  - validates content, builds Astro, deploys `dist/` to GitHub Pages.
- `.github/workflows/blog-publish.yml`
  - validates markdown content and assets integrity.
- `.github/workflows/latex-publish.yml`
  - converts LaTeX to Astro content + PDF and commits generated artifacts.

## Domain

`public/CNAME` is set to:

`cpuritan.cn`
