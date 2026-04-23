# SVG 图表组件规范（SVG Charts Spec）

> 用友产业案例教学课程系统管理后台 — 4 种 SVG 图表组件 + 通用 Tooltip 规范

---

## 0. 颜色方案

### 主色板

| 名称     | 色值       | Tailwind    | 用途              |
|---------|-----------|-------------|------------------|
| 蓝色     | `#3b82f6` | `blue-500`  | 折线图、主数据       |
| 青色     | `#06b6d4` | `cyan-500`  | 柱状图             |
| 绿色     | `#10b981` | `emerald-500`| 水平条形图          |
| 黄色     | `#f59e0b` | `amber-500` | 饼图分片 3          |
| 红色     | `#ef4444` | `red-500`   | 饼图分片 4          |
| 紫色     | `#8b5cf6` | `violet-500`| 饼图分片 5          |

### Hover 色（深一档）

| 原色       | Hover 色    |
|-----------|------------|
| `#3b82f6` | `#2563eb`  |
| `#06b6d4` | `#0891b2`  |
| `#10b981` | `#059669`  |
| `#f59e0b` | `#d97706`  |
| `#ef4444` | `#dc2626`  |
| `#8b5cf6` | `#7c3aed`  |

### 背景色

| 用途     | 色值       |
|---------|-----------|
| 页面背景  | `#f8fafc` |
| SVG 背景 | `#ffffff` |
| 网格线   | `#e2e8f0` |

---

## 1. VisitTimeline 折线图

### 组件接口

```typescript
interface TimelineDataPoint {
  label: string   // X 轴标签，如 "1月"
  value: number   // Y 轴值
}

interface VisitTimelineProps {
  data: TimelineDataPoint[]
  width?: number   // 默认 700
  height?: number  // 默认 300
}
```

### viewBox 与坐标系统

- `viewBox="0 0 700 300"`
- 内边距：`padding = 40`
- 可绘制区域：`x ∈ [40, 660]`，`y ∈ [40, 260]`

### 坐标映射公式

```javascript
const padding = 40
const chartWidth = 700 - padding * 2   // 620
const chartHeight = 300 - padding * 2  // 220

// X 坐标：均匀分布
const x = padding + i * (chartWidth / (n - 1))

// Y 坐标：值映射到像素（SVG Y 轴向下，所以用减法）
const max = Math.max(...data.map(d => d.value))
const y = padding + chartHeight - (value / max) * chartHeight
```

### 完整 Vue 组件代码

