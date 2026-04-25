<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { RotateCcw, Printer, AlertTriangle } from 'lucide-vue-next'
import DOMPurify from 'dompurify'
import http from '@/api/http'
import type { PlanThemeStyleConfig, DisplayTemplateConfig, DisplayBlockConfig } from '@/types'

// ---------- Theme ----------

const defaultStyle: PlanThemeStyleConfig = {
  accentColor: '#C0392B',
  highlightColor: '#C0392B',
  dotColor: '#D4A06A',
  pricingCardBg: 'linear-gradient(135deg, #B83227 0%, #C0392B 35%, #D94A3F 100%)',
  pricingNumberGradient: 'linear-gradient(180deg, #FFE066 0%, #FFD700 40%, #DAA520 100%)',
  pageBg: '#F8F7F4',
  cardBg: '#FFFFFF',
  textColor: '#444444',
  subtitleColor: '#2D2D2D',
}

const activeTheme = ref<PlanThemeStyleConfig | null>(null)
const themeStyle = computed(() => activeTheme.value || defaultStyle)

// ---------- Default display template ----------

const DEFAULT_DISPLAY_TEMPLATE: DisplayTemplateConfig = {
  blocks: {
    title:        { id: 'title',        visible: true, sectionTitle: '',                    order: 0 },
    introduction: { id: 'introduction', visible: true, sectionTitle: '一、总体介绍',         order: 1 },
    modules:      { id: 'modules',      visible: true, sectionTitle: '二、案例课程主要结构',  order: 2, gridCols: 2 },
    positions:    { id: 'positions',    visible: true, sectionTitle: '三、学习后胜任的岗位',  order: 3, gridCols: 2 },
    deliverables: { id: 'deliverables', visible: true, sectionTitle: '四、课程成果物',       order: 4, gridCols: 0 },
    pricing:      { id: 'pricing',      visible: true, sectionTitle: '课程报价',             order: 5 },
    footerNote:   { id: 'footerNote',   visible: true, sectionTitle: '',                    order: 6 },
  },
}

// ---------- Display config ----------

const displayConfig = computed<DisplayTemplateConfig>(() => {
  return themeStyle.value.display_template ?? DEFAULT_DISPLAY_TEMPLATE
})

const orderedVisibleBlocks = computed(() => {
  return Object.values(displayConfig.value.blocks)
    .filter(b => b.visible)
    .sort((a, b) => a.order - b.order)
    .map(b => b.id)
})

function getBlockConfig(blockId: string): DisplayBlockConfig {
  return displayConfig.value.blocks[blockId] ?? DEFAULT_DISPLAY_TEMPLATE.blocks[blockId]
}

function getGridStyle(blockId: string): Record<string, string> {
  const cfg = getBlockConfig(blockId)
  if (!cfg.gridCols || cfg.gridCols === 0) return {}
  return { 'grid-template-columns': `repeat(${cfg.gridCols}, 1fr)` }
}

// ---------- Types ----------

interface CoursePlanModule {
  name: string
  hours: number
  items: string[]
}

interface CoursePlanPosition {
  title: string
  description: string[]
}

interface CoursePlanPricing {
  hour: number
  unit_price: number
  total_cost: number
}

interface CoursePlan {
  title: string
  subtitle: string
  introduction: string
  modules: CoursePlanModule[]
  positions: CoursePlanPosition[]
  deliverables: string[]
  notes: string
  pricing: CoursePlanPricing
}

// ---------- Sanitize ----------

const sanitize = (html: string): string => DOMPurify.sanitize(html)

// ---------- Router ----------

const router = useRouter()
const route = useRoute()

// ---------- Data ----------

const source = computed(() => (route.query.source as string) || sessionStorage.getItem('resultSource') || 'template')

const isTemplateFallback = computed(() => source.value === 'template')

const llmError = computed(() => sessionStorage.getItem('resultLlmError') || '')

