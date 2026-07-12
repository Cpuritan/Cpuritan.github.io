# 修复方案：chip 缩放 + 周期任务分割

## 问题 1：方格内 chip 色块在缩小时文字被遮挡

### 根因
`.cal-cell` 高度从 124px（桌面）降为 96px（≤768px）再到 84px（≤560px），但 chip 字号 `0.71rem` 和 line-height `1.45` 保持不变。4 个 chip + day-num + 间距在 124px 下勉强容纳（~122px），但在 84px 下溢出 ~38px，`overflow: hidden` 直接裁掉底部。

### 修改方案
**A. CSS：在媒体查询中按比例缩小 chip 和相关尺寸**

`@media (max-width: 768px)` 增加：
```css
.cal-cell { height: 96px; padding: 0.3rem 0.25rem 0.2rem; gap: 0.12rem; }
.day-num { width: 1.3rem; height: 1.3rem; font-size: 0.72rem; margin-bottom: 0.04rem; }
.chip { font-size: 0.62rem; line-height: 1.3; padding: 0.02rem 0.25rem; border-left-width: 2px; }
```

`@media (max-width: 560px)` 增加：
```css
.cal-cell { height: 84px; padding: 0.2rem 0.2rem 0.12rem; gap: 0.1rem; }
.day-num { width: 1.1rem; height: 1.1rem; font-size: 0.65rem; margin-bottom: 0.02rem; }
.chip { font-size: 0.54rem; line-height: 1.2; padding: 0.01rem 0.2rem; border-left-width: 1.5px; }
```

同时 `.chip-spacer` 目前是 JS 内联 `height:${bandSlotCount * 22}px`，修改为 `(bandSlotCount * 1.3) + "rem"`，用 rem 单位随根字号缩放。

**B. 调整 period-band JS 的垂直偏移**

`renderPeriodBands` 中 `topOffset = 36 + Math.min(localSlot, 3) * 22` 是写死的像素值。改为基于 rem 的动态值：
```js
const bandRowH = 1.3 * rem;    // ~20.8px desktop, 随 rem 缩放
const baseOff = 2.25 * rem;    // ~36px desktop
topOffset = baseOff + Math.min(localSlot, 3) * bandRowH;
```

## 问题 2：＋N 格式改为 ~N~

### 修改
`schedule.astro` 第 819 行 `+${remaining}` → `~${remaining}~`

## 问题 3：周期任务标记 done 后色带分割

### 当前行为
`renderPeriodBands` 只在**换行（周）**时分割段，每个段的 done 状态仅查起始日期。用户标记中间日期（如 7/3）时，整条色带不会分裂，且段起始日期可能没 mark done，整段不变。

### 目标行为
周期 "A" 从 7/1 到 7/7，用户于 7/3 点在日程栏点 done 两下（done-2），视觉结果：
- 7/1–7/2：色带正常（done-0）
- 7/3：单独一段，带 done-2 样式（横线划除+变淡）
- 7/4–7/7：色带正常（done-0）

### 实现
修改 `renderPeriodBands` 中构建 segments 的循环。当前按 `r`（行号）分割，增加 done 状态检查：

```js
// 改动前：只按行号分割
while (dateCmp(cur, segEnd) <= 0) {
  const idx = cellDates.indexOf(cur);
  if (idx < 0) break;
  const r = Math.floor(idx / 7);
  if (seg && r === seg.rowIdx) seg.endDate = cur;
  else { seg = { rowIdx: r, startDate: cur, endDate: cur }; segs.push(seg); }
  ...
}

// 改动后：按行号 + done 状态共同分割
while (dateCmp(cur, segEnd) <= 0) {
  const idx = cellDates.indexOf(cur);
  if (idx < 0) break;
  const r = Math.floor(idx / 7);
  const dLvl = getDone(p, cur);
  if (seg && r === seg.rowIdx && dLvl === seg.doneLevel) seg.endDate = cur;
  else { seg = { rowIdx: r, startDate: cur, endDate: cur, doneLevel: dLvl }; segs.push(seg); }
  ...
}
```

然后在渲染每个 seg 时，用 `seg.doneLevel` 替代 `getDone(p, segStartDate)` 来设置 done-1/done-2 类。

这利用了 localStorage 已有的 `"id_YYYY-MM-DD"` 逐日 done 标记——无需改动数据层。

## 涉及修改的文件
只改 **`src/pages/schedule.astro`**，不新增/删除其他文件。

## 改动汇总
| 改动点 | 位置 | 改动量 |
|--------|------|--------|
| 媒体查询加 chip/day-num/period-band 缩放 CSS | `@media` 块内 | ~10 行新增 |
| `.chip-spacer` 内联 height 用 rem | JS `renderCalendar` | 1 行 |
| `topOffset` 计算用 rem | JS `renderPeriodBands` | 3 行 |
| `+N` → `~N~` | JS `renderCalendar` | 1 字符 |
| 段分割增加 done 状态检查 | JS `renderPeriodBands` 循环 | ~4 行 |
| 段渲染用 seg.doneLevel | JS `renderPeriodBands` 循环 | ~2 行 |