```vue
<template>
  <div class="relative" ref="containerRef">
    <svg :viewBox="`0 0 ${width} ${height}`" class="w-full h-auto">
      <!-- 背景网格线 -->
      <line
        v-for="i in 4"
        :key="'grid-' + i"
        :x1="padding"
        :y1="padding + i * (chartHeight / 5)"
        :x2="width - padding"
        :y2="padding + i * (chartHeight / 5)"
        stroke="#e2e8f0"
        stroke-width="1"
        stroke-dasharray="4 2"
      />

      <!-- 折线 -->
      <path
        :d="linePath"
        fill="none"
        stroke="#3b82f6"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />

      <!-- 面积填充（可选） -->
      <path
        :d="areaPath"
        fill="url(#lineGradient)"
        opacity="0.15"
      />

      <!-- 渐变定义 -->
      <defs>
        <linearGradient id="lineGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4" />
          <stop offset="100%" stop-color="#3b82f6" stop-opacity="0" />
        </linearGradient>
      </defs>

      <!-- 数据点 -->
      <g v-for="(point, i) in computedPoints" :key="'point-' + i">
        <circle
          :cx="point.x"
          :cy="point.y"
          r="4"
          fill="#3b82f6"
          class="transition-all duration-200"
          :class="{ 'r-6': hoveredIndex === i }"
          @mouseenter="handleMouseEnter(i, $event)"
          @mouseleave="handleMouseLeave"
        />
        <!-- 透明 hover 区域（扩大可点击范围） -->
        <rect
          :x="point.x - 20"
          :y="padding"
          :width="40"
          :height="chartHeight"
          fill="transparent"
          @mouseenter="handleMouseEnter(i, $event)"
          @mouseleave="handleMouseLeave"
        />
      </g>

      <!-- X 轴标签 -->
      <text
        v-for="(point, i) in computedPoints"
        :key="'label-' + i"
        :x="point.x"
        :y="height - 10"
        text-anchor="middle"
        class="text-xs fill-gray-400"
      >
        {{ data[i].label }}
      </text>
    </svg>

    <!-- Tooltip -->
    <SvgTooltip
      :x="tooltipX"
      :y="tooltipY"
      :visible="tooltipVisible"
      :content="tooltipContent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface TimelineDataPoint {
  label: string
  value: number
}

const props = withDefaults(defineProps<{
  data: TimelineDataPoint[]
  width?: number
  height?: number
}>(), {
  width: 700,
  height: 300,
})

const padding = 40
const chartWidth = computed(() => props.width - padding * 2)
const chartHeight = computed(() => props.height - padding * 2)
const max = computed(() => Math.max(...props.data.map(d => d.value)))

const computedPoints = computed(() => {
  const n = props.data.length
  return props.data.map((d, i) => ({
    x: padding + i * (chartWidth.value / (n - 1)),
    y: padding + chartHeight.value - (d.value / max.value) * chartHeight.value,
  }))
})

const linePath = computed(() => {
  return computedPoints.value
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
    .join(' ')
})

const areaPath = computed(() => {
  const points = computedPoints.value
  const first = points[0]
  const last = points[points.length - 1]
  const baseline = padding + chartHeight.value
  return `${linePath.value} L ${last.x} ${baseline} L ${first.x} ${baseline} Z`
})

// Tooltip 状态
const hoveredIndex = ref(-1)
const tooltipVisible = ref(false)
const tooltipX = ref(0)
const tooltipY = ref(0)
const tooltipContent = ref('')

function handleMouseEnter(i: number, e: MouseEvent) {
  hoveredIndex.value = i
  tooltipVisible.value = true
  const point = computedPoints.value[i]
  tooltipX.value = point.x
  tooltipY.value = point.y - 10
  tooltipContent.value = `${props.data[i].label}: ${props.data[i].value}`
}

function handleMouseLeave() {
  hoveredIndex.value = -1
  tooltipVisible.value = false
}
</script>
```

### 可直接复制的 SVG 片段

```svg
<svg viewBox="0 0 700 300" class="w-full h-auto">
  <!-- 网格线 -->
  <line x1="40" y1="84" x2="660" y2="84" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4 2"/>
  <line x1="40" y1="128" x2="660" y2="128" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4 2"/>
  <line x1="40" y1="172" x2="660" y2="172" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4 2"/>
  <line x1="40" y1="216" x2="660" y2="216" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4 2"/>

  <!-- 折线路径 -->
  <path d="M 40 180 L 143 140 L 247 160 L 350 100 L 453 120 L 557 80 L 660 90"
        fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- 数据点 -->
  <circle cx="40" cy="180" r="4" fill="#3b82f6"/>
  <circle cx="143" cy="140" r="4" fill="#3b82f6"/>
  <circle cx="247" cy="160" r="4" fill="#3b82f6"/>
  <circle cx="350" cy="100" r="4" fill="#3b82f6"/>
  <circle cx="453" cy="120" r="4" fill="#3b82f6"/>
  <circle cx="557" cy="80" r="4" fill="#3b82f6"/>
  <circle cx="660" cy="90" r="4" fill="#3b82f6"/>

  <!-- X 轴标签 -->
  <text x="40" y="290" text-anchor="middle" class="text-xs" fill="#94a3b8">1月</text>
  <text x="143" y="290" text-anchor="middle" class="text-xs" fill="#94a3b8">2月</text>
  <text x="247" y="290" text-anchor="middle" class="text-xs" fill="#94a3b8">3月</text>
  <text x="350" y="290" text-anchor="middle" class="text-xs" fill="#94a3b8">4月</text>
  <text x="453" y="290" text-anchor="middle" class="text-xs" fill="#94a3b8">5月</text>
  <text x="557" y="290" text-anchor="middle" class="text-xs" fill="#94a3b8">6月</text>
  <text x="660" y="290" text-anchor="middle" class="text-xs" fill="#94a3b8">7月</text>
</svg>
```

