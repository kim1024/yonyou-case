# 统计面板布局与设计规范（Analytics Layout）

> 用友产业案例教学课程系统管理后台 — 数据分析页面视觉规范

---

## 1. 整体布局结构

统计面板分为两个区域，从上到下依次为：

```
┌──────────────────────────────────────────────────────┐
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

---

## 2. Tailwind CSS 布局方案

### 2.1 页面容器

```html
<div class="min-h-screen bg-[#f8fafc] p-6">
  <!-- 卡片区域 -->
  <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
    <!-- 4 张统计卡片 -->
  </section>

  <!-- 图表区域 -->
  <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <!-- 折线图 -->
    <div class="bg-white rounded-xl shadow-sm p-6">...</div>
    <!-- 柱状图 -->
    <div class="bg-white rounded-xl shadow-sm p-6">...</div>
    <!-- 水平条形图 -->
    <div class="bg-white rounded-xl shadow-sm p-6">...</div>
    <!-- 饼图 -->
    <div class="bg-white rounded-xl shadow-sm p-6">...</div>
  </section>
</div>
```

### 2.2 统计卡片单卡结构

```html
<div class="bg-white rounded-xl shadow-sm p-6 flex items-center justify-between">
  <div>
    <p class="text-sm text-gray-500 mb-1">总访问量</p>
    <p class="text-2xl font-bold text-gray-800">12,345</p>
    <p class="text-xs text-emerald-500 mt-1">+12.5% 较上周</p>
  </div>
  <div class="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center">
    <!-- 图标 -->
  </div>
</div>
```

---

## 3. 设计 Token

### 3.1 颜色（Colors）

| Token 名称         | 色值       | 用途                 |
|-------------------|-----------|---------------------|
| `--color-primary`  | `#3b82f6` | 主色调（蓝），折线图、主按钮  |
| `--color-cyan`     | `#06b6d4` | 辅助色（青），柱状图       |
| `--color-success`  | `#10b981` | 成功/增长（绿），条形图    |
| `--color-warning`  | `#f59e0b` | 警告（黄），饼图分片      |
| `--color-danger`   | `#ef4444` | 危险/下降（红），饼图分片  |
| `--color-purple`   | `#8b5cf6` | 强调（紫），饼图分片      |
| `--color-bg`       | `#f8fafc` | 页面背景色             |
| `--color-card`     | `#ffffff` | 卡片背景色             |
| `--color-text`     | `#1e293b` | 主文字色              |
| `--color-text-sub` | `#64748b` | 次要文字色             |
| `--color-border`   | `#e2e8f0` | 边框色               |

### 3.2 Hover 色（深一档）

| 原色       | Hover 色    |
|-----------|------------|
| `#3b82f6` | `#2563eb`  |
| `#06b6d4` | `#0891b2`  |
| `#10b981` | `#059669`  |
| `#f59e0b` | `#d97706`  |
| `#ef4444` | `#dc2626`  |
| `#8b5cf6` | `#7c3aed`  |

### 3.3 间距（Spacing）

| 场景           | Tailwind 类 | 值      |
|---------------|------------|--------|
| 页面内边距       | `p-6`      | 24px   |
| 卡片间间距       | `gap-6`    | 24px   |
| 卡片内边距       | `p-6`      | 24px   |
| 图表区域内边距    | `p-6`      | 24px   |
| 卡片内容间距      | `gap-4`    | 16px   |
| 文字行间距        | `mb-1`     | 4px    |
| 图标与文字间距    | `gap-3`    | 12px   |

### 3.4 圆角（Border Radius）

| 组件       | Tailwind 类     | 值      |
|-----------|----------------|--------|
| 卡片       | `rounded-xl`   | 12px   |
| 图标容器    | `rounded-lg`   | 8px    |
| 柱状图条形  | `rx="2"`       | 2px    |
| 饼图       | 无（圆形天然无角） | —      |

### 3.5 阴影（Shadow）

| 组件     | Tailwind 类   | CSS 值                              |
|---------|--------------|-------------------------------------|
| 卡片     | `shadow-sm`  | `0 1px 2px 0 rgb(0 0 0 / 0.05)`   |
| 悬浮卡片  | `shadow-md`  | `0 4px 6px -1px rgb(0 0 0 / 0.1)` |

---

## 4. 响应式方案

