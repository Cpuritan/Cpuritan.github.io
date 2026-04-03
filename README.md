# Cpuritan Personal Site

This repository is a Jekyll-based personal homepage and blog for `cpuritan.cn`.

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
