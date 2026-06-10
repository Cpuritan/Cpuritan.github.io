---
title: "Codex CLI 双账号无缝切换方案（Windows）"
date: 2026-06-10 17:45:00 +0800
---

> 在 ChatGPT Business 与 API Key 之间自由切换，兼顾 CLI 与 Antigravity 插件

## 背景

我在 Windows 上使用 OpenAI Codex CLI（`@openai/codex`），拥有两个账号：

- **ChatGPT Business**（Team 订阅）：通过 OAuth 浏览器登录
- **API Key**：通过 `sk-...` 密钥认证

目标是在 Antigravity 终端的 Codex 插件中，实现两个账号的自由切换，且互不干扰。

## 问题一：安装后 `.codex` 目录缺失

### 现象

```powershell
npm install -g @openai/codex   # 安装成功
codex --version                # 报 Warning
```

```
WARNING: CODEX_HOME points to "C:\\Users\\鲍鱼展翅\\.codex",
but that path does not exist
codex-cli 0.139.0
```

### 原因

`npm install -g` 不会自动创建 `~\.codex` 配置目录。

### 解决

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.codex" -Force
```

## 问题二：API Key 登录后无法切回 ChatGPT

### 现象

用 `codex login --with-api-key` 登录 API Key 后，再次执行 `codex login` 直接跳过浏览器 OAuth 流程，无法切换到 ChatGPT Business 账号。

### 根因分析

Codex CLI 的认证状态机由 `~\.codex\auth.json` 控制：

```json
// ChatGPT 模式
{
  "auth_mode": "chatgpt",
  "OPENAI_API_KEY": null,
  "tokens": {
    "access_token": "...",    // 短期 ~1h
    "refresh_token": "...",   // 长期，用于自动续期
    "account_id": "..."
  },
  "last_refresh": "2026-06-10T08:19:55Z"
}

// API Key 模式（--with-api-key 写入）
{
  "auth_mode": "apikey",
  "OPENAI_API_KEY": "sk-..."
}
```

**核心问题：** 当 `auth.json` 处于 `apikey` 模式时，Codex CLI 检测到已有有效凭据（API Key），`codex login` 不再触发浏览器 OAuth。而 `codex logout` 可能向 OpenAI 服务器发送 revoke 请求，导致 refresh_token 在服务端被吊销——即使之后恢复备份的 `auth.json` 也无效。

### 关键发现：Refresh Token Rotation

ChatGPT 的 OAuth token 体系使用了 **Refresh Token Rotation**：每次用 refresh_token 换取新的 access_token 时，旧的 refresh_token 被服务端吊销，同时下发一个新的。这意味着：

- **同一个 ChatGPT 账号的多份 auth.json 副本不可并行使用**：用副本 A 后副本 B 里的 refresh_token 立刻失效
- **ChatGPT ↔ API Key 互不干扰**：两个独立认证体系，OAuth 和 API Key 完全隔离

## 方案探索

### 方案 A：环境变量注入（❌ 仅 CLI 有效）

```powershell
# 原理：Codex 优先级 → $env:OPENAI_API_KEY > auth.json
$env:OPENAI_API_KEY = "sk-..."   # 切到 API Key
Remove-Item Env:\OPENAI_API_KEY  # 切回 ChatGPT
```

**失败原因：**

```
Antigravity 主进程（插件运行处）
├─ 启动时继承 Windows 系统环境变量     ← 终端里的 $env 改不到这里
└─ 内嵌终端
    └─ $env:OPENAI_API_KEY = "sk-..."  ← 只影响此终端子进程
