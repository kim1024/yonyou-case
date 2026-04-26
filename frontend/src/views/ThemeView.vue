<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { Palette, Search, Inbox, Trash2, ChevronLeft, ChevronRight, Plus, Pencil, Zap, Copy, AlertTriangle, ArrowUp, ArrowDown, Eye, EyeOff } from 'lucide-vue-next'
import { adminApi } from '@/api/admin'
import { formatDateTime } from '@/utils/date'
import type { PlanTheme, PlanThemeStyleConfig, DisplayTemplateConfig } from '@/types'

/* ── 默认样式配置 ── */
const DEFAULT_STYLE_CONFIG: PlanThemeStyleConfig = {
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

/* ── 默认展示模板 ── */
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

const BLOCK_LABELS: Record<string, string> = {
  title: '标题区',
  introduction: '总体介绍',
  modules: '课程模块',
  positions: '胜任岗位',
  deliverables: '课程成果物',
  pricing: '价格卡片',
  footerNote: '底部说明',
}

const SECTION_TITLE_EDITABLE: Record<string, boolean> = {
  title: false,
  introduction: true,
  modules: true,
  positions: true,
  deliverables: true,
  pricing: false,
  footerNote: false,
}

const ALWAYS_VISIBLE_BLOCKS = ['title', 'pricing']
const GRID_COLS_BLOCKS = ['modules', 'positions', 'deliverables']

/* ── 颜色配置项定义 ── */
interface ColorField {
  key: Exclude<keyof PlanThemeStyleConfig, 'display_template'>
  label: string
  desc: string
}

const basicColorFields: ColorField[] = [
  { key: 'accentColor', label: '主色调', desc: '标题栏、边框、强调元素' },
  { key: 'highlightColor', label: '强调色', desc: '高亮背景、选中态' },
  { key: 'dotColor', label: '辅助色', desc: '列表圆点、装饰元素' },
  { key: 'pageBg', label: '页面背景', desc: '整体页面背景色' },
  { key: 'cardBg', label: '卡片背景', desc: '模块卡片、岗位卡片' },
  { key: 'textColor', label: '正文文字', desc: '正文内容文字颜色' },
  { key: 'subtitleColor', label: '副标题色', desc: '副标题、小标题' },
]

const pricingColorFields: ColorField[] = [
  { key: 'pricingCardBg', label: '卡片背景色', desc: '价格卡片渐变起始色' },
  { key: 'pricingNumberGradient', label: '数字渐变色', desc: '价格数字渐变起始色' },
]

function getStyleField(key: ColorField['key']): string {
  return formStyle[key]
}

function setStyleField(key: ColorField['key'], value: string) {
  formStyle[key] = value
}

/* ── 列表数据 ── */
const items = ref<PlanTheme[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)
const filterKeyword = ref('')
let debounceTimer: ReturnType<typeof setTimeout> | null = null

/* ── 弹窗状态 ── */
const showModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const editingThemeId = ref<number | null>(null)
const formName = ref('')
const formStyle = reactive<PlanThemeStyleConfig>({ ...DEFAULT_STYLE_CONFIG })
const formTab = ref<'basic' | 'pricing' | 'layout'>('basic')
const formDisplayTemplate = reactive<DisplayTemplateConfig>(JSON.parse(JSON.stringify(DEFAULT_DISPLAY_TEMPLATE)))
const saving = ref(false)

/* ── 删除确认 ── */
const showDeleteConfirm = ref(false)
const deleteItem = ref<PlanTheme | null>(null)
const deleting = ref(false)

/* ── 激活中 ── */
const activatingId = ref<number | null>(null)

/* ── Toast ── */
function showToast(message: string) {
  const toast = document.createElement('div')
  toast.textContent = message
  toast.style.cssText = `
    position: fixed; top: 24px; left: 50%; transform: translateX(-50%);
    padding: 10px 24px; border-radius: 8px; font-size: 13px; font-weight: 500;
    color: #fff; background: rgba(45, 45, 45, 0.92); backdrop-filter: blur(8px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.18); z-index: 200;
    animation: toastIn 250ms cubic-bezier(0.16,1,0.3,1) forwards;
    font-family: var(--font-body);
  `
  document.body.appendChild(toast)
  setTimeout(() => {
    toast.style.opacity = '0'
    toast.style.transform = 'translateX(-50%) translateY(-8px)'
    toast.style.transition = 'all 250ms ease'
    setTimeout(() => toast.remove(), 260)
  }, 2200)
}

/* ── 筛选 ── */
function resetToFirst() {
  page.value = 1
  loadData()
}

function handleSearchDebounce() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => resetToFirst(), 300)
}