const plan = computed<CoursePlan | null>(() => {
  try {
    const raw = sessionStorage.getItem('resultContent')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
})

const formattedPrice = computed(() => {
  return plan.value?.pricing.total_cost?.toLocaleString('zh-CN') ?? '0'
})

// ---------- Deliverable icons (inline SVG) ----------

const deliverableIcons: Record<string, string> = {
  'PPT': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="2" y="4" width="20" height="14" rx="2" fill="#E8563A" fill-opacity="0.15" stroke="#E8563A" stroke-width="1.5"/><polygon points="10,9 10,15 15,12" fill="#E8563A"/><line x1="7" y1="21" x2="17" y2="21" stroke="#E8563A" stroke-width="1.5" stroke-linecap="round"/><line x1="12" y1="18" x2="12" y2="21" stroke="#E8563A" stroke-width="1.5"/></svg>',
  '视频': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="2" y="5" width="15" height="14" rx="2" fill="#E88A3A" fill-opacity="0.15" stroke="#E88A3A" stroke-width="1.5"/><polygon points="8,10 8,16 13,13" fill="#E88A3A"/><path d="M17 9l5-3v12l-5-3V9z" fill="#E88A3A" fill-opacity="0.7" stroke="#E88A3A" stroke-width="1.5" stroke-linejoin="round"/></svg>',
  '指导书': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 4h6a2 2 0 012 2v14a1 1 0 00-1-1H4V4z" fill="#C4883A" fill-opacity="0.15" stroke="#C4883A" stroke-width="1.5" stroke-linejoin="round"/><path d="M20 4h-6a2 2 0 00-2 2v14a1 1 0 011-1h7V4z" fill="#C4883A" fill-opacity="0.15" stroke="#C4883A" stroke-width="1.5" stroke-linejoin="round"/><line x1="8" y1="8" x2="10" y2="8" stroke="#C4883A" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/><line x1="8" y1="11" x2="11" y2="11" stroke="#C4883A" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/><line x1="13" y1="8" x2="16" y2="8" stroke="#C4883A" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/><line x1="13" y1="11" x2="15" y2="11" stroke="#C4883A" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/></svg>',
  '数据集': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><ellipse cx="12" cy="5" rx="8" ry="3" fill="#5B9A6F" fill-opacity="0.15" stroke="#5B9A6F" stroke-width="1.5"/><path d="M4 5v6c0 1.66 3.58 3 8 3s8-1.34 8-3V5" stroke="#5B9A6F" stroke-width="1.5"/><path d="M4 11v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6" fill="#5B9A6F" fill-opacity="0.08" stroke="#5B9A6F" stroke-width="1.5"/><circle cx="8" cy="5" r="0.8" fill="#5B9A6F"/><circle cx="12" cy="5" r="0.8" fill="#5B9A6F"/><circle cx="16" cy="5" r="0.8" fill="#5B9A6F"/></svg>',
  '代码包': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M3 7V5a2 2 0 012-2h4l2 2h6a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2V7z" fill="#4A82C4" fill-opacity="0.15" stroke="#4A82C4" stroke-width="1.5" stroke-linejoin="round"/><polyline points="9,16 5,12 9,8" stroke="#4A82C4" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><polyline points="15,8 19,12 15,16" stroke="#4A82C4" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  '实操环境': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="2" y="3" width="20" height="18" rx="2" fill="#8B6BC4" fill-opacity="0.15" stroke="#8B6BC4" stroke-width="1.5"/><line x1="2" y1="7" x2="22" y2="7" stroke="#8B6BC4" stroke-width="1.5" opacity="0.4"/><circle cx="5" cy="5" r="0.7" fill="#8B6BC4" opacity="0.7"/><circle cx="7.5" cy="5" r="0.7" fill="#8B6BC4" opacity="0.5"/><polyline points="6,12 9,15 6,18" stroke="#8B6BC4" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><line x1="11" y1="18" x2="17" y2="18" stroke="#8B6BC4" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/></svg>',
}

const positionIcons: string[] = [
  // 0: 专业工程师（代码/终端）
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/><line x1="14" y1="4" x2="10" y2="20"/></svg>',
  // 1: 行业解决方案架构师（架构蓝图）
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="8.5" y="14" width="7" height="7" rx="1"/><line x1="6.5" y1="10" x2="12" y2="14"/><line x1="17.5" y1="10" x2="12" y2="14"/></svg>',
  // 2: 项目实施顾问（部署/上线）
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"/><polyline points="5 12 12 5 19 12"/><path d="M5 19h14"/></svg>',
  // 3: 业务分析师（分析/图表）
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><rect x="7" y="10" width="3" height="8" rx="0.5"/><rect x="14" y="6" width="3" height="12" rx="0.5"/><rect x="10" y="14" width="3" height="4" rx="0.5"/></svg>',
  // 4: 技术项目经理（任务板/看板）
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/><line x1="3" y1="9" x2="9" y2="9"/><line x1="3" y1="15" x2="9" y2="15"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="15" y1="8" x2="21" y2="8"/><line x1="15" y1="16" x2="21" y2="16"/></svg>',
  // 5: 数字化运营专员（循环/监控）
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 0 1 10 10"/><polyline points="22 4 22 12 14 12"/><path d="M12 22a10 10 0 0 1-10-10"/><polyline points="2 20 2 12 10 12"/><circle cx="12" cy="12" r="3"/></svg>',
]

const moduleIcons: string[] = [
  // 0: 模块一 - 行业背景与需求分析（趋势/行业）
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 16l4-8 4 4 5-9"/></svg>',
  // 1: 模块二 - 技术基础与工具介绍（工具/齿轮）
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
  // 2: 模块三 - 案例实战与项目实施（动手/代码运行）
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>',
  // 3: 模块四 - 总结与拓展（书签/总结）
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>',
]

// ---------- Fetch active theme ----------

onMounted(async () => {
  try {
    const { data } = await http.get('/api/themes/active')
    if (data?.style_config) {
      activeTheme.value = data.style_config
    }
  } catch {
    // 静默失败，使用默认样式
  }
})

// ---------- Print ----------

function handlePrint() {
  window.print()
}
</script>

<template>
  <div
    class="result-page"
    :style="{
      'min-height': '100vh',
      background: themeStyle.pageBg,
      '--theme-accent': themeStyle.accentColor,
      '--theme-highlight': themeStyle.highlightColor,
      '--theme-dot': themeStyle.dotColor,
      '--theme-text': themeStyle.textColor,
      '--theme-subtitle': themeStyle.subtitleColor,
      '--theme-card-bg': themeStyle.cardBg,
      '--theme-pricing-bg': themeStyle.pricingCardBg,
      '--theme-pricing-number': themeStyle.pricingNumberGradient,
    }"
  >
    <main class="main-content" style="padding:24px 40px 60px">
      <!-- Empty state -->
      <div
        v-if="!plan"
        class="content-card"
        style="background:var(--theme-card-bg);border-radius:16px;padding:80px 56px;margin:0 auto;max-width:1320px;text-align:center"
      >
        <p style="font-size:16px;color:#888">暂无方案数据，请重新定制</p>
      </div>

      <!-- Course plan content -->
      <div v-else class="content-card" style="background:var(--theme-card-bg);border-radius:16px;padding:48px;margin:0 auto;max-width:1320px">

        <div v-for="blockType in orderedVisibleBlocks" :key="blockType">

          <!-- ===== Title area ===== -->
          <template v-if="blockType === 'title'">
            <div style="text-align:center;padding-bottom:24px;border-bottom:2px solid #E8E5DF;margin-bottom:0">
              <h1 class="plan-title">{{ plan.title }}</h1>
              <p class="plan-subtitle">{{ plan.subtitle }}</p>
              <p class="plan-pricing-info">{{ plan.pricing.hour }}课时  ·  课程报价 ¥{{ formattedPrice }}元</p>
            </div>
          </template>

          <!-- ===== Introduction ===== -->
          <template v-else-if="blockType === 'introduction'">
            <div v-if="plan.introduction" class="section-block">
              <h2 class="section-heading">
                <span class="section-heading-bar" />
                {{ getBlockConfig('introduction').sectionTitle }}
              </h2>
              <div class="introduction-content" v-html="sanitize(plan.introduction)" />
            </div>
          </template>

          <!-- ===== Course modules ===== -->
          <template v-else-if="blockType === 'modules'">
            <div v-if="plan.modules.length" class="section-block">
              <h2 class="section-heading">
                <span class="section-heading-bar" />
                {{ getBlockConfig('modules').sectionTitle }}
              </h2>
              <div class="modules-grid" :style="getGridStyle('modules')">
                <div
                  v-for="(mod, i) in plan.modules"
                  :key="i"
                  class="module-card"
                >
                  <h3 class="module-card-title">
                    <span v-if="moduleIcons[i]" class="module-icon" v-html="moduleIcons[i]" />
                    {{ mod.name }}
                  </h3>
                  <ul class="module-items">
                    <li v-for="(item, j) in mod.items" :key="j" class="module-item">
                      <span v-html="sanitize(item)" />
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </template>

          <!-- ===== Positions ===== -->
          <template v-else-if="blockType === 'positions'">
            <div v-if="plan.positions.length" class="section-block">
              <h2 class="section-heading">
                <span class="section-heading-bar" />
                {{ getBlockConfig('positions').sectionTitle }}
              </h2>
              <p class="position-intro">结合相关行业与专业，学员毕业后可胜任以下岗位：</p>
              <div class="positions-grid" :style="getGridStyle('positions')">
                <div
                  v-for="(pos, i) in plan.positions"
                  :key="i"
                  class="position-card"
                >
                  <div class="position-name">
                    <span v-if="positionIcons[i]" class="position-icon" v-html="positionIcons[i]" />
                    {{ pos.title }}
                  </div>
                  <ul v-if="pos.description.length" class="position-items">
                    <li v-for="(desc, j) in pos.description" :key="j" class="position-item">
                      <span v-html="sanitize(desc)" />
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </template>

          <!-- ===== Deliverables ===== -->
          <template v-else-if="blockType === 'deliverables'">
            <div v-if="plan.deliverables.length" class="section-block">
              <h2 class="section-heading">
                <span class="section-heading-bar" />
                {{ getBlockConfig('deliverables').sectionTitle }}
              </h2>
              <div
                class="deliverables-grid"
                :style="getBlockConfig('deliverables').gridCols ? { display: 'grid', 'grid-template-columns': `repeat(${getBlockConfig('deliverables').gridCols}, 1fr)` } : {}"
              >
                <div v-for="(item, i) in plan.deliverables" :key="i" class="deliverable-chip">
                  <span v-html="deliverableIcons[item] || ''" />
                  <span>{{ item }}</span>
                </div>
              </div>
            </div>
          </template>

          <!-- ===== Pricing card ===== -->
          <template v-else-if="blockType === 'pricing'">
            <div class="pricing-card">
              <div class="pricing-card-bar" />
              <div class="pricing-card-label">{{ getBlockConfig('pricing').sectionTitle }}</div>
              <div class="pricing-card-price">
                <span class="pricing-card-symbol">¥</span>
                <span class="pricing-card-number">{{ formattedPrice }}</span>
              </div>
            </div>
          </template>

          <!-- ===== Footer note ===== -->
          <template v-else-if="blockType === 'footerNote'">
            <div v-if="isTemplateFallback" class="llm-warning-banner" style="margin-top:32px;max-width:100%">
              <AlertTriangle :size="16" :stroke-width="2" />
              <span>{{ llmError || '当前方案由模板生成（大模型不可用）。如需 AI 生成的方案，请在后台检查大模型配置（API Key、Base URL）。' }}</span>
            </div>
            <div v-else class="ai-note">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 1 4 4v1a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/><path d="M16 14h.01"/><path d="M8 14h.01"/><path d="M12 18v4"/><path d="M9 22h6"/></svg>
              <span>{{ plan.notes }}</span>
            </div>
          </template>

        </div>
      </div>
    </main>

    <!-- Bottom action bar -->
    <footer class="bottom-bar" style="position:sticky;bottom:0;z-50;background:rgba(255,255,255,0.88);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-top:1px solid #E8E5DF">
      <div class="bottom-bar-inner max-w-4xl mx-auto flex items-center justify-center gap-3" style="padding:16px 40px">
        <button class="btn-secondary flex items-center gap-2" style="padding:10px 24px" @click="router.push('/')">
          <RotateCcw style="width:15px;height:15px" />
          重新定制
        </button>
        <button class="btn-primary flex items-center gap-2" style="padding:10px 24px" @click="handlePrint">
          <Printer style="width:15px;height:15px" />
          打印方案
        </button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* ========================================
   Title area
   ======================================== */
