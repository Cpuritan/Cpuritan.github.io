# Cpuritan Personal Site

This repository is a Jekyll-based personal homepage and blog for `cpuritan.cn`.

For full Chinese deployment steps, see `DEPLOYMENT_CN.md`.

## Quick Publish Flow

1. Create a public GitHub repository named `Cpuritan.github.io`.
2. Push this project to the `main` branch of that repository.
3. In GitHub repository settings, enable Pages from `main` / root.
4. Keep `CNAME` as `cpuritan.cn`.
5. Configure DNS in Alibaba Cloud:
   - `A` `@` -> `185.199.108.153`
   - `A` `@` -> `185.199.109.153`
   - `A` `@` -> `185.199.110.153`
   - `A` `@` -> `185.199.111.153`
   - `CNAME` `www` -> `Cpuritan.github.io`

## Local Preview (optional)

If you want to preview locally:

1. Install Ruby and Bundler.
2. Install dependencies and run:

```bash
bundle install
bundle exec jekyll serve
```

Then open `http://127.0.0.1:4000`.

## Posting New Articles

Create files in `_posts/` using this format:

`YYYY-MM-DD-title.md`

Minimal front matter:

```yaml
---
layout: post
title: "Article Title"
date: 2026-04-03 20:00:00 +0800
---
```

## LaTeX Auto-Publish Pipeline

This repo supports automatic publishing from `latex/*.tex` to:

- `_posts/latex/YYYY-MM-DD-slug.md` (web-readable blog post)
- `assets/papers/slug.pdf` (PDF backup)

### How to author a LaTeX source

Create a file at `latex/<slug>.tex` and include commented front matter at the top:

```tex
% ---
% title: "Post title"
% date: "2026-04-03 20:30:00 +0800"
% categories: [latex]
% tags: [latex, math]
% ---
```

Required fields: `title`, `date`  
Optional fields: `categories`, `tags`

### GitHub Actions behavior

- Triggered on push to `main` when `latex/**`, `scripts/tex_pipeline.py`, or workflow file changes.
- Runs `scripts/tex_pipeline.py` with `pandoc` + `tectonic`.
- Commits generated outputs back to `main` with `[skip ci]`.

### Required repository setting

In GitHub repository settings:

- `Settings -> Actions -> General -> Workflow permissions`
- Enable `Read and write permissions` so the workflow can commit generated files.