/* ── 加载列表 ── */
async function loadData() {
  loading.value = true
  try {
    const res = await adminApi.getThemes({
      page: page.value,
      page_size: pageSize,
      keyword: filterKeyword.value.trim() || undefined,
    })
    items.value = res.data.items
    total.value = res.data.total
    loadAccentColors(items.value)
  } finally {
    loading.value = false
  }
}

/* ── 统计 ── */
const activeCount = computed(() => items.value.filter(t => t.is_active).length)

/* ── 打开创建弹窗 ── */
async function openCreateModal() {
  modalMode.value = 'create'
  editingThemeId.value = null
  formTab.value = 'basic'

  // 获取当前激活主题作为基线
  try {
    const res = await adminApi.getActiveTheme()
    const activeTheme = res.data
    if (activeTheme?.style_config) {
      Object.assign(formStyle, activeTheme.style_config)
    } else {
      Object.assign(formStyle, DEFAULT_STYLE_CONFIG)
    }
    if (activeTheme?.style_config?.display_template) {
      Object.assign(formDisplayTemplate, JSON.parse(JSON.stringify(activeTheme.style_config.display_template)))
    } else {
      Object.assign(formDisplayTemplate, JSON.parse(JSON.stringify(DEFAULT_DISPLAY_TEMPLATE)))
    }
  } catch {
    Object.assign(formStyle, DEFAULT_STYLE_CONFIG)
    Object.assign(formDisplayTemplate, JSON.parse(JSON.stringify(DEFAULT_DISPLAY_TEMPLATE)))
  }

  formName.value = ''
  showModal.value = true
}

/* ── 打开编辑弹窗 ── */
async function openEditModal(theme: PlanTheme) {
  modalMode.value = 'edit'
  editingThemeId.value = theme.id
  formTab.value = 'basic'
  formName.value = theme.name

  // 加载该主题当前版本样式
  try {
    const res = await adminApi.getThemeDetail(theme.id)
    const detail = res.data
    if (detail?.current_version?.style_config) {
      Object.assign(formStyle, detail.current_version.style_config)
    } else {
      Object.assign(formStyle, DEFAULT_STYLE_CONFIG)
    }
    if (detail?.current_version?.style_config?.display_template) {
      Object.assign(formDisplayTemplate, JSON.parse(JSON.stringify(detail.current_version.style_config.display_template)))
    } else {
      Object.assign(formDisplayTemplate, JSON.parse(JSON.stringify(DEFAULT_DISPLAY_TEMPLATE)))
    }
  } catch {
    Object.assign(formStyle, DEFAULT_STYLE_CONFIG)
    Object.assign(formDisplayTemplate, JSON.parse(JSON.stringify(DEFAULT_DISPLAY_TEMPLATE)))
  }

  showModal.value = true
}

/* ── 关闭弹窗 ── */
function closeModal() {
  showModal.value = false
  editingThemeId.value = null
}

function handleModalBackdrop(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('ef-overlay')) {
    closeModal()
  }
}

/* ── 保存主题 ── */
async function handleSave() {
  const name = formName.value.trim()
  if (!name) {
    showToast('请输入主题名称')
    return
  }

  saving.value = true
  try {
    const stylePayload = { ...formStyle, display_template: JSON.parse(JSON.stringify(formDisplayTemplate)) }
    if (modalMode.value === 'create') {
      await adminApi.createTheme({
        name,
        style_config: stylePayload,
      })
      showToast('主题创建成功')
    } else {
      if (editingThemeId.value !== null) {
        // 编辑模式：原子更新名称 + 创建新版本
        await adminApi.updateThemeFull(editingThemeId.value, {
          name,
          style_config: stylePayload,
          remark: '由管理员编辑更新',
        })
        showToast('主题更新成功')
      }
    }
    closeModal()
    loadData()
  } catch {
    showToast('操作失败，请重试')
  } finally {
    saving.value = false
  }
}