.plan-title {
  font-size: 38px;
  font-weight: 700;
  color: var(--theme-accent);
  margin: 0 0 6px;
  line-height: 1.4;
  letter-spacing: 2px;
}

.plan-subtitle {
  font-size: 26px;
  font-weight: 600;
  color: var(--theme-accent);
  margin: 0;
  line-height: 1.4;
  letter-spacing: 1px;
}

.plan-pricing-info {
  font-size: 16px;
  color: #999;
  margin: 12px 0 0;
  letter-spacing: 0.5px;
}

/* ========================================
   Section blocks
   ======================================== */
.section-block {
  margin: 40px 0 0;
}

.section-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 700;
  color: var(--theme-subtitle);
  margin: 0 0 20px;
  line-height: 1.4;
}

.section-heading-bar {
  display: inline-block;
  width: 4px;
  height: 22px;
  background: var(--theme-accent);
  border-radius: 2px;
  flex-shrink: 0;
}

/* ========================================
   Introduction
   ======================================== */
.introduction-content {
  font-size: 17px;
  color: var(--theme-text);
  line-height: 1.75;
}

.introduction-content :deep(.highlight) {
  font-weight: 700;
  color: var(--theme-highlight);
}

/* ========================================
   Modules – 2-column grid
   ======================================== */
