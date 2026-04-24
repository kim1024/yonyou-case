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
  'PPT': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>',
  '视频': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5,3 19,12 5,21"/></svg>',
  '指导书': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>',
  '数据集': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
  '代码包': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
  '实操环境': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
}

// ---------- Print ----------

function handlePrint() {
  window.print()
}
</script>

<template>
  <div class="result-page min-h-screen" style="background:var(--color-neutral-100)">
    <main class="main-content" style="padding:48px 48px 72px">
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
        style="background:var(--color-neutral-0);border-radius:16px;padding:80px 56px;margin:0 auto;box-shadow:var(--shadow-float);max-width:960px;text-align:center"
      >
        <p style="font-size:16px;color:var(--color-neutral-400)">暂无方案数据，请重新定制</p>
      </div>

      <!-- Course plan content -->
      <div v-else class="content-card" style="background:var(--color-neutral-0);border-radius:16px;padding:56px;margin:0 auto;box-shadow:var(--shadow-float);max-width:960px">

        <!-- ===== Title area ===== -->
        <div style="text-align:center;padding-bottom:20px;border-bottom:2px solid var(--color-primary-300);margin-bottom:4px">
          <h1 style="font-size:38px;font-weight:800;color:#DC2626;margin:0 0 8px;line-height:1.3;letter-spacing:0.5px">{{ plan.title }}</h1>
          <p style="font-size:24px;font-weight:800;color:#DC2626;margin:0;padding-bottom:16px;border-bottom:2px solid var(--color-primary-300);line-height:1.3;letter-spacing:0.5px">{{ plan.subtitle }}</p>
        </div>

        <!-- ===== Introduction ===== -->
        <div style="margin:36px 0;padding:20px 24px;border-left:3px solid var(--color-primary-500);background:rgba(99,102,241,0.04);border-radius:0 8px 8px 0">
          <p style="font-size:15px;color:var(--color-neutral-700);line-height:1.75;margin:0">{{ plan.introduction }}</p>
        </div>

        <!-- ===== Course modules ===== -->
        <div v-if="plan.modules.length" style="position:relative;margin:36px 0 0">
          <div class="modules-decor-circle" />
          <h2 style="font-size:22px;font-weight:700;color:var(--color-neutral-900);margin-bottom:20px;padding:10px 18px;border-left:3px solid var(--color-primary-500);background:rgba(99,102,241,0.05);border-radius:0 6px 6px 0;line-height:1.4">课程模块</h2>
          <div class="modules-grid">
            <div
              v-for="(mod, i) in plan.modules"
              :key="i"
              class="module-card"
            >
              <div class="module-card-header">
                <h3 class="module-card-title">{{ mod.name }}</h3>
                <span class="module-card-hours">{{ mod.hours }} 课时</span>
              </div>
              <ul class="module-items">
                <li v-for="(item, j) in mod.items" :key="j" class="module-item">
                  <span class="module-item-dot" />
                  <span>{{ item }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- ===== Positions ===== -->
        <div v-if="plan.positions.length" style="margin:40px 0 0">
          <h2 style="font-size:22px;font-weight:700;color:var(--color-neutral-900);margin-bottom:20px;padding:10px 18px;border-left:3px solid var(--color-primary-500);background:rgba(99,102,241,0.05);border-radius:0 6px 6px 0;line-height:1.4">可胜任岗位</h2>
          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:16px">
            <div
              v-for="(pos, i) in plan.positions"
              :key="i"
              style="background:var(--color-neutral-0);border:1px solid var(--color-neutral-200);border-radius:12px;padding:20px 22px;transition:border-color 0.2s,box-shadow 0.2s"
              class="position-card"
            >
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                <span style="display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:8px;background:var(--color-primary-50);color:var(--color-primary-600);font-size:12px;font-weight:700;flex-shrink:0">{{ i + 1 }}</span>
                <span style="font-weight:600;color:var(--color-neutral-800);font-size:15px">{{ pos.title }}</span>
              </div>
              <ul style="list-style:none;padding:0;margin:0">
                <li v-for="(desc, j) in pos.description" :key="j" style="display:flex;align-items:flex-start;gap:8px;padding:3px 0;font-size:14px;color:var(--color-neutral-600);line-height:1.7">
                  <span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:var(--color-neutral-300);margin-top:8px;flex-shrink:0" />
                  <span>{{ desc }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- ===== Pricing card ===== -->
        <div class="pricing-card">
          <div class="pricing-card-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.5"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
            课程最终报价
          </div>
          <div class="pricing-card-price">¥{{ formattedPrice }}</div>
          <div class="pricing-card-info">
            {{ plan.pricing.hour }} 课时 × {{ plan.pricing.unit_price.toLocaleString('zh-CN') }} 元/课时
          </div>

          <!-- Deliverables -->
          <div v-if="plan.deliverables.length" class="deliverables-grid">
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
    <footer class="bottom-bar" style="position:sticky;bottom:0;z-40;background:rgba(255,255,255,0.88);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-top:1px solid var(--color-neutral-200)">
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
   Modules
   ======================================== */
.modules-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px;
}

.module-card {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-left: 3px solid var(--color-primary-500);
  border-radius: 12px;
  padding: 20px 22px 18px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.module-card:hover {
  border-color: var(--color-primary-300);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.modules-decor-circle {
  position: absolute;
  top: 36px;
  right: -44px;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.05), transparent 70%);
  pointer-events: none;
}

.module-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 14px;
}

