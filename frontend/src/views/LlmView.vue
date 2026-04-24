<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick, onBeforeUnmount } from 'vue'
import {
  Plus, Pencil, Trash2, Check, ChevronLeft, ChevronRight,
  Inbox, Cpu, ArrowLeft, RotateCcw, Sparkles, X, Search,
  Layers, Activity, Zap, Hash, Copy, Info, Maximize2, Minimize2, Eye,
} from 'lucide-vue-next'
import SvgTooltip from '@/components/shared/SvgTooltip.vue'
import ModelConsumptionChart from '@/components/admin/ModelConsumptionChart.vue'
import { adminApi } from '@/api/admin'
import type {
  LlmConfig, LlmConfigCreate, LlmConfigUpdate,
  TokenStats,
  PromptTemplate, PromptVersion,
  PromptTemplateCreate, PromptVersionCreate,
} from '@/types'

/* ═══════════════════════════════════════════════
   全局 Toast 通知
   ═══════════════════════════════════════════════ */
interface ToastItem {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}
const toastItems = ref<ToastItem[]>([])
let toastIdCounter = 0
let toastTimer: ReturnType<typeof setTimeout> | null = null

function showToast(message: string, type: ToastItem['type'] = 'success') {
  const id = ++toastIdCounter
  toastItems.value.push({ id, message, type })
  if (toastItems.value.length > 5) toastItems.value.shift()
  setTimeout(() => { removeToast(id) }, 3200)
}

function removeToast(id: number) {
  const idx = toastItems.value.findIndex(t => t.id === id)
  if (idx !== -1) toastItems.value.splice(idx, 1)
}

/* ═══════════════════════════════════════════════
   公共状态
   ═══════════════════════════════════════════════ */
const activeTab = ref<'llm' | 'token' | 'prompt'>('llm')

/* ═══════════════════════════════════════════════
   Tab 1：模型配置
   ═══════════════════════════════════════════════ */
const llmItems = ref<LlmConfig[]>([])
const llmTotal = ref(0)
const llmPage = ref(1)
const llmPageSize = 20
const llmLoading = ref(false)

const showLlmModal = ref(false)
const editLlmItem = ref<LlmConfig | null>(null)
const llmSaving = ref(false)
const llmErrors = ref<Record<string, string>>({})
const llmForm = ref<Omit<LlmConfigCreate, 'is_active'> & { is_active: boolean }>({
  name: '',
  model: '',
  api_base_url: '',
  api_key: '',
  temperature: 0.7,
  max_tokens: 2000,
  timeout: 60,
  is_active: false,
})

const modelList = ref<string[]>([])
const modelListLoading = ref(false)
const modelInputMode = ref<'select' | 'manual'>('select')

async function fetchModels() {
  const url = llmForm.value.api_base_url.trim()
  const key = llmForm.value.api_key.trim()
  if (!url || !key) {
    showToast('请先填写 Base URL 和 API Key', 'error')
    return
  }
  modelListLoading.value = true
  modelList.value = []
  try {
    const res = await adminApi.fetchModels(url, key)
    const models: string[] = res.data.models ?? []
    if (models.length === 0) {
      showToast('未获取到可用模型', 'info')
      modelInputMode.value = 'manual'
    } else {
      modelList.value = models
      modelInputMode.value = 'select'
      if (llmForm.value.model && !models.includes(llmForm.value.model)) {
        modelInputMode.value = 'manual'
      }
    }
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? '拉取模型列表失败'
    showToast(String(msg), 'error')
    modelInputMode.value = 'manual'
  } finally {
    modelListLoading.value = false
  }
}

async function loadLlmConfigs() {
  llmLoading.value = true
  try {
    const res = await adminApi.getLlmConfigs({ page: llmPage.value, page_size: llmPageSize })
    llmItems.value = res.data.items
    llmTotal.value = res.data.total
  } finally {
    llmLoading.value = false
  }
}

function handleAddLlm() {
  editLlmItem.value = null
  llmErrors.value = {}
  llmForm.value = {
    name: '', model: '', api_base_url: '', api_key: '',
    temperature: 0.7, max_tokens: 2000, timeout: 60, is_active: false,
  }
  modelList.value = []
  modelInputMode.value = 'select'
  showLlmModal.value = true
}

function handleEditLlm(item: LlmConfig) {
  editLlmItem.value = item
  llmErrors.value = {}
  llmForm.value = {
    name: item.name,
    model: item.model,
    api_base_url: item.api_base_url,
    api_key: '',
    temperature: item.temperature,
    max_tokens: item.max_tokens,
    timeout: item.timeout,
    is_active: item.is_active,
  }
  modelList.value = []
  modelInputMode.value = 'select'
  showLlmModal.value = true
  // 编辑模式自动拉取模型列表（需用户提供 api_key）
  nextTick(() => {
    fetchModels()
  })
}

function validateLlmForm(): boolean {
  llmErrors.value = {}
  if (!llmForm.value.name.trim()) llmErrors.value.name = '请输入配置名称'
  if (!llmForm.value.model.trim()) llmErrors.value.model = '请输入模型名称'
  if (!llmForm.value.api_base_url.trim()) llmErrors.value.api_base_url = '请输入 Base URL'
  if (!editLlmItem.value && !llmForm.value.api_key.trim()) llmErrors.value.api_key = '请输入 API Key'
  if (llmForm.value.temperature < 0 || llmForm.value.temperature > 2) llmErrors.value.temperature = '取值范围 0-2'
  return Object.keys(llmErrors.value).length === 0
}

async function handleSaveLlm() {
  if (!validateLlmForm()) return
  llmSaving.value = true
  try {
    if (editLlmItem.value) {
      const payload: LlmConfigUpdate = {
        name: llmForm.value.name,
        model: llmForm.value.model,
        api_base_url: llmForm.value.api_base_url,
        temperature: llmForm.value.temperature,
        max_tokens: llmForm.value.max_tokens,
        timeout: llmForm.value.timeout,
        is_active: llmForm.value.is_active,
      }
      if (llmForm.value.api_key.trim()) payload.api_key = llmForm.value.api_key
      await adminApi.updateLlmConfig(editLlmItem.value.id, payload)
    } else {
      await adminApi.createLlmConfig({
        name: llmForm.value.name,
        model: llmForm.value.model,
        api_base_url: llmForm.value.api_base_url,
        api_key: llmForm.value.api_key,
        temperature: llmForm.value.temperature,
        max_tokens: llmForm.value.max_tokens,
        timeout: llmForm.value.timeout,
        is_active: llmForm.value.is_active,
      })
    }
    showLlmModal.value = false
    modelList.value = []
    modelInputMode.value = 'select'
    loadLlmConfigs()
    showToast('配置已保存，已全局生效', 'success')
  } catch {
    showToast('保存失败，请重试', 'error')
  } finally {
    llmSaving.value = false
  }
}

async function handleDeleteLlm(item: LlmConfig) {
  if (item.is_active) {
    if (!confirm('该配置当前正在使用中，确定要删除吗？删除后需要激活其他配置。')) return
  } else {
    if (!confirm('确定删除该配置？此操作不可恢复。')) return
  }
  try {
    await adminApi.deleteLlmConfig(item.id)
    loadLlmConfigs()
    showToast('配置已删除', 'info')
  } catch {
    showToast('删除失败，请重试', 'error')
  }
}

async function handleActivateLlm(item: LlmConfig) {
  if (item.is_active) return
  try {
    await adminApi.activateLlmConfig(item.id)
    loadLlmConfigs()
    showToast(`「${item.name}」已激活，已全局生效`, 'success')
  } catch {
    showToast('激活失败，请重试', 'error')
  }
}

function handleLlmBackdropClick(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('ef-overlay')) {
    showLlmModal.value = false
    modelList.value = []
    modelInputMode.value = 'select'
  }
}