.modules-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.module-card {
  background: var(--theme-card-bg);
  border: 1px solid #EDEBE7;
  border-left: 3px solid var(--theme-accent);
  border-radius: 6px;
  padding: 14px 16px;
  transition: box-shadow 0.2s ease, transform 0.15s ease;
}

.module-card:hover {
  box-shadow: 0 2px 8px rgba(192, 57, 43, 0.08);
  transform: translateY(-1px);
}

.module-card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--theme-subtitle);
  line-height: 1.4;
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.module-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.module-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

.module-item {
  font-size: 13px;
  color: #666666;
  line-height: 1.6;
  padding-left: 12px;
  margin-bottom: 4px;
  position: relative;
}

.module-item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 7px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--theme-dot);
}

.module-item :deep(.highlight) {
  font-weight: 700;
  color: var(--theme-highlight);
}

/* ========================================
   Positions – 2-column grid
   ======================================== */
.position-intro {
  font-size: 16px;
  color: #666;
  margin: 0 0 16px;
  line-height: 1.7;
}

.positions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.position-card {
  background: var(--theme-card-bg);
  border: 1px solid #EDEBE7;
  border-top: 2.5px solid var(--theme-accent);
  border-radius: 6px;
  padding: 14px 16px;
  transition: box-shadow 0.2s ease, transform 0.15s ease;
}