---

## 2. ProvinceBarChart 柱状图

### 组件接口

```typescript
interface ProvinceData {
  province: string  // 省份名称
  value: number     // 数值
}

interface ProvinceBarChartProps {
  data: ProvinceData[]
  width?: number    // 默认 700
  height?: number   // 默认 300
}
```

### viewBox 与坐标系统

- `viewBox="0 0 700 300"`
- 内边距：`padding = 40`（左/右/上），`paddingBottom = 50`（底部留标签空间）
- 可绘制区域高度：`chartHeight = 300 - 40 - 50 = 210`

### 坐标映射公式

```javascript
const padding = 40
const paddingBottom = 50
const chartWidth = 700 - padding * 2    // 620
const chartHeight = 300 - padding - paddingBottom  // 210
const barGap = 8  // 柱子间距

const n = data.length
const barWidth = (chartWidth - barGap * (n - 1)) / n

// rect 属性
const x = padding + i * (barWidth + barGap)
const h = (value / max) * chartHeight
const y = padding + chartHeight - h
```

### 完整 Vue 组件代码

```vue
<template>
  <div class="relative" ref="containerRef">
    <svg :viewBox="`0 0 ${width} ${height}`" class="w-full h-auto">
      <!-- 水平参考线 -->
      <line
        v-for="i in 4"
        :key="'grid-' + i"
        :x1="padding"
        :y1="padding + i * (chartHeight / 5)"
        :x2="width - padding"
        :y2="padding + i * (chartHeight / 5)"
        stroke="#e2e8f0"
        stroke-width="1"
        stroke-dasharray="4 2"
      />

      <!-- 柱状条 -->
      <g v-for="(bar, i) in computedBars" :key="'bar-' + i">
        <rect
          :x="bar.x"
          :y="bar.y"
          :width="barWidth"
          :height="bar.h"
          :fill="hoveredIndex === i ? '#0891b2' : '#06b6d4'"
          rx="2"
          class="transition-colors duration-200 cursor-pointer"
          @mouseenter="handleMouseEnter(i, $event)"
          @mouseleave="handleMouseLeave"
        />
        <!-- 值标签 -->
        <text
          :x="bar.x + barWidth / 2"
          :y="bar.y - 6"
          text-anchor="middle"
          class="text-xs font-medium"
          :fill="hoveredIndex === i ? '#0891b2' : '#64748b'"
        >
          {{ data[i].value }}
        </text>
        <!-- 省份标签 -->
        <text
          :x="bar.x + barWidth / 2"
          :y="height - 15"
          text-anchor="middle"
          class="text-xs"
          fill="#94a3b8"
        >
          {{ data[i].province }}
        </text>
      </g>
    </svg>

    <SvgTooltip
      :x="tooltipX"
      :y="tooltipY"
      :visible="tooltipVisible"
      :content="tooltipContent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface ProvinceData {
  province: string
  value: number
}

const props = withDefaults(defineProps<{
  data: ProvinceData[]
  width?: number
  height?: number
}>(), {
  width: 700,
  height: 300,
})

const padding = 40
const paddingBottom = 50
const barGap = 8
const chartWidth = computed(() => props.width - padding * 2)
const chartHeight = computed(() => props.height - padding - paddingBottom)
const max = computed(() => Math.max(...props.data.map(d => d.value)))
const barWidth = computed(() =>
  (chartWidth.value - barGap * (props.data.length - 1)) / props.data.length
)

const computedBars = computed(() => {
  return props.data.map((d, i) => {
    const h = (d.value / max.value) * chartHeight.value
    return {
      x: padding + i * (barWidth.value + barGap),
      y: padding + chartHeight.value - h,
      h,
    }
  })
})

const hoveredIndex = ref(-1)
const tooltipVisible = ref(false)
const tooltipX = ref(0)
const tooltipY = ref(0)
const tooltipContent = ref('')

function handleMouseEnter(i: number, e: MouseEvent) {
  hoveredIndex.value = i
  tooltipVisible.value = true
  const bar = computedBars.value[i]
  tooltipX.value = bar.x + barWidth.value / 2
  tooltipY.value = bar.y - 10
  tooltipContent.value = `${props.data[i].province}: ${props.data[i].value}`
}

function handleMouseLeave() {
  hoveredIndex.value = -1
  tooltipVisible.value = false
}
</script>
```

