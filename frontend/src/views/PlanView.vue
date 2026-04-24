<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { FileStack, Search, Inbox, Eye, Trash2, ChevronLeft, ChevronRight, Sparkles, FileText, AlertTriangle, X, Clock, GraduationCap, Building2, MapPin, BookOpen, DollarSign, RotateCcw } from 'lucide-vue-next'
import { adminApi } from '@/api/admin'
import type { GeneratedPlanListItem, GeneratedPlan, CoursePlan, PlanListParams } from '@/types'

/* ── 列表数据 ── */
const items = ref<GeneratedPlanListItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)

/* ── 筛选 ── */
const filterSource = ref<'' | 'ai' | 'template'>('')
const filterKeyword = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
let debounceTimer: ReturnType<typeof setTimeout> | null = null

/* ── 类型下拉 ── */
const showTypeDropdown = ref(false)
const typeDropdownRef = ref<HTMLDivElement | null>(null)
const typeLabel = computed(() => {
  if (filterSource.value === 'ai') return 'AI'
  if (filterSource.value === 'template') return '模板'
  return '全部'
})

function selectType(val: '' | 'ai' | 'template') {
  filterSource.value = val
  showTypeDropdown.value = false
  resetToFirst()
}

function handleClickOutsideType(e: MouseEvent) {
  if (typeDropdownRef.value && !typeDropdownRef.value.contains(e.target as Node)) {
    showTypeDropdown.value = false
  }
}

/* ── 详情弹窗 ── */
const showDetail = ref(false)
const detailItem = ref<GeneratedPlan | null>(null)
const detailLoading = ref(false)

/* ── 删除弹窗 ── */
const showDeleteConfirm = ref(false)
const deleteItem = ref<GeneratedPlanListItem | null>(null)
const deleting = ref(false)

/* ── 筛选逻辑 ── */
function resetToFirst() {
  page.value = 1
  loadData()
}

function handleSearchDebounce() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    resetToFirst()
  }, 300)
}

function handleResetFilters() {
  filterSource.value = ''
  filterKeyword.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  resetToFirst()
}

/* ── 加载数据 ── */
async function loadData() {
  loading.value = true
  try {
    const params: PlanListParams = {
      page: page.value,
      page_size: pageSize,
    }
    if (filterSource.value) params.source = filterSource.value
    if (filterKeyword.value.trim()) params.keyword = filterKeyword.value.trim()
    if (filterDateFrom.value) params.date_from = filterDateFrom.value
    if (filterDateTo.value) params.date_to = filterDateTo.value

    const res = await adminApi.getPlans(params)
    items.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

/* ── 详情 ── */
async function handleViewDetail(item: GeneratedPlanListItem) {
  detailItem.value = null
  showDetail.value = true
  detailLoading.value = true
  try {
    const res = await adminApi.getPlanDetail(item.id)
    detailItem.value = res.data
  } catch {
    showDetail.value = false
  } finally {
    detailLoading.value = false
  }
}

function closeDetail() {
  showDetail.value = false
  detailItem.value = null
}

/* ── 删除 ── */
function handleOpenDelete(item: GeneratedPlanListItem) {
  deleteItem.value = item
  showDeleteConfirm.value = true
}

async function handleConfirmDelete() {
  if (!deleteItem.value) return
  deleting.value = true
  try {
    await adminApi.deletePlan(deleteItem.value.id)
    showDeleteConfirm.value = false
    deleteItem.value = null
    loadData()
  } catch {
    /* silently fail */
  } finally {
    deleting.value = false
  }
}

function closeDeleteConfirm() {
  showDeleteConfirm.value = false
  deleteItem.value = null
}

/* ── 弹窗 backdrop ── */
function handleDetailBackdrop(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('ef-overlay')) {
    closeDetail()
  }
}

function handleDeleteBackdrop(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('ef-overlay')) {
    closeDeleteConfirm()
  }
}

