# GitHub Pages + 阿里云域名上线清单

本文档用于把当前目录的网站发布到：

- https://cpuritan.cn
- https://www.cpuritan.cn

## 1. 在 GitHub 创建仓库

1. 登录 GitHub，进入你的账号 `Cpuritan`。
2. 新建公开仓库：`Cpuritan.github.io`。
3. 不要勾选初始化 README（因为本地已有提交）。

## 2. 推送本地代码

在当前目录执行：

```bash
git remote set-url origin https://github.com/Cpuritan/Cpuritan.github.io.git
git push -u origin main
```

## 3. 启用 GitHub Pages

1. 进入仓库 `Settings -> Pages`。
2. `Build and deployment` 选择：
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/ (root)`
3. `Custom domain` 填写：`cpuritan.cn`
4. 等待证书就绪后，勾选 `Enforce HTTPS`。

## 4. 阿里云 DNS 配置

在阿里云域名解析中添加/确认以下记录（TTL 默认或 600）：

- `A` 记录：主机记录 `@`，记录值 `185.199.108.153`
- `A` 记录：主机记录 `@`，记录值 `185.199.109.153`
- `A` 记录：主机记录 `@`，记录值 `185.199.110.153`
- `A` 记录：主机记录 `@`，记录值 `185.199.111.153`
- `CNAME` 记录：主机记录 `www`，记录值 `Cpuritan.github.io`

删除冲突记录：

- 同名 `@` 的旧 `A/CNAME`
- 同名 `www` 的旧 `A/CNAME`

## 5. 验收检查

DNS 生效后验证：

```bash
nslookup cpuritan.cn
nslookup www.cpuritan.cn
```

期望：

- `cpuritan.cn` 解析到 GitHub Pages 的 4 个 A 记录之一
- `www.cpuritan.cn` 显示 CNAME 指向 `Cpuritan.github.io`

网站验证：

- `https://cpuritan.cn` 可打开主页
- `https://www.cpuritan.cn` 可访问并与主域名一致
- 示例文章可在首页文章列表看到

## 6. 后续发布文章

在 `_posts/` 下新增：

`YYYY-MM-DD-title.md`

含 Front Matter（至少）：

```yaml
---
layout: post
title: "文章标题"
date: 2026-04-03 20:00:00 +0800
---
```

然后执行：

```bash
git add .
git commit -m "Publish new post"
git push
```
