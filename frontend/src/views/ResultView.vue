<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { RotateCcw, Printer, AlertTriangle } from 'lucide-vue-next'

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

// ---------- Router ----------

const router = useRouter()
const route = useRoute()

// ---------- Data ----------

const source = computed(() => (route.query.source as string) || sessionStorage.getItem('resultSource') || 'template')

const isTemplateFallback = computed(() => source.value === 'template')

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
  'PPT': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>',
  '视频': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5,3 19,12 5,21"/></svg>',
  '指导书': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>',
  '数据集': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
  '代码包': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
  '实操环境': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
}

// ---------- Print ----------

function handlePrint() {
  window.print()
}
</script>

<template>
  <div class="result-page" style="min-height:100vh;background:#F8F7F4">
    <main class="main-content" style="padding:48px 48px 80px">
      <!-- LLM fallback warning -->
      <div
        v-if="isTemplateFallback && plan"
        class="llm-warning-banner"
      >
        <AlertTriangle :size="16" :stroke-width="2" />
        <span>当前方案由模板生成（大模型不可用）。如需 AI 生成的方案，请在后台检查大模型配置（API Key、Base URL）。</span>
      </div>

      <!-- Empty state -->
      <div
        v-if="!plan"
        class="content-card"
        style="background:#FFFFFF;border-radius:16px;padding:80px 56px;margin:0 auto;max-width:1080px;text-align:center"
      >
        <p style="font-size:16px;color:#888">暂无方案数据，请重新定制</p>
      </div>

      <!-- Course plan content -->
      <div v-else class="content-card" style="background:#FFFFFF;border-radius:16px;padding:56px;margin:0 auto;max-width:1080px">

        <!-- ===== Title area ===== -->
        <div style="text-align:center;padding-bottom:24px;border-bottom:2px solid #E8E5DF;margin-bottom:0">
          <h1 class="plan-title">{{ plan.title }}</h1>
          <p class="plan-subtitle">{{ plan.subtitle }}</p>
          <p class="plan-pricing-info">{{ plan.pricing.hour }}课时  ·  课程报价 ¥{{ formattedPrice }}元</p>
        </div>

        <!-- ===== Introduction ===== -->
        <div v-if="plan.introduction" class="section-block">
          <h2 class="section-heading"><span class="section-heading-bar" />一、总体介绍</h2>
          <div class="introduction-content" v-html="plan.introduction" />
        </div>

        <!-- ===== Course modules ===== -->
        <div v-if="plan.modules.length" class="section-block">
          <h2 class="section-heading"><span class="section-heading-bar" />二、案例课程主要结构</h2>
          <div class="modules-list">
            <div
              v-for="(mod, i) in plan.modules"
              :key="i"
              class="module-card"
            >
              <h3 class="module-card-title">{{ mod.name }}</h3>
              <ul class="module-items">
                <li v-for="(item, j) in mod.items" :key="j" class="module-item">
                  <span class="module-item-dot">·</span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- ===== Positions ===== -->
        <div v-if="plan.positions.length" class="section-block">
          <h2 class="section-heading"><span class="section-heading-bar" />三、学习后胜任的岗位</h2>
          <p class="position-intro">结合相关行业与专业，学员毕业后可胜任以下岗位：</p>
          <div class="positions-list">
            <div
              v-for="(pos, i) in plan.positions"
              :key="i"
              class="position-card"
            >
              <div class="position-card-header">
                <span class="position-color-block" />
                <span class="position-name">{{ pos.title }}</span>
              </div>
              <ul v-if="pos.description.length" class="position-items">
                <li v-for="(desc, j) in pos.description" :key="j" class="position-item">
                  <span class="position-item-dot">·</span>
                  <span>{{ desc }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- ===== Pricing card ===== -->
        <div class="pricing-card">
          <div class="pricing-card-label">课程报价</div>
          <div class="pricing-card-price">¥{{ formattedPrice }}</div>
          <div class="pricing-card-info">
            {{ plan.pricing.hour }}课时 × {{ plan.pricing.unit_price.toLocaleString('zh-CN') }}元/课时
          </div>
        </div>

        <!-- ===== Deliverables ===== -->
        <div v-if="plan.deliverables.length" class="section-block">
          <h2 class="section-heading"><span class="section-heading-bar" />四、课程成果物</h2>
          <div class="deliverables-grid">
            <div v-for="(item, i) in plan.deliverables" :key="i" class="deliverable-chip">
              <span v-html="deliverableIcons[item] || ''" />
              <span>{{ item }}</span>
            </div>
          </div>
        </div>

        <!-- ===== AI note ===== -->
        <div class="ai-note">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 1 4 4v1a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/><path d="M16 14h.01"/><path d="M8 14h.01"/><path d="M12 18v4"/><path d="M9 22h6"/></svg>
          <span>{{ plan.notes }}</span>
        </div>

      </div>
    </main>

    <!-- Bottom action bar -->
    <footer class="bottom-bar" style="position:sticky;bottom:0;z-40;background:rgba(255,255,255,0.88);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-top:1px solid #E8E5DF">
      <div class="bottom-bar-inner max-w-4xl mx-auto flex items-center justify-center gap-3" style="padding:16px 48px">
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
  font-size: 32px;
  font-weight: 700;
  color: #C0392B;
  margin: 0 0 6px;
  line-height: 1.4;
  letter-spacing: 2px;
}

