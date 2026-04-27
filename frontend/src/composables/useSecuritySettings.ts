import { ref } from 'vue'
import { adminApi } from '@/api/admin'
import type { useToast } from './useToast'

export interface SecuritySettingItem {
  key: string
  value: number
  description: string
  label: string
  min: number
  max: number
  unit: string
}

const securityParamMeta: Record<string, { label: string; description: string; min: number; max: number; unit: string }> = {
  generate_max_requests: {
    label: '每小时最大生成次数',
    description: '单个客户端在 1 小时内允许的最大生成请求次数',
    min: 1, max: 100, unit: '次/小时',
  },
  generate_window_seconds: {
    label: '限流窗口时长',
    description: '滑动窗口的统计时长，用于计算请求频率',
    min: 60, max: 86400, unit: '秒',
  },
  generate_cooldown_seconds: {
    label: '请求冷却间隔',
    description: '两次生成请求之间的最小间隔时间',
    min: 5, max: 300, unit: '秒',
  },
  max_concurrent: {
    label: '最大并发请求数',
    description: '同时处理的最大生成请求数量',
    min: 1, max: 20, unit: '个',
  },
}

export function useSecuritySettings(toast: ReturnType<typeof useToast>) {
  const securitySettings = ref<SecuritySettingItem[]>([])
  const securityLoading = ref(false)
  const securitySaving = ref(false)
  const securityHasChanges = ref(false)

  async function loadSecuritySettings() {
    securityLoading.value = true
    try {
      const res = await adminApi.getSecuritySettings()
      securitySettings.value = res.data.items.map((item: any) => ({
        ...item,
        ...securityParamMeta[item.key],
      }))
      securityHasChanges.value = false
    } catch {
      toast.showToast('加载安全配置失败', 'error')
    } finally {
      securityLoading.value = false
    }
  }

  function handleSecurityChange() {
    securityHasChanges.value = true
  }

  function clampSecurityValue(item: SecuritySettingItem) {
    if (item.value < item.min) item.value = item.min
    if (item.value > item.max) item.value = item.max
    handleSecurityChange()
  }

  async function handleSecuritySave() {
    securitySaving.value = true
    try {
      const payload: Record<string, number> = {}
      for (const s of securitySettings.value) {
        payload[s.key] = s.value
      }
      await adminApi.updateSecuritySettings(payload)
      securityHasChanges.value = false
      toast.showToast('安全配置已保存，已实时生效')
    } catch {
      toast.showToast('保存失败，请重试', 'error')
    } finally {
      securitySaving.value = false
    }
  }

  return {
    securitySettings,
    securityLoading,
    securitySaving,
    securityHasChanges,
    loadSecuritySettings,
    handleSecurityChange,
    clampSecurityValue,
    handleSecuritySave,
  }
}