/* ── 激活主题 ── */
async function handleActivate(theme: PlanTheme) {
  if (theme.is_active || activatingId.value === theme.id) return
  activatingId.value = theme.id
  try {
    await adminApi.activateTheme(theme.id)
    showToast(`「${theme.name}」已激活`)
    loadData()
  } catch {
    showToast('激活失败')
  } finally {
    activatingId.value = null
  }
}

/* ── 复制主题（基于激活主题创建新主题） ── */
async function handleDuplicate(theme: PlanTheme) {
  try {
    // 获取要复制的主题的样式
    const res = await adminApi.getThemeDetail(theme.id)
    const detail = res.data
    const styleConfig = detail?.current_version?.style_config || DEFAULT_STYLE_CONFIG

    await adminApi.createTheme({
      name: `${theme.name} - 副本`,
      style_config: { ...styleConfig },
    })
    showToast(`已创建「${theme.name} - 副本」`)
    loadData()
  } catch {
    showToast('复制失败')
  }
}

/* ── 删除 ── */
function handleOpenDelete(theme: PlanTheme) {
  deleteItem.value = theme
  showDeleteConfirm.value = true
}

async function handleConfirmDelete() {
  if (!deleteItem.value) return
  deleting.value = true
  try {
    await adminApi.deleteTheme(deleteItem.value.id)
    showDeleteConfirm.value = false
    deleteItem.value = null
    showToast('主题已删除')
    loadData()
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '删除失败'
    showToast(msg)
  } finally {
    deleting.value = false
  }
}

function closeDeleteConfirm() {
  showDeleteConfirm.value = false
  deleteItem.value = null
}

function handleDeleteBackdrop(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('ef-overlay')) {
    closeDeleteConfirm()
  }
}

/* ── 主色调提取（列表用） ── */
const accentColorMap = ref<Map<number, string>>(new Map())

async function loadAccentColors(themes: PlanTheme[]) {
  const map = new Map<number, string>()
  for (const theme of themes) {
    try {
      const res = await adminApi.getThemeDetail(theme.id)
      const cfg = res.data?.current_version?.style_config
      map.set(theme.id, cfg?.accentColor || DEFAULT_STYLE_CONFIG.accentColor)
    } catch {
      map.set(theme.id, DEFAULT_STYLE_CONFIG.accentColor)
    }
  }
  accentColorMap.value = map
}

function getAccentColor(themeId: number): string {
  return accentColorMap.value.get(themeId) || DEFAULT_STYLE_CONFIG.accentColor
}

/* ── 实时预览计算 ── */
const previewPricingBg = computed(() => {
  const val = formStyle.pricingCardBg
  if (val.startsWith('linear-gradient') || val.startsWith('radial-gradient')) return val
  return `linear-gradient(135deg, ${val}, ${val}CC)`
})

const previewPricingText = computed(() => {
  const val = formStyle.pricingNumberGradient
  if (val.startsWith('linear-gradient') || val.startsWith('radial-gradient')) return val
  return `linear-gradient(135deg, ${val}, ${val}CC)`
})

/* ── 展示布局操作 ── */
const sortedBlocks = computed(() => {
  return Object.values(formDisplayTemplate.blocks).sort((a, b) => a.order - b.order)
})

function moveBlockUp(blockId: string) {
  const blocks = formDisplayTemplate.blocks
  const current = blocks[blockId]
  if (!current || current.order <= 0) return
  const prevBlock = Object.values(blocks).find(b => b.order === current.order - 1)
  if (prevBlock) {
    const tmpOrder = current.order
    current.order = prevBlock.order
    prevBlock.order = tmpOrder
  }
}

