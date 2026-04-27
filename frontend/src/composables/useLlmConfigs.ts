import { ref, computed, type Ref } from 'vue'
import { adminApi } from '@/api/admin'
import { quotaExceededEvent } from '@/api/http'
import type {
  LlmConfig, LlmConfigCreate, LlmConfigUpdate,
  QuotaStatus, ChainData,
} from '@/types'
import type { useToast } from './useToast'

export function useLlmConfigs(
  toast: ReturnType<typeof useToast>,
  chains: Ref<ChainData[]>,
) {
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
    daily_token_quota: 0,
  })

  const modelList = ref<string[]>([])
  const modelListLoading = ref(false)
  const modelInputMode = ref<'select' | 'manual'>('select')

  /* ═══════════════════════════════════════════════
     限额相关状态与工具函数
     ═══════════════════════════════════════════════ */
  const quotaStatusList = ref<QuotaStatus[]>([])

  async function loadQuotaStatus() {
    try {
      const res = await adminApi.getQuotaStatus()
      quotaStatusList.value = res.data.quota_status ?? []
    } catch {
      // silently ignore
    }
  }

  function getQuotaForConfig(configId: number): QuotaStatus | undefined {
    return quotaStatusList.value.find(q => q.config_id === configId)
  }

  function quotaPercent(q: QuotaStatus): number {
    if (!q.limit || q.limit <= 0) return 0
    return Math.min(100, (q.used / q.limit) * 100)
  }

  function quotaBarColor(q: QuotaStatus): string {
    const pct = quotaPercent(q)
    if (pct >= 95) return 'bg-red-500'
    if (pct >= 80) return 'bg-amber-500'
    return 'bg-emerald-500'
  }

  function quotaPercentForConfig(configId: number): number {
    const quota = getQuotaForConfig(configId)
    return quota ? quotaPercent(quota) : 0
  }

  function quotaBarColorForConfig(configId: number): string {
    const quota = getQuotaForConfig(configId)
    return quota ? quotaBarColor(quota) : 'bg-neutral-200'
  }

  function formatQuotaNumber(val: number): string {
    if (val >= 1_000_000) return (val / 1_000_000).toFixed(val % 1_000_000 === 0 ? 0 : 1) + 'M'
    if (val >= 1_000) return (val / 1_000).toFixed(val % 1_000 === 0 ? 0 : 1) + 'K'
    return val.toLocaleString('zh-CN')
  }

  const hasQuotaLimits = computed(() => quotaStatusList.value.some(q => q.limit > 0))

  const overallQuotaStatus = computed(() => {
    const items = quotaStatusList.value.filter(q => q.limit > 0)
    if (items.length === 0) return { text: '无限制', color: 'bg-neutral-50 text-neutral-400 border-neutral-200' }
    const worstPct = Math.max(...items.map(q => quotaPercent(q)))
    if (worstPct >= 100) return { text: '已耗尽', color: 'bg-red-50 text-red-600 border-red-200' }
    if (worstPct >= 95) return { text: '即将耗尽', color: 'bg-red-50 text-red-500 border-red-200' }
    if (worstPct >= 80) return { text: '告警', color: 'bg-amber-50 text-amber-600 border-amber-200' }
    return { text: '全部正常', color: 'bg-emerald-50 text-emerald-600 border-emerald-200' }
  })

  function percentTextColor(q: QuotaStatus): string {
    const pct = quotaPercent(q)
    if (pct >= 95) return 'text-red-500'
    if (pct >= 80) return 'text-amber-600'
    return 'text-emerald-600'
  }

  const quotaPresets = [
    { label: '100K', value: 100_000 },
    { label: '500K', value: 500_000 },
    { label: '1M', value: 1_000_000 },
    { label: '5M', value: 5_000_000 },
    { label: '不限制', value: 0 },
  ]

  function handleQuotaExceeded(e: Event) {
    const detail = (e as CustomEvent).detail
    const quota = detail.quota
    const resetAt = quota?.reset_at
      ? new Date(quota.reset_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      : '明日'
    const used = quota ? formatQuotaNumber(quota.used) : '?'
    const limit = quota ? formatQuotaNumber(quota.limit) : '?'
    toast.showToast(`Token 配额已用完 (${used}/${limit})，将在 ${resetAt} 重置`, 'error')
  }

  /* ═══════════════════════════════════════════════
     链路相关 helpers（依赖 chains 参数）
     ═══════════════════════════════════════════════ */
  const chainRuntimeMap = computed(() => {
    const map = new Map<number, { isAssigned: boolean; isEnabled: boolean; isRuntimeActive: boolean; status: 'running' | 'standby' | 'cooling' | 'inactive' }>()

    for (const chain of chains.value) {
      const runtime = getEffectiveChainRuntime(chain)
      const isEnabled = !!runtime?.is_enabled
      const activeId = runtime?.active_config_id ?? chain.primary_config_id
      const overallStatus = runtime?.status ?? 'normal'

      const memberIds = [
        chain.primary_config_id,
        ...chain.fallbacks.map(f => f.config_id),
      ]

      for (const memberId of memberIds) {
        let status: 'running' | 'standby' | 'cooling' | 'inactive'
        if (!isEnabled) {
          status = 'inactive'
        } else if (overallStatus === 'cooling') {
          status = 'cooling'
        } else if (activeId === memberId) {
          status = 'running'
        } else {
          status = 'standby'
        }

        map.set(memberId, {
          isAssigned: true,
          isEnabled,
          isRuntimeActive: activeId === memberId,
          status,
        })
      }
    }

    return map
  })

  function isRuntimeActive(item: LlmConfig): boolean {
    const runtime = chainRuntimeMap.value.get(item.id)
    if (runtime) return runtime.isRuntimeActive
    return !!item.is_current_runtime
  }

  function isChainAssigned(item: LlmConfig): boolean {
    return chainRuntimeMap.value.has(item.id) || !!item.fallback_group_id || (item.role != null && item.role !== 'standalone')
  }

  function resolvedRole(item: LlmConfig): 'primary' | 'fallback' | 'standalone' {
    if (item.role === 'primary' || item.role === 'fallback') return item.role
    for (const chain of chains.value) {
      if (chain.primary_config_id === item.id) return 'primary'
      if (chain.fallbacks.some(f => f.config_id === item.id)) return 'fallback'
    }
    return 'standalone'
  }

  function resolvedFallbackOrder(item: LlmConfig): number {
    if (item.fallback_order && item.fallback_order > 0) return item.fallback_order
    for (const chain of chains.value) {
      const fallback = chain.fallbacks.find(f => f.config_id === item.id)
      if (fallback) return fallback.order
    }
    return 0
  }

  function isChainEnabled(item: LlmConfig): boolean {
    const runtime = chainRuntimeMap.value.get(item.id)
    if (runtime) return runtime.isEnabled
    return !!item.is_chain_enabled
  }

  function isChainManagedEditTarget(item: LlmConfig | null): boolean {
    return !!item && isChainAssigned(item)
  }

  function chainUsageText(item: LlmConfig): string {
    if (isRuntimeActive(item)) return '当前使用'
    if (isChainEnabled(item)) return '链路已启用'
    return '链路未启用'
  }

  function chainStatusMeta(item: LlmConfig): { dot: string; text: string; tone: string } {
    const runtime = chainRuntimeMap.value.get(item.id)
    const status = runtime?.status ?? item.chain_runtime_status
    switch (status) {
      case 'running':
        return { dot: 'bg-emerald-500', text: '运行中', tone: 'text-emerald-600' }
      case 'standby':
        return { dot: 'bg-sky-400', text: '待机', tone: 'text-sky-600' }
      case 'cooling':
        return { dot: 'bg-amber-500', text: '冷却中', tone: 'text-amber-600' }
      case 'inactive':
        return { dot: 'bg-neutral-300', text: '未启用', tone: 'text-neutral-500' }
      default:
        return { dot: 'bg-neutral-300', text: '—', tone: 'text-neutral-400' }
    }
  }

  function getEffectiveChainRuntime(chain: ChainData | null): {
    active_config_id: number | null
    status: 'idle' | 'normal' | 'degraded' | 'cooling'
    is_enabled: boolean
  } | null {
    if (!chain) return null
    if (chain.runtime) return chain.runtime

    const primary = chain.primary_config
    const fallbackConfigs = chain.fallbacks.map(f => f.config)
    const activeMember =
      [primary, ...fallbackConfigs].find(config => config?.is_current_runtime || config?.is_active) ?? primary

    return {
      active_config_id: activeMember?.id ?? chain.primary_config_id,
      status: activeMember && activeMember.id !== chain.primary_config_id ? 'degraded' : 'normal',
      is_enabled: true,
    }
  }

  function chainRuntimeSummary(chain: ChainData | null): string {
    const runtime = getEffectiveChainRuntime(chain)
    if (!chain || !runtime) return '未读取链路运行状态'
    if (!runtime.is_enabled) return '当前未启用'
    if (runtime.status === 'cooling') return '链路冷却中'

    const servingConfig =
      chain.primary_config.id === runtime.active_config_id
        ? chain.primary_config
        : chain.fallbacks.find(f => f.config_id === runtime.active_config_id)?.config

    if (!servingConfig) return '运行状态同步中'
    if (runtime.status === 'degraded') return `已切换至 ${servingConfig.name}`
    return `当前使用 ${servingConfig.name}`
  }

  function chainRuntimeBadgeClass(chain: ChainData | null): string {
    switch (getEffectiveChainRuntime(chain)?.status) {
      case 'degraded':
        return 'bg-amber-50 text-amber-600'
      case 'cooling':
        return 'bg-red-50 text-red-600'
      case 'normal':
        return 'bg-emerald-50 text-emerald-600'
      default:
        return 'bg-neutral-100 text-neutral-500'
    }
  }

  /* ═══════════════════════════════════════════════
     模型配置 CRUD
     ═══════════════════════════════════════════════ */
  async function fetchModels() {
    const url = llmForm.value.api_base_url.trim()
    const key = llmForm.value.api_key.trim()
    if (!url) {
      toast.showToast('请先填写 Base URL', 'error')
      return
    }
    if (!key) {
      if (editLlmItem.value) {
        toast.showToast('编辑模式下需填写 API Key 才能拉取模型列表，也可手动输入模型名称', 'info')
        modelInputMode.value = 'manual'
      } else {
        toast.showToast('请先填写 API Key', 'error')
      }
      return
    }
    modelListLoading.value = true
    modelList.value = []
    try {
      const res = await adminApi.fetchModels(url, key)
      const models: string[] = res.data.models ?? []
      if (models.length === 0) {
        toast.showToast('未获取到可用模型', 'info')
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
      toast.showToast(String(msg), 'error')
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
      loadQuotaStatus()
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
      daily_token_quota: 0,
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
      is_active: item.is_current_runtime ?? item.is_active,
      daily_token_quota: item.daily_token_quota ?? 0,
    }
    modelList.value = []
    modelInputMode.value = 'select'
    showLlmModal.value = true
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
          daily_token_quota: llmForm.value.daily_token_quota ?? 0,
        }
        if (!isChainManagedEditTarget(editLlmItem.value)) {
          payload.is_active = llmForm.value.is_active
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
          daily_token_quota: llmForm.value.daily_token_quota ?? 0,
        })
      }
      showLlmModal.value = false
      modelList.value = []
      modelInputMode.value = 'select'
      loadLlmConfigs()
      toast.showToast('配置已保存，已全局生效')
    } catch {
      toast.showToast('保存失败，请重试', 'error')
    } finally {
      llmSaving.value = false
    }
  }

  async function handleDeleteLlm(item: LlmConfig) {
    if (resolvedRole(item) === 'primary') {
      if (!confirm(`「${item.name}」是链路主模型，删除后该链路将被解散，所有备用模型将恢复为独立配置。确定删除？`)) return
    } else if (resolvedRole(item) === 'fallback') {
      if (!confirm(`「${item.name}」是链路备用模型，删除后将从链路中移除。确定删除？`)) return
    } else if (isRuntimeActive(item)) {
      if (!confirm('该配置当前正在使用中，确定要删除吗？删除后需要激活其他配置。')) return
    } else {
      if (!confirm('确定删除该配置？此操作不可恢复。')) return
    }
    try {
      await adminApi.deleteLlmConfig(item.id)
      loadLlmConfigs()
      toast.showToast('配置已删除', 'info')
    } catch {
      toast.showToast('删除失败，请重试', 'error')
    }
  }

  async function handleActivateLlm(item: LlmConfig) {
    if (isRuntimeActive(item)) return
    try {
      await adminApi.activateLlmConfig(item.id)
      loadLlmConfigs()
      toast.showToast(`「${item.name}」已激活，已全局生效`)
    } catch {
      toast.showToast('激活失败，请重试', 'error')
    }
  }

  function handleLlmBackdropClick(e: MouseEvent) {
    if ((e.target as HTMLElement).classList.contains('ef-overlay')) {
      showLlmModal.value = false
      modelList.value = []
      modelInputMode.value = 'select'
    }
  }

  return {
    /* state */
    llmItems,
    llmTotal,
    llmPage,
    llmPageSize,
    llmLoading,
    showLlmModal,
    editLlmItem,
    llmSaving,
    llmErrors,
    llmForm,
    modelList,
    modelListLoading,
    modelInputMode,
    /* quota state */
    quotaStatusList,
    quotaPresets,
    /* quota computed */
    hasQuotaLimits,
    overallQuotaStatus,
    /* chain helpers */
    chainRuntimeMap,
    /* functions */
    fetchModels,
    loadLlmConfigs,
    handleAddLlm,
    handleEditLlm,
    handleSaveLlm,
    handleDeleteLlm,
    handleActivateLlm,
    handleLlmBackdropClick,
    loadQuotaStatus,
    handleQuotaExceeded,
    /* chain helper functions */
    isRuntimeActive,
    isChainAssigned,
    resolvedRole,
    resolvedFallbackOrder,
    isChainEnabled,
    isChainManagedEditTarget,
    chainUsageText,
    chainStatusMeta,
    getEffectiveChainRuntime,
    chainRuntimeSummary,
    chainRuntimeBadgeClass,
    /* quota functions */
    getQuotaForConfig,
    quotaPercent,
    quotaBarColor,
    quotaPercentForConfig,
    quotaBarColorForConfig,
    formatQuotaNumber,
    percentTextColor,
  }
}
