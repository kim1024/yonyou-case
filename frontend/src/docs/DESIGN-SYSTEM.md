# macOS 风格设计系统 — 用友客户案例管理后台

> 版本 1.0 · 2026-04-23
>
> 设计方向：**Apple HIG 融合型管理后台** — 以 macOS Monterey/Ventura 的视觉语言为基础，结合 Web 端管理系统的功能需求，构建精致、高效、一致的交互体验。

---

## 目录

1. [设计哲学](#1-设计哲学)
2. [配色系统](#2-配色系统)
3. [字体层级](#3-字体层级)
4. [圆角规范](#4-圆角规范)
5. [阴影层级](#5-阴影层级)
6. [间距系统](#6-间距系统)
7. [组件规范](#7-组件规范)
8. [页面设计指导](#8-页面设计指导)
9. [动效规范](#9-动效规范)
10. [Tailwind CSS 4 实现参考](#10-tailwind-css-4-实现参考)
11. [设计决策记录](#11-设计决策记录)

---

## 1. 设计哲学

### 核心理念

| 关键词 | 含义 |
|--------|------|
| **通透（Translucency）** | 通过 `backdrop-blur` 和半透明层叠，营造 macOS 标志性的深度感 |
| **克制（Restraint）** | 每个视觉元素都有明确的功能目的，装饰性降到最低 |
| **一致（Consistency）** | 所有组件遵循相同的圆角、阴影、间距节奏，形成统一的视觉韵律 |
| **呼吸（Breathing）** | 充足的留白让界面有呼吸感，避免信息堆砌的压迫感 |

### 视觉优先级

```
功能清晰度 > 信息层级 > 视觉美感 > 动效细节
```

---

## 2. 配色系统

### 2.1 主色（Primary）

macOS 蓝色是整个系统的灵魂色彩，用于所有主要操作和焦点状态。

| 令牌名 | 色值 | 用途 |
|--------|------|------|
| `--color-primary-50` | `#EBF5FF` | 极浅蓝背景（悬停提示） |
| `--color-primary-100` | `#D0E8FF` | 浅蓝背景（标签、选中行） |
| `--color-primary-200` | `#A6D4FF` | 边框高亮 |
| `--color-primary-400` | `#4DA3FF` | 悬停态按钮 |
| `--color-primary-500` | `#007AFF` | **主色** — 按钮、链接、活跃态 |
| `--color-primary-600` | `#0066D6` | 按下态 |
| `--color-primary-700` | `#004C99` | 深色文字场景 |

### 2.2 中性色（Neutral）

macOS 的灰色体系强调"温暖的灰"，避免冷调纯灰。

| 令牌名 | 色值 | 用途 |
|--------|------|------|
| `--color-neutral-0` | `#FFFFFF` | 卡片/面板背景 |
| `--color-neutral-50` | `#FAFAFA` | 页面底层背景 |
| `--color-neutral-100` | `#F5F5F7` | **macOS 标志背景色** |
| `--color-neutral-200` | `#E5E5EA` | 分割线、边框 |
| `--color-neutral-300` | `#D1D1D6` | 禁用边框 |
| `--color-neutral-400` | `#AEAEB2` | 占位文字、图标 |
| `--color-neutral-500` | `#8E8E93` | 辅助文字 |
| `--color-neutral-600` | `#636366` | 二级文字 |
| `--color-neutral-700` | `#48484A` | 正文文字 |
| `--color-neutral-800` | `#3A3A3C` | 标题文字 |
| `--color-neutral-900` | `#1C1C1E` | 最深文字/纯黑替代 |

### 2.3 语义色（Semantic）

| 语义 | 令牌 | 色值 | 用途 |
|------|------|------|------|
| 成功 | `--color-success` | `#30D158` | 成功提示、状态标签 |
| 成功浅 | `--color-success-light` | `#E8FBF0` | 成功背景 |
| 警告 | `--color-warning` | `#FF9F0A` | 警告提示 |
| 警告浅 | `--color-warning-light` | `#FFF8EB` | 警告背景 |
| 错误 | `--color-danger` | `#FF453A` | 错误提示、删除操作 |
| 错误浅 | `--color-danger-light` | `#FFF0EF` | 错误背景 |
| 信息 | `--color-info` | `#64D2FF` | 信息提示 |
| 信息浅 | `--color-info-light` | `#EDFAFF` | 信息背景 |

### 2.4 侧边栏专用色

| 令牌名 | 色值 | 用途 |
|--------|------|------|
| `--sidebar-bg` | `rgba(245, 245, 247, 0.72)` | 侧边栏底色（半透明） |
| `--sidebar-active` | `rgba(0, 122, 255, 0.12)` | 导航项活跃背景 |
| `--sidebar-hover` | `rgba(0, 0, 0, 0.04)` | 导航项悬停背景 |
| `--sidebar-border` | `rgba(0, 0, 0, 0.06)` | 侧边栏右边框 |

### 2.5 毛玻璃遮罩色

| 令牌名 | 色值 | 用途 |
|--------|------|------|
| `--overlay-light` | `rgba(255, 255, 255, 0.6)` | 浅色毛玻璃遮罩 |
| `--overlay-blur` | `backdrop-filter: blur(20px)` | 模态框遮罩 |
| `--overlay-dark` | `rgba(0, 0, 0, 0.45)` | 深色遮罩（确认对话框） |

---

## 3. 字体层级

### 3.1 字体栈

```css
:root {
  /* 标题字体 — SF Pro Display 的 Web 回退方案 */
  --font-display: -apple-system, BlinkMacSystemFont, "SF Pro Display",
    "Helvetica Neue", "PingFang SC", "Noto Sans SC", sans-serif;

  /* 正文字体 */
  --font-body: -apple-system, BlinkMacSystemFont, "SF Pro Text",
    "Helvetica Neue", "PingFang SC", "Noto Sans SC", sans-serif;

  /* 等宽字体 — 数据/代码场景 */
  --font-mono: "SF Mono", "Fira Code", "JetBrains Mono",
    "Cascadia Code", monospace;
}
```

### 3.2 字号层级

| 层级 | 字号 | 字重 | 行高 | 用途 |
|------|------|------|------|------|
| Display | 28px / 1.75rem | 700 | 1.3 | 页面主标题（极少使用） |
| H1 | 22px / 1.375rem | 600 | 1.35 | 页面标题 |
| H2 | 18px / 1.125rem | 600 | 1.4 | 区域标题 |
| H3 | 15px / 0.9375rem | 600 | 1.45 | 卡片标题、表单标题 |
| Body | 14px / 0.875rem | 400 | 1.6 | 正文内容（默认） |
| Caption | 13px / 0.8125rem | 400 | 1.5 | 辅助说明文字 |
| Small | 12px / 0.75rem | 400 | 1.5 | 标签、徽章、时间戳 |
| Micro | 11px / 0.6875rem | 500 | 1.4 | 极小标注 |

### 3.3 macOS 特征

- **文字颜色**：正文使用 `--color-neutral-700`（#48484A），而非纯黑
- **链接色**：`--color-primary-500`（#007AFF），无下划线，悬停加深
- **禁用色**：`--color-neutral-400`（#AEAEB2），配合 `opacity: 0.6`

---

## 4. 圆角规范

macOS 的圆角语言强调"温和但不软弱"。

| 元素 | 圆角值 | Tailwind 类 |
|------|--------|-------------|
| 按钮（小） | 6px | `rounded-md` |
| 按钮（大） | 8px | `rounded-[8px]` |
| 输入框 | 8px | `rounded-[8px]` |
| 卡片 | 12px | `rounded-xl` |
| 模态框 | 14px | `rounded-[14px]` |
| 标签/徽章 | 6px | `rounded-md` |
| 头像（圆形） | 50% | `rounded-full` |
| 大卡片/面板 | 16px | `rounded-2xl` |
| 工具提示 | 8px | `rounded-[8px]` |

### 关键约束

- **全系统圆角统一递进**：6 → 8 → 12 → 14 → 16，不存在其他中间值
- **卡片圆角 ≥ 内容元素圆角**：内部按钮/输入框的圆角不能大于外层卡片
- **嵌套圆角修正**：卡片内的第一个/最后一个子元素的圆角应减去卡片圆角（CSS `:first-child` / `:last-child` 处理）

---

## 5. 阴影层级

macOS 风格的阴影偏柔和，带轻微的蓝色倾向，而非纯黑投影。

| 层级 | 名称 | 阴影值 | 用途 |
|------|------|--------|------|
| 0 | None | `none` | 平铺元素 |
| 1 | Float | `0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)` | 按钮、输入框默认态 |
| 2 | Lifted | `0 4px 12px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.04)` | 卡片、表格行 hover |
| 3 | Elevated | `0 8px 28px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06)` | 侧边栏、下拉菜单 |
| 4 | Overlay | `0 16px 48px rgba(0,0,0,0.16), 0 4px 16px rgba(0,0,0,0.08)` | 模态框、弹出层 |
| 5 | Deep | `0 24px 64px rgba(0,0,0,0.20), 0 8px 24px rgba(0,0,0,0.10)` | 拖拽中的元素 |

### Tailwind 映射

```css
@theme {
  --shadow-float: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-lifted: 0 4px 12px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.04);
  --shadow-elevated: 0 8px 28px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
  --shadow-overlay: 0 16px 48px rgba(0,0,0,0.16), 0 4px 16px rgba(0,0,0,0.08);
  --shadow-deep: 0 24px 64px rgba(0,0,0,0.20), 0 8px 24px rgba(0,0,0,0.10);
}
```

---

## 6. 间距系统

基于 **4px 基础单位**，采用 4 的倍数递进。

| 令牌 | 值 | Tailwind | 典型用途 |
|------|----|----------|----------|
| `--space-0` | 0px | `p-0` / `m-0` | 重置 |
| `--space-1` | 4px | `p-1` / `m-1` | 图标与文字间距 |
| `--space-2` | 8px | `p-2` / `m-2` | 内联元素间距 |
| `--space-3` | 12px | `p-3` / `m-3` | 小组件内部间距 |
| `--space-4` | 16px | `p-4` / `m-4` | 卡片内边距（标准） |
| `--space-5` | 20px | `p-5` / `m-5` | 区块间距 |
| `--space-6` | 24px | `p-6` / `m-6` | 卡片内边距（宽松） |
| `--space-8` | 32px | `p-8` / `m-8` | 大区块分隔 |
| `--space-10` | 40px | `p-10` / `m-10` | 页面级分隔 |
| `--space-12` | 48px | `p-12` / `m-12` | 页面顶/底留白 |
| `--space-16` | 64px | `p-16` / `m-16` | 超大留白 |

### 间距节奏

- **组件内部**：8px / 12px / 16px
- **组件之间**：16px / 24px
- **区块之间**：24px / 32px
- **页面级**：32px / 48px

---

## 7. 组件规范

### 7.1 按钮（Button）

| 变体 | 样式 | 用途 |
|------|------|------|
| **Primary** | `bg-[#007AFF] text-white` 悬停 `bg-[#0066D6]` 按下 `bg-[#004C99]` | 主要操作（保存、提交） |
| **Secondary** | `bg-[#F5F5F7] text-[#3A3A3C] border border-[#E5E5EA]` 悬停 `bg-[#E5E5EA]` | 次要操作（取消、返回） |
| **Danger** | `bg-[#FF453A] text-white` 悬停 `bg-[#E03D33]` | 危险操作（删除） |
| **Ghost** | `text-[#007AFF]` 悬停 `bg-[rgba(0,122,255,0.08)]` | 文本操作（查看详情） |
| **Icon** | 32×32 圆形，`rounded-full` 悬停 `bg-[#F5F5F7]` | 工具栏图标按钮 |

**尺寸规范**：

| 尺寸 | 高度 | 内边距 | 字号 | 圆角 |
|------|------|--------|------|------|
| Small | 28px | `0 10px` | 12px | 6px |
| Default | 32px | `0 14px` | 13px | 8px |
| Large | 36px | `0 18px` | 14px | 8px |

**按钮间距**：相邻按钮间距 8px。

### 7.2 输入框（Input）

```
高度：32px（Default）/ 36px（Large）
圆角：8px
边框：1px solid #E5E5EA
聚焦态：border-color: #007AFF, box-shadow: 0 0 0 3px rgba(0,122,255,0.15)
内边距：0 12px
字号：14px
占位色：#AEAEB2
背景：#FFFFFF（默认）/ #F5F5F7（禁用）
```

**输入框组**：多个输入框间距 12px（表单内）或 16px（筛选栏内）。

**标签**：位于输入框上方，字号 13px，字重 500，颜色 `#48484A`，底部间距 6px。

### 7.3 选择器（Select）

- 视觉与输入框一致
- 右侧下拉箭头图标 16×16，颜色 `#AEAEB2`
- 下拉菜单：白底，`shadow-elevated`，圆角 8px，内边距 4px

### 7.4 表格（Table）

```
表头：
  - 背景：#FAFAFA
  - 文字：12px / 500 / #8E8E93
  - 高度：40px
  - 底部边框：1px solid #E5E5EA
  - 文字对齐：左对齐（首列左，数值右）

数据行：
  - 高度：44px
  - 底部边框：1px solid #F0F0F2（极淡分割线）
  - 文字：14px / 400 / #48484A
  - 斑马纹：偶数行 background #FAFAFA
  - Hover 态：background rgba(0,122,255,0.04) + shadow-lifted

选中行：
  - background: rgba(0,122,255,0.08)
  - 左侧 3px solid #007AFF（活跃指示条）

操作列：
  - 右对齐
  - 操作按钮：Ghost 样式，间距 12px
  - 危险操作（删除）：红色 Ghost
```

### 7.5 标签/徽章（Tag / Badge）

| 类型 | 背景 | 文字 | 圆角 | 用途 |
|------|------|------|------|------|
| 默认 | `#F5F5F7` | `#636366` | 6px | 中性标签 |
| 蓝色 | `#EBF5FF` | `#007AFF` | 6px | 分类标签 |
| 绿色 | `#E8FBF0` | `#30D158` | 6px | 成功/启用 |
| 橙色 | `#FFF8EB` | `#FF9F0A` | 6px | 警告/待审 |
| 红色 | `#FFF0EF` | `#FF453A` | 6px | 错误/禁用 |

- 内边距：`4px 8px`
- 字号：12px
- 字重：500

### 7.6 分页器（Pagination）

```
容器：flex 居中，间距 4px
按钮：32×32 圆形（rounded-full）
默认态：透明背景，文字 #48484A
Hover：background #F5F5F7
活跃态：background #007AFF，文字 white
省略号：文字 #AEAEB2
当前页信息：右侧，13px，#8E8E93
```

### 7.7 模态框（Modal）

```
遮罩层：
  - background: rgba(0, 0, 0, 0.45)
  - backdrop-filter: blur(4px)

卡片：
  - 背景：#FFFFFF
  - 圆角：14px
  - 阴影：shadow-overlay
  - 最大宽度：480px（确认框）/ 640px（表单）/ 800px（大表单）
  - 内边距：24px

标题栏：
  - 标题：18px / 600 / #1C1C1E
  - 关闭按钮：右上角，24×24 圆形
  - 底部分割线：1px solid #E5E5EA

底部操作栏：
  - 内边距：16px 24px
  - 按钮右对齐
  - 按钮间距：8px

入场动画：
  - 遮罩 fadeIn 200ms ease-out
  - 卡片 scale(0.95) → scale(1) + fadeIn 250ms ease-out
```

### 7.8 工具提示（Tooltip）

```
背景：#1C1C1E
文字：#FFFFFF，12px
圆角：8px
内边距：6px 10px
阴影：shadow-elevated
箭头：4px 三角形（可选）
延迟：300ms 显示，100ms 消失
```

### 7.9 空状态（Empty State）

```
图标：48×48，颜色 #D1D1D6
标题：16px / 600 / #48484A
描述：14px / 400 / #8E8E93
操作按钮：Primary / Secondary
垂直间距：图标与标题 16px，标题与描述 8px，描述与按钮 24px
```

### 7.10 加载态

- **Skeleton**：背景 `#F5F5F7`，圆角 6px，shimmer 动画（从左到右的渐变光效）
- **Spinner**：24×24，颜色 `#007AFF`，CSS 旋转动画
- **按钮加载**：按钮内 spinner 替代文字，按钮宽度固定不跳动

---

## 8. 页面设计指导

### 8.1 登录页

#### 布局

```
┌─────────────────────────────────────────────┐
│                                             │
│          渐变背景层（全屏）                   │
│          ┌─────────────────────┐            │
│          │   品牌 Logo/标题     │            │
│          │                     │            │
│          │  ┌───────────────┐  │            │
│          │  │  用户名输入框  │  │            │
│          │  │  密码输入框    │  │            │
│          │  │  [登录按钮]    │  │            │
│          │  └───────────────┘  │            │
│          │                     │            │
│          │   版本信息          │            │
│          └─────────────────────┘            │
│                                             │
└─────────────────────────────────────────────┘
```

#### 设计细节

**背景**：
- 使用 macOS Monterey 风格的渐变：从 `#1a1a2e` 到 `#16213e` 到 `#0f3460`
- 或使用真实壁纸风格的多层渐变叠加
- 底部加一层微妙的噪点纹理（opacity 3%）增加质感

**登录卡片**：
- 背景：`rgba(255, 255, 255, 0.82)`
- `backdrop-filter: blur(40px) saturate(180%)`
- 圆角：16px
- 阴影：`shadow-overlay`
- 宽度：360px
- 内边距：32px
- 边框：`1px solid rgba(255, 255, 255, 0.3)`（顶部和左侧微光边框）

**标题区**：
- Logo/品牌图标：40×40，居中
- 系统名称：20px / 600，颜色 `#1C1C1E`
- 副标题：13px / 400，颜色 `#8E8E93`
- 标题区底部间距：28px

**输入框**：
- 高度：40px（比标准大，提升触感）
- 背景：`#F5F5F7`
- 圆角：10px
- 内边距：`0 14px`
- 标签在输入框内部（浮动标签模式）

**登录按钮**：
- 全宽
- 高度：40px
- 背景渐变：`linear-gradient(135deg, #007AFF, #0055D4)`
- 圆角：10px
- 字号：14px / 600
- Hover：亮度微调 + 阴影加深
- 按下：scale(0.98) 过渡

#### 交互

- 输入框聚焦时：背景变白，边框变蓝，`box-shadow: 0 0 0 3px rgba(0,122,255,0.15)`
- 按钮加载态：文字替换为 spinner，按钮固定宽度
- 错误态：输入框边框变红，下方出现红色错误文字，卡片轻微 shake 动画

---

### 8.2 管理后台布局

#### 整体结构

```
┌──────────┬──────────────────────────────────┐
│          │  顶部栏                            │
│  侧边栏   │──────────────────────────────────│
│          │                                    │
│  Logo    │  页面内容区                         │
│  导航    │                                    │
│  ...     │                                    │
│          │                                    │
│──────────│                                    │
│ 用户信息  │                                    │
│          │                                    │
└──────────┴──────────────────────────────────┘
```

#### 侧边栏

```
宽度：240px（默认）/ 64px（折叠态）
背景：rgba(245, 245, 247, 0.72)
backdrop-filter: blur(20px) saturate(180%)
右边框：1px solid rgba(0, 0, 0, 0.06)
```

**Logo 区域**：
- 高度：56px
- 内边距：`0 20px`
- Logo 图标：28×28
- 系统名称：15px / 600 / #1C1C1E
- 与导航区底部分割线：`1px solid rgba(0,0,0,0.06)`

**导航区域**：
- 分组标题：11px / 600 / #AEAEB2，大写字母（或保持原样），内边距 `12px 20px 6px`
- 导航项高度：36px
- 内边距：`0 16px`（含 4px 左侧缩进对齐圆角）
- 圆角：8px
- 图标：20×20，颜色 `#8E8E93`
- 文字：14px / 400 / #48484A
- 图标与文字间距：10px
- **Hover**：`background: rgba(0, 0, 0, 0.04)`
- **Active**：`background: rgba(0, 122, 255, 0.12)` + 文字色变 `#007AFF` + 图标色变 `#007AFF`
- 导航项间距：2px

**底部用户区**：
- 固定底部
- 高度：56px
- 内边距：`0 16px`
- 顶部分割线：`1px solid rgba(0,0,0,0.06)`
- 头像：32×32，圆形
- 用户名：13px / 500 / #3A3A3C
- 角色：11px / 400 / #8E8E93
- Hover：背景 `rgba(0,0,0,0.04)`，cursor pointer

#### 顶部栏

```
高度：56px
背景：#FFFFFF
底部分割线：1px solid #E5E5EA
内边距：0 24px
```

- 左侧：面包屑导航（13px，颜色 `#8E8E93`，当前页 `#3A3A3C`）
- 右侧：搜索图标、通知图标（24×24，颜色 `#8E8E93`，hover `#48484A`）
- 搜索图标与通知间距：16px

#### 内容区

```
背景：#F5F5F7
内边距：24px
最小高度：calc(100vh - 56px)
```

---

### 8.3 企业管理页

#### 页面结构

```
┌────────────────────────────────────────────┐
│  页面标题          [导入] [新增企业]          │
│────────────────────────────────────────────│
│  🔍 搜索框    状态筛选   行业筛选   [重置]    │
│────────────────────────────────────────────│
│  ┌──────────────────────────────────────┐  │
│  │  企业名称  │ 行业  │ 联系人 │ 状态 │ … │  │
│  │───────────│──────│───────│─────│   │  │
│  │  用友网络  │ IT   │ 张三  │ 启用 │ 编辑│  │
│  │  华为技术  │ 通信  │ 李四  │ 启用 │ 编辑│  │
│  │  ...      │      │       │     │   │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  共 128 条     < 1 2 3 ... 13 >   每页20条  │
└────────────────────────────────────────────┘
```

#### 筛选栏

```
容器：白色背景卡片，圆角 12px，内边距 16px，shadow-float
布局：flex，gap 12px，wrap
```

- 搜索框：min-width 240px，左侧搜索图标（16px，`#AEAEB2`）
- 筛选下拉：min-width 160px
- 重置按钮：Ghost 样式，文字 `#007AFF`
- 筛选项间距：12px

#### 数据表格

- 外层容器：白色背景，圆角 12px，overflow hidden，shadow-float
- 斑马纹 + hover 高亮
- 操作列固定右侧，width 120px
- 行选中：左侧蓝色指示条

#### 分页器

- 位于表格下方，右对齐
- 上方间距：16px
- 左侧显示总数：13px / #8E8E93
- 右侧分页控件

#### 操作按钮区

- 页面标题右侧
- "新增企业"：Primary 按钮
- "导入"：Secondary 按钮
- 按钮间距：8px

---

### 8.4 新增/编辑表单（模态框）

#### 结构

```
┌─ 毛玻璃遮罩 ─────────────────────────────┐
│                                           │
│     ┌── 模态框卡片 ──────────────────┐    │
│     │  ✕  新增企业                    │    │
│     │  ─────────────────────────────  │    │
│     │                                 │    │
│     │  企业名称 *                     │    │
│     │  [________________________]     │    │
│     │                                 │    │
│     │  所属行业 *          所在地区 *  │    │
│     │  [________________] [________]  │    │
│     │                                 │    │
│     │  联系人              联系电话    │    │
│     │  [________________] [________]  │    │
│     │                                 │    │
│     │  企业简介                       │    │
│     │  [________________________]     │    │
│     │  [________________________]     │    │
│     │                                 │    │
│     │  ─────────────────────────────  │    │
│     │              [取消] [确定]       │    │
│     └─────────────────────────────────┘    │
│                                           │
└───────────────────────────────────────────┘
```

#### 表单布局

- 标准双列表单：标签在输入框上方
- 列间距：16px
- 行间距：20px
- 必填标记：红色 `*`，位于标签文字后
- 输入框高度：36px
- textarea 最小高度：80px

#### 验证

- 错误态输入框：border `#FF453A`，`box-shadow: 0 0 0 3px rgba(255,69,58,0.12)`
- 错误文字：12px / #FF453A，位于输入框下方，间距 4px
- 表单提交时：逐个字段校验，首个错误字段自动聚焦

---

### 8.5 导入对话框

#### 结构

```
┌── 模态框卡片（560px 宽）──────────────────┐
│  ✕  导入企业数据                            │
│  ─────────────────────────────────────────  │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │                                     │   │
│  │     📄  拖拽文件到此处               │   │
│  │        或 [浏览文件]                 │   │
│  │                                     │   │
│  │     支持 .xlsx .csv 格式            │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  已选择：企业数据_2026.xlsx (2.3 MB)        │
│                                             │
│  ─────────────────────────────────────────  │
│                          [取消] [开始导入]   │
└─────────────────────────────────────────────┘
```

#### 拖拽上传区

```
边框：2px dashed #D1D1D6（默认）/ #007AFF（拖入态）
圆角：12px
内边距：40px（上下）/ 24px（左右）
背景：#FAFAFA（默认）/ #EBF5FF（拖入态）
文字：#8E8E93
图标：40×40，颜色 #D1D1D6（默认）/ #007AFF（拖入态）
```

#### 导入进度

```
进度条容器：
  - 高度：6px
  - 背景：#E5E5EA
  - 圆角：3px（半高圆角）
  - overflow: hidden

进度条填充：
  - 背景：linear-gradient(90deg, #007AFF, #4DA3FF)
  - 圆角：3px
  - 过渡：width 300ms ease-out

进度文字：
  - 进度条下方
  - 13px / #8E8E93
  - 格式：已导入 45/128 条 (35%)
```

#### 导入结果

```
成功项：左侧绿色圆点 ✓，文字 #30D158
失败项：左侧红色圆点 ✗，文字 #FF453A + hover 显示失败原因
底部：[关闭] + [下载失败记录]（如有失败）
```

---

### 8.6 统计面板

#### 卡片式数据展示

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  企业总数     │ │  本月新增     │ │  活跃客户     │ │  数据完整率   │
│              │ │              │ │              │ │              │
│    128       │ │    +12       │ │     89       │ │   94.5%      │
│              │ │              │ │              │ │              │
│  较上月 +5.2% │ │  较上月 +3   │ │  较上月 -2.1% │ │  较上月 +1.2% │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

#### 统计卡片规范

```
容器：白色背景，圆角 12px，内边距 20px，shadow-float
最小宽度：200px
布局：grid，gap 16px，auto-fill minmax(200px, 1fr)
```

- **标题**：13px / 500 / #8E8E93
- **数值**：28px / 700 / #1C1C1E，与标题间距 8px
- **趋势指示**：
  - 上升：文字 `#30D158`，前缀 `↑`
  - 下降：文字 `#FF453A`，前缀 `↓`
  - 持平：文字 `#8E8E93`，前缀 `—`
- **趋势文字**：12px / 400，与数值间距 4px
- **可选装饰**：卡片左侧或右上角可放置 40×40 的淡色图标（opacity 0.15）

#### Hover 态

- 阴影从 `shadow-float` 过渡到 `shadow-lifted`（200ms ease）
- 卡片轻微上移 `translateY(-2px)`（可选，慎用）

---

## 9. 动效规范

### 9.1 基础参数

| 场景 | 时长 | 缓动 | 用途 |
|------|------|------|------|
| 微交互 | 120ms | ease-out | 按钮 hover、颜色切换 |
| 状态切换 | 200ms | ease-out | 展开/折叠、淡入淡出 |
| 页面过渡 | 250ms | cubic-bezier(0.4, 0, 0.2, 1) | 模态框出入场 |
| 复杂动画 | 350ms | cubic-bezier(0.4, 0, 0.2, 1) | 页面切换、列表重排 |

### 9.2 关键动画

**模态框出入场**：
- 入场：遮罩 fadeIn 200ms + 卡片 scale(0.96→1) + fadeIn 250ms
- 退场：遮罩 fadeOut 150ms + 卡片 scale(1→0.96) + fadeOut 200ms

**侧边栏折叠**：
- 宽度过渡：250ms ease-out
- 文字淡出：100ms（先于宽度变化）
- 文字淡入：200ms（宽度稳定后开始）

**表格行 hover**：
- 背景色过渡：120ms ease-out

**Toast 通知**：
- 入场：从右上角 slideIn + fadeIn，250ms
- 退场：向右 slideOut + fadeOut，200ms

### 9.3 禁用动效

在用户设置 `prefers-reduced-motion: reduce` 时：
- 禁用所有 scale / translateY 变换动画
- 保留颜色过渡（缩短到 100ms）
- 保留 opacity 过渡（缩短到 100ms）

---

## 10. Tailwind CSS 4 实现参考

### 10.1 主题变量定义

```css
/* frontend/src/assets/styles/design-tokens.css */

@import "tailwindcss";

@theme {
  /* === 配色 === */
  --color-primary-50: #EBF5FF;
  --color-primary-100: #D0E8FF;
  --color-primary-200: #A6D4FF;
  --color-primary-400: #4DA3FF;
  --color-primary-500: #007AFF;
  --color-primary-600: #0066D6;
  --color-primary-700: #004C99;

  --color-neutral-0: #FFFFFF;
  --color-neutral-50: #FAFAFA;
  --color-neutral-100: #F5F5F7;
  --color-neutral-200: #E5E5EA;
  --color-neutral-300: #D1D1D6;
  --color-neutral-400: #AEAEB2;
  --color-neutral-500: #8E8E93;
  --color-neutral-600: #636366;
  --color-neutral-700: #48484A;
  --color-neutral-800: #3A3A3C;
  --color-neutral-900: #1C1C1E;

  --color-success: #30D158;
  --color-success-light: #E8FBF0;
  --color-warning: #FF9F0A;
  --color-warning-light: #FFF8EB;
  --color-danger: #FF453A;
  --color-danger-light: #FFF0EF;
  --color-info: #64D2FF;
  --color-info-light: #EDFAFF;

  /* === 阴影 === */
  --shadow-float: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-lifted: 0 4px 12px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.04);
  --shadow-elevated: 0 8px 28px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
  --shadow-overlay: 0 16px 48px rgba(0,0,0,0.16), 0 4px 16px rgba(0,0,0,0.08);
  --shadow-deep: 0 24px 64px rgba(0,0,0,0.20), 0 8px 24px rgba(0,0,0,0.10);

  /* === 字体 === */
  --font-display: -apple-system, BlinkMacSystemFont, "SF Pro Display",
    "Helvetica Neue", "PingFang SC", "Noto Sans SC", sans-serif;
  --font-body: -apple-system, BlinkMacSystemFont, "SF Pro Text",
    "Helvetica Neue", "PingFang SC", "Noto Sans SC", sans-serif;
  --font-mono: "SF Mono", "Fira Code", "JetBrains Mono", monospace;

  /* === 圆角 === */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 14px;
  --radius-2xl: 16px;

  /* === 过渡 === */
  --duration-fast: 120ms;
  --duration-normal: 200ms;
  --duration-slow: 250ms;
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.4, 0, 0.2, 1);
}

/* === 侧边栏变量 === */
:root {
  --sidebar-width: 240px;
  --sidebar-collapsed-width: 64px;
  --sidebar-bg: rgba(245, 245, 247, 0.72);
  --sidebar-active-bg: rgba(0, 122, 255, 0.12);
  --sidebar-hover-bg: rgba(0, 0, 0, 0.04);
  --sidebar-border: rgba(0, 0, 0, 0.06);
}

/* === 全局基础样式 === */
body {
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-neutral-700);
  background-color: var(--color-neutral-100);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### 10.2 常用工具类组合

```css
/* 卡片基础样式 */
.card {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-float);
  transition: box-shadow var(--duration-fast) var(--ease-out);
}
.card:hover {
  box-shadow: var(--shadow-lifted);
}

/* 毛玻璃效果 */
.glass {
  background: rgba(245, 245, 247, 0.72);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
}

/* macOS 风格输入框 */
.input-macos {
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  background: var(--color-neutral-0);
  font-size: 14px;
  color: var(--color-neutral-700);
  transition: border-color var(--duration-fast) var(--ease-out),
              box-shadow var(--duration-fast) var(--ease-out);
}
.input-macos:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15);
}
.input-macos::placeholder {
  color: var(--color-neutral-400);
}
```

---

## 11. 设计决策记录

### Q1: 为什么选择半透明侧边栏而非纯色？

macOS 的侧边栏从 Big Sur 开始采用毛玻璃效果，这是系统最具辨识度的视觉特征之一。在 Web 端实现 `backdrop-filter` 配合半透明背景，能让内容在滚动时产生微妙的透视效果，增强空间层次感。同时半透明侧边栏能与内容区的背景色产生自然融合，避免硬分割的割裂感。

**兼容性**：`backdrop-filter` 在主流浏览器已广泛支持（Chrome 76+、Safari 9+、Firefox 103+），对于管理后台的目标用户群足够安全。

### Q2: 为什么圆角值选择 6-8-12-14-16 的递进而非连续值？

macOS 的设计语言中，圆角遵循"超椭圆"（squircle）的数学逻辑，但 Web 端无法完美实现超椭圆。我们选择离散的递进值来模拟这种视觉节奏：
- 小元素（按钮、标签）使用小圆角，保持精致
- 大元素（卡片、模态框）使用大圆角，保持温和
- 递进间隔统一（2-4px），确保视觉节奏一致

### Q3: 为什么阴影带有蓝色倾向？

macOS 的 UI 在深色模式下阴影带有明显的冷色调倾向。我们在浅色模式下保持了微妙的蓝色底蕴（通过 rgba 的黑色值实现），使阴影与蓝色主色调产生和谐呼应，而非突兀的灰色投影。这在视觉上更加"苹果化"。

### Q4: 为什么正文颜色不是 #000000？

macOS 的 HIG 明确推荐使用 `#1C1C1E`（近黑）替代纯黑作为最深文字色。纯黑在白色背景上的对比度过高（21:1），长时间阅读会造成视觉疲劳。我们进一步将正文色降低到 `#48484A`，仅在标题和重要数字处使用 `#1C1C1E`，形成清晰的层级关系。

### Q5: 为什么表格行高选择 44px？

44px 是 Apple HIG 推荐的最小触控目标尺寸（44×44pt）。虽然管理后台主要面向桌面端，但这个高度确保了：
- 表格行文字（14px）上下有充足的 15px 内边距，阅读舒适
- 鼠标 hover 时有足够的交互区域
- 支持未来可能的平板触控场景

### Q6: 字体栈为何包含 PingFang SC 和 Noto Sans SC？

macOS 原生使用苹方（PingFang SC），这是最佳选择。但考虑到跨平台一致性：
- macOS/iOS：回退到 SF Pro + PingFang SC
- Windows：回退到 Helvetica Neue + Noto Sans SC（通过 Google Fonts 或本地安装）
- Linux：回退到 Noto Sans SC

这确保了所有平台都有高质量的中文渲染。