function moveBlockDown(blockId: string) {
  const blocks = formDisplayTemplate.blocks
  const current = blocks[blockId]
  const maxOrder = Object.values(blocks).reduce((max, b) => Math.max(max, b.order), 0)
  if (!current || current.order >= maxOrder) return
  const nextBlock = Object.values(blocks).find(b => b.order === current.order + 1)
  if (nextBlock) {
    const tmpOrder = current.order
    current.order = nextBlock.order
    nextBlock.order = tmpOrder
  }
}

function toggleBlockVisibility(blockId: string) {
  if (ALWAYS_VISIBLE_BLOCKS.includes(blockId)) return
  formDisplayTemplate.blocks[blockId].visible = !formDisplayTemplate.blocks[blockId].visible
}

/* ── 预览区块可见性 ── */
const previewVisibleBlocks = computed(() => {
  return Object.values(formDisplayTemplate.blocks)
    .filter(b => b.visible)
    .sort((a, b) => a.order - b.order)
    .map(b => b.id)
})

/* ── 生命周期 ── */
onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="animate-fade-up">
    <!-- 标题栏 -->
    <div class="page-header flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-xl flex items-center justify-center"
          style="background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);"
        >
          <Palette :size="20" color="#fff" :stroke-width="1.8" />
        </div>
        <div>
          <h1>样式主题管理</h1>
          <p>管理课程方案结果页的显示样式和配色方案</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-4 text-xs">
          <span class="text-neutral-500">全部 <span class="font-semibold text-neutral-800">{{ total }}</span></span>
          <span class="text-neutral-500">已激活 <span class="font-semibold text-emerald-600">{{ activeCount }}</span></span>
        </div>
        <button class="btn-primary" @click="openCreateModal">
          <Plus :size="15" />
          新建主题
        </button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="flex items-center gap-2.5 mb-5">
      <div class="relative">
        <input
          v-model="filterKeyword"
          type="text"
          placeholder="搜索主题名称"
          class="input-macos w-64 pl-8"
          @input="handleSearchDebounce"
          @keyup.enter="resetToFirst"
        />
        <Search :size="14" class="absolute left-2.5 top-1/2 -translate-y-1/2 text-neutral-400 pointer-events-none" />
      </div>
    </div>

    <!-- 表格 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-neutral-50">
          <tr class="border-b border-neutral-200">
            <th class="px-4 py-3 text-left text-neutral-500 font-medium" style="width:200px">主题名称</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium" style="width:130px">主色调</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium" style="width:90px">当前版本</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium" style="width:80px">状态</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium" style="width:150px">创建时间</th>
            <th class="px-4 py-3 text-center text-neutral-500 font-medium" style="width:180px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in items"
            :key="item.id"
            class="border-t border-neutral-100 transition-colors duration-100 group"
            :class="index % 2 === 1 ? 'bg-neutral-50/50' : ''"
          >
            <!-- 主题名称 -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <span
                  v-if="item.is_active"
                  class="inline-block w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0"
                  style="animation: pulse 2s cubic-bezier(0.4,0,0.6,1) infinite;"
                />
                <span class="font-medium text-neutral-800 truncate max-w-[180px]" :title="item.name">{{ item.name }}</span>
              </div>
            </td>
            <!-- 主色调 -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <span
                  class="inline-block w-5 h-5 rounded-md border border-neutral-200 flex-shrink-0"
                  :style="{ background: getAccentColor(item.id) }"
                />
                <span class="text-neutral-500 text-xs font-mono">{{ getAccentColor(item.id) }}</span>
              </div>
            </td>
            <!-- 版本 -->
            <td class="px-4 py-3 text-neutral-600">
              v{{ item.current_version_number ?? 0 }}
            </td>
            <!-- 状态 -->
            <td class="px-4 py-3">
              <span
                v-if="item.is_active"
                class="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 rounded-full px-2.5 py-1 text-xs font-medium"
              >
                <Zap :size="11" />
                激活
              </span>
              <span
                v-else
                class="inline-flex items-center bg-neutral-100 text-neutral-500 rounded-full px-2.5 py-1 text-xs font-medium"
              >
                未激活
              </span>
            </td>
            <!-- 创建时间 -->
            <td class="px-4 py-3 text-neutral-500 text-xs font-mono">{{ formatDateTime(item.created_at) }}</td>
            <!-- 操作 -->
            <td class="px-4 py-3 text-center">
              <div class="inline-flex items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                <button class="btn-ghost text-primary-500 !px-1.5 !py-1.5" title="编辑" @click="openEditModal(item)">
                  <Pencil :size="14" />
                </button>
                <button
                  class="btn-ghost !px-1.5 !py-1.5"
                  :class="item.is_active ? 'text-neutral-300 cursor-not-allowed' : 'text-danger'"
                  :title="item.is_active ? '激活主题不可删除' : '删除'"
                  :disabled="item.is_active"
                  @click="!item.is_active && handleOpenDelete(item)"
                >
                  <Trash2 :size="14" />
                </button>
                <div class="w-px h-4 bg-neutral-200 mx-0.5" />
                <button
                  v-if="!item.is_active"
                  class="btn-ghost text-emerald-600 !px-1.5 !py-1.5"
                  title="激活"
                  :disabled="activatingId === item.id"
                  @click="handleActivate(item)"
                >
                  <Zap :size="14" />
                </button>
                <button
                  class="btn-ghost text-neutral-500 !px-1.5 !py-1.5"
                  title="复制主题"
                  @click="handleDuplicate(item)"
                >
                  <Copy :size="14" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="6" class="px-4 py-16 text-center">
              <div class="flex flex-col items-center gap-3 text-neutral-400">
                <Inbox :size="40" :stroke-width="1.2" />
                <span class="text-sm">{{ loading ? '加载中...' : '暂无主题' }}</span>
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

    <!-- ==================== 创建/编辑弹窗 ==================== -->
    <Teleport to="body">
      <div v-if="showModal" class="ef-overlay" @click="handleModalBackdrop">
        <div class="ef-dialog ef-dialog--theme">
          <div class="ef-header">
            <h2 class="ef-title">{{ modalMode === 'create' ? '新建主题' : '编辑主题' }}</h2>
            <button class="ef-close-btn" @click="closeModal" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>

          <div class="ef-body theme-modal-body">
            <!-- 左侧：表单 -->
            <div class="theme-form-panel">
              <!-- 主题名称 -->
              <div class="mb-5">
                <label class="theme-field-label">主题名称</label>
                <input
                  v-model="formName"
                  type="text"
                  class="input-macos"
                  placeholder="输入主题名称，如：中国红"
                />
              </div>

              <!-- Tab 切换 -->
              <div class="theme-tabs mb-4">
                <button
                  class="theme-tab"
                  :class="{ 'theme-tab--active': formTab === 'basic' }"
                  @click="formTab = 'basic'"
                >
                  基础颜色
                </button>
                <button
                  class="theme-tab"
                  :class="{ 'theme-tab--active': formTab === 'pricing' }"
                  @click="formTab = 'pricing'"
                >
                  价格卡片
                </button>
                <button
                  class="theme-tab"
                  :class="{ 'theme-tab--active': formTab === 'layout' }"
                  @click="formTab = 'layout'"
                >
                  展示布局
                </button>
              </div>

              <!-- 基础颜色 -->
              <div v-if="formTab === 'basic'" class="theme-color-list">
                <div
                  v-for="field in basicColorFields"
                  :key="field.key"
                  class="theme-color-item"
                >
                  <div class="theme-color-info">
                    <span class="theme-color-label">{{ field.label }}</span>
                    <span class="theme-color-desc">{{ field.desc }}</span>
                  </div>
                  <div class="theme-color-input-wrap">
                    <input
                      type="color"
                      :value="getStyleField(field.key)"
                      class="theme-color-picker"
                      @input="setStyleField(field.key, ($event.target as HTMLInputElement).value)"
                    />
                    <input
                      type="text"
                      :value="getStyleField(field.key)"
                      class="theme-color-hex"
                      maxlength="7"
                      @input="setStyleField(field.key, ($event.target as HTMLInputElement).value)"
                    />
                  </div>
                </div>
              </div>

              <!-- 价格卡片 -->
              <div v-if="formTab === 'pricing'" class="theme-color-list">
                <div
                  v-for="field in pricingColorFields"
                  :key="field.key"
                  class="theme-color-item"
                >
                  <div class="theme-color-info">
                    <span class="theme-color-label">{{ field.label }}</span>
                    <span class="theme-color-desc">{{ field.desc }}</span>
                  </div>
                  <div class="theme-color-input-wrap">
                    <input
                      type="text"
                      :value="getStyleField(field.key)"
                      class="theme-color-hex gradient-input"
                      @input="setStyleField(field.key, ($event.target as HTMLInputElement).value)"
                    />
                  </div>
                </div>
              </div>

              <!-- 展示布局 -->
              <div v-if="formTab === 'layout'" class="layout-config-panel">
                <div class="layout-block-list">
                  <div
                    v-for="block in sortedBlocks"
                    :key="block.id"
                    class="layout-block-item"
                    :class="{ 'layout-block-item--hidden': !block.visible }"
                  >
                    <!-- 排序按钮 -->
                    <div class="layout-block-order">
                      <button
                        class="layout-order-btn"
                        :disabled="block.order <= 0"
                        title="上移"
                        @click="moveBlockUp(block.id)"
                      >
                        <ArrowUp :size="12" />
                      </button>
                      <button
                        class="layout-order-btn"
                        :disabled="block.order >= Object.values(formDisplayTemplate.blocks).length - 1"
                        title="下移"
                        @click="moveBlockDown(block.id)"
                      >
                        <ArrowDown :size="12" />
                      </button>
                    </div>

                    <!-- 可见性切换 -->
                    <button
                      class="layout-visibility-btn"
                      :class="{ 'layout-visibility-btn--locked': ALWAYS_VISIBLE_BLOCKS.includes(block.id) }"
                      :disabled="ALWAYS_VISIBLE_BLOCKS.includes(block.id)"
                      :title="ALWAYS_VISIBLE_BLOCKS.includes(block.id) ? '始终显示' : (block.visible ? '点击隐藏' : '点击显示')"
                      @click="toggleBlockVisibility(block.id)"
                    >
                      <Eye v-if="block.visible" :size="14" />
                      <EyeOff v-else :size="14" />
                    </button>

                    <!-- 区块名称 -->
                    <span class="layout-block-name">{{ BLOCK_LABELS[block.id] || block.id }}</span>

                    <!-- 标题文案输入 -->
                    <input
                      v-if="SECTION_TITLE_EDITABLE[block.id]"
                      v-model="formDisplayTemplate.blocks[block.id].sectionTitle"
                      type="text"
                      class="layout-title-input input-macos"
                      placeholder="区块标题"
                    />
                    <span v-else class="layout-title-fixed">{{ block.sectionTitle || '—' }}</span>

                    <!-- 列数选择 -->
                    <div v-if="GRID_COLS_BLOCKS.includes(block.id)" class="layout-cols-select">
                      <label class="layout-cols-label">列数</label>
                      <select
                        v-model.number="formDisplayTemplate.blocks[block.id].gridCols"
                        class="input-macos layout-cols-dropdown"
                      >
                        <template v-if="block.id === 'deliverables'">
                          <option :value="0">自适应</option>
                          <option v-for="n in 6" :key="n" :value="n">{{ n }} 列</option>
                        </template>
                        <template v-else>
                          <option v-for="n in 4" :key="n" :value="n">{{ n }} 列</option>
                        </template>
                      </select>
                    </div>
                  </div>
                </div>
                <p class="layout-hint">
                  通过上下箭头调整区块排列顺序，点击眼睛图标切换显示/隐藏。
                </p>
              </div>
            </div>

            <!-- 右侧：实时预览 -->
            <div class="theme-preview-panel">
              <div class="theme-preview-label">实时预览</div>
              <div
                class="theme-preview-frame"
                :style="{ background: formStyle.pageBg }"
              >
                <template v-for="blockId in previewVisibleBlocks" :key="blockId">
                  <!-- 标题栏 -->
                  <div v-if="blockId === 'title'" class="theme-prev-titlebar" :style="{ background: formStyle.accentColor }">
                    <div class="theme-prev-titlebar-text" :style="{ color: '#fff' }">方案标题示例</div>
                  </div>

                  <!-- Section Heading (introduction/modules/positions/deliverables 共用) -->
                  <div
                    v-else-if="['introduction', 'modules', 'positions', 'deliverables'].includes(blockId)"
                    class="theme-prev-section-heading"
                    :style="{ background: formStyle.accentColor + '14', borderLeft: `3px solid ${formStyle.accentColor}` }"
                  >
                    <span :style="{ color: formStyle.subtitleColor }" class="theme-prev-section-title">
                      {{ formDisplayTemplate.blocks[blockId].sectionTitle }}
                    </span>
                  </div>

                  <!-- Module Card -->
                  <div
                    v-if="blockId === 'modules'"
                    class="theme-prev-card"
                    :style="{ background: formStyle.cardBg, borderLeft: `3px solid ${formStyle.accentColor}`, boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }"
                  >
                    <div class="theme-prev-card-header" :style="{ color: formStyle.subtitleColor }">数据分析模块</div>
                    <ul class="theme-prev-list">
                      <li :style="{ color: formStyle.textColor }">
                        <span class="theme-prev-dot" :style="{ background: formStyle.dotColor }" />
                        基础数据概念讲解
                      </li>
                    </ul>
                  </div>

                  <!-- Position Card -->
                  <div
                    v-if="blockId === 'positions'"
                    class="theme-prev-card"
                    :style="{ background: formStyle.cardBg, borderTop: `3px solid ${formStyle.accentColor}`, boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }"
                  >
                    <div class="theme-prev-card-header" :style="{ color: formStyle.subtitleColor }">培养岗位</div>
                    <div class="theme-prev-card-body" :style="{ color: formStyle.textColor }">数据分析师</div>
                  </div>

                  <!-- Pricing Card -->
                  <div v-if="blockId === 'pricing'" class="theme-prev-pricing" :style="{ background: previewPricingBg }">
                    <div class="theme-prev-pricing-label" style="color: rgba(255,255,255,0.8);">课程总价</div>
                    <div
                      class="theme-prev-pricing-number"
                      :style="{ background: previewPricingText, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }"
                    >
                      ¥36,000
                    </div>
                  </div>
                </template>

                <!-- 底部副标题始终显示 -->
                <div class="theme-prev-subtitle" :style="{ color: formStyle.subtitleColor }">
                  用友教育 · 产业案例教学
                </div>
              </div>
            </div>
          </div>

          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="closeModal">取消</button>
            <button type="button" class="btn-primary" :disabled="saving" @click="handleSave">
              {{ saving ? '保存中...' : (modalMode === 'create' ? '创建主题' : '保存更新') }}
            </button>
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
              确定要删除主题「<span class="font-medium text-neutral-700">{{ deleteItem?.name }}</span>」？此操作将同时删除所有历史版本，且不可恢复。
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
/* ── Overlay & Dialog ── */
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

