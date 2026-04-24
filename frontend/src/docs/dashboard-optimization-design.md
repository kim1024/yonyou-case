# 统计面板与导航栏交互优化设计规范

> 用友产业案例教学课程系统管理后台 — 交互优化设计文档
>
> 版本 1.0 · 2026-04-24
>
> 设计师：UX Designer

---

## 目录

1. [设计任务 1：时间维度切换器](#设计任务-1时间维度切换器)
2. [设计任务 2：导航栏收缩/展开按钮优化](#设计任务-2导航栏收缩展开按钮优化)
3. [设计决策说明](#设计决策说明)

---

## 设计任务 1：时间维度切换器

### 1.1 设计决策

#### 放置位置：页面顶部统一控制

**决策**：在统计卡片区域上方、页面标题区域下方，放置一个全局时间维度切换器，统一控制所有 4 个图表的数据范围。

**理由**：
- 减少重复操作——管理员切换时间维度时，通常希望看到同一时间范围下的全部数据，而不是逐个图表切换
- 保持视觉一致性——4 个图表使用相同的时间维度，便于数据对比和综合分析
- 符合后台管理系统操作模式——"全局筛选 → 局部筛选"是常见层级

#### 交互方式：Segmented Control（分段控制器）

**决策**：使用 macOS 风格的 Segmented Control 样式，而非 Tab 或下拉选择。

**理由**：
- 选项数量为 3 个（今天 / 最近7天 / 最近30天），属于少量固定选项，Segmented Control 是最优解
- 视觉权重适中，不干扰主要数据展示
- 符合 macOS 设计语言——系统原生使用 Segmented Control 进行同类选项切换
- 相比 Tab，更紧凑；相比下拉选择，更直观（无需展开即可看到所有选项）

#### 默认选中值：最近7天

**理由**：管理员日常最常关注的趋势数据周期为一周，7 天数据既有趋势意义，又不会因数据量过大导致图表信息稀疏。

---

### 1.2 组件结构

#### 整体页面布局变化

```
┌──────────────────────────────────────────────────────┐
│                    页面标题区域                        │
│  统计面板 — 系统访问数据与业务洞察                      │
├──────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────┐  │
│  │  ┌─────────┐ ┌───────────┐ ┌────────────┐     │  │
│  │  │  今天   │ │ 最近7天 ● │ │ 最近30天   │     │  │
│  │  └─────────┘ └───────────┘ └────────────┘     │  │
│  └────────────────────────────────────────────────┘  │
│                    时间切换器区域                       │
├──────────────────────────────────────────────────────┤
│                    统计卡片区域（4 张）                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ 总访问量  │ │ 案例总数  │ │ 活跃用户  │ │ 完课率   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
├──────────────────────────────────────────────────────┤
│                    图表区域（2×2 网格）                 │
│  ┌───────────────────┐ ┌───────────────────┐         │
│  │   折线图（访问趋势） │ │  柱状图（省份分布）  │         │
│  └───────────────────┘ └───────────────────┘         │
│  ┌───────────────────┐ ┌───────────────────┐         │
│  │  水平条形图（案例）  │ │   饼图（行业分布）   │         │
│  └───────────────────┘ └───────────────────┘         │
└──────────────────────────────────────────────────────┘
```

#### HTML 结构描述

```html
<!-- 时间维度切换器 -->
<div class="flex items-center gap-3 mb-6">
  <!-- 切换器容器 -->
  <div
    class="inline-flex items-center p-1 rounded-lg bg-neutral-100 border border-neutral-200"
  >
    <!-- 选项：今天 -->
    <button
      class="segment-item"
      :class="{ 'segment-active': selectedRange === 'today' }"
      @click="selectedRange = 'today'"
    >
      今天
    </button>

    <!-- 选项：最近7天 -->
    <button
      class="segment-item"
      :class="{ 'segment-active': selectedRange === '7d' }"
      @click="selectedRange = '7d'"
    >
      最近7天
    </button>

    <!-- 选项：最近30天 -->
    <button
      class="segment-item"
      :class="{ 'segment-active': selectedRange === '30d' }"
      @click="selectedRange = '30d'"
    >
      最近30天
    </button>
  </div>

  <!-- 可选：当前时间范围提示文字 -->
  <span class="text-xs text-neutral-500">
    {{ dateRangeLabel }}
  </span>
</div>
```

---

### 1.3 样式规范

#### Segmented Control 容器

| 属性 | 值 |
|------|-----|
| `display` | `inline-flex` |
| `align-items` | `center` |
| `padding` | `4px`（`p-1`） |
| `background` | `var(--color-neutral-100)` → `#F5F3F0` |
| `border` | `1px solid var(--color-neutral-200)` → `#E7E5E4` |
| `border-radius` | `var(--radius-lg)` → `12px` |
| `box-shadow` | `inset 0 1px 2px rgba(28, 25, 23, 0.04)` |

#### Segmented Item — 默认状态

| 属性 | 值 |
|------|-----|
| `padding` | `6px 16px` |
| `font-size` | `13px` |
| `font-weight` | `500` |
| `color` | `var(--color-neutral-500)` → `#78716C` |
| `background` | `transparent` |
| `border-radius` | `var(--radius-md)` → `8px` |
| `cursor` | `pointer` |
| `transition` | `all 0.2s cubic-bezier(0.4, 0, 0.2, 1)` |

#### Segmented Item — 悬停状态（Hover）

| 属性 | 值 |
|------|-----|
| `color` | `var(--color-neutral-700)` → `#44403C` |
| `background` | `rgba(0, 0, 0, 0.03)` |

#### Segmented Item — 选中状态（Active）

| 属性 | 值 |
|------|-----|
| `padding` | `6px 16px` |
| `font-size` | `13px` |
| `font-weight` | `600` |
| `color` | `var(--color-neutral-800)` → `#292524` |
| `background` | `var(--color-neutral-0)` → `#FFFFFF` |
| `border-radius` | `var(--radius-md)` → `8px` |
| `box-shadow` | `0 1px 3px rgba(28, 25, 23, 0.08), 0 1px 2px rgba(28, 25, 23, 0.04)` |
| `transition` | `all 0.2s cubic-bezier(0.4, 0, 0.2, 1)` |

#### Tailwind CSS 类名

```html
<!-- 容器 -->
<div class="inline-flex items-center p-1 rounded-lg bg-neutral-100 border border-neutral-200"
     style="box-shadow: inset 0 1px 2px rgba(28,25,23,0.04);">

  <!-- 默认项 -->
  <button class="px-4 py-1.5 text-[13px] font-medium text-neutral-500 rounded-md
                 transition-all duration-200 ease-out
                 hover:text-neutral-700 hover:bg-black/[0.03]">
    今天
  </button>

  <!-- 选中项 -->
  <button class="px-4 py-1.5 text-[13px] font-semibold text-neutral-800 bg-white rounded-md
                 transition-all duration-200 ease-out
                 shadow-[0_1px_3px_rgba(28,25,23,0.08),0_1px_2px_rgba(28,25,23,0.04)]">
    最近7天
  </button>
</div>
```

---

### 1.4 交互行为

#### 数据加载状态

切换时间维度时，图表区域进入短暂加载状态：

1. **切换触发**：点击任一选项 → 选中态立即切换（无延迟，即时视觉反馈）
2. **加载指示**：图表卡片内显示骨架屏（skeleton），复用现有 `.skeleton` 类
3. **数据呈现**：数据返回后，图表使用淡入动画（`fadeUp 0.3s`）呈现

```
点击"最近30天" → Segmented Control 立即切换选中态
                → 4 个图表卡片同时显示骨架屏
                → 数据加载完成后图表淡入
```

#### 切换动画细节

选中态的背景切换应有平滑过渡：

- **背景滑动效果**（可选增强）：选中项背景从上一个位置滑动到新位置
- **实现方式**：使用 CSS `transform: translateX()` + `transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1)`
- **简化方案**：仅使用背景色渐变过渡（`transition: background-color 0.2s`），无需额外 DOM 元素

#### 键盘交互

- 使用 `Tab` 键在三个选项间移动焦点
- 使用 `←` `→` 方向键切换选中项
- 使用 `Enter` / `Space` 确认选择

---

### 1.5 响应式适配

| 断点 | 布局变化 |
|------|----------|
| `≥ 1024px`（lg） | 切换器在标题行右侧对齐，水平排列 |
| `768px ~ 1023px`（md） | 切换器在标题下方独占一行 |
| `< 768px`（sm） | 切换器在标题下方独占一行，选项紧凑排列 |

```html
<!-- 响应式布局 -->
<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
  <div class="page-header mb-0 pb-0 border-0">
    <h1>统计面板</h1>
    <p>系统访问数据与业务洞察</p>
  </div>
  <div class="inline-flex items-center p-1 rounded-lg bg-neutral-100 border border-neutral-200">
    <!-- Segmented items -->
  </div>
</div>
```

---

### 1.6 图标建议

时间维度切换器本身无需图标（文字已足够清晰）。若需要增强视觉，可在每个选项前添加图标：

| 选项 | 图标 | Lucide 名称 |
|------|------|-------------|
| 今天 | 日历（当日） | `CalendarCheck` |
| 最近7天 | 日历（周） | `CalendarDays` |
| 最近30天 | 日历（月） | `CalendarRange` |

**建议**：不使用图标。原因——图标会增加视觉复杂度，对于 3 个简洁的文字选项而言，图标是冗余的。保持纯文字更符合后台管理系统的效率导向。

---

## 设计任务 2：导航栏收缩/展开按钮优化

### 2.1 设计决策

#### 按钮位置：侧边栏右侧边缘中间位置

**决策**：将收缩/展开按钮从侧边栏底部移到侧边栏右侧边缘的垂直居中位置，悬浮于侧边栏与内容区的交界处。

**理由**：
- **符合 Fitts 定律**：鼠标在内容区操作时，侧边栏边缘中间位置是距离最近的可达点
- **视觉直觉**：按钮位于"边缘"上，暗示"推拉"侧边栏的交互语义
- **不与现有功能冲突**：底部已有用户信息区和退出按钮，避免拥挤
- **参考成熟产品**：VS Code、Notion、Linear 等产品均将侧边栏收缩按钮置于边缘位置

#### 按钮样式：纯图标，无文字

**决策**：仅使用一个 `ChevronLeft` / `ChevronRight` 图标按钮，不包含任何文字标签。

**理由**：
- 图标语义已足够清晰——左箭头表示"收起"，右箭头表示"展开"
- 消除文字在收起状态下的布局异常（当前"收缩"/"展开"文字在窄视口下会截断）
- 符合 macOS 设计语言——系统控件倾向于图标优先

#### 图标变化逻辑

| 侧边栏状态 | 按钮显示图标 | 语义 |
|-----------|-------------|------|
| 展开（256px） | `ChevronLeft` ← | "点击可收起" |
| 收起（72px） | `ChevronRight` → | "点击可展开" |

---

### 2.2 按钮位置精确规格

```
                    ┌──────┐
                    │ 侧  │
                    │ 边  │
                    │ 栏  │
                    │    ─┼── ← 按钮中心点（垂直居中）
                    │    ○│    距顶部 50%
                    │     │
                    └──────┘
                      ↑
                  按钮紧贴侧边栏右边框外侧
                  水平偏移：-12px（向右突出 12px，一半在侧边栏内，一半在内容区上）
```

#### 按钮定位参数

| 属性 | 值 |
|------|-----|
| `position` | `absolute`（相对侧边栏） |
| `top` | `50%` |
| `transform` | `translateY(-50%) translateX(50%)` |
| `right` | `0` |
| `z-index` | `40`（高于侧边栏 z-30，低于弹窗） |

---

### 2.3 按钮尺寸与样式

#### 按钮本体

| 属性 | 值 |
|------|-----|
| `width` | `24px` |
| `height` | `24px` |
| `border-radius` | `6px`（`rounded-md`） |
| `background` | `var(--sidebar-dark-bg)` → `#0F0F1A` |
| `border` | `1px solid rgba(255, 255, 255, 0.10)` |
| `color` | `rgba(255, 255, 255, 0.50)` |
| `cursor` | `pointer` |
| `display` | `flex` |
| `align-items` | `center` |
| `justify-content` | `center` |

#### 图标尺寸

| 属性 | 值 |
|------|-----|
| `size` | `14px` |
| `stroke-width` | `2` |

#### 交互状态

| 状态 | `background` | `color` | `border-color` | `transform` |
|------|-------------|---------|----------------|-------------|
| **Default** | `#0F0F1A` | `rgba(255,255,255,0.50)` | `rgba(255,255,255,0.10)` | — |
| **Hover** | `rgba(99, 102, 241, 0.30)` | `rgba(255,255,255,0.90)` | `rgba(99, 102, 241, 0.40)` | `scale(1.1)` |
| **Active** | `rgba(99, 102, 241, 0.45)` | `#FFFFFF` | `rgba(99, 102, 241, 0.50)` | `scale(0.95)` |

#### Tailwind CSS 类名

```html
<!-- 收缩/展开按钮 -->
<button
  class="absolute right-0 top-1/2 z-40 flex items-center justify-center
         w-6 h-6 rounded-md border
         transition-all duration-200 ease-out
         hover:scale-110 active:scale-95"
  :style="{
    transform: 'translateY(-50%) translateX(50%)',
    background: 'var(--sidebar-dark-bg)',
    borderColor: 'rgba(255,255,255,0.10)',
    color: 'rgba(255,255,255,0.50)'
  }"
  :title="collapsed ? '展开导航' : '收缩导航'"
  @click="collapsed = !collapsed"
>
  <ChevronLeft v-if="!collapsed" :size="14" :stroke-width="2" />
  <ChevronRight v-else :size="14" :stroke-width="2" />
</button>
```

```css
/* 悬停与激活状态 */
.sidebar-toggle-handle {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-toggle-handle:hover {
  background-color: rgba(99, 102, 241, 0.30) !important;
  color: rgba(255, 255, 255, 0.90) !important;
  border-color: rgba(99, 102, 241, 0.40) !important;
  transform: translateY(-50%) translateX(50%) scale(1.1);
}

.sidebar-toggle-handle:active {
  background-color: rgba(99, 102, 241, 0.45) !important;
  color: #FFFFFF !important;
  border-color: rgba(99, 102, 241, 0.50) !important;
  transform: translateY(-50%) translateX(50%) scale(0.95);
}
```

---

### 2.4 悬停状态的视觉反馈

#### 悬停效果描述

当鼠标悬停在收缩/展开按钮上时：

1. **背景色变化**：从侧边栏深色（`#0F0F1A`）渐变为半透明靛蓝色（`rgba(99, 102, 241, 0.30)`），呼应系统主色 `#6366F1`
2. **图标颜色变化**：从半透明白色（`50%`）变为高亮白色（`90%`）
3. **微缩放**：按钮整体 `scale(1.1)`，增加交互反馈感
4. **边框色变化**：边框从低对比白色变为靛蓝色半透明，增强品牌感

#### 动画时间线

```
鼠标进入按钮区域
  → 0ms：开始 transition
  → 200ms：达到最终悬停态（背景色、图标色、缩放同时完成）
  → 持续悬停：保持悬停态
  → 鼠标离开
  → 0ms：开始 transition
  → 200ms：恢复默认态
```

#### Tooltip 提示

悬停 500ms 后显示原生 `title` 提示：
- 展开状态：显示"收缩导航"
- 收起状态：显示"展开导航"

---

### 2.5 侧边栏整体结构调整

将按钮移到边缘中间后，侧边栏底部区域需要调整：

#### 调整前（当前）

```
┌──────────────┐
│  品牌区       │
├──────────────┤
│  导航列表     │
├──────────────┤
│  收缩/展开按钮 │  ← 移除此处的按钮
├──────────────┤
│  用户信息 + 退出│
└──────────────┘
```

#### 调整后（优化后）

```
┌──────────────┐
│  品牌区       │
├──────────────┤
│  导航列表     │
├──────────────┤
│  用户信息 + 退出│  ← 底部仅有用户区，更简洁
└──────○───────┘  ← 边缘中间：收缩/展开按钮（浮动）
```

底部用户区结构保持不变，但移除了原来的收缩按钮区域，使底部更简洁。用户信息和退出按钮之间不再有收缩按钮的视觉干扰。

---

### 2.6 图标选择

| 用途 | 当前图标 | 建议图标 | Lucide 名称 | 理由 |
|------|---------|---------|-------------|------|
| 收起（展开状态下） | `ChevronLeft` | `PanelLeftClose` | `PanelLeftClose` | 语义更明确——表示"关闭左侧边栏面板" |
| 展开（收起状态下） | `ChevronRight` | `PanelLeftOpen` | `PanelLeftOpen` | 语义更明确——表示"打开左侧边栏面板" |

**备选方案**：若希望保持简洁，继续使用 `ChevronLeft` / `ChevronRight` 也是合理选择。`PanelLeftClose` / `PanelLeftOpen` 更专业，但图标稍复杂。

**最终建议**：使用 `ChevronLeft` / `ChevronRight`。原因——按钮尺寸很小（24x24px），复杂图标在这个尺寸下细节不易辨认，简单箭头更清晰。

---

## 设计决策说明

### 为什么 Segmented Control 而不是 Tab？

| 维度 | Segmented Control | Tab |
|------|------------------|-----|
| 视觉权重 | 低，嵌入页面内容 | 高，独立导航层级 |
| 适用场景 | 少量同类选项切换（2-5个） | 页面/模块级导航 |
| 操作效率 | 一键切换，无跳转 | 可能触发页面跳转 |
| macOS 原生感 | 强——系统设置中大量使用 | 中——Safari 标签页用 |

对于"今天/7天/30天"这组选项，它们是**同一维度的不同取值**，不是不同页面，因此 Segmented Control 是正确选择。

### 为什么按钮放在侧边栏边缘中间而不是底部？

| 位置 | 优点 | 缺点 |
|------|------|------|
| 底部（当前） | 与用户信息区聚合 | 与退出按钮竞争空间；操作路径长 |
| 顶部 | 视觉层级高 | 与品牌区冲突；频繁操作时手指/鼠标移动距离长 |
| **边缘中间（推荐）** | 距内容区最近；语义直观；不干扰其他功能 | 需要额外 z-index 处理 |

### 为什么不用文字标签？

- 按钮宽度仅 24px，无法容纳中文文字
- 收起状态下侧边栏仅 72px 宽，文字标签会破坏布局
- 左右箭头图标在收缩/展开场景下是**通用隐喻**，全球用户都能理解
- Tooltip 已提供文字说明，满足可访问性需求

---

## 实现注意事项

### 时间维度切换器

1. 将 `selectedRange` 状态提升到 `AnalyticsView.vue` 的 `<script setup>` 中
2. 修改 `onMounted` 中的 API 调用，传入时间范围参数
3. 添加 `watch(selectedRange, ...)` 监听变化，重新请求数据
4. 骨架屏复用现有 `.skeleton` 类，无需额外样式

### 侧边栏按钮

1. 从 `AdminLayout.vue` 底部区域移除原有收缩按钮
2. 在 `<aside>` 标签内新增绝对定位的浮动按钮
3. 确保 `<aside>` 设置 `position: relative`（已满足，因为是 `fixed` 定位）
4. 按钮的 `z-index: 40` 高于侧边栏的 `z-30`
5. 底部用户区的 `border-t` 保留，视觉上仍与导航区有分割

---

> 设计文档结束。如有疑问，请联系 UX Designer。