### 可直接复制的 SVG 片段

```svg
<svg viewBox="0 0 700 300" class="w-full h-auto">
  <!-- 参考线 -->
  <line x1="40" y1="82" x2="660" y2="82" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4 2"/>
  <line x1="40" y1="124" x2="660" y2="124" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4 2"/>
  <line x1="40" y1="166" x2="660" y2="166" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4 2"/>
  <line x1="40" y1="208" x2="660" y2="208" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4 2"/>

  <!-- 柱状条（示例 6 个省份） -->
  <rect x="55"  y="72"  width="80" height="178" fill="#06b6d4" rx="2"/>
  <rect x="155" y="100" width="80" height="150" fill="#06b6d4" rx="2"/>
  <rect x="255" y="130" width="80" height="120" fill="#06b6d4" rx="2"/>
  <rect x="355" y="150" width="80" height="100" fill="#06b6d4" rx="2"/>
  <rect x="455" y="170" width="80" height="80"  fill="#06b6d4" rx="2"/>
  <rect x="555" y="190" width="80" height="60"  fill="#06b6d4" rx="2"/>

  <!-- 值标签 -->
  <text x="95"  y="66" text-anchor="middle" fill="#64748b" class="text-xs font-medium">1520</text>
  <text x="195" y="94" text-anchor="middle" fill="#64748b" class="text-xs font-medium">1280</text>
  <text x="295" y="124" text-anchor="middle" fill="#64748b" class="text-xs font-medium">1020</text>
  <text x="395" y="144" text-anchor="middle" fill="#64748b" class="text-xs font-medium">860</text>
  <text x="495" y="164" text-anchor="middle" fill="#64748b" class="text-xs font-medium">680</text>
  <text x="595" y="184" text-anchor="middle" fill="#64748b" class="text-xs font-medium">510</text>

  <!-- 省份标签 -->
  <text x="95"  y="280" text-anchor="middle" fill="#94a3b8" class="text-xs">北京</text>
  <text x="195" y="280" text-anchor="middle" fill="#94a3b8" class="text-xs">上海</text>
  <text x="295" y="280" text-anchor="middle" fill="#94a3b8" class="text-xs">广东</text>
  <text x="395" y="280" text-anchor="middle" fill="#94a3b8" class="text-xs">浙江</text>
  <text x="495" y="280" text-anchor="middle" fill="#94a3b8" class="text-xs">江苏</text>
  <text x="595" y="280" text-anchor="middle" fill="#94a3b8" class="text-xs">四川</text>
</svg>
```

---

## 3. CaseFrequencyChart 水平条形图

### 组件接口

```typescript
interface CaseFrequency {
  name: string    // 企业/案例名称
  value: number   // 频率数值
}

interface CaseFrequencyChartProps {
  data: CaseFrequency[]  // 通常取 Top 10
  width?: number         // 默认 700
  height?: number        // 默认 400
}
```

### viewBox 与坐标系统

- `viewBox="0 0 700 400"`
- 左侧标签区宽度：`labelWidth = 140`
- 右侧条形区宽度：`chartWidth = 700 - labelWidth - padding = 520`（padding = 40）
- 每行高度：`rowHeight = 36`
- 条形高度：`barHeight = 20`

### 坐标映射公式

```javascript
const labelWidth = 140
const padding = 40
const chartWidth = 700 - labelWidth - padding  // 520
const rowHeight = 36
const barHeight = 20
const max = Math.max(...data.map(d => d.value))

// rect 属性
const x = labelWidth
const y = i * rowHeight + (rowHeight - barHeight) / 2  // 垂直居中
const w = (value / max) * chartWidth
```