.ef-dialog--theme {
  max-width: 960px;
  max-height: 90vh;
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

/* ── Active pulse animation ── */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* ── Theme Modal: two-column layout ── */
.theme-modal-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  min-height: 480px;
}

.theme-form-panel {
  display: flex;
  flex-direction: column;
}

.theme-preview-panel {
  display: flex;
  flex-direction: column;
}

.theme-preview-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-neutral-400);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
}

/* ── Tabs ── */
.theme-tabs {
  display: flex;
  gap: 2px;
  background: var(--color-neutral-100);
  border-radius: 8px;
  padding: 3px;
}

.theme-tab {
  flex: 1;
  padding: 7px 0;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-neutral-500);
  cursor: pointer;
  transition: all 0.15s ease;
}

.theme-tab--active {
  background: var(--color-neutral-0);
  color: var(--color-neutral-800);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

/* ── Field label ── */
.theme-field-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-neutral-700);
  margin-bottom: 6px;
}

/* ── Color list ── */
.theme-color-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.theme-color-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: var(--color-neutral-50);
  border-radius: 8px;
  border: 1px solid var(--color-neutral-100);
  transition: border-color 0.15s ease;
}

.theme-color-item:hover {
  border-color: var(--color-neutral-200);
}

.theme-color-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.theme-color-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-neutral-800);
  line-height: 1.3;
}