```

环境变量设置在终端窗口内，无法传递到 Antigravity 主进程中的 Codex 插件。

### 方案 B：仅替换 auth.json（⚠️ 部分可行但有风险）

- OAuth token 会轮转，多份 auth.json 副本会互相淘汰
- sessions/cache/SQLite 数据库可能交叉污染

### 方案 C：完整 `.codex` 目录隔离（✅ 最终方案）

将整个 `.codex` 目录做两份完整备份，切换时直接交换目录名。

## 最终实现

### 目录结构

```
C:\Users\<用户名>\
├── .codex\              ← Antigravity 插件当前读取这个目录
├── .codex_chatgpt\      ← ChatGPT Business 完整环境（OAuth tokens + sessions + cache）
└── .codex_api\          ← API Key 环境（auth.json + 最小配置）
```

### Step 1：备份当前 ChatGPT 环境

```powershell
Copy-Item "$env:USERPROFILE\.codex" "$env:USERPROFILE\.codex_chatgpt" -Recurse -Force
```

### Step 2：隔离生成 API Key 环境

用临时 `CODEX_HOME` 隔离路径，避免触碰当前 ChatGPT 配置：

```powershell
$tempHome = "$env:USERPROFILE\.codex_api_temp"
Remove-Item $tempHome -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory $tempHome -Force | Out-Null

$apiKey = Read-Host "请粘贴你的 OpenAI API Key"
$env:CODEX_HOME = $tempHome
$apiKey | codex login --with-api-key 2>&1
Remove-Item Env:\CODEX_HOME -ErrorAction SilentlyContinue

# 移动到最终位置
$finalDir = "$env:USERPROFILE\.codex_api"
if (Test-Path $finalDir) { Remove-Item $finalDir -Recurse -Force }
Move-Item $tempHome $finalDir
```

### Step 3：PowerShell Profile 切换脚本

写入 `C:\Users\<用户名>\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`：

```powershell
# ============================================================
# Codex 账号切换助手 — 目录隔离版
# ============================================================
# .codex          ← Antigravity 插件当前读取
# .codex_chatgpt  ← ChatGPT Business 备份
# .codex_api      ← API Key 备份
# ============================================================

$_codex_chatgpt = "$env:USERPROFILE\.codex_chatgpt"
$_codex_api      = "$env:USERPROFILE\.codex_api"
$_codex_active   = "$env:USERPROFILE\.codex"

function Show-CodexStatus {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor White
    if (-not (Test-Path "$_codex_active\auth.json")) {
        Write-Host "  Codex 状态: 未配置" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor White
        return
    }
    $auth = Get-Content "$_codex_active\auth.json" -Raw | ConvertFrom-Json
    switch ($auth.auth_mode) {
        "chatgpt" {
            Write-Host "  当前: ChatGPT Business (OAuth)" -ForegroundColor Green
            if ($auth.tokens -and $auth.tokens.account_id) {
                Write-Host "  ID: $($auth.tokens.account_id)" -ForegroundColor Gray
            }
        }
        "apikey" {
            Write-Host "  当前: API Key" -ForegroundColor Cyan
            if ($auth.OPENAI_API_KEY) {
                $tail = $auth.OPENAI_API_KEY.Substring($auth.OPENAI_API_KEY.Length - 6)
                Write-Host "  Key: sk...$tail" -ForegroundColor Gray
            }
        }
        default {
            Write-Host "  当前: $($auth.auth_mode)" -ForegroundColor Yellow
        }
    }
    Write-Host "========================================" -ForegroundColor White
    Write-Host ""
    Write-Host "  备选: ChatGPT → $(if (Test-Path $_codex_chatgpt) {'已备份'+(Get-Item $_codex_chatgpt).LastWriteTime.ToString(' HH:mm:ss')} else {'缺失'})" -ForegroundColor Gray
    Write-Host "  备选: API Key  → $(if (Test-Path $_codex_api) {'已备份'+(Get-Item $_codex_api).LastWriteTime.ToString(' HH:mm:ss')} else {'缺失'})" -ForegroundColor Gray
}

function Switch-CodexChatGPT {
    if (-not (Test-Path "$_codex_chatgpt\auth.json")) {
        Write-Host "[Codex] 错误: .codex_chatgpt 备份不存在，无法切换" -ForegroundColor Red
        return
    }
    if (Test-Path "$_codex_active\auth.json") {
        $current = (Get-Content "$_codex_active\auth.json" -Raw | ConvertFrom-Json).auth_mode
        if ($current -eq "chatgpt") {
            Write-Host "[Codex] 当前已是 ChatGPT Business 模式" -ForegroundColor Yellow
            return
        }
    }
    Write-Host "══ 关闭 Antigravity 后按 Enter 继续 ══" -ForegroundColor Red
    Read-Host

    if (Test-Path $_codex_api) { Remove-Item $_codex_api -Recurse -Force }
    Rename-Item $_codex_active $_codex_api
    Rename-Item $_codex_chatgpt $_codex_active
    Write-Host "[Codex] 已切换至 ChatGPT Business，请重启 Antigravity" -ForegroundColor Green
}