### 完整 Vue 组件代码

```vue
<template>
  <div class="relative" ref="containerRef">
    <svg :viewBox="`0 0 ${width} ${height}`" class="w-full h-auto">
      <g v-for="(bar, i) in computedBars" :key="'bar-' + i">
        <!-- 企业名称 -->
        <text
          :x="labelWidth - 8"
          :y="bar.y + barHeight / 2 + 4"
          text-anchor="end"
          class="text-xs"
          :fill="hoveredIndex === i ? '#1e293b' : '#64748b'"
        >
          {{ data[i].name }}
        </text>

        <!-- 背景条 -->
        <rect
          :x="labelWidth"
          :y="bar.y"
          :width="chartWidth"
          :height="barHeight"
          fill="#f1f5f9"
          rx="3"
        />

        <!-- 数据条 -->
        <rect
          :x="labelWidth"
          :y="bar.y"
          :width="bar.w"
          :height="barHeight"
          :fill="hoveredIndex === i ? '#059669' : '#10b981'"
          rx="3"
          class="transition-all duration-200 cursor-pointer"
          @mouseenter="handleMouseEnter(i, $event)"
          @mouseleave="handleMouseLeave"
        />

        <!-- 数值 -->
        <text
          :x="labelWidth + bar.w + 6"
          :y="bar.y + barHeight / 2 + 4"
          class="text-xs font-medium"
          :fill="hoveredIndex === i ? '#059669' : '#64748b'"
        >
          {{ data[i].value }}
        </text>
      </g>
    </svg>

    <SvgTooltip
      :x="tooltipX"
      :y="tooltipY"
      :visible="tooltipVisible"
      :content="tooltipContent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface CaseFrequency {
  name: string
  value: number
}

const props = withDefaults(defineProps<{
  data: CaseFrequency[]
  width?: number
  height?: number
}>(), {
  width: 700,
  height: 400,
})

const labelWidth = 140
const padding = 40
const rowHeight = 36
const barHeight = 20
const chartWidth = computed(() => props.width - labelWidth - padding)
const max = computed(() => Math.max(...props.data.map(d => d.value)))

const computedBars = computed(() => {
  return props.data.map((d, i) => ({
    y: i * rowHeight + (rowHeight - barHeight) / 2,
    w: (d.value / max.value) * chartWidth.value,
  }))
})

const hoveredIndex = ref(-1)
const tooltipVisible = ref(false)
const tooltipX = ref(0)
const tooltipY = ref(0)
const tooltipContent = ref('')

function handleMouseEnter(i: number, e: MouseEvent) {
  hoveredIndex.value = i
  tooltipVisible.value = true
  const bar = computedBars.value[i]
  tooltipX.value = labelWidth + bar.w / 2
  tooltipY.value = bar.y - 10
  tooltipContent.value = `${props.data[i].name}: ${props.data[i].value} 次`
}

function handleMouseLeave() {
  hoveredIndex.value = -1
  tooltipVisible.value = false
}
</script>
```

### 可直接复制的 SVG 片段