/* ═══════════════════════════════════════════════
   Tab 2：Token 统计
   ═══════════════════════════════════════════════ */
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
let trendResizeObs: ResizeObserver | null = null

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

/* ═══════════════════════════════════════════════
   Tab 3：提示词模板
   ═══════════════════════════════════════════════ */
const promptItems = ref<PromptTemplate[]>([])
const promptTotal = ref(0)
const promptPage = ref(1)
const promptPageSize = 20
const promptLoading = ref(false)
const promptKeyword = ref('')
const showPromptList = ref(true)

/* ── 模板 CRUD 弹窗 ── */
const showPromptModal = ref(false)
const editPromptItem = ref<PromptTemplate | null>(null)
const promptSaving = ref(false)
const promptErrors = ref<Record<string, string>>({})
const promptForm = ref({ name: '', description: '', content: '', remark: '' })

/* ── 版本详情 ── */
const currentTemplateId = ref<number | null>(null)
const currentTemplateName = ref('')
const versions = ref<PromptVersion[]>([])
const selectedVersionId = ref<number | null>(null)
const versionsLoading = ref(false)

/* ── 创建版本弹窗 ── */
const showVersionModal = ref(false)
const versionSaving = ref(false)
const versionForm = ref({ content: '', remark: '' })

/* ── 回滚确认弹窗 ── */
const showRollbackModal = ref(false)
const rollbackTarget = ref<PromptVersion | null>(null)
const rollbackLoading = ref(false)

/* ── 提示词变量说明 ── */
const promptVariables = [
  { name: '{major}', desc: '专业名称' },
  { name: '{industry}', desc: '所属行业' },
  { name: '{enterprise_name}', desc: '企业名称' },
  { name: '{region}', desc: '所属地区' },
  { name: '{hour}', desc: '课时数' },
  { name: '{company_intro}', desc: '企业简介' },
  { name: '{yonyou_content}', desc: '用友产品内容' },
  { name: '{total_cost}', desc: '总费用' },
]

/* ── 编辑器 ref ── */
const promptModalTextareaRef = ref<HTMLTextAreaElement | null>(null)
const versionModalTextareaRef = ref<HTMLTextAreaElement | null>(null)

/* ── 全屏模式 ── */
const versionFullscreen = ref(false)

/* ── 预览模式 ── */
const showPreview = ref(false)
const previewContent = ref('')
const previewVersionId = ref<number | null>(null)

/* 变量示例值映射 */
const variableExamples: Record<string, string> = {
  '{major}': '大数据技术',
  '{industry}': '制造行业',
  '{enterprise_name}': '示例企业有限公司',
  '{region}': '华东地区',
  '{hour}': '32',
  '{company_intro}': '该企业是一家专注于智能制造的高新技术企业，成立于2010年，拥有员工500余人。',
  '{yonyou_content}': '用友U8 cloud 云端ERP系统，提供财务、供应链、生产制造一体化解决方案。',
  '{total_cost}': '158,000',
}

/** 在指定 textarea 的光标位置插入文本 */
function insertVariableAtCursor(textareaRef: HTMLTextAreaElement | null, variableName: string) {
  if (!textareaRef) return
  const el = textareaRef
  const start = el.selectionStart
  const end = el.selectionEnd
  const current = el.value
  el.value = current.substring(0, start) + variableName + current.substring(end)
  el.selectionStart = el.selectionEnd = start + variableName.length
  el.focus()
  // 触发 v-model 更新
  el.dispatchEvent(new Event('input'))
}

/** 处理 prompt 模板弹窗中的变量插入 */
function insertVariableToPromptModal(variableName: string) {
  insertVariableAtCursor(promptModalTextareaRef.value, variableName)
}

/** 处理版本弹窗中的变量插入 */
function insertVariableToVersionModal(variableName: string) {
  insertVariableAtCursor(versionModalTextareaRef.value, variableName)
}

/** 计算 textarea 字符数 */
function computeCharCount(text: string): number {
  return text.length
}

/** 切换全屏模式 */
function toggleVersionFullscreen() {
  versionFullscreen.value = !versionFullscreen.value
}

/** 生成预览内容（替换变量占位符为示例值） */
function generatePreview(content: string): string {
  let result = content
  for (const [key, value] of Object.entries(variableExamples)) {
    result = result.replaceAll(key, value)
  }
  return result
}

/** 显示/隐藏预览 */
function togglePreview() {
  if (showPreview.value) {
    showPreview.value = false
    return
  }
  if (selectedVersion.value) {
    previewContent.value = generatePreview(selectedVersion.value.content)
    previewVersionId.value = selectedVersion.value.id
    showPreview.value = true
  }
}

async function loadPromptTemplates() {
  promptLoading.value = true
  try {
    const res = await adminApi.getPromptTemplates({
      page: promptPage.value, page_size: promptPageSize,
      keyword: promptKeyword.value || undefined,
    })
    promptItems.value = res.data.items
    promptTotal.value = res.data.total
  } finally {
    promptLoading.value = false
  }
}

function handleAddPrompt() {
  editPromptItem.value = null
  promptErrors.value = {}
  promptForm.value = { name: '', description: '', content: '', remark: '' }
  showPromptModal.value = true
}

function handleEditPrompt(item: PromptTemplate) {
  editPromptItem.value = item
  promptErrors.value = {}
  promptForm.value = {
    name: item.name,
    description: item.description ?? '',
    content: '',
    remark: '',
  }
  showPromptModal.value = true
}

function validatePromptForm(): boolean {
  promptErrors.value = {}
  if (!promptForm.value.name.trim()) promptErrors.value.name = '请输入模板名称'
  if (!editPromptItem.value && !promptForm.value.content.trim()) promptErrors.value.content = '请输入提示词内容'
  return Object.keys(promptErrors.value).length === 0
}

async function handleSavePrompt() {
  if (!validatePromptForm()) return
  promptSaving.value = true
  try {
    if (editPromptItem.value) {
      await adminApi.updatePromptTemplate(editPromptItem.value.id, {
        name: promptForm.value.name,
        description: promptForm.value.description || undefined,
      })
    } else {
      await adminApi.createPromptTemplate({
        name: promptForm.value.name,
        description: promptForm.value.description || undefined,
        content: promptForm.value.content,
        remark: promptForm.value.remark || undefined,
      } as PromptTemplateCreate)
    }
    showPromptModal.value = false
    loadPromptTemplates()
    showToast(editPromptItem.value ? '模板已更新' : '模板已创建', 'success')
  } catch {
    showToast('保存失败，请重试', 'error')
  } finally {
    promptSaving.value = false
  }
}

async function handleDeletePrompt(item: PromptTemplate) {
  if (!confirm(`确定删除模板「${item.name}」？此操作不可恢复。`)) return
  try {
    await adminApi.deletePromptTemplate(item.id)
    loadPromptTemplates()
    showToast('模板已删除', 'info')
  } catch {
    showToast('删除失败，请重试', 'error')
  }
}

async function handleViewVersions(item: PromptTemplate) {
  currentTemplateId.value = item.id
  currentTemplateName.value = item.name
  showPromptList.value = false
  await loadVersions(item.id)
}

async function loadVersions(templateId: number) {
  versionsLoading.value = true
  try {
    const res = await adminApi.getPromptVersions(templateId)
    versions.value = res.data.items
    if (res.data.items.length > 0) {
      selectedVersionId.value = res.data.items[0].id
    }
  } finally {
    versionsLoading.value = false
  }
}

const selectedVersion = computed(() =>
  versions.value.find(v => v.id === selectedVersionId.value) ?? null
)

function handleBackToList() {
  showPromptList.value = true
  currentTemplateId.value = null
  versions.value = []
  selectedVersionId.value = null
}

/** 复制当前版本内容创建新版本 */
async function handleCreateVersion() {
  if (!currentTemplateId.value) return
  /* 预填当前版本内容 */
  const current = versions.value.find(v => v.is_current)
  versionForm.value = { content: current?.content ?? '', remark: '' }
  showVersionModal.value = true
}

