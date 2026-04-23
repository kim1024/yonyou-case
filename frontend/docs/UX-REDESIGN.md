# 用友产业案例教学课程定制系统 — UX 重设计方案

> 设计方向：**「精确出版」(Precision Editorial)**
> 以信息层级为核心，用克制的色彩和精确的排版建立专业感。拒绝千篇一律的圆角卡片，改用清晰的视觉层次引导用户完成 5 步向导。

---

## 1. 设计系统（Design System）

### 1.1 色彩体系

```
┌─ 主色 (Primary) ─────────────────────────────────────┐
│  用友蓝 — 品牌识别色，用于核心交互元素                      │
│  primary-50:  #EEF2FF   背景填充、hover 底色            │
│  primary-100: #E0E7FF   tag 背景                        │
│  primary-200: #C7D2FE   disabled 边框                   │
│  primary-400: #818CF8   图标 hover                      │
│  primary-500: #6366F1   主按钮、进度条、选中态            │
│  primary-600: #4F46E5   按钮 hover、active              │
│  primary-700: #4338CA   按钮 pressed                    │
│  primary-800: #3730A3   深色文字强调                    │
│  primary-900: #312E81   极深，仅用于文字                 │
└────────────────────────────────────────────────────────┘

┌─ 辅助色 (Accent) ────────────────────────────────────┐
│  琥珀金 — 费用突出、重要标记                               │
│  accent-400: #FBBF24                                     │
│  accent-500: #F59E0B   总费用金额、星标                  │
│  accent-600: #D97706                                     │
│                                                         │
│  青碧 — 成功、完成态                                      │
│  success-50:  #ECFDF5                                    │
│  success-400: #34D399                                    │
│  success-500: #10B981   已完成步骤、生成成功              │
│  success-600: #059669                                    │
│  success-700: #047857                                    │
└────────────────────────────────────────────────────────┘

┌─ 语义色 ─────────────────────────────────────────────┐
│  info:    #6366F1  (复用 primary-500)                   │
│  warning: #F59E0B  (复用 accent-500)                    │
│  error:   #EF4444                                         │
└────────────────────────────────────────────────────────┘

┌─ 中性色 (Neutral) ───────────────────────────────────┐
│  gray-50:   #FAFAFA   页面背景                           │
│  gray-100:  #F5F5F5   卡片背景                          │
│  gray-200:  #E5E5E5   边框、分割线                       │
│  gray-300:  #D4D4D4   disabled 背景                     │
│  gray-400:  #A3A3A8   placeholder、辅助图标              │
│  gray-500:  #737373   辅助文字                           │
│  gray-600:  #52525B   正文二级                           │
│  gray-700:  #404040   正文主体                           │
│  gray-800:  #262626   标题                               │
│  gray-900:  #171717   大标题                             │
│  white:     #FFFFFF   卡片、模态框                        │
└────────────────────────────────────────────────────────┘
```

### 1.2 字体层级

> 推荐引入 `Noto Sans SC`（Google Fonts）作为中文正文字体，`DM Sans` 作为数字/英文辅助字体。通过 Tailwind CSS 4.2 的 `@theme` 自定义。

| Token | 字号 | 行高 | 字重 | 用途 |
|-------|------|------|------|------|
| `display-lg` | 36px / 2.25rem | 1.2 | 700 | 结果页大标题 |
| `display-md` | 28px / 1.75rem | 1.3 | 700 | 页面主标题 |
| `heading-lg` | 22px / 1.375rem | 1.35 | 600 | 步骤标题 |
| `heading-md` | 18px / 1.125rem | 1.4 | 600 | 卡片标题、panel 标题 |
| `heading-sm` | 16px / 1rem | 1.5 | 600 | 小标题、标签名 |
| `body-lg` | 16px / 1rem | 1.6 | 400 | 正文主体 |
| `body-md` | 14px / 0.875rem | 1.5 | 400 | 卡片内容、表单文字 |
| `body-sm` | 13px / 0.8125rem | 1.5 | 400 | 辅助说明文字 |
| `caption` | 12px / 0.75rem | 1.4 | 500 | 标签、badge、时间戳 |

```css
/* Tailwind CSS 4.2 @theme 定义 */
@import "tailwindcss";

@theme {
  --font-display: 'Noto Sans SC', 'DM Sans', system-ui, sans-serif;
  --font-body: 'Noto Sans SC', 'DM Sans', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
}
```

### 1.3 间距体系

采用 **4px 基础网格**，间距按 4 的倍数递增：