/* ── 日期格式化 ── */
function fmtDate(iso: string): string {
  if (!iso) return '-'
  const d = new Date(iso)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}`
}

/* ── 价格格式化 ── */
function fmtPrice(n: number): string {
  return n.toLocaleString('zh-CN')
}

/* ── 生命周期 ── */
onMounted(() => {
  loadData()
  document.addEventListener('mousedown', handleClickOutsideType)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutsideType)
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<template>
  <div class="animate-fade-up">
    <!-- 标题栏 -->
    <div class="page-header flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-xl flex items-center justify-center"
          style="background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);"
        >
          <FileStack :size="20" color="#fff" :stroke-width="1.8" />
        </div>
        <div>
          <h1>方案生成管理</h1>
          <p>查看和管理所有课程方案的生成记录</p>
        </div>
      </div>
      <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 text-indigo-600 text-xs font-semibold">
        <span>共 {{ total }} 条记录</span>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="flex items-center gap-3 mb-6 flex-wrap">
      <!-- 类型下拉 -->
      <div ref="typeDropdownRef" class="relative">
        <button
          class="btn-secondary min-w-[90px] justify-between"
          @click="showTypeDropdown = !showTypeDropdown"
        >
          <span>{{ typeLabel }}</span>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" class="ml-1">
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <div
          v-if="showTypeDropdown"
          class="absolute top-full left-0 mt-1 w-32 bg-white border border-neutral-200 rounded-lg shadow-lg z-10 overflow-hidden"
        >
          <button class="w-full text-left px-3 py-2 text-sm hover:bg-neutral-50 transition-colors" :class="filterSource === '' ? 'text-primary-600 font-medium bg-primary-50/50' : 'text-neutral-700'" @click="selectType('')">全部</button>
          <button class="w-full text-left px-3 py-2 text-sm hover:bg-neutral-50 transition-colors flex items-center gap-1.5" :class="filterSource === 'ai' ? 'text-primary-600 font-medium bg-primary-50/50' : 'text-neutral-700'" @click="selectType('ai')">
            <Sparkles :size="13" class="text-indigo-500" />
            AI
          </button>
          <button class="w-full text-left px-3 py-2 text-sm hover:bg-neutral-50 transition-colors flex items-center gap-1.5" :class="filterSource === 'template' ? 'text-primary-600 font-medium bg-primary-50/50' : 'text-neutral-700'" @click="selectType('template')">
            <FileText :size="13" class="text-amber-500" />
            模板
          </button>
        </div>
      </div>

      <!-- 日期范围 -->
      <input v-model="filterDateFrom" type="date" class="input-macos w-[150px]" placeholder="开始日期" @change="resetToFirst" />
      <span class="text-neutral-400 text-xs">至</span>
      <input v-model="filterDateTo" type="date" class="input-macos w-[150px]" placeholder="结束日期" @change="resetToFirst" />

      <!-- 关键词搜索 -->
      <div class="relative">
        <input
          v-model="filterKeyword"
          type="text"
          placeholder="搜索专业、行业、方案名称"
          class="input-macos w-60 pl-8"
          @input="handleSearchDebounce"
          @keyup.enter="resetToFirst"
        />
        <Search :size="14" class="absolute left-2.5 top-1/2 -translate-y-1/2 text-neutral-400 pointer-events-none" />
      </div>

      <!-- 重置 -->
      <button class="btn-ghost text-neutral-500" @click="handleResetFilters">
        <RotateCcw :size="14" />
        重置
      </button>
    </div>

    <!-- 表格 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-neutral-50">
          <tr class="border-b border-neutral-200">
            <th class="px-4 py-3 text-left text-neutral-500 font-medium" style="width:160px">生成时间</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium" style="width:100px">类型</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium" style="width:130px">专业</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium" style="width:130px">行业</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium" style="width:110px">省份</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">方案名称</th>
            <th class="px-4 py-3 text-center text-neutral-500 font-medium" style="width:110px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in items"
            :key="item.id"
            class="border-t border-neutral-100 transition-colors duration-100 group"
            :class="index % 2 === 1 ? 'bg-neutral-50/50' : ''"
          >
            <td class="px-4 py-3 text-neutral-500 text-xs font-mono">{{ fmtDate(item.created_at) }}</td>
            <td class="px-4 py-3">
              <span
                v-if="item.source === 'ai'"
                class="inline-flex items-center gap-1 bg-indigo-50 text-indigo-700 rounded-full px-2.5 py-1 text-xs font-medium"
              >
                <Sparkles :size="12" />
                AI
              </span>
              <span
                v-else
                class="inline-flex items-center gap-1 bg-amber-50 text-amber-700 rounded-full px-2.5 py-1 text-xs font-medium"
              >
                <FileText :size="12" />
                模板
              </span>
            </td>
            <td class="px-4 py-3 text-neutral-700 font-medium truncate max-w-[130px]" :title="item.major">{{ item.major }}</td>
            <td class="px-4 py-3 text-neutral-500 truncate max-w-[130px]" :title="item.industry">{{ item.industry }}</td>
            <td class="px-4 py-3 text-neutral-500 truncate max-w-[110px]" :title="item.province">{{ item.province }}</td>
            <td class="px-4 py-3 text-neutral-700 truncate" :title="item.plan_title">{{ item.plan_title }}</td>
            <td class="px-4 py-3 text-center">
              <div class="inline-flex items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                <button class="btn-ghost text-primary-500 !px-1.5 !py-1.5" title="查看详情" @click="handleViewDetail(item)">
                  <Eye :size="14" />
                </button>
                <button class="btn-ghost text-danger !px-1.5 !py-1.5" title="删除" @click="handleOpenDelete(item)">
                  <Trash2 :size="14" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="7" class="px-4 py-16 text-center">
              <div class="flex flex-col items-center gap-3 text-neutral-400">
                <Inbox :size="40" :stroke-width="1.2" />
                <span class="text-sm">{{ loading ? '加载中...' : '暂无方案记录' }}</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="mt-4 flex items-center justify-between text-sm text-neutral-500">
      <span>共 <span class="font-medium text-neutral-700">{{ total }}</span> 条</span>
      <div class="flex items-center gap-1">
        <button :disabled="page <= 1" class="btn-ghost" @click="page--; loadData()">
          <ChevronLeft :size="16" />
          上一页
        </button>
        <span class="px-3 py-1 text-neutral-600">第 {{ page }} 页</span>
        <button :disabled="page * pageSize >= total" class="btn-ghost" @click="page++; loadData()">
          下一页
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <Teleport to="body">
      <div v-if="showDetail" class="ef-overlay" @click="handleDetailBackdrop">
        <div class="ef-dialog ef-dialog--detail">
          <!-- 固定头部 -->
          <div class="ef-header">
            <div class="flex items-center gap-3 min-w-0">
              <h2 class="ef-title truncate">{{ detailItem?.plan_title || '方案详情' }}</h2>
              <span class="text-xs text-neutral-400 flex-shrink-0">{{ detailItem ? fmtDate(detailItem.created_at) : '' }}</span>
            </div>
            <button class="ef-close-btn" @click="closeDetail" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>

          <!-- 可滚动内容 -->
          <div class="ef-body">
            <!-- 加载态 -->
            <div v-if="detailLoading" class="flex items-center justify-center py-12 text-neutral-400">
              <span class="text-sm">加载中...</span>
            </div>

            <template v-else-if="detailItem">
              <!-- 生成参数 -->
              <div class="grid grid-cols-3 gap-3">
                <div class="param-cell">
                  <div class="param-icon bg-indigo-50 text-indigo-500"><GraduationCap :size="14" /></div>
                  <div class="param-text">
                    <span class="param-label">专业</span>
                    <span class="param-value">{{ detailItem.major }}</span>
                  </div>
                </div>
                <div class="param-cell">
                  <div class="param-icon bg-emerald-50 text-emerald-500"><Building2 :size="14" /></div>
                  <div class="param-text">
                    <span class="param-label">行业</span>
                    <span class="param-value">{{ detailItem.industry }}</span>
                  </div>
                </div>
                <div class="param-cell">
                  <div class="param-icon bg-violet-50 text-violet-500"><Building2 :size="14" /></div>
                  <div class="param-text">
                    <span class="param-label">企业</span>
                    <span class="param-value">{{ detailItem.enterprise }}</span>
                  </div>
                </div>
                <div class="param-cell">
                  <div class="param-icon bg-sky-50 text-sky-500"><MapPin :size="14" /></div>
                  <div class="param-text">
                    <span class="param-label">省份</span>
                    <span class="param-value">{{ detailItem.province }}</span>
                  </div>
                </div>
                <div class="param-cell">
                  <div class="param-icon bg-amber-50 text-amber-500"><Clock :size="14" /></div>
                  <div class="param-text">
                    <span class="param-label">课时</span>
                    <span class="param-value">{{ detailItem.hour }} 课时</span>
                  </div>
                </div>
                <div class="param-cell">
                  <div class="param-icon bg-rose-50 text-rose-500">
                    <Sparkles v-if="detailItem.source === 'ai'" :size="14" />
                    <FileText v-else :size="14" />
                  </div>
                  <div class="param-text">
                    <span class="param-label">来源</span>
                    <span class="param-value">{{ detailItem.source === 'ai' ? 'AI 生成' : '模板生成' }}</span>
                  </div>
                </div>
              </div>

              <!-- 方案内容（来自 plan_data） -->
              <template v-if="detailItem.plan_data">
                <div class="mt-1 border-t border-neutral-100 pt-5">
                  <!-- 标题 + 副标题 -->
                  <div class="mb-4">
                    <h3 class="text-lg font-bold text-neutral-900" style="font-family: var(--font-display);">{{ detailItem.plan_data.title }}</h3>
                    <p class="text-sm text-neutral-500 mt-1">{{ detailItem.plan_data.subtitle }}</p>
                  </div>

                  <!-- 课程介绍 -->
                  <div v-if="detailItem.plan_data.introduction" class="mb-5">
                    <h4 class="section-title">
                      <BookOpen :size="14" />
                      课程介绍
                    </h4>
                    <div class="bg-gray-50/80 rounded-lg p-4 text-sm text-neutral-700 leading-relaxed intro-content" v-html="detailItem.plan_data.introduction" />
                  </div>

                  <!-- 课程模块 -->
                  <div v-if="detailItem.plan_data.modules?.length" class="mb-5">
                    <h4 class="section-title">
                      <BookOpen :size="14" />
                      课程模块
                    </h4>
                    <div class="space-y-3">
                      <div v-for="(mod, mi) in detailItem.plan_data.modules" :key="mi" class="bg-white border border-neutral-100 rounded-lg p-4 shadow-sm">
                        <div class="flex items-center justify-between mb-2">
                          <span class="font-semibold text-neutral-800 text-sm">{{ mod.name }}</span>
                          <span class="text-xs text-neutral-400 bg-neutral-100 rounded-full px-2 py-0.5">{{ mod.hours }} 课时</span>
                        </div>
                        <ul class="space-y-1">
                          <li v-for="(item, ii) in mod.items" :key="ii" class="text-sm text-neutral-600 flex items-start gap-2">
                            <span class="w-1 h-1 rounded-full bg-primary-400 mt-2 flex-shrink-0" />
                            {{ item }}
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <!-- 培养岗位 -->
                  <div v-if="detailItem.plan_data.positions?.length" class="mb-5">
                    <h4 class="section-title">
                      <GraduationCap :size="14" />
                      培养岗位
                    </h4>
                    <div class="space-y-3">
                      <div v-for="(pos, pi) in detailItem.plan_data.positions" :key="pi" class="bg-white border border-neutral-100 rounded-lg p-4 shadow-sm">
                        <span class="font-semibold text-neutral-800 text-sm block mb-2">{{ pos.title }}</span>
                        <ul class="space-y-1">
                          <li v-for="(desc, di) in pos.description" :key="di" class="text-sm text-neutral-600 flex items-start gap-2">
                            <span class="w-1 h-1 rounded-full bg-emerald-400 mt-2 flex-shrink-0" />
                            {{ desc }}
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <!-- 交付物 -->
                  <div v-if="detailItem.plan_data.deliverables?.length" class="mb-5">
                    <h4 class="section-title">
                      <FileText :size="14" />
                      交付物
                    </h4>
                    <div class="grid grid-cols-2 gap-2">
                      <div
                        v-for="(d, di) in detailItem.plan_data.deliverables"
                        :key="di"
                        class="flex items-center gap-2 bg-amber-50 text-amber-700 rounded-lg px-3 py-2 text-sm font-medium"
                      >
                        <FileText :size="13" />
                        {{ d }}
                      </div>
                    </div>
                  </div>

                  <!-- 价格信息 -->
                  <div v-if="detailItem.plan_data.pricing" class="mb-2">
                    <h4 class="section-title">
                      <DollarSign :size="14" />
                      价格信息
                    </h4>
                    <div class="bg-rose-50 border border-rose-100 rounded-lg p-4 flex items-center gap-6">
                      <div class="text-center">
                        <span class="text-xs text-rose-400 block mb-0.5">课时</span>
                        <span class="text-lg font-bold text-rose-700">{{ detailItem.plan_data.pricing.hour }}</span>
                      </div>
                      <div class="w-px h-8 bg-rose-200" />
                      <div class="text-center">
                        <span class="text-xs text-rose-400 block mb-0.5">单价（元/课时）</span>
                        <span class="text-lg font-bold text-rose-700">¥{{ fmtPrice(detailItem.plan_data.pricing.unit_price) }}</span>
                      </div>
                      <div class="w-px h-8 bg-rose-200" />
                      <div class="text-center">
                        <span class="text-xs text-rose-400 block mb-0.5">总价（元）</span>
                        <span class="text-lg font-bold text-rose-700">¥{{ fmtPrice(detailItem.plan_data.pricing.total_cost) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </template>
          </div>

          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="closeDetail">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <div v-if="showDeleteConfirm" class="ef-overlay" style="z-index: 60;" @click="handleDeleteBackdrop">
        <div class="ef-dialog ef-dialog--confirm">
          <div class="p-6 flex flex-col items-center text-center">
            <div class="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center mb-4">
              <AlertTriangle :size="22" class="text-red-500" />
            </div>
            <h3 class="text-base font-semibold text-neutral-900 mb-1">确认删除</h3>
            <p class="text-sm text-neutral-500 max-w-xs leading-relaxed">
              确定要删除方案「<span class="font-medium text-neutral-700">{{ deleteItem?.plan_title }}</span>」？此操作不可恢复。
            </p>
          </div>
          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="closeDeleteConfirm">取消</button>
            <button type="button" class="btn-danger" :disabled="deleting" @click="handleConfirmDelete">
              <Trash2 :size="14" />
              {{ deleting ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
/* ── Overlay & Dialog (copied from MajorView) ── */
.ef-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  animation: ef-fade-in 200ms ease-out forwards;
}

.ef-dialog {
  width: 100%;
  max-width: 640px;
  max-height: 90vh;
  background: #FFFFFF;
  border-radius: 14px;
  box-shadow: var(--shadow-overlay);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: ef-scale-in 250ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.ef-dialog--detail {
  max-width: 640px;
  max-height: 85vh;
}

.ef-dialog--confirm {
  max-width: 420px;
  max-height: 90vh;
}

.ef-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 24px;
  border-bottom: 1px solid var(--color-neutral-200);
  flex-shrink: 0;
}

.ef-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
  color: var(--color-neutral-900);
  line-height: 1;
}

.ef-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: transparent;
  border: none;
  color: var(--color-neutral-400);
  cursor: pointer;
  padding: 0;
  transition: background-color var(--duration-fast) ease, color var(--duration-fast) ease;
}

.ef-close-btn:hover {
  background-color: var(--color-neutral-100);
  color: var(--color-neutral-700);
}

.ef-body {
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ef-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-neutral-200);
  flex-shrink: 0;
}

@keyframes ef-fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes ef-scale-in {
  from {
    opacity: 0;
    transform: scale(0.96);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* ── Detail-specific styles ── */
.param-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--color-neutral-50);
  border-radius: 8px;
  border: 1px solid var(--color-neutral-100);
}

.param-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.param-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.param-label {
  font-size: 11px;
  color: var(--color-neutral-400);
  line-height: 1;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.param-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-neutral-800);
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-neutral-700);
  margin-bottom: 10px;
  line-height: 1;
}

.intro-content :deep(h1),
.intro-content :deep(h2),
.intro-content :deep(h3),
.intro-content :deep(h4) {
  font-weight: 600;
  margin-top: 12px;
  margin-bottom: 6px;
}

.intro-content :deep(p) {
  margin-bottom: 8px;
  line-height: 1.7;
}

.intro-content :deep(ul),
.intro-content :deep(ol) {
  padding-left: 18px;
  margin-bottom: 8px;
}

.intro-content :deep(li) {
  margin-bottom: 2px;
  line-height: 1.7;
}

.intro-content :deep(strong) {
  font-weight: 600;
  color: var(--color-neutral-800);
}
</style>