/** 从模板列表直接复制为新版本 */
async function handleCopyAsNewVersion(item: PromptTemplate) {
  currentTemplateId.value = item.id
  currentTemplateName.value = item.name
  showPromptList.value = false
  await loadVersions(item.id)
  await nextTick()
  handleCreateVersion()
}

async function handleSaveVersion() {
  if (!currentTemplateId.value || !versionForm.value.content.trim()) return
  versionSaving.value = true
  try {
    await adminApi.createPromptVersion(currentTemplateId.value, {
      content: versionForm.value.content,
      remark: versionForm.value.remark || undefined,
    } as PromptVersionCreate)
    showVersionModal.value = false
    await loadVersions(currentTemplateId.value)
    showToast('新版本已创建，已全局生效', 'success')
  } catch {
    showToast('创建版本失败，请重试', 'error')
  } finally {
    versionSaving.value = false
  }
}

function handleRollback(version: PromptVersion) {
  rollbackTarget.value = version
  showRollbackModal.value = true
}

async function confirmRollback() {
  if (!currentTemplateId.value || !rollbackTarget.value) return
  rollbackLoading.value = true
  try {
    await adminApi.rollbackPromptVersion(currentTemplateId.value, rollbackTarget.value.id)
    showRollbackModal.value = false
    await loadVersions(currentTemplateId.value)
    showToast('回滚成功，已全局生效', 'success')
  } catch {
    showToast('回滚失败，请重试', 'error')
  } finally {
    rollbackLoading.value = false
  }
}

function handlePromptBackdropClick(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('ef-overlay')) showPromptModal.value = false
}
function handleVersionBackdropClick(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('ef-overlay')) showVersionModal.value = false
}
function handleRollbackBackdropClick(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('ef-overlay')) showRollbackModal.value = false
}

function handlePromptSearch() {
  promptPage.value = 1
  loadPromptTemplates()
}

/* ═══════════════════════════════════════════════
   初始化 & 销毁
   ═══════════════════════════════════════════════ */
onMounted(() => {
  loadLlmConfigs()
  loadTokenStats()
  loadPromptTemplates()
})

/* ResizeObserver: 用 watch 而非 onMounted，处理 v-if 隐藏的 tab 切换后元素才挂载的情况 */
watch(trendContainerEl, (el) => {
  trendResizeObs?.disconnect()
  if (el) {
    trendContainerWidth.value = el.offsetWidth
    trendResizeObs = new ResizeObserver(([entry]) => { trendContainerWidth.value = entry.contentRect.width })
    trendResizeObs.observe(el)
  }
})

onBeforeUnmount(() => {
  trendResizeObs?.disconnect()
  if (toastTimer) clearTimeout(toastTimer)
})

/* Tab 切换时按需加载 */
function switchTab(tab: 'llm' | 'token' | 'prompt') {
  activeTab.value = tab
  if (tab === 'llm' && llmItems.value.length === 0) loadLlmConfigs()
  if (tab === 'token' && !tokenStats.value) loadTokenStats()
  if (tab === 'prompt' && promptItems.value.length === 0) loadPromptTemplates()
}

const llmFormRef = ref<HTMLFormElement | null>(null)
const promptNameRef = ref<HTMLInputElement | null>(null)
</script>