| Token | 值 | 用途 |
|-------|-----|------|
| `space-1` | 4px | 极小间距 |
| `space-2` | 8px | 图标与文字间距 |
| `space-3` | 12px | 小组件内边距 |
| `space-4` | 16px | 卡片内边距、元素间距 |
| `space-5` | 20px | 卡片间距（小） |
| `space-6` | 24px | 卡片间距（标准） |
| `space-8` | 32px | 区块间距 |
| `space-10` | 40px | 页面边距 |
| `space-12` | 48px | 大区块间距 |
| `space-16` | 64px | 页面上下间距 |

### 1.4 圆角 / 阴影 / 边框

```css
/* 圆角 */
--radius-sm: 6px;    /* 小型元素：badge、小按钮 */
--radius-md: 10px;   /* 中型元素：卡片、输入框 */
--radius-lg: 14px;   /* 大型元素：面板、弹窗 */
--radius-xl: 20px;   /* 特殊：结果页头部装饰 */
--radius-full: 9999px; /* 圆形：avatar、进度圆点 */

/* 阴影层级 */
--shadow-xs: 0 1px 2px rgba(0,0,0,0.04);
--shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
--shadow-md: 0 4px 6px -1px rgba(0,0,0,0.06), 0 2px 4px -2px rgba(0,0,0,0.04);
--shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.06), 0 4px 6px -4px rgba(0,0,0,0.04);
--shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.04);

/* 选中态外发光 */
--shadow-glow: 0 0 0 3px rgba(99, 102, 241, 0.15);

/* 边框 */
--border-default: 1px solid #E5E5E5;
--border-focus: 2px solid #6366F1;
```

### 1.5 卡片样式规范

**未选中卡片（默认态）**
```
bg-white
border border-gray-200
rounded-[10px]
p-6
shadow-xs
transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1)

hover:
  border-color → primary-400 (#818CF8)
  shadow → shadow-md
  transform → translateY(-2px)
```

**选中卡片**
```
bg-primary-50 (#EEF2FF)
border-2 border-primary-500 (#6366F1)
rounded-[10px]
p-6
shadow-glow (外发光 ring)
transform → translateY(-2px)
transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1)
```

**禁用/空状态**
```
bg-gray-100
border border-gray-200
opacity: 0.6
cursor: not-allowed
```

### 1.6 按钮样式

| 变体 | 样式 |
|------|------|
| **primary** | `bg-primary-500 text-white rounded-[10px] px-6 py-3 font-body-md font-semibold hover:bg-primary-600 active:bg-primary-700 shadow-sm hover:shadow-md transition-all duration-200` |
| **secondary** | `bg-white text-primary-600 border-2 border-primary-200 rounded-[10px] px-6 py-3 font-body-md font-semibold hover:bg-primary-50 hover:border-primary-400 transition-all duration-200` |
| **ghost** | `bg-transparent text-gray-600 rounded-[10px] px-4 py-2 font-body-md hover:bg-gray-100 transition-all duration-200` |
| **danger** | `bg-red-500 text-white rounded-[10px] px-6 py-3 font-body-md font-semibold hover:bg-red-600 transition-all duration-200` |

**按钮尺寸变体**
| 尺寸 | padding | 字号 | 圆角 |
|------|---------|------|------|
| sm | px-4 py-2 | 13px | 8px |
| md (default) | px-6 py-3 | 14px | 10px |
| lg | px-8 py-3.5 | 16px | 12px |
| xl | px-10 py-4 | 18px | 14px |

### 1.7 过渡 / 动效

```css
/* 通用过渡 timing */
--ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

/* 步骤切换动效 */
transition: all 300ms var(--ease-standard);

/* 卡片 hover/选中 */
transition: all 200ms var(--ease-standard);

/* 页面切换 (Vue transition) */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 300ms var(--ease-standard);
}
.slide-left-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 反向（回退时使用） */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 300ms var(--ease-standard);
}
.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}
.slide-right-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* 卡片选中弹跳 */
@keyframes selectPop {
  0% { transform: scale(1); }
  50% { transform: scale(1.03); }
  100% { transform: scale(1); }
}
.animate-select-pop {
  animation: selectPop 250ms var(--ease-spring);
}

/* 骨架屏闪烁 */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 6px;
}

/* 顶部进度条加载 */
@keyframes progressFill {
  from { width: 0; }
}
.progress-fill {
  animation: progressFill 400ms var(--ease-standard) forwards;
}
```

---

## 2. 步骤进度条重设计

### 2.1 整体布局

进度条从目前的横向五步改为**「水平进度轨道 + 圆点节点 + 标签」**，占据页面顶部固定区域。

