<script setup lang="ts">
import { Link2, Gauge } from 'lucide-vue-next'
import type { useChainManager } from '@/composables/useChainManager'
import type { useLlmConfigs } from '@/composables/useLlmConfigs'

const props = defineProps<{
  cm: ReturnType<typeof useChainManager>
  llm: ReturnType<typeof useLlmConfigs>
}>()
</script>

<template>
  <Teleport to="body">
    <div v-if="cm.chainDrawerVisible.value" class="chain-drawer-overlay" @click.self="cm.chainDrawerVisible.value = false">
      <div class="chain-drawer-panel">
        <!-- 头部 -->
        <div class="chain-drawer-header">
          <h2 class="chain-drawer-title">
            <Link2 :size="18" class="text-emerald-600" />
            链路管理 — {{ cm.chainDrawerConfig.value?.name || '' }}
          </h2>
          <button class="ef-close-btn" @click="cm.chainDrawerVisible.value = false" type="button">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>

        <!-- 内容 -->
        <div class="chain-drawer-body">

          <!-- MODE: 未分配 -->
          <div v-if="cm.chainDrawerMode.value === 'unassigned'">
            <p class="text-sm text-neutral-600 mb-4">
              调用链路至少需要 2 个模型。启用链路后，独立模型设置将自动失效，系统只按链路中的主备顺序调用。
            </p>
            <div class="mt-4">
              <label class="ef-label">选择模型配置</label>
              <select v-model="cm.chainSelectedConfigId.value" class="input-macos mt-1">
                <option :value="null" disabled>请选择</option>
                <option v-for="opt in cm.availableStandaloneOptions.value" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>
            <div class="space-y-3">
              <label class="chain-radio-card" :class="{ 'chain-radio-card--active': cm.chainAssignmentChoice.value === 'primary' }">
                <input type="radio" v-model="cm.chainAssignmentChoice.value" value="primary" class="sr-only" />
                <div class="chain-radio-dot" :class="{ 'chain-radio-dot--active': cm.chainAssignmentChoice.value === 'primary' }" />
                <div>
                  <div class="text-sm font-medium text-neutral-800">设为主模型</div>
                  <div class="text-xs text-neutral-500 mt-0.5">创建链路并立即生效，需同时选择至少 1 个备用模型</div>
                </div>
              </label>
              <label class="chain-radio-card" :class="{ 'chain-radio-card--active': cm.chainAssignmentChoice.value === 'join' }">
                <input type="radio" v-model="cm.chainAssignmentChoice.value" value="join" class="sr-only" />
                <div class="chain-radio-dot" :class="{ 'chain-radio-dot--active': cm.chainAssignmentChoice.value === 'join' }" />
                <div>
                  <div class="text-sm font-medium text-neutral-800">作为备用模型</div>
                  <div class="text-xs text-neutral-500 mt-0.5">加入已有的主模型链路，作为故障转移备选</div>
                </div>
              </label>
            </div>

            <div v-if="cm.chainAssignmentChoice.value === 'primary'" class="mt-4">
              <label class="ef-label">选择备用模型</label>
              <select v-model="cm.initialFallbackId.value" class="input-macos mt-1">
                <option :value="null" disabled>请选择</option>
                <option v-for="opt in cm.availablePrimaryFallbackOptions.value" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>

            <div v-if="cm.chainAssignmentChoice.value === 'join'" class="mt-4">
              <label class="ef-label">选择主模型链路</label>
              <select v-model="cm.joinTargetChainId.value" class="input-macos mt-1">
                <option :value="null" disabled>请选择</option>
                <option v-for="opt in cm.existingChainOptions.value" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>

            <div class="chain-drawer-footer">
              <button class="btn-secondary" @click="cm.chainDrawerVisible.value = false">取消</button>
              <button
                class="btn-primary"
                :disabled="!cm.chainSelectedConfigId.value || (cm.chainAssignmentChoice.value === 'join' && !cm.joinTargetChainId.value) || (cm.chainAssignmentChoice.value === 'primary' && !cm.initialFallbackId.value)"
                @click="cm.handleChainAssignment()"
              >确认</button>
            </div>
          </div>

          <!-- MODE: 编辑链路 -->
          <div v-if="cm.chainDrawerMode.value === 'editing' && cm.chainData.value">
            <!-- 主模型卡片 -->
            <div class="chain-primary-card">
              <div class="flex items-center gap-2">
                <span class="chain-star">★</span>
                <span class="text-sm font-semibold text-neutral-800">主模型：{{ cm.chainData.value.primary_config?.name }}</span>
                <span class="ml-auto px-2 py-0.5 rounded-full text-[11px] font-medium" :class="cm.chainRuntimeBadgeClass(cm.chainData.value)">
                  {{ cm.chainRuntimeSummary(cm.chainData.value) }}
                </span>
              </div>
              <div class="text-xs text-neutral-500 mt-1">
                {{ cm.chainData.value.primary_config?.model }} · temp={{ cm.chainData.value.primary_config?.temperature }}
              </div>
            </div>

            <!-- 链路限额概览卡片 -->
            <div v-if="cm.chainData.value.quota_info && cm.chainData.value.quota_info.limit > 0" class="chain-quota-card">
              <div class="flex items-center gap-2 mb-3">
                <Gauge :size="15" class="text-indigo-500" />
                <span class="text-sm font-semibold text-neutral-700">链路限额概览</span>
                <span class="text-[10px] text-neutral-400 ml-auto">主备模型共享此限额</span>
              </div>
              <div class="grid grid-cols-3 gap-3 mb-3">
                <div class="text-center">
                  <div class="text-[11px] text-neutral-400 mb-0.5">每日限额</div>
                  <div class="text-sm font-semibold text-neutral-800 tabular-nums">{{ llm.formatQuotaNumber(cm.chainData.value.quota_info.limit) }}</div>
                </div>
                <div class="text-center">
                  <div class="text-[11px] text-neutral-400 mb-0.5">今日已用</div>
                  <div class="text-sm font-semibold text-neutral-800 tabular-nums">{{ llm.formatQuotaNumber(cm.chainData.value.quota_info.used) }}</div>
                </div>
                <div class="text-center">
                  <div class="text-[11px] text-neutral-400 mb-0.5">剩余额度</div>
                  <div class="text-sm font-semibold tabular-nums" :class="cm.chainData.value.quota_info.remaining <= 0 ? 'text-red-500' : 'text-emerald-600'">
                    {{ llm.formatQuotaNumber(cm.chainData.value.quota_info.remaining) }}
                  </div>
                </div>
              </div>
              <div class="h-1.5 rounded-full bg-neutral-100 overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-300"
                  :class="
                    (cm.chainData.value.quota_info.used / cm.chainData.value.quota_info.limit) >= 0.95 ? 'bg-red-500' :
                    (cm.chainData.value.quota_info.used / cm.chainData.value.quota_info.limit) >= 0.8 ? 'bg-amber-500' :
                    'bg-emerald-500'
                  "
                  :style="{ width: Math.min(100, (cm.chainData.value.quota_info.used / cm.chainData.value.quota_info.limit) * 100) + '%' }"
                />
              </div>
            </div>

            <!-- 故障切换指示 -->
            <div class="chain-fallback-divider">
              <span class="chain-fallback-divider-line" />
              <span class="chain-fallback-divider-text">↓ 故障自动切换</span>
              <span class="chain-fallback-divider-line" />
            </div>

            <!-- 备用模型列表 -->
            <div v-if="cm.chainData.value.fallbacks.length === 0" class="chain-empty-fallback">
              <span class="text-neutral-400 text-xs">暂无备用模型，请通过下方添加</span>
            </div>
            <div v-for="(fb, idx) in cm.chainData.value.fallbacks" :key="fb.config_id" class="chain-fallback-row">
              <span class="chain-fallback-order">{{ idx + 1 }}.</span>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-neutral-800 truncate flex items-center gap-2">
                  <span class="truncate">{{ fb.config?.name }}</span>
                  <span
                    v-if="fb.config?.chain_runtime_status"
                    class="shrink-0 px-1.5 py-0.5 rounded-full text-[10px] font-medium"
                    :class="fb.config.chain_runtime_status === 'running'
                      ? 'bg-emerald-50 text-emerald-600'
                      : fb.config.chain_runtime_status === 'standby'
                        ? 'bg-sky-50 text-sky-600'
                        : fb.config.chain_runtime_status === 'cooling'
                          ? 'bg-amber-50 text-amber-600'
                          : 'bg-neutral-100 text-neutral-500'"
                  >
                    {{ cm.chainStatusMeta(fb.config).text }}
                  </span>
                </div>
                <div class="text-xs text-neutral-400 truncate">{{ fb.config?.model }}</div>
              </div>
              <button
                class="btn-ghost text-xs px-1.5"
                :disabled="idx === 0"
                @click="cm.moveFallbackUp(idx)"
                title="上移"
              >↑</button>
              <button
                class="btn-ghost text-xs px-1.5"
                :disabled="idx === cm.chainData.value.fallbacks.length - 1"
                @click="cm.moveFallbackDown(idx)"
                title="下移"
              >↓</button>
              <button
                class="btn-ghost text-danger text-xs px-1.5"
                @click="cm.removeFallbackFromChain(fb.config_id)"
                title="移除"
              >✕</button>
            </div>

            <!-- 添加备用模型 -->
            <div class="mt-3">
              <select
                v-model="cm.addFallbackId.value"
                class="input-macos text-sm"
                @change="cm.addFallbackId.value !== null && cm.handleAddFallback(cm.addFallbackId.value)"
              >
                <option :value="null" disabled>+ 添加备用模型</option>
                <option v-for="opt in cm.availableFallbackOptions.value" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>

            <!-- 故障转移策略 -->
            <div class="chain-threshold-section">
              <h4 class="text-sm font-semibold text-neutral-700 mb-3">故障转移策略</h4>
              <div class="chain-threshold-row">
                <label class="text-xs text-neutral-600 w-24 shrink-0">连续失败次数</label>
                <input
                  v-model.number="cm.chainThresholds.value.failure_threshold"
                  type="number"
                  min="1"
                  max="20"
                  class="input-macos w-20 text-center text-sm"
                />
                <span class="text-xs text-neutral-400 ml-1">次</span>
              </div>
              <div class="chain-threshold-row">
                <label class="text-xs text-neutral-600 w-24 shrink-0">超时阈值</label>
                <input
                  v-model.number="cm.chainThresholds.value.timeout_seconds"
                  type="number"
                  min="1"
                  max="20"
                  class="input-macos w-20 text-center text-sm"
                />
                <span class="text-xs text-neutral-400 ml-1">秒</span>
              </div>
              <div class="chain-threshold-row">
                <label class="text-xs text-neutral-600 w-24 shrink-0">冷却恢复</label>
                <input
                  v-model.number="cm.chainThresholds.value.cooldown_seconds"
                  type="number"
                  min="60"
                  max="3600"
                  class="input-macos w-20 text-center text-sm"
                />
                <span class="text-xs text-neutral-400 ml-1">秒</span>
              </div>
            </div>

            <!-- 底部按钮 -->
            <div class="chain-drawer-footer">
              <button class="btn-danger-ghost" @click="cm.handleDissolveChain()">解散链路</button>
              <div class="flex-1" />
              <button class="btn-secondary" @click="cm.chainDrawerVisible.value = false">取消</button>
              <button class="btn-primary" :disabled="cm.chainSaving.value" @click="cm.handleSaveChain()">
                {{ cm.chainSaving.value ? '保存中...' : '保存' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
@import './llm-dialog.css';

/* ── 链路管理 Drawer ── */
.chain-drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(2px);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.15s ease;
}

.chain-drawer-panel {
  width: 480px;
  max-width: 90vw;
  height: 100%;
  background: #fff;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  animation: slideInRight 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideInRight {
  from { transform: translateX(100%); opacity: 0.6; }
  to { transform: translateX(0); opacity: 1; }
}

.chain-drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-neutral-100);
  flex-shrink: 0;
}

