## 修复 schedule.astro 的左右布局放大 + 日历重影 bug

### 改动 A — 放开外层 920px 封顶，让大屏真正左右铺开
文件：`src/pages/schedule.astro`

- **Line 199–203** `.page-shell:has(.sched-page)`：把 `max-width: 920px` 改为 `max-width: 1280px`，让大屏下页面真能放宽。同步把陈旧注释（"Override base .page-shell 920px cap so the schedule page can use the full viewport width"）改为与新代码一致的说明。

### 改动 B — 优化 `.sched-grid` 的右侧栏宽度
- **Line 226**：`grid-template-columns: minmax(0, 1fr) minmax(280px, 340px)` → `minmax(0, 1fr) minmax(320px, 360px)`，让大屏两栏视觉差异更明显，右侧 agenda/musings 列在大屏更舒展。

### 改动 C — 调整断点（保持/微调）
- **Line 484–492** `@media (max-width: 768px)`：阈值保留 768px。由于改动 A 让外层不再卡 920px，现在 768px 切换为单列（上下分布）意味着**真的整窗宽 ≤768px**，语义更符合"窗口缩到一定程度才上下分布"。无需新增断点。

### 改动 D — 修复日历重影 bug（核心）
文件：`src/pages/schedule.astro`，**Line 1497–1506** 的 `scheduleBandLayout()`：

把 resize 时的 `renderPeriodBands(cellDates)` 调用改为 **`renderCalendar()`**。理由：
- `.cal-bands-layer`（absolute, inset:0, z-index:2）与 `.cal-cell` 内联的 `.chip-spacer` 预留位必须在同一帧重算，否则跨 768px 断点时两层错位、表现为"压着半个日历"。
- 仅需多一次 innerHTML 重赋值（~42 个 cell），且 resize 已有 RAF 节流，开销可忽略。

伪代码示意：
```ts
function scheduleBandLayout() {
  if (_resizeRaf !== null) return;
  _resizeRaf = requestAnimationFrame(() => {
    _resizeRaf = null;
    const cells = Array.from(calBody.querySelectorAll<HTMLElement>(".cal-cell"));
    if (!cells.length) return;
    renderCalendar();   // ← 改这里：从 renderPeriodBands 改为 renderCalendar
  });
}
```

### 不动的东西
- `global.css` 的 `.page-shell max-width:920px` 通用规则（其他页面依赖）
- period band 的 absolute 坐标算法本体
- `chip` / `day-num` 的配色与样式
- 不引入任何新组件

## 验证步骤
拖动窗口边界反复跨过 768px 断点：
1. 全屏（>1280）→ 左右铺开、放大跟着宽
2. 中屏（~900–1100）→ 仍左右两栏
3. ≤768px → 自动上下
4. 跨断点过程中不再出现日历下"压着半个日历"的双层重影