.plan-subtitle {
  font-size: 22px;
  font-weight: 600;
  color: #C0392B;
  margin: 0;
  line-height: 1.4;
  letter-spacing: 1px;
}

.plan-pricing-info {
  font-size: 15px;
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
  font-size: 20px;
  font-weight: 700;
  color: #2D2D2D;
  margin: 0 0 20px;
  line-height: 1.5;
}

.section-heading-bar {
  display: inline-block;
  width: 4px;
  height: 22px;
  background: #C0392B;
  border-radius: 2px;
  flex-shrink: 0;
}

/* ========================================
   Introduction
   ======================================== */
.introduction-content {
  font-size: 16px;
  color: #444444;
  line-height: 1.8;
}

.introduction-content :deep(.highlight) {
  font-weight: 700;
  color: #C0392B;
}

/* ========================================
   Modules – single column
   ======================================== */
.modules-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.module-card {
  background: #FAFAF8;
  border: 1px solid #EDEBE7;
  border-left: 3px solid #C0392B;
  border-radius: 8px;
  padding: 20px 24px 18px;
}

.module-card-title {
  font-size: 17px;
  font-weight: 700;
  color: #2D2D2D;
  margin: 0 0 12px;
  line-height: 1.5;
}

.module-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

.module-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 4px 0 4px 24px;
  font-size: 15px;
  color: #444;
  line-height: 1.7;
}

.module-item-dot {
  color: #C0392B;
  font-weight: 700;
  font-size: 16px;
  line-height: 1.7;
  flex-shrink: 0;
}

/* ========================================
   Positions – single column
   ======================================== */
.position-intro {
  font-size: 15px;
  color: #666;
  margin: 0 0 16px;
  line-height: 1.7;
}

.positions-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.position-card {
  background: #FFFFFF;
  border: 1px solid #EDEBE7;
  border-radius: 8px;
  padding: 20px 24px 18px;
}

.position-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.position-color-block {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 2px;
  background: #C0392B;
  flex-shrink: 0;
}

.position-name {
  font-size: 16px;
  font-weight: 600;
  color: #2D2D2D;
}

.position-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

.position-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 3px 0 3px 24px;
  font-size: 15px;
  color: #444;
  line-height: 1.7;
}

.position-item-dot {
  color: #C0392B;
  font-weight: 700;
  font-size: 16px;
  line-height: 1.7;
  flex-shrink: 0;
}

/* ========================================
   Pricing card – dark theme
   ======================================== */
.pricing-card {
  text-align: center;
  margin: 44px auto 0;
  padding: 40px 32px 32px;
  background: linear-gradient(135deg, #2D2D2D, #3D3D3D);
  border-radius: 12px;
  max-width: 480px;
}

.pricing-card-label {
  font-size: 14px;
  font-weight: 500;
  color: #AAAAAA;
  letter-spacing: 3px;
  margin-bottom: 12px;
}

.pricing-card-price {
  font-size: 42px;
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: -1px;
  line-height: 1.1;
}

.pricing-card-info {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 15px;
  color: #999999;
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
  gap: 6px;
  padding: 7px 15px;
  background: #F5F3EF;
  border: 1px solid #DDD8D0;
  border-radius: 20px;
  font-size: 13px;
  color: #444;
}

/* ========================================
   LLM warning banner
   ======================================== */
.llm-warning-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 1080px;
  margin: 0 auto 20px;
  padding: 14px 20px;
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.9), rgba(254, 240, 138, 0.5));
  border: 1px solid rgba(234, 179, 8, 0.3);
  border-radius: 12px;
  font-size: 13px;
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
  font-size: 12px;
  color: #999;
}

/* ========================================
   Responsive: mobile (<768px)
   ======================================== */
@media (max-width: 767px) {
  .main-content {
    padding: 20px 20px 60px !important;
  }

  .content-card {
    padding: 28px 20px !important;
    border-radius: 12px !important;
  }

  .plan-title {
    font-size: 24px;
  }

  .plan-subtitle {
    font-size: 18px;
  }

  .plan-pricing-info {
    font-size: 14px;
  }

  .section-heading {
    font-size: 17px;
  }

  .introduction-content {
    font-size: 15px;
  }

  .module-card-title {
    font-size: 15px;
  }

  .module-item {
    font-size: 14px;
  }

  .position-item {
    font-size: 14px;
  }

  .pricing-card-price {
    font-size: 32px;
  }

  .pricing-card {
    padding: 32px 20px 24px;
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