.module-card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-neutral-800);
  margin: 0;
  line-height: 1.5;
}

.module-card-hours {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  background: rgba(99, 102, 241, 0.08);
  color: var(--color-primary-600);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.module-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

.module-item {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  padding: 5px 0;
  font-size: 14px;
  color: var(--color-neutral-700);
  line-height: 1.7;
}

.module-item-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #818cf8;
  margin-top: 9px;
  flex-shrink: 0;
}

/* ========================================
   Position cards
   ======================================== */
.position-card:hover {
  border-color: var(--color-primary-300);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

/* ========================================
   Pricing card
   ======================================== */
.pricing-card {
  text-align: center;
  margin: 40px 0 0;
  padding: 36px 32px 28px;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.06), rgba(255, 193, 37, 0.03));
  border-radius: 20px;
  border: 1px solid rgba(212, 175, 55, 0.2);
}

.pricing-card-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 600;
  color: #888;
  letter-spacing: 2px;
  margin-bottom: 16px;
}

.pricing-card-price {
  font-size: 56px;
  font-weight: 800;
  color: #D4A017;
  letter-spacing: -1px;
  text-shadow: 0 2px 4px rgba(212, 160, 23, 0.15);
  line-height: 1.1;
}

.pricing-card-info {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(212, 175, 55, 0.12);
  font-size: 15px;
  color: var(--color-neutral-600);
}

/* ========================================
   Deliverables
   ======================================== */
.deliverables-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(212, 175, 55, 0.12);
}

.deliverable-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 15px;
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: 24px;
  font-size: 13px;
  color: var(--color-neutral-700);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.deliverable-chip:hover {
  border-color: var(--color-primary-300);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.06);
}

/* ========================================
   LLM warning banner
   ======================================== */
.llm-warning-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 960px;
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
  margin-top: 28px;
  padding: 0;
  font-size: 12px;
  color: #999;
}

/* ========================================
   Responsive: tablet
   ======================================== */
@media (max-width: 1023px) and (min-width: 768px) {
  .bottom-bar-inner {
    padding-left: 32px !important;
    padding-right: 32px !important;
  }
  .main-content {
    padding-left: 32px !important;
    padding-right: 32px !important;
  }
  .content-card {
    padding: 40px 36px !important;
  }
}

/* ========================================
   Responsive: mobile
   ======================================== */
@media (max-width: 767px) {
  .bottom-bar-inner {
    padding-left: 20px !important;
    padding-right: 20px !important;
  }
  .main-content {
    padding: 20px !important;
  }
  .content-card {
    padding: 28px 20px !important;
    border-radius: 12px !important;
  }

  .modules-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .pricing-card-price {
    font-size: 42px;
  }

  .module-card-header {
    flex-direction: column;
    gap: 6px;
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
    border: 1px solid #e5e5ea !important;
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