<template>
  <div class="animate-fade-up">
    <!-- ═══ Toast 通知层 ═══ -->
    <Teleport to="body">
      <div class="fixed top-5 right-5 z-[100] flex flex-col gap-2 pointer-events-none">
        <TransitionGroup name="toast">
          <div
            v-for="toast in toastItems"
            :key="toast.id"
            class="pointer-events-auto toast-item flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg backdrop-blur-sm"
            :class="{
              'toast-success': toast.type === 'success',
              'toast-error': toast.type === 'error',
              'toast-info': toast.type === 'info',
            }"
            @click="removeToast(toast.id)"
          >
            <div class="toast-icon-wrap">
              <Check v-if="toast.type === 'success'" :size="14" :stroke-width="2.5" />
              <X v-else-if="toast.type === 'error'" :size="14" :stroke-width="2.5" />
              <Info v-else :size="14" :stroke-width="2.5" />
            </div>
            <span class="text-sm font-medium">{{ toast.message }}</span>
          </div>
        </TransitionGroup>
      </div>
    </Teleport>

    <!-- ═══ 标题栏 ═══ -->
    <div class="page-header">
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-xl flex items-center justify-center"
          style="background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);"
        >
          <Cpu :size="20" color="#fff" :stroke-width="1.8" />
        </div>
        <div>
          <h1>大模型管理</h1>
          <p>管理 LLM 配置、Token 消耗和提示词模板</p>
        </div>
      </div>
    </div>

    <!-- ═══ Tab 栏 ═══ -->
    <div class="tab-bar">
      <button
        class="tab-btn"
        :class="{ 'tab-btn--active': activeTab === 'llm' }"
        @click="switchTab('llm')"
      >
        <Cpu :size="15" :stroke-width="1.8" />
        模型配置
      </button>
      <button
        class="tab-btn"
        :class="{ 'tab-btn--active': activeTab === 'token' }"
        @click="switchTab('token')"
      >
        <Activity :size="15" :stroke-width="1.8" />
        Token 统计
      </button>
      <button
        class="tab-btn"
        :class="{ 'tab-btn--active': activeTab === 'prompt' }"
        @click="switchTab('prompt')"
      >
        <Sparkles :size="15" :stroke-width="1.8" />
        提示词模板
      </button>
    </div>

    <!-- ═══════════════════════════════════════════
         Tab 1 — 模型配置
         ═══════════════════════════════════════════ -->
    <div v-if="activeTab === 'llm'">
      <!-- Skeleton Loading -->
      <div v-if="llmLoading && llmItems.length === 0" class="space-y-4">
        <div class="skeleton h-10 w-32 rounded-lg" />
        <div class="bg-white rounded-xl shadow-sm overflow-hidden">
          <div v-for="i in 5" :key="i" class="flex gap-4 p-4 border-b border-neutral-100">
            <div class="skeleton h-4 flex-1 rounded" />
            <div class="skeleton h-4 w-24 rounded" />
            <div class="skeleton h-4 w-20 rounded" />
          </div>
        </div>
      </div>

      <template v-else>
        <!-- 顶部操作栏 -->
        <div class="flex items-center justify-between mb-5">
          <span class="text-sm text-neutral-500">
            共 <span class="font-medium text-neutral-700">{{ llmTotal }}</span> 条配置
          </span>
          <button class="btn-primary" @click="handleAddLlm">
            <Plus :size="16" />
            新增配置
          </button>
        </div>

        <!-- 表格 -->
        <div class="bg-white rounded-xl shadow-sm overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-neutral-50">
                <tr class="border-b border-neutral-200">
                  <th class="px-4 py-3 text-left text-neutral-500 font-medium">#</th>
                  <th class="px-4 py-3 text-left text-neutral-500 font-medium">配置名称</th>
                  <th class="px-4 py-3 text-left text-neutral-500 font-medium">模型</th>
                  <th class="px-4 py-3 text-left text-neutral-500 font-medium">Base URL</th>
                  <th class="px-4 py-3 text-left text-neutral-500 font-medium">API Key</th>
                  <th class="px-4 py-3 text-center text-neutral-500 font-medium">Temperature</th>
                  <th class="px-4 py-3 text-center text-neutral-500 font-medium">Max Tokens</th>
                  <th class="px-4 py-3 text-center text-neutral-500 font-medium">当前使用</th>
                  <th class="px-4 py-3 text-center text-neutral-500 font-medium">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, index) in llmItems"
                  :key="item.id"
                  class="border-t border-neutral-100 transition-colors duration-100 llm-row"
                  :class="[
                    index % 2 === 1 ? 'bg-neutral-50/50' : '',
                    item.is_active ? 'llm-row--active' : '',
                  ]"
                >
                  <td class="px-4 py-3 text-neutral-400">{{ (llmPage - 1) * llmPageSize + index + 1 }}</td>
                  <td class="px-4 py-3 font-medium text-neutral-800">
                    <div class="flex items-center gap-2">
                      <span>{{ item.name }}</span>
                      <span v-if="item.is_active" class="active-badge">
                        <Zap :size="10" :stroke-width="2.5" />
                        使用中
                      </span>
                    </div>
                  </td>
                  <td class="px-4 py-3">
                    <span class="inline-block px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-600 text-xs font-medium">
                      {{ item.model }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-neutral-500 max-w-[180px] truncate" :title="item.api_base_url">
                    {{ item.api_base_url }}
                  </td>
                  <td class="px-4 py-3 text-neutral-400 font-mono text-xs">{{ item.api_key_masked }}</td>
                  <td class="px-4 py-3 text-center tabular-nums">{{ item.temperature }}</td>
                  <td class="px-4 py-3 text-center tabular-nums">{{ item.max_tokens.toLocaleString() }}</td>
                  <td class="px-4 py-3 text-center">
                    <button
                      v-if="!item.is_active"
                      class="btn-activate"
                      @click="handleActivateLlm(item)"
                    >
                      <Check :size="13" :stroke-width="2.5" />
                      设为当前
                    </button>
                    <span v-else class="active-indicator">
                      <span class="active-dot" />
                      当前使用
                    </span>
                  </td>
                  <td class="px-4 py-3 text-center">
                    <div class="flex items-center justify-center gap-1">
                      <button class="btn-ghost text-primary-500" @click="handleEditLlm(item)">
                        <Pencil :size="14" />
                      </button>
                      <button class="btn-ghost text-danger" @click="handleDeleteLlm(item)">
                        <Trash2 :size="14" />
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="llmItems.length === 0">
                  <td colspan="9" class="px-4 py-16 text-center">
                    <div class="flex flex-col items-center gap-2 text-neutral-400">
                      <Inbox :size="36" />
                      <span>暂无模型配置</span>
                      <button class="btn-secondary mt-2" @click="handleAddLlm">
                        <Plus :size="14" />
                        新增配置
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="llmTotal > llmPageSize" class="mt-4 flex items-center justify-between text-sm text-neutral-500">
          <span />
          <div class="flex items-center gap-1">
            <button :disabled="llmPage <= 1" class="btn-ghost" @click="llmPage--; loadLlmConfigs()">
              <ChevronLeft :size="16" />上一页
            </button>
            <span class="px-3 py-1 text-neutral-600">第 {{ llmPage }} 页</span>
            <button :disabled="llmPage * llmPageSize >= llmTotal" class="btn-ghost" @click="llmPage++; loadLlmConfigs()">
              下一页<ChevronRight :size="16" />
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- ═══════════════════════════════════════════
         Tab 2 — Token 统计
         ═══════════════════════════════════════════ -->
    <div v-if="activeTab === 'token'">
      <!-- Skeleton -->
      <div v-if="tokenLoading" class="space-y-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <div v-for="i in 4" :key="i" class="gradient-card p-5 space-y-3">
            <div class="skeleton h-4 w-20 rounded" />
            <div class="skeleton h-9 w-28 rounded" />
          </div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div v-for="i in 2" :key="i" class="gradient-card p-6">
            <div class="skeleton h-5 w-32 mb-4 rounded" />
            <div class="skeleton h-64 w-full rounded-lg" />
          </div>
        </div>
      </div>

      <template v-else-if="tokenStats">
        <!-- 4 张统计卡片 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <div
            v-for="(card, idx) in tokenStatCards"
            :key="card.key"
            class="gradient-card p-5 relative overflow-hidden"
            :style="{ animationDelay: `${idx * 80}ms` }"
            style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both"
          >
            <div class="absolute top-0 left-0 right-0 h-[3px]" :style="{ background: card.gradient }" />
            <div class="absolute -top-6 -right-6 w-20 h-20 rounded-full opacity-10 blur-xl" :style="{ background: card.gradient }" />
            <div class="flex items-center justify-center gap-2 mb-4">
              <div
                class="flex items-center justify-center w-7 h-7 rounded-lg"
                :style="{ background: card.gradient.replace('linear-gradient(90deg', 'linear-gradient(135deg') + ', rgba(255,255,255,0.18))' }"
              >
                <component :is="card.icon" :size="15" class="text-white" />
              </div>
              <span class="text-xs font-medium text-neutral-500 tracking-wide uppercase">{{ card.label }}</span>
            </div>
            <div class="text-center">
              <div class="text-[36px] font-bold text-neutral-900 leading-none tracking-tight tabular-nums">
                {{ formatTokenNumber(card.value) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 图表区域 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- 趋势折线图 -->
          <div
            class="gradient-card p-6 relative overflow-hidden"
            style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) 320ms both"
          >
            <div ref="trendContainerEl" class="relative">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-base font-semibold text-neutral-800">Token 消耗趋势</h3>
                <div class="flex gap-1 p-0.5 bg-neutral-100 rounded-lg">
                  <button
                    class="px-3 py-1 text-xs font-medium rounded-md transition-all duration-150"
                    :class="trendDays === 7 ? 'bg-white text-neutral-800 shadow-sm' : 'text-neutral-500 hover:text-neutral-700'"
                    @click="trendDays = 7; loadTokenStats()"
                  >7 天</button>
                  <button
                    class="px-3 py-1 text-xs font-medium rounded-md transition-all duration-150"
                    :class="trendDays === 30 ? 'bg-white text-neutral-800 shadow-sm' : 'text-neutral-500 hover:text-neutral-700'"
                    @click="trendDays = 30; loadTokenStats()"
                  >30 天</button>
                </div>
              </div>
              <svg :viewBox="`0 0 ${LINE_W} ${LINE_H}`" class="w-full">
                <defs>
                  <linearGradient id="tokenAreaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#6366F1" stop-opacity="0.25" />
                    <stop offset="100%" stop-color="#6366F1" stop-opacity="0.02" />
                  </linearGradient>
                </defs>
                <line v-for="(y, i) in trendGridLines" :key="'g'+i" :x1="LINE_PAD" :y1="y" :x2="LINE_W-LINE_PAD" :y2="y" stroke="#f1f5f9" stroke-width="1" />
                <line :x1="LINE_PAD" :y1="LINE_H-LINE_PAD" :x2="LINE_W-LINE_PAD" :y2="LINE_H-LINE_PAD" stroke="#e2e8f0" stroke-width="1" />
                <line :x1="LINE_PAD" :y1="LINE_PAD" :x2="LINE_PAD" :y2="LINE_H-LINE_PAD" stroke="#e2e8f0" stroke-width="1" />
                <path v-if="trendData.length" :d="trendAreaD" fill="url(#tokenAreaGrad)" />
                <path v-if="trendData.length" :d="trendPathD" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="token-line-animate" />
                <circle
                  v-for="(d, i) in trendData" :key="i"
                  :cx="trendPx(i)" :cy="trendPy(d.tokens)"
                  :r="trendHoverIdx === i ? 6 : 4"
                  fill="#6366F1" stroke="white" stroke-width="2"
                  class="cursor-pointer"
                  style="transition: r 0.15s ease"
                  @mouseenter="trendHoverIdx = i; showTrendTooltip($event, d)"
                  @mouseleave="trendHoverIdx = -1; hideTrendTooltip()"
                />
                <text
                  v-for="i in trendVisibleLabelIndices" :key="'l'+i"
                  :x="trendPx(i)" :y="LINE_H-LINE_PAD+20"
                  text-anchor="middle" class="text-[10px] fill-neutral-400"
                >{{ trendData[i].date.slice(5) }}</text>
              </svg>
              <SvgTooltip v-bind="trendTooltip" :container-width="trendContainerWidth" />
            </div>
          </div>

          <!-- 模型分布环形图 -->
          <div
            class="gradient-card p-6 relative overflow-hidden"
            style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) 400ms both"
          >
            <ModelConsumptionChart :data="tokenStats?.by_model ?? []" />
          </div>
        </div>
      </template>
    </div>

    <!-- ═══════════════════════════════════════════
         Tab 3 — 提示词模板
         ═══════════════════════════════════════════ -->
    <div v-if="activeTab === 'prompt'">
      <!-- ── 列表视图 ── -->
      <template v-if="showPromptList">
        <!-- Skeleton -->
        <div v-if="promptLoading && promptItems.length === 0" class="space-y-4">
          <div class="skeleton h-10 w-32 rounded-lg" />
          <div class="bg-white rounded-xl shadow-sm overflow-hidden">
            <div v-for="i in 5" :key="i" class="flex gap-4 p-4 border-b border-neutral-100">
              <div class="skeleton h-4 flex-1 rounded" />
              <div class="skeleton h-4 w-24 rounded" />
            </div>
          </div>
        </div>

        <template v-else>
          <!-- 筛选 & 操作栏 -->
          <div class="flex items-center justify-between mb-5 gap-3 flex-wrap">
            <div class="flex gap-3 flex-wrap">
              <input
                v-model="promptKeyword"
                type="text" placeholder="搜索模板名称" class="input-macos w-56"
                @keyup.enter="handlePromptSearch"
              />
              <button class="btn-secondary" @click="handlePromptSearch">
                <Search :size="15" />
                搜索
              </button>
            </div>
            <button class="btn-primary" @click="handleAddPrompt">
              <Plus :size="16" />
              新增模板
            </button>
          </div>

          <!-- 表格 -->
          <div class="bg-white rounded-xl shadow-sm overflow-hidden">
            <table class="w-full text-sm">
              <thead class="bg-neutral-50">
                <tr class="border-b border-neutral-200">
                  <th class="px-4 py-3 text-left text-neutral-500 font-medium w-12">#</th>
                  <th class="px-4 py-3 text-left text-neutral-500 font-medium">模板名称</th>
                  <th class="px-4 py-3 text-center text-neutral-500 font-medium">当前版本</th>
                  <th class="px-4 py-3 text-left text-neutral-500 font-medium">更新时间</th>
                  <th class="px-4 py-3 text-center text-neutral-500 font-medium">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, index) in promptItems"
                  :key="item.id"
                  class="border-t border-neutral-100 transition-colors duration-100"
                  :class="index % 2 === 1 ? 'bg-neutral-50/50' : ''"
                >
                  <td class="px-4 py-3 text-neutral-400">{{ (promptPage - 1) * promptPageSize + index + 1 }}</td>
                  <td class="px-4 py-3 font-medium text-neutral-800">{{ item.name }}</td>
                  <td class="px-4 py-3 text-center">
                    <span v-if="item.current_version_number" class="inline-block px-2 py-0.5 rounded-full bg-purple-50 text-purple-600 text-xs font-medium">
                      v{{ item.current_version_number }}
                    </span>
                    <span v-else class="text-neutral-400 text-xs">-</span>
                  </td>
                  <td class="px-4 py-3 text-neutral-500">{{ item.updated_at?.slice(0, 10) ?? '-' }}</td>
                  <td class="px-4 py-3 text-center">
                    <div class="flex items-center justify-center gap-1">
                      <button class="btn-ghost text-primary-500" @click="handleViewVersions(item)" title="查看版本">
                        <Layers :size="14" />
                      </button>
                      <button class="btn-ghost text-primary-500" @click="handleCopyAsNewVersion(item)" title="复制创建新版本">
                        <Copy :size="14" />
                      </button>
                      <button class="btn-ghost text-primary-500" @click="handleEditPrompt(item)">
                        <Pencil :size="14" />
                      </button>
                      <button class="btn-ghost text-danger" @click="handleDeletePrompt(item)">
                        <Trash2 :size="14" />
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="promptItems.length === 0">
                  <td colspan="5" class="px-4 py-16 text-center">
                    <div class="flex flex-col items-center gap-2 text-neutral-400">
                      <Inbox :size="36" />
                      <span>暂无提示词模板</span>
                      <button class="btn-secondary mt-2" @click="handleAddPrompt">
                        <Plus :size="14" />
                        新增模板
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页 -->
          <div v-if="promptTotal > promptPageSize" class="mt-4 flex items-center justify-between text-sm text-neutral-500">
            <span />
            <div class="flex items-center gap-1">
              <button :disabled="promptPage <= 1" class="btn-ghost" @click="promptPage--; loadPromptTemplates()">
                <ChevronLeft :size="16" />上一页
              </button>
              <span class="px-3 py-1 text-neutral-600">第 {{ promptPage }} 页</span>
              <button :disabled="promptPage * promptPageSize >= promptTotal" class="btn-ghost" @click="promptPage++; loadPromptTemplates()">
                下一页<ChevronRight :size="16" />
              </button>
            </div>
          </div>
        </template>
      </template>

      <!-- ── 版本详情视图 ── -->
      <template v-else>
        <!-- 面包屑导航 -->
        <div class="flex items-center gap-2 mb-6">
          <button class="btn-ghost text-primary-500" @click="handleBackToList">
            <ArrowLeft :size="16" />
            返回列表
          </button>
          <span class="text-neutral-300">/</span>
          <span class="text-sm font-medium text-neutral-700">{{ currentTemplateName }}</span>
        </div>

        <!-- Skeleton -->
        <div v-if="versionsLoading" class="grid grid-cols-1 lg:grid-cols-5 gap-6">
          <div class="lg:col-span-2 space-y-3">
            <div v-for="i in 4" :key="i" class="skeleton h-20 w-full rounded-xl" />
          </div>
          <div class="lg:col-span-3">
            <div class="skeleton h-96 w-full rounded-xl" />
          </div>
        </div>

        <div v-else class="grid grid-cols-1 lg:grid-cols-5 gap-6">
          <!-- 左侧：版本时间线 -->
          <div class="lg:col-span-2 space-y-3">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-semibold text-neutral-700">版本历史</h3>
              <button class="btn-primary text-xs px-3 py-1.5" @click="handleCreateVersion">
                <Plus :size="13" />
                创建新版本
              </button>
            </div>

            <div v-if="versions.length === 0" class="bg-white rounded-xl p-8 text-center text-neutral-400 text-sm">
              暂无版本
            </div>

            <div
              v-for="ver in versions" :key="ver.id"
              class="version-card bg-white rounded-xl p-4 cursor-pointer border-2 transition-all duration-150"
              :class="selectedVersionId === ver.id ? 'border-primary-500 shadow-md' : 'border-transparent hover:border-neutral-200'"
              @click="selectedVersionId = ver.id"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-semibold text-neutral-800">v{{ ver.version_number }}</span>
                  <span
                    v-if="ver.is_current"
                    class="inline-block px-1.5 py-0.5 rounded-full bg-green-50 text-green-600 text-[10px] font-medium"
                  >当前</span>
                </div>
                <button
                  v-if="!ver.is_current"
                  class="btn-ghost text-xs text-amber-600"
                  @click.stop="handleRollback(ver)"
                >
                  <RotateCcw :size="12" />
                  回滚
                </button>
              </div>
              <p v-if="ver.remark" class="text-xs text-neutral-500 mb-2 line-clamp-2">{{ ver.remark }}</p>
              <div class="flex items-center gap-3 text-[11px] text-neutral-400">
                <span v-if="ver.created_by">{{ ver.created_by }}</span>
                <span v-if="ver.created_at">{{ ver.created_at?.slice(0, 16).replace('T', ' ') }}</span>
              </div>
            </div>
          </div>

          <!-- 右侧：版本内容 -->
          <div class="lg:col-span-3">
            <div v-if="selectedVersion" class="bg-white rounded-xl shadow-sm overflow-hidden">
              <div class="px-5 py-4 border-b border-neutral-100 flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-semibold text-neutral-800">版本 v{{ selectedVersion.version_number }} 内容</h3>
                  <p v-if="selectedVersion.remark" class="text-xs text-neutral-500 mt-1">{{ selectedVersion.remark }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    class="btn-secondary text-xs px-3 py-1.5"
                    :class="{ 'btn-preview-active': showPreview && previewVersionId === selectedVersion.id }"
                    @click="togglePreview"
                    :title="showPreview ? '退出预览' : '预览模板效果'"
                  >
                    <Eye :size="13" />
                    {{ showPreview && previewVersionId === selectedVersion.id ? '退出预览' : '预览' }}
                  </button>
                  <button class="btn-primary text-xs px-3 py-1.5" @click="handleCreateVersion">
                    <Plus :size="13" />
                    新版本
                  </button>
                </div>
              </div>
              <div class="p-5">
                <!-- 正常内容显示 -->
                <pre v-if="!showPreview || previewVersionId !== selectedVersion.id" class="version-content-display text-sm text-neutral-700 whitespace-pre-wrap font-mono leading-relaxed bg-neutral-50 rounded-lg p-4 max-h-[500px] overflow-y-auto">{{ selectedVersion.content }}</pre>
                <!-- 预览内容显示 -->
                <div v-else class="version-preview-display">
                  <div class="version-preview-banner">
                    <Eye :size="14" :stroke-width="2" />
                    <span>预览模式 - 变量已替换为示例值</span>
                  </div>
                  <pre class="text-sm text-neutral-700 whitespace-pre-wrap font-mono leading-relaxed bg-indigo-50/40 rounded-lg p-4 max-h-[500px] overflow-y-auto border border-indigo-100">{{ previewContent }}</pre>
                  <!-- 变量示例值说明 -->
                  <div class="mt-3 p-3 bg-blue-50/60 rounded-lg border border-blue-100">
                    <p class="text-[11px] text-blue-600 font-medium mb-2">示例值映射：</p>
                    <div class="flex flex-wrap gap-x-3 gap-y-1">
                      <span v-for="(val, key) in variableExamples" :key="key" class="text-[10px] text-blue-500">
                        <code class="font-mono font-semibold">{{ key }}</code> → {{ val }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="bg-white rounded-xl shadow-sm p-12 text-center text-neutral-400 text-sm">
              选择一个版本查看内容
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- ═══════════════════════════════════════════
         弹窗：新增/编辑模型配置
         ═══════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="showLlmModal" class="ef-overlay" @click="handleLlmBackdropClick">
        <div class="ef-dialog" style="max-width: 580px;">
          <div class="ef-header">
            <h2 class="ef-title">{{ editLlmItem ? '编辑配置' : '新增配置' }}</h2>
            <button class="ef-close-btn" @click="showLlmModal = false; modelList = []; modelInputMode = 'select'" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <form ref="llmFormRef" @submit.prevent="handleSaveLlm" class="ef-body" novalidate>
            <div class="ef-field">
              <label class="ef-label">配置名称<span class="ef-required">*</span></label>
              <input v-model="llmForm.name" type="text" class="input-macos" :class="{ 'ef-input-error': llmErrors.name }" @input="delete llmErrors.name" placeholder="如：主配置、备用配置" />
              <span v-if="llmErrors.name" class="ef-error-text">{{ llmErrors.name }}</span>
            </div>
            <div class="ef-field">
              <label class="ef-label">模型名称<span class="ef-required">*</span></label>
              <div class="flex gap-2 items-start">
                <div class="flex-1">
                  <template v-if="modelInputMode === 'select' && modelList.length > 0">
                    <select v-model="llmForm.model" class="input-macos" :class="{ 'ef-input-error': llmErrors.model }" @change="delete llmErrors.model">
                      <option value="" disabled>请选择模型</option>
                      <option v-for="m in modelList" :key="m" :value="m">{{ m }}</option>
                    </select>
                  </template>
                  <template v-else>
                    <input v-model="llmForm.model" type="text" class="input-macos" :class="{ 'ef-input-error': llmErrors.model }" @input="delete llmErrors.model" placeholder="手动输入模型名称" />
                  </template>
                </div>
                <button
                  type="button"
                  class="btn-secondary whitespace-nowrap"
                  style="margin-top: 0"
                  :disabled="modelListLoading"
                  @click="fetchModels"
                >
                  <RotateCcw v-if="modelListLoading" :size="14" class="animate-spin" />
                  <Search v-else :size="14" />
                  {{ modelListLoading ? '拉取中...' : '拉取模型' }}
                </button>
                <button
                  v-if="modelInputMode === 'select' && modelList.length > 0"
                  type="button"
                  class="btn-ghost text-xs whitespace-nowrap"
                  style="margin-top: 4px"
                  @click="modelInputMode = 'manual'"
                  title="切换为手动输入"
                >
                  手动输入
                </button>
                <button
                  v-else-if="modelList.length > 0"
                  type="button"
                  class="btn-ghost text-xs whitespace-nowrap"
                  style="margin-top: 4px"
                  @click="modelInputMode = 'select'"
                  title="切换为下拉选择"
                >
                  下拉选择
                </button>
              </div>
              <span v-if="llmErrors.model" class="ef-error-text">{{ llmErrors.model }}</span>
            </div>
            <div class="ef-field">
              <label class="ef-label">Base URL<span class="ef-required">*</span></label>
              <input v-model="llmForm.api_base_url" type="text" class="input-macos" :class="{ 'ef-input-error': llmErrors.api_base_url }" @input="delete llmErrors.api_base_url" placeholder="如：https://api.openai.com（系统自动补全 /v1 路径）" />
              <span v-if="llmErrors.api_base_url" class="ef-error-text">{{ llmErrors.api_base_url }}</span>
            </div>
            <div class="ef-field">
              <label class="ef-label">
                API Key<span v-if="!editLlmItem" class="ef-required">*</span>
              </label>
              <input
                v-model="llmForm.api_key"
                type="password"
                class="input-macos"
                :class="{ 'ef-input-error': llmErrors.api_key }"
                @input="delete llmErrors.api_key"
                :placeholder="editLlmItem ? '留空则保持原值' : '请输入 API Key'"
                autocomplete="off"
              />
              <span v-if="llmErrors.api_key" class="ef-error-text">{{ llmErrors.api_key }}</span>
            </div>
            <div class="grid grid-cols-3 gap-4">
              <div class="ef-field">
                <label class="ef-label">Temperature</label>
                <input v-model.number="llmForm.temperature" type="number" step="0.1" min="0" max="2" class="input-macos" :class="{ 'ef-input-error': llmErrors.temperature }" @input="delete llmErrors.temperature" />
                <span v-if="llmErrors.temperature" class="ef-error-text">{{ llmErrors.temperature }}</span>
              </div>
              <div class="ef-field">
                <label class="ef-label">Max Tokens</label>
                <input v-model.number="llmForm.max_tokens" type="number" min="1" class="input-macos" />
              </div>
              <div class="ef-field">
                <label class="ef-label">Timeout (s)</label>
                <input v-model.number="llmForm.timeout" type="number" min="1" class="input-macos" />
              </div>
            </div>
            <div class="ef-field">
              <label class="flex items-center gap-2 cursor-pointer select-none">
                <input
                  v-model="llmForm.is_active"
                  type="checkbox"
                  class="w-4 h-4 rounded border-neutral-300 text-primary-500 focus:ring-primary-500"
                />
                <span class="text-sm text-neutral-700">设为当前激活配置</span>
              </label>
            </div>
          </form>
          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="showLlmModal = false; modelList = []; modelInputMode = 'select'">取消</button>
            <button type="button" class="btn-primary" :disabled="llmSaving" @click="handleSaveLlm">
              {{ llmSaving ? '保存中...' : (editLlmItem ? '保存' : '创建') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ═══════════════════════════════════════════
         弹窗：新增/编辑提示词模板
         ═══════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="showPromptModal" class="ef-overlay" @click="handlePromptBackdropClick">
        <div class="ef-dialog" style="max-width: 580px;">
          <div class="ef-header">
            <h2 class="ef-title">{{ editPromptItem ? '编辑模板' : '新增模板' }}</h2>
            <button class="ef-close-btn" @click="showPromptModal = false" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <form @submit.prevent="handleSavePrompt" class="ef-body" novalidate>
            <div class="ef-field">
              <label class="ef-label">模板名称<span class="ef-required">*</span></label>
              <input ref="promptNameRef" v-model="promptForm.name" type="text" class="input-macos" :class="{ 'ef-input-error': promptErrors.name }" @input="delete promptErrors.name" />
              <span v-if="promptErrors.name" class="ef-error-text">{{ promptErrors.name }}</span>
            </div>
            <div class="ef-field">
              <label class="ef-label">描述</label>
              <input v-model="promptForm.description" type="text" class="input-macos" placeholder="可选" />
            </div>
            <div v-if="!editPromptItem" class="ef-field">
              <label class="ef-label">提示词内容<span class="ef-required">*</span></label>
              <div class="editor-wrapper">
                <div class="editor-gutter">
                  <span v-for="n in Math.max(12, promptForm.content.split('\n').length)" :key="n" class="editor-line-num">{{ n }}</span>
                </div>
                <textarea
                  ref="promptModalTextareaRef"
                  v-model="promptForm.content"
                  rows="12"
                  class="input-macos editor-textarea"
                  :class="{ 'ef-input-error': promptErrors.content }"
                  @input="delete promptErrors.content"
                  placeholder="输入提示词内容..."
                />
              </div>
              <div class="editor-footer-bar">
                <span v-if="promptErrors.content" class="ef-error-text">{{ promptErrors.content }}</span>
                <span class="editor-char-count">{{ computeCharCount(promptForm.content) }} 字符</span>
              </div>
            </div>
            <!-- 变量占位符说明 & 一键插入 -->
            <div class="variable-hint-box">
              <div class="variable-hint-title">
                <Info :size="13" :stroke-width="2" />
                支持的变量占位符
                <span class="variable-insert-hint">（点击插入到编辑器）</span>
              </div>
              <div class="variable-hint-grid">
                <button
                  v-for="v in promptVariables" :key="v.name"
                  class="variable-tag variable-tag--clickable"
                  :title="`点击插入 ${v.name} 到编辑器`"
                  type="button"
                  @click="insertVariableToPromptModal(v.name)"
                >
                  <code>{{ v.name }}</code>
                  <span class="variable-tag-desc">{{ v.desc }}</span>
                </button>
              </div>
            </div>
          </form>
          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="showPromptModal = false">取消</button>
            <button type="button" class="btn-primary" :disabled="promptSaving" @click="handleSavePrompt">
              {{ promptSaving ? '保存中...' : (editPromptItem ? '保存' : '创建') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ═══════════════════════════════════════════
         弹窗：创建新版本
         ═══════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="showVersionModal" class="ef-overlay" @click="handleVersionBackdropClick">
        <div class="ef-dialog ef-dialog--version" :class="{ 'ef-dialog--fullscreen': versionFullscreen }" :style="versionFullscreen ? {} : { maxWidth: '640px' }">
          <div class="ef-header">
            <h2 class="ef-title">创建新版本</h2>
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="fullscreen-toggle-btn"
                :title="versionFullscreen ? '退出全屏' : '全屏编辑'"
                @click="toggleVersionFullscreen"
              >
                <Minimize2 v-if="versionFullscreen" :size="15" :stroke-width="1.8" />
                <Maximize2 v-else :size="15" :stroke-width="1.8" />
              </button>
              <button class="ef-close-btn" @click="showVersionModal = false; versionFullscreen = false" type="button">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
          <form @submit.prevent="handleSaveVersion" class="ef-body" :class="{ 'ef-body--fullscreen': versionFullscreen }" novalidate>
            <div class="ef-field">
              <label class="ef-label">提示词内容<span class="ef-required">*</span></label>
              <div class="editor-wrapper" :class="{ 'editor-wrapper--fullscreen': versionFullscreen }">
                <div class="editor-gutter">
                  <span v-for="n in Math.max(16, versionForm.content.split('\n').length)" :key="n" class="editor-line-num">{{ n }}</span>
                </div>
                <textarea
                  ref="versionModalTextareaRef"
                  v-model="versionForm.content"
                  :rows="versionFullscreen ? 28 : 16"
                  class="input-macos editor-textarea"
                  placeholder="输入提示词内容..."
                />
              </div>
              <div class="editor-footer-bar">
                <span class="editor-char-count">{{ computeCharCount(versionForm.content) }} 字符</span>
              </div>
            </div>
            <!-- 变量占位符说明 & 一键插入 -->
            <div class="variable-hint-box">
              <div class="variable-hint-title">
                <Info :size="13" :stroke-width="2" />
                支持的变量占位符
                <span class="variable-insert-hint">（点击插入到编辑器）</span>
              </div>
              <div class="variable-hint-grid">
                <button
                  v-for="v in promptVariables" :key="v.name"
                  class="variable-tag variable-tag--clickable"
                  :title="`点击插入 ${v.name} 到编辑器`"
                  type="button"
                  @click="insertVariableToVersionModal(v.name)"
                >
                  <code>{{ v.name }}</code>
                  <span class="variable-tag-desc">{{ v.desc }}</span>
                </button>
              </div>
            </div>
            <div class="ef-field">
              <label class="ef-label">备注</label>
              <input v-model="versionForm.remark" type="text" class="input-macos" placeholder="描述本次修改内容" />
            </div>
          </form>
          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="showVersionModal = false; versionFullscreen = false">取消</button>
            <button type="button" class="btn-primary" :disabled="versionSaving || !versionForm.content.trim()" @click="handleSaveVersion">
              {{ versionSaving ? '保存中...' : '保存版本' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ═══════════════════════════════════════════
         弹窗：回滚确认
         ═══════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="showRollbackModal" class="ef-overlay" @click="handleRollbackBackdropClick">
        <div class="ef-dialog" style="max-width: 420px;">
          <div class="ef-header">
            <h2 class="ef-title">确认回滚</h2>
            <button class="ef-close-btn" @click="showRollbackModal = false" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <div class="ef-body">
            <p class="text-sm text-neutral-600 leading-relaxed">
              确定要回滚到
              <span class="font-semibold text-neutral-800">v{{ rollbackTarget?.version_number }}</span>
              吗？系统将该版本设为当前活跃版本，原有版本历史将完整保留。
            </p>
            <div v-if="rollbackTarget?.remark" class="mt-3 p-3 bg-neutral-50 rounded-lg">
              <p class="text-xs text-neutral-500 mb-1">版本备注：</p>
              <p class="text-xs text-neutral-700">{{ rollbackTarget.remark }}</p>
            </div>
          </div>
          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="showRollbackModal = false">取消</button>
            <button type="button" class="btn-danger" :disabled="rollbackLoading" @click="confirmRollback">
              {{ rollbackLoading ? '回滚中...' : '确认回滚' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
/* ── Tab 栏 ── */
.tab-bar {
  display: flex;
  gap: 4px;
  margin-bottom: 28px;
  padding: 4px;
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-float);
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-neutral-500);
  cursor: pointer;
  transition: all var(--duration-normal) ease;
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--color-neutral-700);
  background-color: var(--color-neutral-50);
}

.tab-btn--active {
  color: var(--color-primary-600);
  background-color: var(--color-primary-50);
  box-shadow: 0 1px 3px rgba(99, 102, 241, 0.12);
}

/* ── 模型配置行 ── */
.llm-row--active {
  background-color: rgba(16, 185, 129, 0.04) !important;
  border-left: 3px solid var(--color-success);
}

.llm-row--active td:first-child {
  padding-left: 12px;
}

/* ── Active Badge（名称旁） ── */
.active-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 7px;
  background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
  color: #059669;
  font-size: 10px;
  font-weight: 600;
  border-radius: 20px;
  letter-spacing: 0.02em;
  border: 1px solid rgba(16, 185, 129, 0.18);
  white-space: nowrap;
}

/* ── Active Indicator（当前使用列） ── */
.active-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #059669;
}

.active-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #10B981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.18);
  animation: activeDotPulse 2s ease-in-out infinite;
}

@keyframes activeDotPulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.18); }
  50% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.08); }
}