```
┌──────────────────────────────────────────────────────────────┐
│  ① ──── ② ──── ③ ──── ④ ──── ⑤                            │
│  专业   行业   省份   企业   课时                             │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 节点视觉状态

| 状态 | 样式 |
|------|------|
| **已完成（visited）** | `w-9 h-9 rounded-full bg-success-500 text-white flex items-center justify-center cursor-pointer hover:scale-110 transition` 内容：白色勾号 ✓ |
| **当前步（active）** | `w-10 h-10 rounded-full bg-primary-500 text-white flex items-center justify-center shadow-md ring-4 ring-primary-100` 内容：步骤编号 |
| **未来步（inactive）** | `w-9 h-9 rounded-full bg-gray-200 text-gray-400 flex items-center justify-center cursor-default` 内容：步骤编号 |

### 2.3 连接线

- 已完成段：`bg-success-500` 实线
- 当前段：`bg-primary-300` 半填充
- 未完成段：`bg-gray-200` 虚线

### 2.4 交互方式

- **点击已完成节点**：直接跳转到该步骤，回退时清除该步骤之后的所有选择
- **点击当前节点**：无操作（already active）
- **点击未来节点**：无操作（disabled）
- **Hover 已完成节点**：显示 tooltip「返回重新选择：[步骤名]」
- 回退逻辑：
  - 回到 Step 1 → 清除所有选择
  - 回到 Step 2 → 保留 major，清除 industry/region/enterprise/hour
  - 回到 Step 3 → 保留 major + industry，清除 region/enterprise/hour
  - 以此类推

### 2.5 移动端适配

在 `<768px` 宽度下：
- 进度条改为**竖向侧边栏**或**紧凑水平条**（仅显示圆点，隐藏标签文字）
- 点击圆点展开 tooltip 显示步骤名
- 使用 `overflow-x-auto` 允许横向滚动，但优先推荐紧凑模式

```
移动端紧凑模式：
┌──────────────┐
│ ●──●──○──○──○ │  ← 仅圆点，点击展开
└──────────────┘
```

---

## 3. 各步骤页面布局

### 3.0 全局页面结构

所有步骤页面共享以下页面容器：

```html
<div class="min-h-screen bg-gray-50 font-body">
  <!-- 顶部固定 Header -->
  <header class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
          <!-- 用友 logo 或 icon -->
        </div>
        <span class="font-heading-md text-gray-900">产业案例课程定制</span>
      </div>
      <button class="ghost-button">重新开始</button>
    </div>
  </header>

  <!-- 进度条区域 -->
  <div class="bg-white border-b border-gray-100">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <StepProgress ... />
    </div>
  </div>

  <!-- 步骤内容区域 -->
  <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <Transition :name="transitionName">
      <!-- 步骤组件 -->
    </Transition>
  </main>
</div>
```

### 3.1 Step 1 — 选择专业方向

**标题区域**
```
┌─────────────────────────────────────────┐
│  01  选择专业方向                         │
│  请选择您的教学专业，我们将为您定制专属案例  │
└─────────────────────────────────────────┘

结构：
- 步骤编号：`text-primary-500 font-mono text-sm font-bold`（小字）
- 步骤标题：`text-heading-lg text-gray-900`
- 步骤描述：`text-body-md text-gray-500 mt-1`
```

**卡片网格**

3 个专业方向卡片，每个卡片包含：
```
┌─────────────────────────────────────┐
│  [图标]                              │
│                                     │
│  大数据与会计                        │
│  涵盖智能财务、数据审计等方向         │
│                                     │
└─────────────────────────────────────┘

- 图标区：48x48 圆形，浅色背景 + 专业 icon
- 标题：font-heading-md, text-gray-900
- 描述：font-body-sm, text-gray-500
- 卡片：bg-white border rounded-[10px] p-6
- 选中：border-2 border-primary-500 bg-primary-50 shadow-glow
- 网格：`grid grid-cols-1 md:grid-cols-3 gap-6`
```

**图标建议（使用 lucide-vue-next）**
| 专业 | 图标 |
|------|------|
| 大数据与会计 | `Calculator` 或 `BarChart3` |
| 工商企业管理 | `Building2` 或 `Briefcase` |
| 市场营销 | `TrendingUp` 或 `Megaphone` |

### 3.2 Step 2 — 选择行业

**标题区域**（同上结构）
```
02  选择行业
选择案例所属行业，系统将匹配该行业的标杆企业
```

**卡片网格**

动态加载行业列表，卡片较 Step 1 更紧凑：
```
网格：grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4

