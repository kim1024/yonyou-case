import { ref, computed } from 'vue'
import { Layers, Activity, Zap, Hash } from 'lucide-vue-next'
import { adminApi } from '@/api/admin'
import type { TokenStats } from '@/types'

export function useTokenStats() {
  const tokenStats = ref<TokenStats | null>(null)
  const tokenLoading = ref(false)
  const trendDays = ref<7 | 30>(7)

  async function loadTokenStats() {
    tokenLoading.value = true
    try {
      const res = await adminApi.getTokenStats(trendDays.value)
      tokenStats.value = res.data
    } finally {
      tokenLoading.value = false
    }
  }

  function formatTokenNumber(val: number | null | undefined): string {
    if (val == null) return '--'
    if (val >= 1_000_000) return (val / 1_000_000).toFixed(1) + 'M'
    if (val >= 1_000) return (val / 1_000).toFixed(1) + 'K'
    return val.toLocaleString('zh-CN')
  }

  const tokenStatCards = computed(() => [
    { label: '总消耗 Token', value: tokenStats.value?.total_tokens ?? null, icon: Layers, gradient: 'linear-gradient(90deg, #6366F1, #A78BFA)', key: 'total' },
    { label: '今日消耗', value: tokenStats.value?.today_tokens ?? null, icon: Zap, gradient: 'linear-gradient(90deg, #10B981, #6EE7B7)', key: 'today' },
    { label: '总调用次数', value: tokenStats.value?.total_calls ?? null, icon: Activity, gradient: 'linear-gradient(90deg, #F59E0B, #FCD34D)', key: 'calls' },
    { label: '平均每次 Token', value: tokenStats.value?.avg_tokens_per_call ?? null, icon: Hash, gradient: 'linear-gradient(90deg, #EC4899, #F9A8D4)', key: 'avg' },
  ])

  /* ── 折线图 ── */
  const LINE_W = 700, LINE_H = 300, LINE_PAD = 50
  const trendHoverIdx = ref(-1)
  const trendContainerEl = ref<HTMLElement | null>(null)
  const trendContainerWidth = ref(0)

  const trendData = computed(() => {
    if (!tokenStats.value?.daily_trend) return []
    return tokenStats.value.daily_trend.slice(-trendDays.value)
  })

  const trendMax = computed(() => Math.max(1, ...trendData.value.map(d => d.tokens)))

  function trendPx(i: number) {
    return trendData.value.length <= 1 ? LINE_PAD : LINE_PAD + i * (LINE_W - LINE_PAD * 2) / (trendData.value.length - 1)
  }
  function trendPy(val: number) {
    return LINE_H - LINE_PAD - (val / trendMax.value) * (LINE_H - LINE_PAD * 2)
  }

  interface SvgPoint { x: number; y: number }
  function smoothPath(points: SvgPoint[]): string {
    if (points.length < 2) return points.length === 1 ? `M ${points[0].x} ${points[0].y}` : ''
    const tension = 6
    const minY = LINE_PAD
    const maxY = LINE_H - LINE_PAD
    const d: string[] = [`M ${points[0].x} ${points[0].y}`]
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[Math.max(0, i - 1)]
      const p1 = points[i]
      const p2 = points[i + 1]
      const p3 = points[Math.min(points.length - 1, i + 2)]
      const cp1x = p1.x + (p2.x - p0.x) / tension
      const cp1y = Math.max(minY, Math.min(maxY, p1.y + (p2.y - p0.y) / tension))
      const cp2x = p2.x - (p3.x - p1.x) / tension
      const cp2y = Math.max(minY, Math.min(maxY, p2.y - (p3.y - p1.y) / tension))
      d.push(`C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`)
    }
    return d.join(' ')
  }

  const trendPoints = computed<SvgPoint[]>(() =>
    trendData.value.map((d, i) => ({ x: trendPx(i), y: trendPy(d.tokens) }))
  )
  const trendPathD = computed(() => smoothPath(trendPoints.value))
  const trendAreaD = computed(() => {
    if (!trendPoints.value.length) return ''
    const lastX = trendPoints.value[trendPoints.value.length - 1].x
    const firstX = trendPoints.value[0].x
    const baseY = LINE_H - LINE_PAD
    return `${trendPathD.value} L ${lastX} ${baseY} L ${firstX} ${baseY} Z`
  })
  const trendGridLines = computed(() => {
    const lines: number[] = []
    for (let i = 1; i <= 4; i++) lines.push(LINE_H - LINE_PAD - (i / 4) * (LINE_H - LINE_PAD * 2))
    return lines
  })

  const trendVisibleLabelIndices = computed(() => {
    if (trendData.value.length <= 10) return trendData.value.map((_, i) => i)
    const step = Math.ceil(trendData.value.length / 10)
    return trendData.value.map((_, i) => i).filter(i => i % step === 0)
  })

  const trendTooltip = ref({ visible: false, x: 0, y: 0, content: '' })

  function showTrendTooltip(e: MouseEvent, d: { date: string; tokens: number; calls: number }) {
    const rect = trendContainerEl.value!.getBoundingClientRect()
    trendTooltip.value = {
      visible: true, x: e.clientX - rect.left, y: e.clientY - rect.top,
      content: `${d.date}: ${d.tokens.toLocaleString()} Token`,
    }
  }
  function hideTrendTooltip() { trendTooltip.value.visible = false }

  return {
    tokenStats,
    tokenLoading,
    trendDays,
    loadTokenStats,
    formatTokenNumber,
    tokenStatCards,
    /* chart constants */
    LINE_W,
    LINE_H,
    LINE_PAD,
    /* chart state */
    trendHoverIdx,
    trendContainerEl,
    trendContainerWidth,
    trendData,
    trendMax,
    trendPx,
    trendPy,
    trendPoints,
    trendPathD,
    trendAreaD,
    trendGridLines,
    trendVisibleLabelIndices,
    trendTooltip,
    showTrendTooltip,
    hideTrendTooltip,
  }
}