/* ── 激活按钮 ── */
.btn-activate {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background-color: transparent;
  color: var(--color-primary-500);
  border: 1px solid var(--color-primary-200);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.btn-activate:hover {
  background-color: var(--color-primary-50);
  border-color: var(--color-primary-400);
  color: var(--color-primary-600);
  box-shadow: 0 1px 4px rgba(99, 102, 241, 0.15);
}

.btn-activate:active {
  background-color: var(--color-primary-100);
}

/* ── 变量占位符提示 ── */
.variable-hint-box {
  background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: 12px 14px;
}

.variable-hint-title {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-neutral-600);
  margin-bottom: 8px;
}

.variable-insert-hint {
  font-weight: 400;
  color: var(--color-neutral-400);
  font-size: 11px;
}

.variable-hint-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.variable-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: 6px;
  font-size: 11px;
  line-height: 1.4;
  color: var(--color-neutral-600);
  cursor: default;
  transition: border-color var(--duration-fast) ease, background var(--duration-fast) ease;
}

.variable-tag:hover {
  border-color: var(--color-primary-300);
  background-color: var(--color-primary-50);
}

.variable-tag--clickable {
  cursor: pointer;
  user-select: none;
}

.variable-tag--clickable:active {
  transform: scale(0.96);
  background-color: var(--color-primary-100);
  border-color: var(--color-primary-400);
}