单个卡片：
┌────────────────────┐
│  [行业 icon]        │
│  制造业             │
└────────────────────┘

- 图标区：36x36 圆形，浅色背景
- 标题：font-body-md font-semibold, text-gray-800
- 卡片：bg-white border rounded-[10px] p-4
- 选中：同上选中态
```

**行业 icon 映射建议**（可动态匹配，无匹配时用 `Factory`）
| 行业关键词 | 图标 |
|------------|------|
| 制造 | `Factory` |
| 零售/商贸 | `ShoppingBag` |
| 金融 | `Landmark` |
| 医疗/健康 | `HeartPulse` |
| 教育 | `GraduationCap` |
| 房地产 | `Building` |
| 餐饮 | `UtensilsCrossed` |
| 默认 | `Building2` |

### 3.3 Step 3 — 选择省份

**标题区域**
```
03  选择省份
选择企业所在省份，缩小企业匹配范围
```

**卡片网格**

省份作为简单标签式按钮，紧凑排列：
```
网格：grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3

单个卡片：
┌────────────────┐
│  [省旗/地图 icon] │
│  广东省          │
└────────────────┘

- 省份 icon：24x24，使用 `MapPin` 图标
- 标题：font-body-sm font-medium, text-gray-700
- 卡片：bg-white border rounded-lg p-3 text-center
- 选中：border-2 border-primary-500 bg-primary-50 shadow-glow
- 网格支持 overflow-y-auto，max-h-[400px]，内容多时滚动
```

### 3.4 Step 4 — 选择企业 + 企业信息面板（核心改动）

**这是本次重设计的核心改动。**

#### 4.1 布局结构

采用**双栏布局**：左侧企业列表 + 右侧企业信息面板。

```
┌────────────────────────────────────────────────────────────┐
│  04  选择企业                                               │
│  选择一家企业，查看其详细信息和用友可提供的内容                │
├──────────────────────┬─────────────────────────────────────┤
│                      │                                     │
│  [搜索框 🔍]          │   企业详情（选中前展示占位态）         │
│                      │                                     │
│  ┌────────────────┐  │   ┌─────────────────────────────┐   │
│  │ 企业 A    [✓]  │  │   │  [建筑 icon]                 │   │
│  ├────────────────┤  │   │                             │   │
│  │ 企业 B         │  │   │  华为技术有限公司             │   │
│  ├────────────────┤  │   │  广东省 · 深圳市              │   │
│  │ 企业 C         │  │   │  制造业                       │   │
│  ├────────────────┤  │   │                             │   │
│  │ 企业 D         │  │   │  ─── 企业简介 ───            │   │
│  ├────────────────┤  │   │  华为技术有限公司是一家...     │   │
│  │ 企业 E         │  │   │                             │   │
│  ├────────────────┤  │   │  ─── 用友可提供的内容 ───     │   │
│  │ 企业 F         │  │   │  数字化转型方案、ERP系统...    │   │
│  └────────────────┘  │   │                             │   │
│                      │   └─────────────────────────────┘   │
│  共 12 家企业        │                                     │
│                      │   ┌─────────────────────────────┐   │
│                      │   │  下一步 →                     │   │
│                      │   └─────────────────────────────┘   │
│                      │                                     │
└──────────────────────┴─────────────────────────────────────┘
```

#### 4.2 关键交互流程

**当前行为（有问题）：** 点击企业 → 立即跳到 Step 5

**新行为：**

1. 点击企业 → 企业高亮（选中态），右侧加载企业详情
2. 页面**停留在 Step 4**，不自动跳转
3. 右侧面板展示完整企业信息：
   - 企业名称（大字）
   - 省份 + 城市
   - 所属行业
   - 企业简介（`company_intro`）
   - 用友可提供的内容（`yonyou_content`）
4. 右下角出现**「下一步 →」按钮**
5. 用户确认后点击按钮才跳到 Step 5

#### 4.3 企业列表设计

```
左侧列表（占 40% 宽度）：
- 顶部搜索框：支持企业名模糊搜索
- 列表项高度：64px，可滚动（max-h-[480px]）
- 选中项：bg-primary-50 border-l-3 border-primary-500
- 未选中项：hover:bg-gray-50
- 列表底部：灰色小字显示「共 N 家企业」
```

#### 4.4 企业详情面板设计

```
右侧详情（占 60% 宽度）：

未选中时：
┌─────────────────────────────────┐
│  (建筑 icon, 灰色半透明)         │
│                                 │
│  请从左侧选择一家企业             │
│  查看详细信息                    │
└─────────────────────────────────┘