.position-card:hover {
  box-shadow: 0 2px 8px rgba(192, 57, 43, 0.08);
  transform: translateY(-1px);
}

.position-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--theme-subtitle);
  line-height: 1.4;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.position-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.position-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

.position-item {
  font-size: 13px;
  color: #666666;
  line-height: 1.6;
  margin-bottom: 4px;
  padding-left: 12px;
  position: relative;
}

.position-item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 7px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--theme-dot);
}

.position-item :deep(.highlight) {
  font-weight: 700;
  color: var(--theme-highlight);
}

/* ========================================
   Pricing card – red background + gold digits
   ======================================== */
.pricing-card {
  text-align: center;
  margin: 44px auto 0;
  max-width: 360px;
  width: 100%;
  background: var(--theme-pricing-bg);
  border-radius: 8px;
  padding: 24px 28px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.pricing-card::before {
  content: "";
  position: absolute;
  right: -30px;
  top: -30px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
  pointer-events: none;
}

.pricing-card::after {
  content: "";
  position: absolute;
  left: -20px;
  bottom: -20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
  pointer-events: none;
}

.pricing-card-bar {
  width: 40px;
  height: 2px;
  background: #FFD700;
  border-radius: 1px;
  margin: 0 auto 12px;
  opacity: 0.7;
}

.pricing-card-label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.65);
  letter-spacing: 0.18em;
  margin-bottom: 10px;
}

.pricing-card-price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 2px;
}

.pricing-card-symbol {
  font-size: 22px;
  font-weight: 500;
  color: #FFD700;
  line-height: 1;
  opacity: 0.9;
}