.theme-color-desc {
  font-size: 11px;
  color: var(--color-neutral-400);
  line-height: 1.3;
}

.theme-color-input-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.theme-color-picker {
  width: 30px;
  height: 30px;
  border: 2px solid var(--color-neutral-200);
  border-radius: 6px;
  padding: 0;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  overflow: hidden;
  flex-shrink: 0;
}

.theme-color-picker::-webkit-color-swatch-wrapper {
  padding: 2px;
}

.theme-color-picker::-webkit-color-swatch {
  border: none;
  border-radius: 3px;
}

.theme-color-hex {
  width: 72px;
  height: 30px;
  padding: 0 6px;
  border: 1px solid var(--color-neutral-200);
  border-radius: 6px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-neutral-700);
  background: var(--color-neutral-0);
  outline: none;
  transition: border-color 0.15s ease;
}

.theme-color-hex:focus {
  border-color: var(--color-primary-500);
}

.gradient-input {
  width: 280px;
}

/* ── Preview Frame ── */
.theme-preview-frame {
  flex: 1;
  border-radius: 10px;
  border: 1px solid var(--color-neutral-200);
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.theme-prev-titlebar {
  padding: 14px 16px;
  text-align: center;
}

.theme-prev-titlebar-text {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.theme-prev-section-heading {
  margin: 12px 12px 0;
  padding: 8px 10px;
  border-radius: 0 6px 6px 0;
}

.theme-prev-section-title {
  font-size: 12px;
  font-weight: 600;
}

.theme-prev-card {
  margin: 8px 12px 0;
  padding: 12px;
  border-radius: 8px;
}

.theme-prev-card-header {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
}

.theme-prev-card-body {
  font-size: 12px;
  line-height: 1.5;
}

.theme-prev-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.theme-prev-list li {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  line-height: 1.5;
}

.theme-prev-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  flex-shrink: 0;
}

.theme-prev-pricing {
  margin: 10px 12px 0;
  padding: 14px 16px;
  border-radius: 10px;
  text-align: center;
}

.theme-prev-pricing-label {
  font-size: 11px;
  margin-bottom: 2px;
}

.theme-prev-pricing-number {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.2;
}

.theme-prev-subtitle {
  padding: 10px 12px;
  font-size: 11px;
  text-align: center;
  opacity: 0.7;
}

/* ── 展示布局配置 ── */
.layout-config-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.layout-block-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.layout-block-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: #FAFAFA;
  border: 1px solid #E8E5E0;
  border-radius: 8px;
  transition: all 150ms ease;
}