选中后：
┌─────────────────────────────────┐
│  [行业 icon 大图]                │
│                                 │
│  企业名称                        │
│  ● 省份 · 城市                   │
│  ○ 行业                          │
│                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                 │
│  关于该企业                      │
│  {company_intro}                 │
│                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                 │
│  用友可提供的内容                 │
│  {yonyou_content}                │
│                                 │
│  ┌──────────────────────────┐   │
│  │       下一步 →            │   │
│  └──────────────────────────┘   │
└─────────────────────────────────┘
```

#### 4.5 移动端适配

在 `<768px` 宽度下，双栏改为**上下布局**：
- 企业列表先显示（max-h-[300px] 可滚动）
- 选中企业后，企业详情在下方展开（可折叠/展开）
- 「下一步」按钮固定在底部

### 3.5 Step 5 — 选择课时

**标题区域**
```
05  课时安排
选择课程总课时数，不同课时数对应不同的内容深度
```

**卡片网格**

4 个课时选项，突出数字视觉效果：
```
网格：grid grid-cols-2 md:grid-cols-4 gap-6

单个卡片：
┌────────────────────┐
│                    │
│       8            │  ← 超大数字，强调视觉冲击
│      课时          │
│                    │
│  约 4 周完成       │  ← 副信息
│                    │
└────────────────────┘

- 数字：font-mono text-4xl font-bold
  选中：text-primary-600
  未选中：text-gray-300 → hover:text-gray-600
- 单位：text-body-sm text-gray-400
- 副信息：text-caption text-gray-500
- 卡片：bg-white border rounded-[10px] p-8 text-center
- 选中：border-2 border-primary-500 bg-primary-50 shadow-glow + 顶部 3px primary-500 装饰条
```

**课时与周数对应**（前端硬编码映射）
| 课时 | 约周数 |
|------|--------|
| 8 | 约 4 周 |
| 16 | 约 8 周 |
| 24 | 约 12 周 |
| 32 | 约 16 周 |

---

## 4. 结果页设计方案

### 4.1 页面整体结构

```
┌─────────────────────────────────────────────────────────────┐
│  [Header: 产业案例课程定制 · 返回重新定制]                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          课程方案                                     │   │
│  │     大数据与会计 · 制造业 · 华为技术有限公司            │   │
│  │          32 课时                                     │   │
│  │                                                     │   │
│  │  [AI 生成] [模板生成]  ← 标签                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─ 选择摘要卡片 ────────────────────────────────────────┐  │
│  │  [专业 icon]    [行业 icon]    [企业 icon]    [课时]  │  │
│  │  大数据与会计   制造业          华为技术       32课时   │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ 课程方案正文 ──────────────────────────────────────┐   │
│  │  [格式化后的 Markdown 内容]                           │   │
│  │  - 大标题用 h1 样式                                   │   │
│  │  - 章节用 h2/h3                                       │   │
│  │  - 重点内容用高亮色块                                  │   │
│  │  - 费用总额用特殊样式                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─ 费用总计卡片（固定/突出） ──────────────────────────┐   │
│  │  💰 课程总费用                                        │   │
│  │  ¥ 128,000.00                                       │   │
│  │  ← 琥珀金色，大号字体，特殊卡片样式                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [返回重新定制]  [打印方案]                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 选择摘要卡片

位于结果页顶部，以横向排列展示用户之前的所有选择：

```
┌──────────┬──────────┬──────────┬──────────┐
│ 📊       │ 🏭       │ 🏢       │ 🕐       │
│ 大数据与  │ 制造业    │ 华为技术  │ 32 课时   │
│ 会计     │          │ 有限公司  │          │
└──────────┴──────────┴──────────┴──────────┘

- 每个卡片：bg-white rounded-[10px] p-4 border
- 图标：w-10 h-10 rounded-full bg-primary-50 text-primary-500
- 网格：grid grid-cols-2 md:grid-cols-4 gap-4
- 标签文字：font-body-sm text-gray-500（上方小字）
- 选择值文字：font-heading-sm text-gray-900（下方加粗）
```

### 4.3 课程方案正文格式化

使用自定义 `marked` 渲染器，为不同 Markdown 元素添加 Tailwind 样式：