.variable-tag code {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary-600);
  background: none;
  padding: 0;
}

.variable-tag-desc {
  color: var(--color-neutral-400);
  font-size: 10px;
}

/* ── 弹窗覆盖层 ── */
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
  max-width: 520px;
  max-height: 90vh;
  background: #FFFFFF;
  border-radius: 14px;
  box-shadow: var(--shadow-overlay);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: ef-scale-in 250ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
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
  gap: 18px;
}

.ef-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ef-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-neutral-700);
  line-height: 1;
}

.ef-required {
  color: var(--color-danger);
  margin-left: 2px;
  font-weight: 500;
}

.ef-input-error {
  border-color: var(--color-danger) !important;
  box-shadow: 0 0 0 3px rgba(255, 69, 58, 0.12) !important;
}

.ef-error-text {
  font-size: 12px;
  color: var(--color-danger);
  line-height: 1;
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

/* ── Toast 通知 ── */
.toast-item {
  min-width: 260px;
  max-width: 400px;
  cursor: pointer;
  pointer-events: auto;
  animation: toastSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.toast-success {
  background: linear-gradient(135deg, rgba(236, 253, 245, 0.95) 0%, rgba(209, 250, 229, 0.95) 100%);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: #065f46;
}

.toast-error {
  background: linear-gradient(135deg, rgba(254, 242, 242, 0.95) 0%, rgba(254, 226, 226, 0.95) 100%);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #991b1b;
}

.toast-info {
  background: linear-gradient(135deg, rgba(236, 253, 245, 0.95) 0%, rgba(207, 250, 254, 0.95) 100%);
  border: 1px solid rgba(6, 182, 212, 0.2);
  color: #164e63;
}

.toast-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  flex-shrink: 0;
}

.toast-success .toast-icon-wrap {
  background-color: rgba(16, 185, 129, 0.15);
  color: #059669;
}

.toast-error .toast-icon-wrap {
  background-color: rgba(239, 68, 68, 0.15);
  color: #DC2626;
}

.toast-info .toast-icon-wrap {
  background-color: rgba(6, 182, 212, 0.15);
  color: #0891B2;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(24px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

/* Toast TransitionGroup */
.toast-enter-active {
  animation: toastSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.toast-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 1, 1);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(24px) scale(0.96);
}

.toast-move {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

/* ── 折线图动画 ── */
@keyframes tokenLineDrawIn {
  from { stroke-dashoffset: 2000; }
  to   { stroke-dashoffset: 0; }
}

.token-line-animate {
  stroke-dasharray: 2000;
  stroke-dashoffset: 2000;
  animation: tokenLineDrawIn 1.2s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
}

/* ══════════════════════════════════════════════════
   编辑器增强：行号 + 等宽字体 + 字数统计
   ══════════════════════════════════════════════════ */
.editor-wrapper {
  display: flex;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  background: var(--color-neutral-0);
  overflow: hidden;
  transition: border-color var(--duration-fast) ease, box-shadow var(--duration-fast) ease;
}

.editor-wrapper:focus-within {
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.editor-gutter {
  display: flex;
  flex-direction: column;
  padding: 10px 0;
  min-width: 36px;
  background: var(--color-neutral-50);
  border-right: 1px solid var(--color-neutral-200);
  user-select: none;
  overflow: hidden;
}

.editor-line-num {
  display: block;
  height: 19.2px;
  line-height: 19.2px;
  text-align: right;
  padding: 0 8px 0 4px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--color-neutral-350, #a3a3a3);
  font-variant-numeric: tabular-nums;
}

.editor-textarea {
  flex: 1;
  border: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  resize: vertical;
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 19.2px;
  padding: 10px 12px;
  min-height: 228px;
  background: transparent;
}

.editor-textarea::placeholder {
  color: var(--color-neutral-400);
}

.editor-footer-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 22px;
}

.editor-char-count {
  font-size: 11px;
  color: var(--color-neutral-400);
  font-variant-numeric: tabular-nums;
  margin-left: auto;
}

/* ══════════════════════════════════════════════════
   全屏编辑模式
   ══════════════════════════════════════════════════ */
.fullscreen-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 6px;
  background: transparent;
  border: 1px solid var(--color-neutral-200);
  color: var(--color-neutral-500);
  cursor: pointer;
  padding: 0;
  transition: all var(--duration-fast) ease;
}

.fullscreen-toggle-btn:hover {
  background-color: var(--color-neutral-100);
  color: var(--color-neutral-700);
  border-color: var(--color-neutral-300);
}

.ef-dialog--fullscreen {
  max-width: 100vw !important;
  width: 100vw !important;
  height: 100vh !important;
  max-height: 100vh !important;
  border-radius: 0 !important;
  animation: ef-fullscreen-in 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.ef-body--fullscreen {
  flex: 1;
  overflow-y: auto;
}

.ef-body--fullscreen .editor-wrapper {
  flex: 1;
}

.ef-body--fullscreen .editor-wrapper--fullscreen {
  min-height: 0;
  flex: 1;
}

.ef-body--fullscreen .editor-wrapper--fullscreen .editor-textarea {
  min-height: 0;
  flex: 1;
}

@keyframes ef-fullscreen-in {
  from {
    opacity: 0;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* ══════════════════════════════════════════════════
   版本预览
   ══════════════════════════════════════════════════ */
.btn-preview-active {
  background: var(--color-primary-50) !important;
  border-color: var(--color-primary-400) !important;
  color: var(--color-primary-600) !important;
}

.version-preview-display {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.version-preview-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary-600);
}

.version-content-display {
  transition: opacity 0.2s ease;
}
</style>