| 断点    | 类名前缀 | 卡片列数 | 图表列数 | 行为                    |
|--------|---------|---------|---------|------------------------|
| < 640px | 默认    | 1       | 1       | 单列堆叠，卡片占满宽度       |
| ≥ 640px | `sm:`  | 2       | 1       | 卡片双列，图表仍单列         |
| ≥ 768px | `md:`  | 2       | 2       | 卡片双列，图表双列           |
| ≥ 1024px| `lg:`  | 4       | 2       | 卡片四列并排，图表双列        |

### 关键断点 Tailwind 类

```html
<!-- 卡片网格 -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">

<!-- 图表网格 -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
```

---

## 5. 四张统计卡片布局规格

### 卡片 1：总访问量

```html
<div class="bg-white rounded-xl shadow-sm p-6 flex items-center justify-between">
  <div class="flex-1">
    <p class="text-sm text-[#64748b] mb-1">总访问量</p>
    <p class="text-2xl font-bold text-[#1e293b]">12,345</p>
    <p class="text-xs text-[#10b981] mt-1 flex items-center gap-1">
      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z"/></svg>
      +12.5% 较上周
    </p>
  </div>
  <div class="w-12 h-12 rounded-lg bg-[#3b82f6]/10 flex items-center justify-center flex-shrink-0">
    <svg class="w-6 h-6 text-[#3b82f6]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
  </div>
</div>
```

### 卡片 2：案例总数

```html
<div class="bg-white rounded-xl shadow-sm p-6 flex items-center justify-between">
  <div class="flex-1">
    <p class="text-sm text-[#64748b] mb-1">案例总数</p>
    <p class="text-2xl font-bold text-[#1e293b]">286</p>
    <p class="text-xs text-[#10b981] mt-1 flex items-center gap-1">
      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z"/></svg>
      +8 本周新增
    </p>
  </div>
  <div class="w-12 h-12 rounded-lg bg-[#06b6d4]/10 flex items-center justify-center flex-shrink-0">
    <svg class="w-6 h-6 text-[#06b6d4]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
  </div>
</div>
```

### 卡片 3：活跃用户

```html
<div class="bg-white rounded-xl shadow-sm p-6 flex items-center justify-between">
  <div class="flex-1">
    <p class="text-sm text-[#64748b] mb-1">活跃用户</p>
    <p class="text-2xl font-bold text-[#1e293b]">3,892</p>
    <p class="text-xs text-[#ef4444] mt-1 flex items-center gap-1">
      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z"/></svg>
      -3.2% 较上周
    </p>
  </div>
  <div class="w-12 h-12 rounded-lg bg-[#10b981]/10 flex items-center justify-center flex-shrink-0">
    <svg class="w-6 h-6 text-[#10b981]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
  </div>
</div>
```

### 卡片 4：完课率

```html
<div class="bg-white rounded-xl shadow-sm p-6 flex items-center justify-between">
  <div class="flex-1">
    <p class="text-sm text-[#64748b] mb-1">完课率</p>
    <p class="text-2xl font-bold text-[#1e293b]">78.6%</p>
    <p class="text-xs text-[#10b981] mt-1 flex items-center gap-1">
      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z"/></svg>
      +5.1% 较上周
    </p>
  </div>
  <div class="w-12 h-12 rounded-lg bg-[#f59e0b]/10 flex items-center justify-center flex-shrink-0">
    <svg class="w-6 h-6 text-[#f59e0b]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
  </div>
</div>
```

---

## 6. 完整页面骨架模板

```html
<template>
  <div class="min-h-screen bg-[#f8fafc] p-6">
    <!-- 统计卡片 -->
    <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <StatCard v-for="card in statCards" :key="card.title" v-bind="card" />
    </section>

    <!-- 图表区域 -->
    <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="text-base font-semibold text-[#1e293b] mb-4">访问趋势</h3>
        <VisitTimeline :data="timelineData" />
      </div>
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="text-base font-semibold text-[#1e293b] mb-4">省份分布</h3>
        <ProvinceBarChart :data="provinceData" />
      </div>
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="text-base font-semibold text-[#1e293b] mb-4">案例频率 Top 10</h3>
        <CaseFrequencyChart :data="frequencyData" />
      </div>
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="text-base font-semibold text-[#1e293b] mb-4">行业分布</h3>
        <IndustryPieChart :data="industryData" />
      </div>
    </section>
  </div>
</template>
```
