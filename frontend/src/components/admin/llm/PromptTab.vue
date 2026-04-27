<script setup lang="ts">
import {
  Plus, Pencil, Trash2, ChevronLeft, ChevronRight,
  Inbox, ArrowLeft, RotateCcw, Search,
  Layers, Copy, Info, Maximize2, Minimize2, Eye,
} from 'lucide-vue-next'
import type { usePromptTemplates } from '@/composables/usePromptTemplates'

const props = defineProps<{
  p: ReturnType<typeof usePromptTemplates>
}>()
</script>

<template>
  <div>
    <!-- ── 列表视图 ── -->
    <template v-if="p.showPromptList.value">
      <!-- Skeleton -->
      <div v-if="p.promptLoading.value && p.promptItems.value.length === 0" class="space-y-4">
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
              v-model="p.promptKeyword.value"
              type="text" placeholder="搜索模板名称" class="input-macos w-56"
              @keyup.enter="p.handlePromptSearch()"
            />
            <button class="btn-secondary" @click="p.handlePromptSearch()">
              <Search :size="15" />
              搜索
            </button>
          </div>
          <button class="btn-primary" @click="p.handleAddPrompt()">
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
                v-for="(item, index) in p.promptItems.value"
                :key="item.id"
                class="border-t border-neutral-100 transition-colors duration-100"
                :class="index % 2 === 1 ? 'bg-neutral-50/50' : ''"
              >
                <td class="px-4 py-3 text-neutral-400">{{ (p.promptPage.value - 1) * p.promptPageSize + index + 1 }}</td>
                <td class="px-4 py-3 font-medium text-neutral-800">{{ item.name }}</td>
                <td class="px-4 py-3 text-center">
                  <span v-if="item.current_version_number" class="inline-block px-2 py-0.5 rounded-full bg-purple-50 text-purple-600 text-xs font-medium">
                    v{{ item.current_version_number }}
                  </span>
                  <span v-else class="text-neutral-400 text-xs">-</span>
                </td>
                <td class="px-4 py-3 text-neutral-500">{{ p.formatDate(item.updated_at) }}</td>
                <td class="px-4 py-3 text-center">
                  <div class="flex items-center justify-center gap-1">
                    <button class="btn-ghost text-primary-500" @click="p.handleViewVersions(item)" title="查看版本">
                      <Layers :size="14" />
                    </button>
                    <button class="btn-ghost text-primary-500" @click="p.handleCopyAsNewVersion(item)" title="复制创建新版本">
                      <Copy :size="14" />
                    </button>
                    <button class="btn-ghost text-primary-500" @click="p.handleEditPrompt(item)">
                      <Pencil :size="14" />
                    </button>
                    <button class="btn-ghost text-danger" @click="p.handleDeletePrompt(item)">
                      <Trash2 :size="14" />
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="p.promptItems.value.length === 0">
                <td colspan="5" class="px-4 py-16 text-center">
                  <div class="flex flex-col items-center gap-2 text-neutral-400">
                    <Inbox :size="36" />
                    <span>暂无提示词模板</span>
                    <button class="btn-secondary mt-2" @click="p.handleAddPrompt()">
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
        <div v-if="p.promptTotal.value > p.promptPageSize" class="mt-4 flex items-center justify-between text-sm text-neutral-500">
          <span />
          <div class="flex items-center gap-1">
            <button :disabled="p.promptPage.value <= 1" class="btn-ghost" @click="p.promptPage.value--; p.loadPromptTemplates()">
              <ChevronLeft :size="16" />上一页
            </button>
            <span class="px-3 py-1 text-neutral-600">第 {{ p.promptPage.value }} 页</span>
            <button :disabled="p.promptPage.value * p.promptPageSize >= p.promptTotal.value" class="btn-ghost" @click="p.promptPage.value++; p.loadPromptTemplates()">
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
        <button class="btn-ghost text-primary-500" @click="p.handleBackToList()">
          <ArrowLeft :size="16" />
          返回列表
        </button>
        <span class="text-neutral-300">/</span>
        <span class="text-sm font-medium text-neutral-700">{{ p.currentTemplateName.value }}</span>
      </div>

      <!-- Skeleton -->
      <div v-if="p.versionsLoading.value" class="grid grid-cols-1 lg:grid-cols-5 gap-6">
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
            <button class="btn-primary text-xs px-3 py-1.5" @click="p.handleCreateVersion()">
              <Plus :size="13" />
              创建新版本
            </button>
          </div>

          <div v-if="p.versions.value.length === 0" class="bg-white rounded-xl p-8 text-center text-neutral-400 text-sm">
            暂无版本
          </div>

          <div
            v-for="ver in p.versions.value" :key="ver.id"
            class="version-card bg-white rounded-xl p-4 cursor-pointer border-2 transition-all duration-150"
            :class="p.selectedVersionId.value === ver.id ? 'border-primary-500 shadow-md' : 'border-transparent hover:border-neutral-200'"
            @click="p.selectedVersionId.value = ver.id"
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
                @click.stop="p.handleRollback(ver)"
              >
                <RotateCcw :size="12" />
                回滚
              </button>
            </div>
            <p v-if="ver.remark" class="text-xs text-neutral-500 mb-2 line-clamp-2">{{ ver.remark }}</p>
            <div class="flex items-center gap-3 text-[11px] text-neutral-400">
              <span v-if="ver.created_by">{{ ver.created_by }}</span>
              <span v-if="ver.created_at">{{ p.formatDateTime(ver.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- 右侧：版本内容 -->
        <div class="lg:col-span-3">
          <div v-if="p.selectedVersion.value" class="bg-white rounded-xl shadow-sm overflow-hidden">
            <div class="px-5 py-4 border-b border-neutral-100 flex items-center justify-between">
              <div>
                <h3 class="text-sm font-semibold text-neutral-800">版本 v{{ p.selectedVersion.value.version_number }} 内容</h3>
                <p v-if="p.selectedVersion.value.remark" class="text-xs text-neutral-500 mt-1">{{ p.selectedVersion.value.remark }}</p>
              </div>
              <div class="flex items-center gap-2">
                <button
                  class="btn-secondary text-xs px-3 py-1.5"
                  :class="{ 'btn-preview-active': p.showPreview.value && p.previewVersionId.value === p.selectedVersion.value.id }"
                  @click="p.togglePreview()"
                  :title="p.showPreview.value ? '退出预览' : '预览模板效果'"
                >
                  <Eye :size="13" />
                  {{ p.showPreview.value && p.previewVersionId.value === p.selectedVersion.value.id ? '退出预览' : '预览' }}
                </button>
                <button class="btn-primary text-xs px-3 py-1.5" @click="p.handleCreateVersion()">
                  <Plus :size="13" />
                  新版本
                </button>
              </div>
            </div>
            <div class="p-5">
              <!-- 正常内容显示 -->
              <pre v-if="!p.showPreview.value || p.previewVersionId.value !== p.selectedVersion.value.id" class="version-content-display text-sm text-neutral-700 whitespace-pre-wrap font-mono leading-relaxed bg-neutral-50 rounded-lg p-4 max-h-[500px] overflow-y-auto">{{ p.selectedVersion.value.content }}</pre>
              <!-- 预览内容显示 -->
              <div v-else class="version-preview-display">
                <div class="version-preview-banner">
                  <Eye :size="14" :stroke-width="2" />
                  <span>预览模式 - 变量已替换为示例值</span>
                </div>
                <pre class="text-sm text-neutral-700 whitespace-pre-wrap font-mono leading-relaxed bg-indigo-50/40 rounded-lg p-4 max-h-[500px] overflow-y-auto border border-indigo-100">{{ p.previewContent.value }}</pre>
                <!-- 变量示例值说明 -->
                <div class="mt-3 p-3 bg-blue-50/60 rounded-lg border border-blue-100">
                  <p class="text-[11px] text-blue-600 font-medium mb-2">示例值映射：</p>
                  <div class="flex flex-wrap gap-x-3 gap-y-1">
                    <span v-for="(val, key) in p.variableExamples" :key="key" class="text-[10px] text-blue-500">
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

    <!-- ═══════════════════════════════════════════
         弹窗：新增/编辑提示词模板
         ═══════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="p.showPromptModal.value" class="ef-overlay" @click="p.handlePromptBackdropClick($event)">
        <div class="ef-dialog" style="max-width: 580px;">
          <div class="ef-header">
            <h2 class="ef-title">{{ p.editPromptItem.value ? '编辑模板' : '新增模板' }}</h2>
            <button class="ef-close-btn" @click="p.showPromptModal.value = false" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <form @submit.prevent="p.handleSavePrompt()" class="ef-body" novalidate>
            <div class="ef-field">
              <label class="ef-label">模板名称<span class="ef-required">*</span></label>
              <input ref="p.promptNameRef" v-model="p.promptForm.value.name" type="text" class="input-macos" :class="{ 'ef-input-error': p.promptErrors.value.name }" @input="delete p.promptErrors.value.name" />
              <span v-if="p.promptErrors.value.name" class="ef-error-text">{{ p.promptErrors.value.name }}</span>
            </div>
            <div class="ef-field">
              <label class="ef-label">描述</label>
              <input v-model="p.promptForm.value.description" type="text" class="input-macos" placeholder="可选" />
            </div>
            <div v-if="!p.editPromptItem.value" class="ef-field">
              <label class="ef-label">提示词内容<span class="ef-required">*</span></label>
              <div class="editor-wrapper">
                <div class="editor-gutter">
                  <span v-for="n in Math.max(12, p.promptForm.value.content.split('\n').length)" :key="n" class="editor-line-num">{{ n }}</span>
                </div>
                <textarea
                  ref="p.promptModalTextareaRef"
                  v-model="p.promptForm.value.content"
                  rows="12"
                  class="input-macos editor-textarea"
                  :class="{ 'ef-input-error': p.promptErrors.value.content }"
                  @input="delete p.promptErrors.value.content"
                  placeholder="输入提示词内容..."
                />
              </div>
              <div class="editor-footer-bar">
                <span v-if="p.promptErrors.value.content" class="ef-error-text">{{ p.promptErrors.value.content }}</span>
                <span class="editor-char-count">{{ p.computeCharCount(p.promptForm.value.content) }} 字符</span>
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
                  v-for="v in p.promptVariables" :key="v.name"
                  class="variable-tag variable-tag--clickable"
                  :title="`点击插入 ${v.name} 到编辑器`"
                  type="button"
                  @click="p.insertVariableToPromptModal(v.name)"
                >
                  <code>{{ v.name }}</code>
                  <span class="variable-tag-desc">{{ v.desc }}</span>
                </button>
              </div>
            </div>
          </form>
          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="p.showPromptModal.value = false">取消</button>
            <button type="button" class="btn-primary" :disabled="p.promptSaving.value" @click="p.handleSavePrompt()">
              {{ p.promptSaving.value ? '保存中...' : (p.editPromptItem.value ? '保存' : '创建') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ═══════════════════════════════════════════
         弹窗：创建新版本
         ═══════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="p.showVersionModal.value" class="ef-overlay" @click="p.handleVersionBackdropClick($event)">
        <div class="ef-dialog ef-dialog--version" :class="{ 'ef-dialog--fullscreen': p.versionFullscreen.value }" :style="p.versionFullscreen.value ? {} : { maxWidth: '640px' }">
          <div class="ef-header">
            <h2 class="ef-title">创建新版本</h2>
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="fullscreen-toggle-btn"
                :title="p.versionFullscreen.value ? '退出全屏' : '全屏编辑'"
                @click="p.toggleVersionFullscreen()"
              >
                <Minimize2 v-if="p.versionFullscreen.value" :size="15" :stroke-width="1.8" />
                <Maximize2 v-else :size="15" :stroke-width="1.8" />
              </button>
              <button class="ef-close-btn" @click="p.showVersionModal.value = false; p.versionFullscreen.value = false" type="button">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
          <form @submit.prevent="p.handleSaveVersion()" class="ef-body" :class="{ 'ef-body--fullscreen': p.versionFullscreen.value }" novalidate>
            <div class="ef-field">
              <label class="ef-label">提示词内容<span class="ef-required">*</span></label>
              <div class="editor-wrapper" :class="{ 'editor-wrapper--fullscreen': p.versionFullscreen.value }">
                <div class="editor-gutter">
                  <span v-for="n in Math.max(16, p.versionForm.value.content.split('\n').length)" :key="n" class="editor-line-num">{{ n }}</span>
                </div>
                <textarea
                  ref="p.versionModalTextareaRef"
                  v-model="p.versionForm.value.content"
                  :rows="p.versionFullscreen.value ? 28 : 16"
                  class="input-macos editor-textarea"
                  placeholder="输入提示词内容..."
                />
              </div>
              <div class="editor-footer-bar">
                <span class="editor-char-count">{{ p.computeCharCount(p.versionForm.value.content) }} 字符</span>
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
                  v-for="v in p.promptVariables" :key="v.name"
                  class="variable-tag variable-tag--clickable"
                  :title="`点击插入 ${v.name} 到编辑器`"
                  type="button"
                  @click="p.insertVariableToVersionModal(v.name)"
                >
                  <code>{{ v.name }}</code>
                  <span class="variable-tag-desc">{{ v.desc }}</span>
                </button>
              </div>
            </div>
            <div class="ef-field">
              <label class="ef-label">备注</label>
              <input v-model="p.versionForm.value.remark" type="text" class="input-macos" placeholder="描述本次修改内容" />
            </div>
          </form>
          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="p.showVersionModal.value = false; p.versionFullscreen.value = false">取消</button>
            <button type="button" class="btn-primary" :disabled="p.versionSaving.value || !p.versionForm.value.content.trim()" @click="p.handleSaveVersion()">
              {{ p.versionSaving.value ? '保存中...' : '保存版本' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ═══════════════════════════════════════════
         弹窗：回滚确认
         ═══════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="p.showRollbackModal.value" class="ef-overlay" @click="p.handleRollbackBackdropClick($event)">
        <div class="ef-dialog" style="max-width: 420px;">
          <div class="ef-header">
            <h2 class="ef-title">确认回滚</h2>
            <button class="ef-close-btn" @click="p.showRollbackModal.value = false" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <div class="ef-body">
            <p class="text-sm text-neutral-600 leading-relaxed">
              确定要回滚到
              <span class="font-semibold text-neutral-800">v{{ p.rollbackTarget.value?.version_number }}</span>
              吗？系统将该版本设为当前活跃版本，原有版本历史将完整保留。
            </p>
            <div v-if="p.rollbackTarget.value?.remark" class="mt-3 p-3 bg-neutral-50 rounded-lg">
              <p class="text-xs text-neutral-500 mb-1">版本备注：</p>
              <p class="text-xs text-neutral-700">{{ p.rollbackTarget.value.remark }}</p>
            </div>
          </div>
          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="p.showRollbackModal.value = false">取消</button>
            <button type="button" class="btn-danger" :disabled="p.rollbackLoading.value" @click="p.confirmRollback()">
              {{ p.rollbackLoading.value ? '回滚中...' : '确认回滚' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
@import './llm-dialog.css';

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
