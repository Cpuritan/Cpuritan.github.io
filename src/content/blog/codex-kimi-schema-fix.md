---
title: "Codex 更新后经 cc-switch 连 Kimi 报 400 的排查与修复"
date: 2026-08-31 17:30:00 +0800
---

> 一段真实的排查记录：Codex 更新后工具参数 schema 的写法变了，Kimi 网关的严格校验直接 400，最后用一个本地中转代理解决。

## 现象

莫名其妙 Codex 更新后，走 cc-switch 转发到 Kimi For Coding（k3-256k）的请求开始报：

```
CC Switch local proxy failed while handling Codex endpoint /responses.
Provider: Kimi For Coding; model: k3-256k;
upstream_status: HTTP 400;
cause: tools.function.parameters is not a valid moonshot flavored json schema,
details: <At path '$defs.__schema20': when using $ref, type should be defined
in the referenced schema instead of the parent schema>
```

但之前一切正常：翻 cc-switch 的请求日志，8 月初到中旬有上千次成功请求，8 月 31 日才第一次出现该报错（与 Codex 更新同日）

## 根因

三层叠加的结果：

1. **Codex 侧**：更新后动态工具（如 Plan 模式的 `request_user_input`）生成的参数 schema 变成 JSON Schema 2020-12 风格，`$defs` 里 `$ref` 与 `type`/`format` 等兄弟关键字并存：

   ```json
   { "$ref": "#/$defs/__schema7", "type": "string", "format": "uuid", "minLength": 1 }
   ```

   这在 2020-12 规范里合法（`$ref` 只是普通 applicator，官方明确允许兄弟关键字共存），OpenAI 自家 API 自然接受。

2. **Kimi 侧**：Kimi 网关对工具 schema 做编译期校验（社区称 walle / "Moonshot Flavored JSON Schema"），比 draft-07 更严格——draft-07 对 `$ref` 兄弟关键字只是"忽略"，Kimi 直接拒绝并返回 400。

3. **cc-switch 侧**：本地代理原样转发，不做规范化；官方修复 PR（#5125、#6627）截至 2026-08-31 均未合并，升级解决不了。

## 解决

在 cc-switch 与 Kimi 之间插一个本地中转代理，把工具参数里的 `$ref` 全部就地展开（兄弟关键字优先、带循环保护），顺便处理 `/v1` 路径重复，再转发给 Kimi：

```
Codex → cc-switch(:15721) → 本地代理(:8787) → api.kimi.com/coding/v1
```

三步启用：

1. 启动代理：`python kimi_schema_fix.py`（监听 127.0.0.1:8787）
2. cc-switch 中把 Kimi For Coding 的 `base_url` 改为 `http://127.0.0.1:8787`
3. 重启 cc-switch，正常使用

代理已实测：`$ref` 全部展开、`Authorization` 透传、SSE 流式逐段转发均正常。代码与完整文档见 [github.com/Cpuritan/kimi-schema-fix](https://github.com/Cpuritan/kimi-schema-fix)。

---

*环境：Windows 10 · Codex 桌面端 · cc-switch · Kimi For Coding (k3 / k3-256k)*