.chain-drawer-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-neutral-800);
  margin: 0;
}

.chain-drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.chain-drawer-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--color-neutral-100);
}

/* ── 未分配模式 Radio 卡片 ── */
.chain-radio-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  border: 1.5px solid var(--color-neutral-200);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.chain-radio-card:hover {
  border-color: var(--color-primary-300);
  background: var(--color-primary-50);
}

.chain-radio-card--active {
  border-color: var(--color-primary-400);
  background: var(--color-primary-50);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.chain-radio-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid var(--color-neutral-300);
  flex-shrink: 0;
  margin-top: 1px;
  transition: all 0.15s ease;
  position: relative;
}

.chain-radio-dot--active {
  border-color: var(--color-primary-500);
}

.chain-radio-dot--active::after {
  content: '';
  position: absolute;
  top: 3px; left: 3px;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--color-primary-500);
}

/* ── 编辑模式：主模型卡片 ── */
.chain-primary-card {
  padding: 14px 16px;
  background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: 10px;
}

.chain-star {
  color: #F59E0B;
  font-size: 14px;
}

/* ── 故障切换分隔线 ── */
.chain-fallback-divider {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 16px 0;
}

.chain-fallback-divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--color-neutral-200), transparent);
}

.chain-fallback-divider-text {
  font-size: 12px;
  color: var(--color-neutral-400);
  white-space: nowrap;
}

/* ── 备用模型行 ── */
.chain-fallback-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--color-neutral-50);
  border: 1px solid var(--color-neutral-100);
  border-radius: 8px;
  margin-bottom: 6px;
  transition: background 0.1s;
}

.chain-fallback-row:hover {
  background: var(--color-neutral-100);
}

.chain-fallback-order {
  font-weight: 700;
  font-size: 13px;
  color: var(--color-neutral-400);
  min-width: 20px;
}

.chain-empty-fallback {
  text-align: center;
  padding: 20px;
  border: 1px dashed var(--color-neutral-200);
  border-radius: 8px;
  margin-bottom: 8px;
}

/* ── 故障转移策略 ── */
.chain-threshold-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-neutral-100);
}

.chain-threshold-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

/* ── 危险按钮 Ghost 变体 ── */
.btn-danger-ghost {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  background: transparent;
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-danger);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-danger-ghost:hover {
  background: rgba(239, 68, 68, 0.06);
}

/* ── 链路限额概览卡片 ── */
.chain-quota-card {
  margin-top: 16px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
  border: 1px solid rgba(139, 92, 246, 0.15);
  border-radius: 10px;
}
</style>
