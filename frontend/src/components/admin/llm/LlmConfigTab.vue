<script setup lang="ts">
import {
  Plus, Pencil, Trash2, Check, ChevronLeft, ChevronRight,
  Inbox, Zap, Search, RotateCcw,
  AlertTriangle, Link2, Info,
} from 'lucide-vue-next'
import type { useLlmConfigs } from '@/composables/useLlmConfigs'
import type { useChainManager } from '@/composables/useChainManager'
import ChainDrawer from './ChainDrawer.vue'

const props = defineProps<{
  llm: ReturnType<typeof useLlmConfigs>
  cm: ReturnType<typeof useChainManager>
}>()
</script>

<template>
  <div>
    <!-- Skeleton Loading -->
    <div v-if="llm.llmLoading.value && llm.llmItems.value.length === 0" class="space-y-4">
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
          共 <span class="font-medium text-neutral-700">{{ llm.llmTotal.value }}</span> 条配置
        </span>
        <div class="flex items-center gap-2">
          <button
            class="btn-secondary"
            :disabled="cm.availableForChain.value.length < 2"
            @click="cm.handleCreateChain()"
          >
            <Link2 :size="16" />
            新增链路
          </button>
          <button class="btn-primary" @click="llm.handleAddLlm()">
            <Plus :size="16" />
            新增配置
          </button>
        </div>
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
                <th class="px-4 py-3 text-center text-neutral-500 font-medium">每日限额</th>
                <th class="px-4 py-3 text-center text-neutral-500 font-medium">当前使用</th>
                <th class="px-4 py-3 text-center text-neutral-500 font-medium">角色</th>
                <th class="px-4 py-3 text-center text-neutral-500 font-medium">链路状态</th>
                <th class="px-4 py-3 text-center text-neutral-500 font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, index) in llm.llmItems.value"
                :key="item.id"
                class="border-t border-neutral-100 transition-colors duration-100 llm-row"
                :class="[
                  index % 2 === 1 ? 'bg-neutral-50/50' : '',
                  llm.isRuntimeActive(item) ? 'llm-row--active' : '',
                ]"
              >
                <td class="px-4 py-3 text-neutral-400">{{ (llm.llmPage.value - 1) * llm.llmPageSize + index + 1 }}</td>
                <td class="px-4 py-3 font-medium text-neutral-800">
                  <div class="flex items-center gap-2">
                    <span>{{ item.name }}</span>
                    <span v-if="llm.isRuntimeActive(item)" class="active-badge">
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
                <!-- 每日限额列 -->
                <td class="px-4 py-3 text-center">
                  <template v-if="!item.daily_token_quota || item.daily_token_quota <= 0">
                    <span class="text-neutral-400 text-xs">不限制</span>
                  </template>
                  <template v-else-if="llm.getQuotaForConfig(item.id)">
                    <div class="inline-flex flex-col items-center gap-1">
                      <span class="text-xs tabular-nums text-neutral-600">
                        {{ llm.formatQuotaNumber(llm.getQuotaForConfig(item.id)?.used ?? 0) }}/{{ llm.formatQuotaNumber(llm.getQuotaForConfig(item.id)?.limit ?? 0) }}
                      </span>
                      <div class="relative w-20 h-1 rounded-full bg-neutral-100 overflow-hidden">
                        <div
                          class="absolute inset-y-0 left-0 rounded-full transition-all duration-300"
                          :class="llm.quotaBarColorForConfig(item.id)"
                          :style="{ width: Math.min(100, llm.quotaPercentForConfig(item.id)) + '%' }"
                        />
                      </div>
                      <template v-if="llm.quotaPercentForConfig(item.id) >= 95">
                        <span class="inline-flex items-center gap-0.5 text-[10px] text-red-500 font-medium">
                          <AlertTriangle :size="10" />
                          {{ llm.quotaPercentForConfig(item.id) >= 100 ? '已耗尽' : '即将耗尽' }}
                        </span>
                      </template>
                    </div>
                  </template>
                  <template v-else>
                    <span class="text-xs tabular-nums text-neutral-500">
                      {{ llm.formatQuotaNumber(item.daily_token_quota) }}/天
                    </span>
                  </template>
                </td>
                <td class="px-4 py-3 text-center">
                  <template v-if="!llm.isChainAssigned(item)">
                    <button
                      v-if="!llm.isRuntimeActive(item)"
                      class="btn-activate"
                      @click="llm.handleActivateLlm(item)"
                    >
                      <Check :size="13" :stroke-width="2.5" />
                      设为当前
                    </button>
                    <span v-else class="active-indicator">
                      <span class="active-dot" />
                      当前使用
                    </span>
                  </template>
                  <template v-else>
                    <span
                      class="inline-flex items-center gap-1.5 text-xs"
                      :class="llm.isRuntimeActive(item) ? 'text-emerald-600' : (llm.isChainEnabled(item) ? 'text-sky-600' : 'text-neutral-500')"
                    >
                      <span
                        class="inline-block w-2 h-2 rounded-full"
                        :class="llm.isRuntimeActive(item) ? 'bg-emerald-500' : (llm.isChainEnabled(item) ? 'bg-sky-400' : 'bg-neutral-300')"
                      />
                      {{ llm.chainUsageText(item) }}
                    </span>
                  </template>
                </td>
                <!-- 角色列 -->
                <td class="px-4 py-3 text-center">
                  <span
                    v-if="llm.resolvedRole(item) === 'primary'"
                    class="inline-block px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 text-xs font-medium"
                  >主模型</span>
                  <span
                    v-else-if="llm.resolvedRole(item) === 'fallback'"
                    class="inline-block px-2 py-0.5 rounded-full bg-amber-50 text-amber-600 text-xs font-medium"
                  >备用→{{ llm.resolvedFallbackOrder(item) }}</span>
                  <span
                    v-else
                    class="inline-block px-2 py-0.5 rounded-full bg-neutral-100 text-neutral-500 text-xs font-medium"
                  >独立</span>
                </td>
                <!-- 链路状态列 -->
                <td class="px-4 py-3 text-center">
                  <template v-if="!llm.isChainAssigned(item)">
                    <span class="text-neutral-400">—</span>
                  </template>
                  <template v-else>
                    <span class="inline-flex items-center gap-1.5 text-xs">
                      <span
                        class="inline-block w-2 h-2 rounded-full"
                        :class="llm.chainStatusMeta(item).dot"
                      />
                      <span :class="llm.chainStatusMeta(item).tone">
                        {{ llm.chainStatusMeta(item).text }}
                      </span>
                    </span>
                  </template>
                </td>
                <!-- 操作列 -->
                <td class="px-4 py-3 text-center">
                  <div class="flex items-center justify-center gap-1">
                    <button
                      class="btn-ghost text-emerald-600"
                      title="链路管理"
                      @click="cm.openChainDrawer(item)"
                    >
                      <Link2 :size="14" />
                    </button>
                    <button class="btn-ghost text-primary-500" @click="llm.handleEditLlm(item)">
                      <Pencil :size="14" />
                    </button>
                    <button class="btn-ghost text-danger" @click="llm.handleDeleteLlm(item)">
                      <Trash2 :size="14" />
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="llm.llmItems.value.length === 0">
                <td colspan="12" class="px-4 py-16 text-center">
                  <div class="flex flex-col items-center gap-2 text-neutral-400">
                    <Inbox :size="36" />
                    <span>暂无模型配置</span>
                    <button class="btn-secondary mt-2" @click="llm.handleAddLlm()">
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
      <div v-if="llm.llmTotal.value > llm.llmPageSize" class="mt-4 flex items-center justify-between text-sm text-neutral-500">
        <span />
        <div class="flex items-center gap-1">
          <button :disabled="llm.llmPage.value <= 1" class="btn-ghost" @click="llm.llmPage.value--; llm.loadLlmConfigs()">
            <ChevronLeft :size="16" />上一页
          </button>
          <span class="px-3 py-1 text-neutral-600">第 {{ llm.llmPage.value }} 页</span>
          <button :disabled="llm.llmPage.value * llm.llmPageSize >= llm.llmTotal.value" class="btn-ghost" @click="llm.llmPage.value++; llm.loadLlmConfigs()">
            下一页<ChevronRight :size="16" />
          </button>
        </div>
      </div>
    </template>

    <!-- ═══════════════════════════════════════════
         弹窗：新增/编辑模型配置
         ═══════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="llm.showLlmModal.value" class="ef-overlay" @click="llm.handleLlmBackdropClick($event)">
        <div class="ef-dialog" style="max-width: 580px;">
          <div class="ef-header">
            <h2 class="ef-title">{{ llm.editLlmItem.value ? '编辑配置' : '新增配置' }}</h2>
            <button class="ef-close-btn" @click="llm.showLlmModal.value = false; llm.modelList.value = []; llm.modelInputMode.value = 'select'" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <form @submit.prevent="llm.handleSaveLlm()" class="ef-body" novalidate>
            <div class="ef-field">
              <label class="ef-label">配置名称<span class="ef-required">*</span></label>
              <input v-model="llm.llmForm.value.name" type="text" class="input-macos" :class="{ 'ef-input-error': llm.llmErrors.value.name }" @input="delete llm.llmErrors.value.name" placeholder="如：主配置、备用配置" />
              <span v-if="llm.llmErrors.value.name" class="ef-error-text">{{ llm.llmErrors.value.name }}</span>
            </div>
            <div class="ef-field">
              <label class="ef-label">模型名称<span class="ef-required">*</span></label>
              <div class="flex gap-2 items-start">
                <div class="flex-1">
                  <template v-if="llm.modelInputMode.value === 'select' && llm.modelList.value.length > 0">
                    <select v-model="llm.llmForm.value.model" class="input-macos" :class="{ 'ef-input-error': llm.llmErrors.value.model }" @change="delete llm.llmErrors.value.model">
                      <option value="" disabled>请选择模型</option>
                      <option v-for="m in llm.modelList.value" :key="m" :value="m">{{ m }}</option>
                    </select>
                  </template>
                  <template v-else>
                    <input v-model="llm.llmForm.value.model" type="text" class="input-macos" :class="{ 'ef-input-error': llm.llmErrors.value.model }" @input="delete llm.llmErrors.value.model" placeholder="手动输入模型名称" />
                  </template>
                </div>
                <button
                  type="button"
                  class="btn-secondary whitespace-nowrap"
                  style="margin-top: 0"
                  :disabled="llm.modelListLoading.value"
                  @click="llm.fetchModels()"
                >
                  <RotateCcw v-if="llm.modelListLoading.value" :size="14" class="animate-spin" />
                  <Search v-else :size="14" />
                  {{ llm.modelListLoading.value ? '拉取中...' : '拉取模型' }}
                </button>
                <button
                  v-if="llm.modelInputMode.value === 'select' && llm.modelList.value.length > 0"
                  type="button"
                  class="btn-ghost text-xs whitespace-nowrap"
                  style="margin-top: 4px"
                  @click="llm.modelInputMode.value = 'manual'"
                  title="切换为手动输入"
                >
                  手动输入
                </button>
                <button
                  v-else-if="llm.modelList.value.length > 0"
                  type="button"
                  class="btn-ghost text-xs whitespace-nowrap"
                  style="margin-top: 4px"
                  @click="llm.modelInputMode.value = 'select'"
                  title="切换为下拉选择"
                >
                  下拉选择
                </button>
              </div>
              <span v-if="llm.llmErrors.value.model" class="ef-error-text">{{ llm.llmErrors.value.model }}</span>
            </div>
            <div class="ef-field">
              <label class="ef-label">Base URL<span class="ef-required">*</span></label>
              <input v-model="llm.llmForm.value.api_base_url" type="text" class="input-macos" :class="{ 'ef-input-error': llm.llmErrors.value.api_base_url }" @input="delete llm.llmErrors.value.api_base_url" placeholder="如：https://api.openai.com（系统自动补全 /v1 路径）" />
              <span v-if="llm.llmErrors.value.api_base_url" class="ef-error-text">{{ llm.llmErrors.value.api_base_url }}</span>
            </div>
            <div class="ef-field">
              <label class="ef-label">
                API Key<span v-if="!llm.editLlmItem.value" class="ef-required">*</span>
              </label>
              <input
                v-model="llm.llmForm.value.api_key"
                type="password"
                class="input-macos"
                :class="{ 'ef-input-error': llm.llmErrors.value.api_key }"
                @input="delete llm.llmErrors.value.api_key"
                :placeholder="llm.editLlmItem.value ? '留空则保持原值' : '请输入 API Key'"
                autocomplete="off"
              />
              <span v-if="llm.llmErrors.value.api_key" class="ef-error-text">{{ llm.llmErrors.value.api_key }}</span>
            </div>
            <div class="grid grid-cols-3 gap-4">
              <div class="ef-field">
                <label class="ef-label">Temperature</label>
                <input v-model.number="llm.llmForm.value.temperature" type="number" step="0.1" min="0" max="2" class="input-macos" :class="{ 'ef-input-error': llm.llmErrors.value.temperature }" @input="delete llm.llmErrors.value.temperature" />
                <span v-if="llm.llmErrors.value.temperature" class="ef-error-text">{{ llm.llmErrors.value.temperature }}</span>
              </div>
              <div class="ef-field">
                <label class="ef-label">Max Tokens</label>
                <input v-model.number="llm.llmForm.value.max_tokens" type="number" min="1" class="input-macos" />
              </div>
              <div class="ef-field">
                <label class="ef-label">Timeout (s)</label>
                <input v-model.number="llm.llmForm.value.timeout" type="number" min="1" class="input-macos" />
              </div>
            </div>
            <!-- 每日 Token 限额 -->
            <div class="ef-field">
              <label class="ef-label">每日 Token 限额</label>
              <div class="flex items-center gap-2">
                <input
                  v-model.number="llm.llmForm.value.daily_token_quota"
                  type="number"
                  min="0"
                  class="input-macos flex-1 tabular-nums"
                  placeholder="0 = 不限制"
                />
                <span class="inline-block px-2.5 py-1.5 rounded-lg text-xs font-medium bg-neutral-100 text-neutral-600 whitespace-nowrap">
                  tokens/天
                </span>
              </div>
              <div class="flex flex-wrap gap-1.5 mt-2">
                <button
                  v-for="preset in llm.quotaPresets"
                  :key="preset.value"
                  type="button"
                  class="quota-preset-btn"
                  :class="{ 'quota-preset-btn--active': llm.llmForm.value.daily_token_quota === preset.value }"
                  @click="llm.llmForm.value.daily_token_quota = preset.value"
                >
                  {{ preset.label }}
                </button>
              </div>
              <p class="text-[11px] text-neutral-400 mt-1.5 leading-relaxed">
                <Info :size="11" class="inline -mt-px" />
                设为 0 表示不限制。限额按 UTC+8 每日 00:00 重置。链路模式下主备共享限额。
              </p>
            </div>
            <div class="ef-field">
              <label class="flex items-center gap-2 cursor-pointer select-none">
                <input
                  :checked="llm.isChainManagedEditTarget(llm.editLlmItem.value) ? true : llm.llmForm.value.is_active"
                  type="checkbox"
                  :disabled="llm.isChainManagedEditTarget(llm.editLlmItem.value)"
                  class="w-4 h-4 rounded border-neutral-300 text-primary-500 focus:ring-primary-500"
                  @change="!llm.isChainManagedEditTarget(llm.editLlmItem.value) && (llm.llmForm.value.is_active = ($event.target as HTMLInputElement).checked)"
                />
                <span class="text-sm text-neutral-700">
                  {{ llm.isChainManagedEditTarget(llm.editLlmItem.value) ? '链路成员通过主备链路自动切换' : '设为当前激活配置' }}
                </span>
              </label>
            </div>
          </form>
          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="llm.showLlmModal.value = false; llm.modelList.value = []; llm.modelInputMode.value = 'select'">取消</button>
            <button type="button" class="btn-primary" :disabled="llm.llmSaving.value" @click="llm.handleSaveLlm()">
              {{ llm.llmSaving.value ? '保存中...' : (llm.editLlmItem.value ? '保存' : '创建') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 链路管理 Drawer -->
    <ChainDrawer :cm="cm" :llm="llm" />
  </div>
</template>

<style scoped>
@import './llm-dialog.css';

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
</style>
