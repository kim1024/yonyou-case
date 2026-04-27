import { ref, computed, watch, type Ref } from 'vue'
import { adminApi } from '@/api/admin'
import type { LlmConfig, ChainData } from '@/types'
import type { useToast } from './useToast'

export function useChainManager(
  toast: ReturnType<typeof useToast>,
  chains: Ref<ChainData[]>,
  llmItems: Ref<LlmConfig[]>,
  opts: {
    isChainAssigned: (item: LlmConfig) => boolean
    resolvedRole: (item: LlmConfig) => 'primary' | 'fallback' | 'standalone'
    isRuntimeActive: (item: LlmConfig) => boolean
    isChainEnabled: (item: LlmConfig) => boolean
    chainStatusMeta: (item: LlmConfig) => { dot: string; text: string; tone: string }
    getEffectiveChainRuntime: (chain: ChainData | null) => { active_config_id: number | null; status: 'idle' | 'normal' | 'degraded' | 'cooling'; is_enabled: boolean } | null
    chainRuntimeSummary: (chain: ChainData | null) => string
    chainRuntimeBadgeClass: (chain: ChainData | null) => string
  },
  reloadLlmConfigs: () => Promise<void>,
) {
  const chainDrawerVisible = ref(false)
  const chainDrawerConfig = ref<LlmConfig | null>(null)
  const chainDrawerMode = ref<'unassigned' | 'editing'>('unassigned')
  const chainAssignmentChoice = ref<'primary' | 'join'>('primary')
  const chainSelectedConfigId = ref<number | null>(null)
  const joinTargetChainId = ref<number | null>(null)
  const initialFallbackId = ref<number | null>(null)
  const chainData = ref<ChainData | null>(null)
  const chainThresholds = ref({ failure_threshold: 3, timeout_seconds: 5, cooldown_seconds: 300 })
  const chainSaving = ref(false)
  const addFallbackId = ref<number | null>(null)

  const availableForChain = computed(() =>
    llmItems.value.filter(c => opts.resolvedRole(c) === 'standalone')
  )

  const availableStandaloneOptions = computed(() =>
    availableForChain.value.map(c => ({
      label: `${c.name} (${c.model})`,
      value: c.id,
    }))
  )

  const existingChainOptions = computed(() =>
    chains.value.map(c => ({
      label: c.primary_config?.name || `主配置 #${c.primary_config_id}`,
      value: c.id,
    }))
  )

  const availablePrimaryFallbackOptions = computed(() => {
    if (!chainSelectedConfigId.value) return []
    return availableForChain.value
      .filter(c => c.id !== chainSelectedConfigId.value)
      .map(c => ({ label: `${c.name} (${c.model})`, value: c.id }))
  })

  const availableFallbackOptions = computed(() => {
    if (!chainData.value) return []
    const chainConfigIds = new Set([
      chainData.value.primary_config_id,
      ...chainData.value.fallbacks.map(f => f.config_id),
    ])
    return llmItems.value
      .filter(c => !chainConfigIds.has(c.id) && opts.resolvedRole(c) === 'standalone')
      .map(c => ({ label: `${c.name} (${c.model})`, value: c.id }))
  })

  async function loadChains() {
    try {
      const res = await adminApi.getChains()
      chains.value = res.data.chains || []
    } catch (e) {
      console.error('Failed to load chains', e)
    }
  }

  async function openChainDrawer(config: LlmConfig) {
    chainDrawerConfig.value = config
    chainSelectedConfigId.value = config.id
    chainAssignmentChoice.value = 'primary'
    joinTargetChainId.value = null
    initialFallbackId.value = null
    addFallbackId.value = null

    if (!opts.isChainAssigned(config)) {
      chainDrawerMode.value = 'unassigned'
      chainData.value = null
    } else {
      chainDrawerMode.value = 'editing'
      const chain = chains.value.find(c =>
        c.primary_config_id === config.id ||
        c.fallbacks.some(f => f.config_id === config.id)
      )
      if (chain) {
        chainData.value = JSON.parse(JSON.stringify(chain))
        chainThresholds.value = {
          failure_threshold: chain.failure_threshold,
          timeout_seconds: chain.timeout_seconds,
          cooldown_seconds: chain.cooldown_seconds,
        }
      }
    }

    chainDrawerVisible.value = true
  }

  watch(chainSelectedConfigId, (configId) => {
    if (!configId) {
      chainDrawerConfig.value = null
      initialFallbackId.value = null
      return
    }

    const selected = llmItems.value.find(c => c.id === configId) ?? null
    chainDrawerConfig.value = selected

    if (initialFallbackId.value === configId) {
      initialFallbackId.value = null
    }

    const hasSelectedFallback = availablePrimaryFallbackOptions.value.some(opt => opt.value === initialFallbackId.value)
    if (!hasSelectedFallback) {
      initialFallbackId.value = null
    }
  })

  async function handleChainAssignment() {
    const selectedConfig = llmItems.value.find(c => c.id === chainSelectedConfigId.value) ?? chainDrawerConfig.value
    if (!selectedConfig) {
      toast.showToast('请选择模型配置', 'error')
      return
    }

    if (chainAssignmentChoice.value === 'primary') {
      if (!initialFallbackId.value) {
        toast.showToast('请至少选择 1 个备用模型', 'error')
        return
      }
      try {
        await adminApi.createChain({
          primary_config_id: selectedConfig.id,
          fallback_config_ids: [initialFallbackId.value],
          failure_threshold: 3,
          timeout_seconds: 5,
          cooldown_seconds: 300,
        })
        toast.showToast('链路已创建并立即生效')
        await loadChains()
        await reloadLlmConfigs()
        const updatedConfig = llmItems.value.find(c => c.id === selectedConfig.id)
        if (updatedConfig) openChainDrawer(updatedConfig)
      } catch (e: any) {
        toast.showToast(e.response?.data?.detail || '创建失败', 'error')
      }
    } else if (chainAssignmentChoice.value === 'join' && joinTargetChainId.value) {
      try {
        await adminApi.addFallback(joinTargetChainId.value, { config_id: selectedConfig.id })
        toast.showToast('已加入链路')
        await loadChains()
        await reloadLlmConfigs()
        chainDrawerVisible.value = false
      } catch (e: any) {
        toast.showToast(e.response?.data?.detail || '加入失败', 'error')
      }
    }
  }

  function moveFallbackUp(idx: number) {
    if (!chainData.value || idx <= 0) return
    const list = chainData.value.fallbacks
    ;[list[idx], list[idx - 1]] = [list[idx - 1], list[idx]]
    list.forEach((f, i) => f.order = i + 1)
  }

  function moveFallbackDown(idx: number) {
    if (!chainData.value || idx >= chainData.value.fallbacks.length - 1) return
    const list = chainData.value.fallbacks
    ;[list[idx], list[idx + 1]] = [list[idx + 1], list[idx]]
    list.forEach((f, i) => f.order = i + 1)
  }

  async function handleAddFallback(configId: number) {
    if (!chainData.value) return
    try {
      await adminApi.addFallback(chainData.value.id, { config_id: configId })
      const res = await adminApi.getChain(chainData.value.id)
      chainData.value = res.data
      await reloadLlmConfigs()
      addFallbackId.value = null
      toast.showToast('已添加备用模型')
    } catch (e: any) {
      toast.showToast(e.response?.data?.detail || '添加失败', 'error')
    }
  }

  async function removeFallbackFromChain(configId: number) {
    if (!chainData.value) return
    try {
      await adminApi.removeFallback(chainData.value.id, configId)
      await loadChains()
      await reloadLlmConfigs()

      const updatedChain = chains.value.find(c => c.id === chainData.value?.id)
      if (updatedChain) {
        chainData.value = JSON.parse(JSON.stringify(updatedChain))
      } else {
        toast.showToast('链路已自动解散')
        chainDrawerVisible.value = false
      }
    } catch (e: any) {
      toast.showToast(e.response?.data?.detail || '移除失败', 'error')
    }
  }

  async function handleSaveChain() {
    if (!chainData.value) return
    chainSaving.value = true
    try {
      const fallbackIds = chainData.value.fallbacks.map(f => f.config_id)
      await adminApi.updateChain(chainData.value.id, {
        failure_threshold: chainThresholds.value.failure_threshold,
        timeout_seconds: chainThresholds.value.timeout_seconds,
        cooldown_seconds: chainThresholds.value.cooldown_seconds,
        fallback_config_ids: fallbackIds,
      })
      toast.showToast('链路已保存')
      await loadChains()
      await reloadLlmConfigs()
      chainDrawerVisible.value = false
    } catch (e: any) {
      toast.showToast(e.response?.data?.detail || '保存失败', 'error')
    } finally {
      chainSaving.value = false
    }
  }

  async function handleDissolveChain() {
    if (!chainData.value) return
    if (!confirm('解散链路后，所有模型将恢复为独立配置，故障转移策略将被清除。确定解散？')) return
    try {
      await adminApi.deleteChain(chainData.value.id)
      toast.showToast('链路已解散')
      await loadChains()
      await reloadLlmConfigs()
      chainDrawerVisible.value = false
    } catch (e: any) {
      toast.showToast(e.response?.data?.detail || '解散失败', 'error')
    }
  }

  async function handleCreateChain() {
    if (availableForChain.value.length < 2) {
      toast.showToast('至少需要 2 个独立配置才能创建链路', 'error')
      return
    }
    openChainDrawer(availableForChain.value[0])
  }

  return {
    /* state */
    chainDrawerVisible,
    chainDrawerConfig,
    chainDrawerMode,
    chainAssignmentChoice,
    chainSelectedConfigId,
    joinTargetChainId,
    initialFallbackId,
    chainData,
    chainThresholds,
    chainSaving,
    addFallbackId,
    /* computed */
    availableForChain,
    availableStandaloneOptions,
    existingChainOptions,
    availablePrimaryFallbackOptions,
    availableFallbackOptions,
    /* functions */
    loadChains,
    openChainDrawer,
    handleChainAssignment,
    moveFallbackUp,
    moveFallbackDown,
    handleAddFallback,
    removeFallbackFromChain,
    handleSaveChain,
    handleDissolveChain,
    handleCreateChain,
    /* re-exported from opts for template use */
    chainRuntimeSummary: opts.chainRuntimeSummary,
    chainRuntimeBadgeClass: opts.chainRuntimeBadgeClass,
    chainStatusMeta: opts.chainStatusMeta,
  }
}