```svg
<svg viewBox="0 0 700 400" class="w-full h-auto">
  <!-- 第 1 行 -->
  <text x="132" y="28" text-anchor="end" fill="#64748b" class="text-xs">华为技术有限公司</text>
  <rect x="140" y="12" width="520" height="20" fill="#f1f5f9" rx="3"/>
  <rect x="140" y="12" width="520" height="20" fill="#10b981" rx="3"/>
  <text x="666" y="28" fill="#64748b" class="text-xs font-medium">245</text>

  <!-- 第 2 行 -->
  <text x="132" y="64" text-anchor="end" fill="#64748b" class="text-xs">比亚迪汽车</text>
  <rect x="140" y="48" width="520" height="20" fill="#f1f5f9" rx="3"/>
  <rect x="140" y="48" width="440" height="20" fill="#10b981" rx="3"/>
  <text x="586" y="64" fill="#64748b" class="text-xs font-medium">207</text>

  <!-- 第 3 行 -->
  <text x="132" y="100" text-anchor="end" fill="#64748b" class="text-xs">宁德时代</text>
  <rect x="140" y="84" width="520" height="20" fill="#f1f5f9" rx="3"/>
  <rect x="140" y="84" width="380" height="20" fill="#10b981" rx="3"/>
  <text x="526" y="100" fill="#64748b" class="text-xs font-medium">179</text>

  <!-- 第 4 行 -->
  <text x="132" y="136" text-anchor="end" fill="#64748b" class="text-xs">阿里巴巴集团</text>
  <rect x="140" y="120" width="520" height="20" fill="#f1f5f9" rx="3"/>
  <rect x="140" y="120" width="320" height="20" fill="#10b981" rx="3"/>
  <text x="466" y="136" fill="#64748b" class="text-xs font-medium">152</text>

  <!-- 第 5 行 -->
  <text x="132" y="172" text-anchor="end" fill="#64748b" class="text-xs">腾讯科技</text>
  <rect x="140" y="156" width="520" height="20" fill="#f1f5f9" rx="3"/>
  <rect x="140" y="156" width="270" height="20" fill="#10b981" rx="3"/>
  <text x="416" y="172" fill="#64748b" class="text-xs font-medium">128</text>
</svg>
```

---

## 4. IndustryPieChart 饼图

### 组件接口

```typescript
interface IndustrySlice {
  name: string    // 行业名称
  value: number   // 数值
  color?: string  // 可选自定义颜色
}

interface IndustryPieChartProps {
  data: IndustrySlice[]
  width?: number   // 默认 400
  height?: number  // 默认 400
  cx?: number      // 圆心 X，默认 200
  cy?: number      // 圆心 Y，默认 200
  radius?: number  // 半径，默认 150
}
```

### viewBox 与坐标系统

- `viewBox="0 0 400 400"`
- 圆心：`(200, 200)`
- 半径：`150`
- 起始角度：`-90°`（12 点钟方向）

### 弧形路径计算公式

```javascript
const cx = 200, cy = 200, r = 150
const total = data.reduce((sum, d) => sum + d.value, 0)

let startAngle = -90  // 从 12 点钟方向开始

data.forEach((slice, i) => {
  const sweepAngle = (slice.value / total) * 360
  const endAngle = startAngle + sweepAngle

  // 起点
  const x1 = cx + r * cos(startAngle)
  const y1 = cy + r * sin(startAngle)

  // 终点
  const x2 = cx + r * cos(endAngle)
  const y2 = cy + r * sin(endAngle)

  // 是否大弧（> 180°）
  const largeArcFlag = sweepAngle > 180 ? 1 : 0

  // SVG path
  // M cx cy        → 移动到圆心
  // L x1 y1        → 画线到弧起点
  // A r r 0 large-arc-flag 1 x2 y2  → 画弧到终点
  // Z              → 闭合路径
  const pathD = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`

  startAngle = endAngle
})
```

### 角度转弧度辅助

```javascript
function degToRad(deg: number) {
  return (deg * Math.PI) / 180
}
```

### 完整 Vue 组件代码

```vue
<template>
  <div class="relative" ref="containerRef">
    <svg :viewBox="`0 0 ${width} ${height}`" class="w-full h-auto">
      <g v-for="(slice, i) in computedSlices" :key="'slice-' + i">
        <path
          :d="slice.path"
          :fill="slice.color"
          :stroke="'#ffffff'"
          :stroke-width="hoveredIndex === i ? 3 : 2"
          class="transition-all duration-200 cursor-pointer"
          :transform="hoveredIndex === i ? `translate(${slice.offsetX}, ${slice.offsetY})` : ''"
          @mouseenter="handleMouseEnter(i, $event)"
          @mouseleave="handleMouseLeave"
        />
      </g>

      <!-- 中心空白圆（甜甜圈效果，可选） -->
      <!--
      <circle :cx="cx" :cy="cy" :r="radius * 0.55" fill="#ffffff"/>
      <text :x="cx" :y="cy - 6" text-anchor="middle" class="text-sm font-bold" fill="#1e293b">
        {{ total }}
      </text>
      <text :x="cx" :y="cy + 14" text-anchor="middle" class="text-xs" fill="#94a3b8">
        总计
      </text>
      -->
    </svg>

    <!-- 图例 -->
    <div class="flex flex-wrap gap-x-4 gap-y-2 mt-4 justify-center">
      <div
        v-for="(slice, i) in computedSlices"
        :key="'legend-' + i"
        class="flex items-center gap-1.5 text-xs text-[#64748b]"
      >
        <span class="w-2.5 h-2.5 rounded-sm flex-shrink-0" :style="{ backgroundColor: slice.color }"/>
        {{ data[i].name }}
      </div>
    </div>

    <SvgTooltip
      :x="tooltipX"
      :y="tooltipY"
      :visible="tooltipVisible"
      :content="tooltipContent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface IndustrySlice {
  name: string
  value: number
  color?: string
}

