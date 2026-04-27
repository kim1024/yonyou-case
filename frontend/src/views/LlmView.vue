<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { Cpu, Activity, Sparkles, Shield, Check, X, Info } from 'lucide-vue-next'
import { quotaExceededEvent } from '@/api/http'

/* ── Composables ── */
import { useToast } from '@/composables/useToast'
import { useLlmConfigs } from '@/composables/useLlmConfigs'
import { useChainManager } from '@/composables/useChainManager'
import { useTokenStats } from '@/composables/useTokenStats'
import { usePromptTemplates } from '@/composables/usePromptTemplates'
import { useSecuritySettings } from '@/composables/useSecuritySettings'

/* ── Sub-components ── */
import LlmConfigTab from '@/components/admin/llm/LlmConfigTab.vue'
import TokenStatsTab from '@/components/admin/llm/TokenStatsTab.vue'
import PromptTab from '@/components/admin/llm/PromptTab.vue'
import SecurityTab from '@/components/admin/llm/SecurityTab.vue'
import ChainDrawer from '@/components/admin/llm/ChainDrawer.vue'

import type { ChainData } from '@/types'

/* ═══════════════════════════════════════════════
   初始化 Composables
   ═══════════════════════════════════════════════ */
// Shared chains ref - both composables read/write the same data
const chains = ref<ChainData[]>([])

const toast = useToast()
const llm = useLlmConfigs(toast, chains)
const cm = useChainManager(
  toast,
  chains,
  llm.llmItems,
  {
    isChainAssigned: llm.isChainAssigned,
    resolvedRole: llm.resolvedRole,
    isRuntimeActive: llm.isRuntimeActive,
    isChainEnabled: llm.isChainEnabled,
    chainStatusMeta: llm.chainStatusMeta,
    getEffectiveChainRuntime: llm.getEffectiveChainRuntime,
    chainRuntimeSummary: llm.chainRuntimeSummary,
    chainRuntimeBadgeClass: llm.chainRuntimeBadgeClass,
  },
  llm.loadLlmConfigs,
)
const tokenStats = useTokenStats()
const prompt = usePromptTemplates(toast)
const security = useSecuritySettings(toast)

/* ═══════════════════════════════════════════════
   公共状态
   ═══════════════════════════════════════════════ */
const activeTab = ref<'llm' | 'token' | 'prompt' | 'security'>('llm')

/* ═══════════════════════════════════════════════
   初始化 & 销毁
   ═══════════════════════════════════════════════ */
onMounted(() => {
  llm.loadLlmConfigs()
  cm.loadChains()
  tokenStats.loadTokenStats()
  prompt.loadPromptTemplates()
  llm.loadQuotaStatus()
  quotaExceededEvent.addEventListener('quota-exceeded', llm.handleQuotaExceeded)
})

/* ResizeObserver: 用 watch 而非 onMounted，处理 v-if 隐藏的 tab 切换后元素才挂载的情况 */
let trendResizeObs: ResizeObserver | null = null
watch(tokenStats.trendContainerEl, (el) => {
  trendResizeObs?.disconnect()
  if (el) {
    tokenStats.trendContainerWidth.value = el.offsetWidth
    trendResizeObs = new ResizeObserver(([entry]) => { tokenStats.trendContainerWidth.value = entry.contentRect.width })
    trendResizeObs.observe(el)
  }
})

onBeforeUnmount(() => {
  trendResizeObs?.disconnect()
  quotaExceededEvent.removeEventListener('quota-exceeded', llm.handleQuotaExceeded)
})

/* Tab 切换时按需加载 */
function switchTab(tab: 'llm' | 'token' | 'prompt' | 'security') {
  activeTab.value = tab
  if (tab === 'llm' && llm.llmItems.value.length === 0) llm.loadLlmConfigs()
  if (tab === 'token') {
    if (!tokenStats.tokenStats.value) tokenStats.loadTokenStats()
    llm.loadQuotaStatus()
  }
  if (tab === 'prompt' && prompt.promptItems.value.length === 0) prompt.loadPromptTemplates()
  if (tab === 'security' && security.securitySettings.value.length === 0) security.loadSecuritySettings()
}
</script>

<template>
  <div class="animate-fade-up">
    <!-- ═══ Toast 通知层 ═══ -->
    <Teleport to="body">
      <div class="fixed top-5 right-5 z-[100] flex flex-col gap-2 pointer-events-none">
        <TransitionGroup name="toast">
          <div
            v-for="item in toast.toastItems.value"
            :key="item.id"
            class="pointer-events-auto toast-item flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg backdrop-blur-sm"
            :class="{
              'toast-success': item.type === 'success',
              'toast-error': item.type === 'error',
              'toast-info': item.type === 'info',
            }"
            @click="toast.removeToast(item.id)"
          >
            <div class="toast-icon-wrap">
              <Check v-if="item.type === 'success'" :size="14" :stroke-width="2.5" />
              <X v-else-if="item.type === 'error'" :size="14" :stroke-width="2.5" />
              <Info v-else :size="14" :stroke-width="2.5" />
            </div>
            <span class="text-sm font-medium">{{ item.message }}</span>
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
          <p>管理 LLM 配置、Token 消耗、提示词模板和安全设置</p>
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
      <button
        class="tab-btn"
        :class="{ 'tab-btn--active': activeTab === 'security' }"
        @click="switchTab('security')"
      >
        <Shield :size="15" :stroke-width="1.8" />
        安全设置
      </button>
    </div>

    <!-- ═══ Tab 内容 ═══ -->
    <LlmConfigTab v-if="activeTab === 'llm'" :llm="llm" :cm="cm" />

    <TokenStatsTab
      v-if="activeTab === 'token'"
      :ts="tokenStats"
      :has-quota-limits="llm.hasQuotaLimits.value"
      :overall-quota-status="llm.overallQuotaStatus.value"
      :quota-status-list="llm.quotaStatusList.value"
      :quota-percent="llm.quotaPercent"
      :quota-bar-color="llm.quotaBarColor"
      :format-quota-number="llm.formatQuotaNumber"
      :percent-text-color="llm.percentTextColor"
    />

    <PromptTab v-if="activeTab === 'prompt'" :p="prompt" />

    <SecurityTab
      v-if="activeTab === 'security'"
      :security-settings="security.securitySettings.value"
      :security-loading="security.securityLoading.value"
      :security-saving="security.securitySaving.value"
      :security-has-changes="security.securityHasChanges.value"
      @clamp-value="security.clampSecurityValue($event)"
      @save="security.handleSecuritySave()"
    />

    <!-- ═══ 链路管理 Drawer ═══ -->
    <ChainDrawer :cm="cm" :llm="llm" />
  </div>
</template>

<style>
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

/* ── 限额快捷按钮 ── */
.quota-preset-btn {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  color: var(--color-neutral-500);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  white-space: nowrap;
}

.quota-preset-btn:hover {
  border-color: var(--color-primary-300);
  color: var(--color-primary-600);
  background: var(--color-primary-50);
}

.quota-preset-btn--active {
  border-color: var(--color-primary-400);
  background: var(--color-primary-50);
  color: var(--color-primary-600);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
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