function Switch-CodexAPI {
    if (-not (Test-Path "$_codex_api\auth.json")) {
        Write-Host "[Codex] 错误: .codex_api 备份不存在，无法切换" -ForegroundColor Red
        return
    }
    if (Test-Path "$_codex_active\auth.json") {
        $current = (Get-Content "$_codex_active\auth.json" -Raw | ConvertFrom-Json).auth_mode
        if ($current -eq "apikey") {
            Write-Host "[Codex] 当前已是 API Key 模式" -ForegroundColor Yellow
            return
        }
    }
    Write-Host "══ 关闭 Antigravity 后按 Enter 继续 ══" -ForegroundColor Red
    Read-Host

    if (Test-Path $_codex_chatgpt) { Remove-Item $_codex_chatgpt -Recurse -Force }
    Rename-Item $_codex_active $_codex_chatgpt
    Rename-Item $_codex_api $_codex_active
    Write-Host "[Codex] 已切换至 API Key，请重启 Antigravity" -ForegroundColor Cyan
}

Show-CodexStatus
Write-Host ""
Write-Host "[Codex] Switch-CodexChatGPT | Switch-CodexAPI | Show-CodexStatus" -ForegroundColor DarkGray
```

### 附加修复：PowerShell 执行策略

Windows PowerShell 5.1 默认禁止运行 `.ps1` 脚本，需解除：

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 附加修复：UTF-8 BOM 编码

Windows PowerShell 5.1 要求 `.ps1` 文件带 BOM 才能正确识别中文字符。**必须用 PowerShell 的 `Out-File -Encoding utf8` 写入**，不能直接文本编辑器保存为 UTF-8 without BOM。

## 使用方式

新开终端，自动显示当前状态：

```
[Codex] Switch-CodexChatGPT | Switch-CodexAPI | Show-CodexStatus
```

```powershell
Switch-CodexAPI        # 切换到 API Key（提示关闭 Antigravity → 按 Enter → 重启）
Switch-CodexChatGPT    # 切换到 ChatGPT Business
Show-CodexStatus       # 查看当前模式
```

## 切换流程

```
ChatGPT → API:
  .codex ──备份为──▶ .codex_chatgpt
  .codex_api ──激活为──▶ .codex

API → ChatGPT:
  .codex ──备份为──▶ .codex_api
  .codex_chatgpt ──激活为──▶ .codex
```

每次切换自动把当前状态（含完整会话历史）保存到对应备份目录。

## 设计原则

| 原则 | 实现方式 |
|------|----------|
| 永不 `codex logout` | 全程只做文件系统 rename，不触发服务端 revoke |
| 进程隔离 | 关闭 Antigravity 再切换，文件锁提供天然保护 |
| 完整隔离 | 整个 `.codex` 目录（sessions/cache/SQLite/记忆）独立，不交叉污染 |
| ChatGPT ↔ API Key 物理隔离 | 两种认证体系文件完全独立，无竞争条件 |

## 踩过的坑

1. **Read-Host 在 NonInteractive 模式下无效**——用 `PowerShell` 工具执行脚本时无法交互，需让用户在自己终端中完成关键登录步骤
2. **`Write` 工具写出的文件是 UTF-8 without BOM**——Windows PowerShell 5.1 以 ANSI/GBK 回退解析，中文变乱码触发 `ParserError`。修复：用 PowerShell 自身的 `Out-File -Encoding utf8` 重写
3. **环境变量方案对 CLI 有效、对 IDE 插件无效**——IDE 主进程不继承终端子进程的环境变量。这一判断也适用于 VSCode Codex 扩展

```

---

*环境：Windows 10 · PowerShell 5.1 · Codex CLI 0.139.0 · Antigravity*