.layout-block-item--hidden {
  opacity: 0.5;
}

.layout-block-order {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.layout-order-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 16px;
  border: none;
  background: transparent;
  color: #999;
  cursor: pointer;
  border-radius: 3px;
  transition: all 150ms;
}

.layout-order-btn:hover:not(:disabled) {
  background: #E8E5E0;
  color: #444;
}

.layout-order-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.layout-visibility-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #666;
  cursor: pointer;
  border-radius: 6px;
  transition: all 150ms;
  flex-shrink: 0;
}

.layout-visibility-btn:hover:not(:disabled) {
  background: #E8E5E0;
}

.layout-visibility-btn--locked {
  color: #BBB;
  cursor: not-allowed;
}

.layout-block-name {
  font-size: 13px;
  font-weight: 500;
  color: #444;
  min-width: 70px;
  flex-shrink: 0;
}

.layout-title-input {
  flex: 1;
  font-size: 12px;
  padding: 4px 8px;
  min-width: 0;
}

.layout-title-fixed {
  font-size: 12px;
  color: #999;
  flex: 1;
}

.layout-cols-select {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.layout-cols-label {
  font-size: 11px;
  color: #999;
}

.layout-cols-dropdown {
  font-size: 12px;
  padding: 3px 6px;
  width: 70px;
}

.layout-hint {
  font-size: 12px;
  color: #999;
  margin: 0;
  padding: 0 4px;
}
</style>