const props = withDefaults(defineProps<{
  data: IndustrySlice[]
  width?: number
  height?: number
}>(), {
  width: 400,
  height: 400,
})

const defaultColors = ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

const cx = 200
const cy = 200
const radius = 150
const total = computed(() => props.data.reduce((sum, d) => sum + d.value, 0))

function degToRad(deg: number) {
  return (deg * Math.PI) / 180
}

const computedSlices = computed(() => {
  let startAngle = -90
  return props.data.map((d, i) => {
    const sweepAngle = (d.value / total.value) * 360
    const endAngle = startAngle + sweepAngle

    const startRad = degToRad(startAngle)
    const endRad = degToRad(endAngle)

    const x1 = cx + radius * Math.cos(startRad)
    const y1 = cy + radius * Math.sin(startRad)
    const x2 = cx + radius * Math.cos(endRad)
    const y2 = cy + radius * Math.sin(endRad)

    const largeArcFlag = sweepAngle > 180 ? 1 : 0
    const path = `M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`

    // hover 偏移方向（沿中点角度向外）
    const midAngle = degToRad((startAngle + endAngle) / 2)
    const offsetX = Math.cos(midAngle) * 6
    const offsetY = Math.sin(midAngle) * 6

    const color = d.color || defaultColors[i % defaultColors.length]

    startAngle = endAngle
    return { path, color, offsetX, offsetY }
  })
})

const hoveredIndex = ref(-1)
const tooltipVisible = ref(false)
const tooltipX = ref(0)
const tooltipY = ref(0)
const tooltipContent = ref('')

function handleMouseEnter(i: number, e: MouseEvent) {
  hoveredIndex.value = i
  tooltipVisible.value = true
  const pct = ((props.data[i].value / total.value) * 100).toFixed(1)
  tooltipContent.value = `${props.data[i].name}: ${props.data[i].value} (${pct}%)`
  // tooltip 定位到饼图中点方向
  let startAngle = -90
  for (let j = 0; j <= i; j++) {
    if (j === i) {
      const midAngle = degToRad(startAngle + (props.data[i].value / total.value) * 180)
      tooltipX.value = cx + (radius * 0.6) * Math.cos(midAngle)
      tooltipY.value = cy + (radius * 0.6) * Math.sin(midAngle) - 10
    }
    startAngle += (props.data[j].value / total.value) * 360
  }
  tooltipVisible.value = true
}