```css
/* 结果页 prose 样式 */
.result-prose h1 {
  @apply text-display-lg font-bold text-gray-900 mb-2;
  padding-bottom: 12px;
  border-bottom: 2px solid #E5E5E5;
}

.result-prose h2 {
  @apply text-heading-lg font-semibold text-gray-800 mt-10 mb-4;
  padding-left: 12px;
  border-left: 3px solid #6366F1;
}

.result-prose h3 {
  @apply text-heading-md font-semibold text-gray-700 mt-6 mb-3;
}

.result-prose p {
  @apply text-body-lg text-gray-700 leading-relaxed mb-4;
}

.result-prose ul {
  @apply space-y-2 mb-4;
}

.result-prose li {
  @apply text-body-md text-gray-700;
  padding-left: 20px;
  position: relative;
}

.result-prose li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  width: 6px;
  height: 6px;
  background: #6366F1;
  border-radius: 50%;
}

/* 表格样式 */
.result-prose table {
  @apply w-full border-collapse my-6;
}

.result-prose th {
  @apply bg-gray-50 text-left text-body-sm font-semibold text-gray-700 px-4 py-3 border-b-2 border-gray-200;
}

.result-prose td {
  @apply text-body-md text-gray-700 px-4 py-3 border-b border-gray-100;
}

.result-prose tr:hover td {
  @apply bg-gray-50;
}

/* 代码块（如果有） */
.result-prose code {
  @apply bg-gray-100 text-primary-700 px-1.5 py-0.5 rounded text-body-sm font-mono;
}

/* 引用块（可用来做高亮） */
.result-prose blockquote {
  @apply border-l-4 border-primary-500 bg-primary-50 rounded-r-[10px] px-6 py-4 my-6;
}

.result-prose blockquote p {
  @apply text-gray-700 italic;
}

/* 强调/加粗 — 选择内容高亮 */
.result-prose strong {
  @apply text-primary-800 font-semibold;
}

/* 费用金额 — 特殊样式（通过自定义渲染器识别） */
.amount-highlight {
  @apply text-2xl font-bold text-accent-600 bg-accent-50 px-3 py-1 rounded-lg;
}
```

### 4.4 自定义 marked 渲染器

```typescript
// 在 ResultView 中使用自定义 renderer
import { marked } from 'marked'
import type { marked as MarkedType } from 'marked'

const renderer = new marked.Renderer()

// 为 h1 添加特殊装饰
renderer.heading = function({ text, depth }: { text: string; depth: number }) {
  if (depth === 1) {
    return `<div class="result-page-header mb-8 pb-6 border-b-2 border-gray-200">
      <h1 class="text-3xl font-bold text-gray-900">${text}</h1>
    </div>`
  }
  if (depth === 2) {
    return `<h2 class="text-xl font-semibold text-gray-800 mt-10 mb-4 pl-3 border-l-[3px] border-indigo-500">${text}</h2>`
  }
  return `<h${depth} class="text-lg font-semibold text-gray-700 mt-6 mb-3">${text}</h${depth}>`
}

// 为表格添加容器样式
renderer.table = function({ header, rows }: { header: string; rows: string[][] }) {
  return `<div class="my-6 overflow-x-auto rounded-lg border border-gray-200">
    <table class="w-full">
      <thead>${header}</thead>
      <tbody>${rows.map(row => `<tr class="hover:bg-gray-50 transition-colors">${row.join('')}</tr>`).join('')}</tbody>
    </table>
  </div>`
}

// 为列表项添加自定义样式
renderer.listitem = function({ text }: { text: string }) {
  return `<li class="flex items-start gap-2 py-1">
    <span class="mt-1.5 w-1.5 h-1.5 rounded-full bg-indigo-500 flex-shrink-0"></span>
    <span class="text-gray-700">${text}</span>
  </li>`
}

marked.use({ renderer })
```

### 4.5 费用总额突出展示

如果 Markdown 内容中包含费用相关内容，使用特殊的「费用总额卡片」突出展示：

```
┌─────────────────────────────────────────────┐
│                                             │
│  💰  课程总费用                              │
│                                             │
│      ¥ 128,000.00                           │
│                                             │
│  ─────────────────────────────────────────  │
│  包含：师资培训费 · 场地费 · 材料费 · ...     │
│                                             │
└─────────────────────────────────────────────┘

样式：
- 背景：linear-gradient(135deg, #FFFBEB, #FEF3C7)（琥珀渐变）
- 边框：2px solid #F59E0B
- 圆角：14px
- 金额字体：font-mono text-4xl font-bold text-accent-600
- 位置：紧跟在课程方案正文中费用相关内容之后，或固定在页面底部
```

### 4.6 图表建议

使用纯 SVG 或轻量图表库（如不引入，可用 Tailwind CSS 画简单图表）：

**课时分布柱状图（示意）**
```
可用 CSS 实现简单的水平柱状图：

理论课  ████████████████░░░░  60%
实践课  ████████████░░░░░░░░  40%

或使用 SVG 内联实现更精致的图表。
```