.pricing-card-number {
  font-size: 48px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.02em;
  background: var(--theme-pricing-number);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ========================================
   Deliverables
   ======================================== */
.deliverables-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.deliverable-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px 5px 8px;
  background: #F5F3EF;
  border: 1px solid #DDD8D0;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  color: #444;
  transition: all 0.2s ease;
  cursor: default;
}

.deliverable-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06);
}

.deliverable-chip svg {
  flex-shrink: 0;
}

/* ========================================
   LLM warning banner
   ======================================== */
.llm-warning-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 32px 0 0;
  padding: 14px 20px;
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.9), rgba(254, 240, 138, 0.5));
  border: 1px solid rgba(234, 179, 8, 0.3);
  border-radius: 12px;
  font-size: 14px;
  color: #92400e;
  line-height: 1.5;
}

.llm-warning-banner svg {
  flex-shrink: 0;
  color: #d97706;
}

/* ========================================
   AI note
   ======================================== */
.ai-note {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 32px;
  padding: 0;
  font-size: 13px;
  color: #999;
}

/* ========================================
   Responsive: mobile (<768px)
   ======================================== */
@media (max-width: 767px) {
  .main-content {
    padding: 16px 16px 48px !important;
  }

  .content-card {
    padding: 24px 16px !important;
    border-radius: 12px !important;
  }

  .plan-title {
    font-size: 28px;
  }

  .plan-subtitle {
    font-size: 20px;
  }

  .plan-pricing-info {
    font-size: 14px;
  }

  .section-heading {
    font-size: 19px;
  }

  .introduction-content {
    font-size: 15px;
  }

  .modules-grid {
    grid-template-columns: 1fr !important;
    gap: 10px;
  }

  .module-card {
    padding: 12px 14px;
  }

  .module-card-title {
    font-size: 14px;
  }

  .positions-grid {
    grid-template-columns: 1fr !important;
    gap: 10px;
  }

  .position-card {
    padding: 12px 14px;
  }

  .position-intro {
    font-size: 15px;
  }

  .position-name {
    font-size: 14px;
  }

  .position-item {
    font-size: 13px;
  }

  .deliverable-chip {
    font-size: 13px;
  }

  .llm-warning-banner {
    font-size: 13px;
  }

  .ai-note {
    font-size: 12px;
  }

  .pricing-card {
    max-width: 100%;
    padding: 20px 22px;
  }

  .pricing-card-number {
    font-size: 36px;
  }

  .pricing-card-symbol {
    font-size: 18px;
  }

  .pricing-card-label {
    font-size: 11px;
  }

  .bottom-bar-inner {
    padding-left: 20px !important;
    padding-right: 20px !important;
  }
}

/* ========================================
   Print styles
   ======================================== */
@media print {
  .bottom-bar {
    display: none !important;
  }
  .main-content {
    padding: 0 !important;
    max-width: 100% !important;
  }
  .content-card {
    box-shadow: none !important;
    border: none !important;
    max-width: 100% !important;
    padding: 40px !important;
    break-inside: avoid;
  }
  .module-card,
  .position-card {
    break-inside: avoid;
  }
  .result-page {
    background: white !important;
  }
}
</style>

<style>
/* ========================================
   Custom Scrollbar (global — targets viewport
   and .result-page via non-scoped selectors)
   ======================================== */
html,
.result-page {
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.35) transparent;
}

html::-webkit-scrollbar,
.result-page::-webkit-scrollbar {
  width: 7px;
  height: 7px;
}

html::-webkit-scrollbar-track,
.result-page::-webkit-scrollbar-track {
  background: transparent;
}

html::-webkit-scrollbar-thumb,
.result-page::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.35);
  border-radius: 9999px;
  border: 1px solid transparent;
  background-clip: content-box;
  transition: background 0.2s ease;
}

html::-webkit-scrollbar-thumb:hover,
.result-page::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 102, 241, 0.45);
  background-clip: content-box;
  border: 1px solid transparent;
}

html::-webkit-scrollbar-corner,
.result-page::-webkit-scrollbar-corner {
  background: transparent;
}

/* Print: hide scrollbar */
@media print {
  html,
  .result-page {
    scrollbar-width: none !important;
  }
  html::-webkit-scrollbar,
  .result-page::-webkit-scrollbar {
    display: none !important;
  }
}
</style>