function handleMouseLeave() {
  hoveredIndex.value = -1
  tooltipVisible.value = false
}
</script>
```

### 可直接复制的 SVG 片段（5 扇饼图）

```svg
<svg viewBox="0 0 400 400" class="w-full h-auto">
  <!-- 扇形 1: 制造业 35% — 蓝色 -->
  <path d="M 200 200 L 200 50 A 150 150 0 0 1 342.66 275 Z"
        fill="#3b82f6" stroke="#ffffff" stroke-width="2"/>

  <!-- 扇形 2: 科技业 25% — 青色 -->
  <path d="M 200 200 L 342.66 275 A 150 150 0 0 1 96.34 314.9 Z"
        fill="#06b6d4" stroke="#ffffff" stroke-width="2"/>

  <!-- 扇形 3: 金融业 20% — 绿色 -->
  <path d="M 200 200 L 96.34 314.9 A 150 150 0 0 1 57.34 134.1 Z"
        fill="#10b981" stroke="#ffffff" stroke-width="2"/>

  <!-- 扇形 4: 零售业 12% — 黄色 -->
  <path d="M 200 200 L 57.34 134.1 A 150 150 0 0 1 142.66 57.34 Z"
        fill="#f59e0b" stroke="#ffffff" stroke-width="2"/>

  <!-- 扇形 5: 其他 8% — 紫色 -->
  <path d="M 200 200 L 142.66 57.34 A 150 150 0 0 1 200 50 Z"
        fill="#8b5cf6" stroke="#ffffff" stroke-width="2"/>
</svg>
```

> **注意**：以上 SVG 片段中的弧形端点坐标是示例值。实际使用时，请根据真实数据按上述公式计算精确坐标。推荐使用 Vue 组件动态计算，避免手动计算误差。

---

## 5. 通用 Tooltip 组件（SvgTooltip）

### 组件接口

```typescript
interface SvgTooltipProps {
  x: number        // 相对于 SVG 容器的 X 坐标
  y: number        // 相对于 SVG 容器的 Y 坐标
  visible: boolean // 是否显示
  content: string  // 显示的文字内容
}
```

### 实现方案

Tooltip 使用绝对定位的 `<div>` 覆盖在 SVG 容器上方，通过 CSS `transition` 实现淡入效果。

### 完整 Vue 组件代码

```vue
<template>
  <Transition name="tooltip">
    <div
      v-if="visible"
      class="absolute pointer-events-none z-50 px-3 py-1.5 bg-[#1e293b] text-white text-xs rounded-lg shadow-md whitespace-nowrap"
      :style="{
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translate(-50%, -100%)',
      }"
    >
      {{ content }}
      <!-- 小三角 -->
      <div
        class="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-t-[5px] border-t-[#1e293b]"
      />
    </div>
  </Transition>
</template>

<script setup lang="ts">
defineProps<{
  x: number
  y: number
  visible: boolean
  content: string
}>()
</script>

<style scoped>
.tooltip-enter-active,
.tooltip-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
  transform: translate(-50%, -100%) translateY(4px);
}
</style>
```

### 父容器要求

SVG 容器的父元素需要设置 `relative` 定位，确保 Tooltip 的 `absolute` 定位相对于 SVG：

```html
<div class="relative" ref="containerRef">
  <svg viewBox="0 0 700 300" class="w-full h-auto">
    <!-- SVG 内容 -->
  </svg>
  <SvgTooltip
    :x="tooltipX"
    :y="tooltipY"
    :visible="tooltipVisible"
    :content="tooltipContent"
  />
</div>
```

---

## 6. 通用规范

### 6.1 SVG 渲染注意事项

1. **viewBox 固定**：所有图表的 `viewBox` 固定，通过 `class="w-full h-auto"` 实现响应式缩放。
2. **文字基线**：SVG `<text>` 元素的 Y 坐标指的是基线位置，居中时需偏移约 `fontSize * 0.35`。
3. **鼠标事件**：在数据点/条形上方叠加透明 `<rect>` 扩大 hover 可交互区域。
4. **动画**：使用 CSS `transition` 处理颜色和位移变化，不使用 SMIL 动画。

### 6.2 性能建议

- 数据量超过 200 个点时，折线图应做降采样处理。
- 饼图扇形数量建议不超过 8 个，超出部分归入"其他"。
- Tooltip 的 DOM 切换频率较高，使用 `v-if` 而非 `v-show` 避免不必要的渲染。

### 6.3 无障碍

- 所有 SVG 元素添加 `role="img"` 和 `aria-label`。
- 饼图图例需要与扇形一一对应，支持键盘 Tab 焦点切换。