**费用明细饼图**
```
建议使用 SVG 内联实现环形图：

         ╭───────╮
        │ 师资  │
       │ 45%    │
        │       │
         ╰───────╯

可参考现有 admin 目录下的 IndustryPieChart.vue 实现。
```

> **实现建议**：如果后端返回的课程方案 Markdown 中已包含表格形式的课时分布和费用明细，前端可以用 `marked` 解析后用 CSS 美化表格即可，无需额外图表库。复杂图表建议在 Markdown 渲染后，用 JavaScript 解析表格数据并用 SVG 重绘。

### 4.7 icon 使用场景汇总

| 场景 | 推荐 icon（lucide-vue-next） |
|------|------|
| 步骤 1 专业方向 | `Calculator` `Building2` `TrendingUp` |
| 步骤 2 行业 | `Factory` `ShoppingBag` `Landmark` `HeartPulse` `GraduationCap` |
| 步骤 3 省份 | `MapPin` `Globe` |
| 步骤 4 企业 | `Building2` `Users` `Briefcase` |
| 步骤 5 课时 | `Clock` `Calendar` |
| 结果页-摘要 | `BookOpen` `Factory` `Building2` `Clock` |
| 结果页-费用 | `Coins` 或 `Banknote` |
| 导航-返回 | `ArrowLeft` `RotateCcw` |
| 导航-下一步 | `ArrowRight` |
| 搜索 | `Search` |
| 加载中 | `Loader2`（加 spin 动画） |

---

## 5. 交互流程图

### 5.1 完整用户流程（含回退路径）

```
开始
 │
 ▼
┌──────────────────────┐
│ Step 1: 选择专业方向   │ ← 首次进入
│ 显示 3 个专业卡片      │
└──────────┬───────────┘
           │ 点击专业卡片
           ▼
┌──────────────────────┐
│ Step 2: 选择行业       │ ← 可从进度条回退到 Step 1
│ 显示行业网格           │
└──────────┬───────────┘
           │ 点击行业卡片 → 加载省份
           ▼
┌──────────────────────┐
│ Step 3: 选择省份       │ ← 可回退到 Step 1/2
│ 显示省份网格           │
└──────────┬───────────┘
           │ 点击省份卡片 → 加载企业
           ▼
┌──────────────────────┐
│ Step 4: 选择企业       │ ← 可回退到 Step 1/2/3
│ ┌──────────┬────────┐ │
│ │ 企业列表  │ 详情面板│ │
│ └──────────┴────────┘ │
│                       │
│ 点击企业 → 详情加载     │
│ ⚠️ 停留在此页面        │
│                       │
│ 点击「下一步」→         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Step 5: 选择课时       │ ← 可回退到 Step 1/2/3/4
│ 显示 4 个课时卡片      │
│                       │
│ 点击课时卡片 → 选中     │
│ 点击「生成课程方案」    │
└──────────┬───────────┘
           │ API 调用生成
           ▼
┌──────────────────────┐
│ 加载状态页             │
│ 显示 loading 动画      │
│ "正在为您定制课程方案..." │
└──────────┬───────────┘
           │ 成功
           ▼
┌──────────────────────┐
│ 结果页                 │
│ ┌─ 摘要卡片 ─────────┐│
│ │ 专业 | 行业 | 企业  ││
│ │ 课时              ││
│ └───────────────────┘│
│                       │
│ ┌─ 课程方案正文 ─────┐│
│ │ Markdown 格式化    ││
│ │ 费用突出显示        ││
│ └───────────────────┘│
│                       │
│ [返回重新定制]         │
│ [打印方案]             │
└───────────────────────┘
```

### 5.2 回退逻辑详细说明

```
用户在 Step 4 点击进度条的 Step 2：
│
├─ 保留：major（Step 1 的选择）
├─ 清除：industry, region, enterprise, hour
├─ 清除级联数据：regions, enterprises, enterpriseInfo
├─ 跳转到 Step 2
└─ 重新选择行业 → 自动重新加载省份

用户在 Step 5 点击进度条的 Step 4：
│
├─ 保留：major, industry, region, enterprise
├─ 清除：hour
├─ 跳转到 Step 4
├─ 企业列表仍显示（未清除）
├─ 如果之前已选企业，企业详情仍展示
└─ 用户可重新选择企业或点击下一步
```

### 5.3 useWizard composable 新增逻辑

