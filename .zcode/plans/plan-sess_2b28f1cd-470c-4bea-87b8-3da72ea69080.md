## 实施计划：周期间任务连续色带 + 格高4任务 + 窄屏显示

### 修改范围
仅一个文件：`src/pages/schedule.astro`

### 一、周期任务连续色带（Outlook 风格）

**当前问题**：周期任务在每个日历格渲染为独立 `.chip.is-period`，虽然 rank 保证纵向对齐，但每个 cell 的 border-left、圆角、边距导致视觉断裂。

**方案**：在 `.cal-body` 的 CSS Grid 中添加**跨格叠加层色带元素**，每个周期任务渲染为一个 `grid-column: a / b; grid-row: r` 的连续 `<div>`，覆盖多个 cell。

**JS 修改**（`renderCalendar` 函数）：
1. 遍历 `schedule.__periods__`，计算每个周期与当前月视图的交集
2. 周期跨周时拆分为多个 segement（每行一个连续段），计算 `grid-column` 和 `grid-row`
3. 每个 segement 生成：`<div class="period-band" style="grid-column:C1/C2;grid-row:R;background:...">标题</div>`
4. 用 `insertAdjacentHTML('beforeend', ...)` 追加到所有 cell 之后
5. 周期事件**不再**渲染为 cell 内的 chip
6. `eventsFor()` 保持完整（agenda 面板仍需周期数据）
7. 同一 grid 行有多个色带时，按 rank 分配 `margin-top: 30px + n*22px` 纵向错开

**CSS 新增**：
```css
.period-band {
  align-self: start; margin-top: 30px;
  z-index: 2; pointer-events: auto;
  overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
  border-radius: 3px; padding: 0.03rem 0.4rem;
  font-size: 0.71rem; font-weight: 500; line-height: 1.45;
  color: var(--chip-c, ...);
  background: var(--chip-t, ...);
  border-left: 3px solid var(--chip-cb, ...);
}
```

**Global Rank 调整**：`computeGlobalRanks()` 中不再包含周期条目（因为不再渲染为 chip）。

### 二、日历格子高度扩大，容纳 4 个任务

当前 JS 中 `MAX_CHIPS = 4` 已正确，只是 CSS 高度不足。

**CSS 修改**：
- 桌面：`.cal-cell { height: 112px → 140px }`
- 移动端：`.cal-cell { height: 80px → 110px }`，并调整 `padding`

### 三、窄屏（上下布局）保留色块显示

**CSS 删除**以下整块规则：
```css
@media (max-width: 760px) {
  .chip { display: none; }
}
```
改为正常显示 chip（配合增大后的移动端 cell 高度）。

### 完成标准
1. 暑期学校（7/14-7/18）和项目冲刺周（7/22-7/25）以连续色带显示，而非每格独立色块
2. 每个格子最多显示 4 个任务 chip，超出显示 `+N`
3. 缩小页面到上下布局时，日历格中仍显示色块
4. Agenda 面板无影响
5. 编辑、done 标记、翻月等所有交互功能正常
