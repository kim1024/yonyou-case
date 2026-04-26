<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Shield, Check, Info, Loader2 } from 'lucide-vue-next'
import { adminApi } from '@/api/admin'

interface SettingItem {
  key: string
  value: number
  description: string
  label: string
  min: number
  max: number
  unit: string
}

const settings = ref<SettingItem[]>([])
const loading = ref(false)
const saving = ref(false)
const hasChanges = ref(false)

/* ═══════════════════════════════════════════════
   全局 Toast 通知
   ═══════════════════════════════════════════════ */
interface ToastItem {
  id: number
  message: string
  type: 'success' | 'error'
}
const toastItems = ref<ToastItem[]>([])
let toastIdCounter = 0

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

const PARAM_META: Record<string, { label: string; description: string; min: number; max: number; unit: string }> = {
  generate_max_requests: {
    label: '每小时最大生成次数',
    description: '单个客户端在 1 小时内允许的最大生成请求次数',
    min: 1,
    max: 100,
    unit: '次/小时',
  },
  generate_window_seconds: {
    label: '限流窗口时长',
    description: '滑动窗口的统计时长，用于计算请求频率',
    min: 60,
    max: 86400,
    unit: '秒',
  },
  generate_cooldown_seconds: {
    label: '请求冷却间隔',
    description: '两次生成请求之间的最小间隔时间',
    min: 5,
    max: 300,
    unit: '秒',
  },
  max_concurrent: {
    label: '最大并发请求数',
    description: '同时处理的最大生成请求数量',
    min: 1,
    max: 20,
    unit: '个',
  },
}

async function loadSettings() {
  loading.value = true
  try {
    const res = await adminApi.getSecuritySettings()
    settings.value = res.data.items.map((item: any) => ({
      ...item,
      ...PARAM_META[item.key],
    }))
    hasChanges.value = false
  } catch {
    showToast('加载安全配置失败', 'error')
  } finally {
    loading.value = false
  }
}

function handleChange() {
  hasChanges.value = true
}

function clampValue(item: SettingItem) {
  if (item.value < item.min) item.value = item.min
  if (item.value > item.max) item.value = item.max
  handleChange()
}

async function handleSave() {
  saving.value = true
  try {
    const payload: Record<string, number> = {}
    for (const s of settings.value) {
      payload[s.key] = s.value
    }
    await adminApi.updateSecuritySettings(payload)
    hasChanges.value = false
    showToast('安全配置已保存，已实时生效')
  } catch {
    showToast('保存失败，请重试', 'error')
  } finally {
    saving.value = false
  }
}

onMounted(loadSettings)
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
            }"
            @click="removeToast(toast.id)"
          >
            <div class="toast-icon-wrap">
              <Check v-if="toast.type === 'success'" :size="14" :stroke-width="2.5" />
              <svg v-else width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
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
          style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);"
        >
          <Shield :size="20" color="#fff" :stroke-width="1.8" />
        </div>
        <div>
          <h1>安全设置</h1>
          <p>管理访问限制和安全防护参数，修改后实时生效</p>
        </div>
      </div>
    </div>

    <!-- ═══ 设置卡片 ═══ -->
    <div
      class="gradient-card"
      style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both"
    >
      <!-- Skeleton Loading -->
      <div v-if="loading" class="p-6 space-y-8">
        <div v-for="i in 4" :key="i" class="flex items-center gap-6">
          <div class="flex-1 space-y-2">
            <div class="skeleton h-4 w-40 rounded" />
            <div class="skeleton h-3 w-64 rounded" />
          </div>
          <div class="skeleton h-10 w-28 rounded-lg" />
        </div>
      </div>

      <!-- 设置表单 -->
      <div v-else class="divide-y divide-neutral-100">
        <div
          v-for="(item, index) in settings"
          :key="item.key"
          class="flex flex-col sm:flex-row sm:items-center gap-4 p-6"
          :style="{ animationDelay: `${index * 60}ms` }"
          style="animation: fadeUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both"
        >
          <!-- 左侧：标签和描述 -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <h3 class="text-sm font-semibold text-neutral-800">{{ item.label }}</h3>
            </div>
            <p class="text-xs text-neutral-500 mt-1 leading-relaxed">{{ item.description }}</p>
            <p class="text-[11px] text-neutral-400 mt-1.5">
              允许范围：<span class="font-medium text-neutral-500">{{ item.min }}</span>
              ~
              <span class="font-medium text-neutral-500">{{ item.max }}</span>
              {{ item.unit }}
            </p>
          </div>

          <!-- 右侧：输入框 + 单位标签 -->
          <div class="flex items-center gap-2 flex-shrink-0">
            <div class="relative">
              <input
                v-model.number="item.value"
                type="number"
                :min="item.min"
                :max="item.max"
                class="input-macos w-28 text-center tabular-nums"
                @input="clampValue(item)"
              />
            </div>
            <span
              class="inline-block px-2.5 py-1.5 rounded-lg text-xs font-medium bg-neutral-100 text-neutral-600 whitespace-nowrap"
            >
              {{ item.unit }}
            </span>
          </div>
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div
        v-if="settings.length > 0"
        class="flex items-center justify-between px-6 py-4 border-t border-neutral-100"
      >
        <div class="flex items-center gap-2 text-xs text-neutral-400">
          <Info :size="14" :stroke-width="1.8" />
          <span>修改后点击保存即刻生效，无需重启服务</span>
        </div>
        <button
          class="btn-primary"
          :disabled="saving || !hasChanges"
          @click="handleSave"
        >
          <Loader2 v-if="saving" :size="15" class="animate-spin" />
          <Check v-else :size="15" :stroke-width="2.5" />
          {{ saving ? '保存中...' : '保存配置' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
</style>