```typescript
// 新增函数：回退到指定步骤
function goToStep(targetStep: number) {
  // 只允许回到已完成的步骤
  if (targetStep >= state.currentStep) return

  // 清除 targetStep 之后的所有选择
  if (targetStep < 5) state.hour = null
  if (targetStep < 4) {
    state.enterprise = null
    cascade.enterpriseInfo = null
  }
  if (targetStep < 3) {
    state.region = null
    cascade.enterprises = []
  }
  if (targetStep < 2) {
    state.industry = null
    cascade.regions = []
  }
  if (targetStep < 1) {
    state.major = null
  }

  state.currentStep = targetStep
}

// 新增：Step 4 选择企业后不自动跳转
function selectEnterprise(name: string) {
  state.enterprise = name
  // ❌ 删除: state.currentStep = 5
  // ✅ 保持 currentStep = 4，等待用户点击「下一步」

  loading.enterpriseInfo = true
  // ... 加载企业详情
}

// 新增：确认进入下一步（从 Step 4 到 Step 5）
function confirmEnterprise() {
  if (state.enterprise) {
    state.currentStep = 5
  }
}
```

### 5.4 企业信息停留页交互细节

```
1. 页面初始状态
   ─────────────
   左侧列表：所有企业显示，无选中
   右侧面板：占位态，提示「请从左侧选择一家企业」
   底部：无「下一步」按钮

2. 用户点击某企业
   ─────────────
   左侧列表：该企业高亮（bg-primary-50, 左边框 accent）
   右侧面板：显示 loading 骨架屏（1-2 秒）
   右侧面板：加载完成后显示企业完整信息
   底部：滑入出现「下一步 →」按钮（fade-in + slide-up 动画）

3. 用户切换选中企业
   ─────────────
   左侧列表：新企业高亮，旧企业取消
   右侧面板：先显示 loading，再显示新企业信息
   底部：「下一步」按钮保持显示

4. 用户点击「下一步」
   ─────────────
   触发 confirmEnterprise()
   过渡动画：slide-left，进入 Step 5
```

---

## 6. 实现优先级与文件清单

### 需要修改的文件

| 文件 | 改动内容 |
|------|---------|
| `src/style.css` | 添加 @theme 自定义设计系统变量 |
| `src/views/WizardView.vue` | 页面容器重构、进度条集成、过渡动画 |
| `src/views/ResultView.vue` | 结果页完全重写 |
| `src/components/wizard/StepProgress.vue` | 可点击回退的进度条 |
| `src/components/wizard/StepMajor.vue` | 卡片视觉升级 + icon |
| `src/components/wizard/StepIndustry.vue` | 卡片视觉升级 + icon |
| `src/components/wizard/StepRegion.vue` | 卡片视觉升级 + icon |
| `src/components/wizard/StepEnterprise.vue` | 双栏布局重写 |
| `src/components/wizard/EnterpriseInfoPanel.vue` | 详情面板重新设计 |
| `src/components/wizard/StepHour.vue` | 卡片视觉升级 |
| `src/composables/useWizard.ts` | 新增 goToStep / confirmEnterprise |
| `package.json` | 新增 `lucide-vue-next` 依赖 |

### 新增文件

| 文件 | 用途 |
|------|------|
| `src/components/wizard/StepHeader.vue` | 步骤标题区（复用组件：编号+标题+描述） |
| `src/components/wizard/SkeletonCard.vue` | 骨架屏加载组件 |
| `src/components/result/SelectionSummary.vue` | 结果页选择摘要卡片 |
| `src/components/result/CourseContent.vue` | 结果页 Markdown 格式化渲染 |
| `src/components/result/TotalCost.vue` | 费用总额突出展示卡片 |

### 新增依赖

```bash
pnpm add lucide-vue-next
```

---

## 7. 设计决策备忘

| 决策点 | 选择 | 原因 |
|--------|------|------|
| 色调 | Indigo 主色 + Amber 辅助 | 区分交互色与强调色，避免单调 |
| 字体 | Noto Sans SC + DM Sans | 中文正文字体 + 数字/英文增强 |
| 圆角 | 10px 基础 + 多档变化 | 统一但不单调 |
| 阴影 | 5 级层级 + 外发光 | 用阴影表达深度关系 |
| 动效 | CSS transition 为主 | 轻量，不引入动画库 |
| 图标库 | lucide-vue-next | 轻量、风格一致、tree-shakeable |
| 步骤回退 | 进度条节点可点击 | 直觉操作，符合用户心理模型 |
| 企业停留 | 显式「下一步」按钮 | 给用户充分时间查看企业信息 |
| 结果页 | 自定义 marked 渲染器 | 控制 HTML 输出的视觉样式 |
