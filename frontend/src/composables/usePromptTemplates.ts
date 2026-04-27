import { ref, computed, nextTick } from 'vue'
import { adminApi } from '@/api/admin'
import { formatDate, formatDateTime } from '@/utils/date'
import type {
  PromptTemplate, PromptVersion,
  PromptTemplateCreate, PromptVersionCreate,
} from '@/types'
import type { useToast } from './useToast'

export function usePromptTemplates(toast: ReturnType<typeof useToast>) {
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
    el.dispatchEvent(new Event('input'))
  }

  function insertVariableToPromptModal(variableName: string) {
    insertVariableAtCursor(promptModalTextareaRef.value, variableName)
  }

  function insertVariableToVersionModal(variableName: string) {
    insertVariableAtCursor(versionModalTextareaRef.value, variableName)
  }

  function computeCharCount(text: string): number {
    return text.length
  }

  function toggleVersionFullscreen() {
    versionFullscreen.value = !versionFullscreen.value
  }

  function generatePreview(content: string): string {
    let result = content
    for (const [key, value] of Object.entries(variableExamples)) {
      result = result.replaceAll(key, value)
    }
    return result
  }

  const selectedVersion = computed(() =>
    versions.value.find(v => v.id === selectedVersionId.value) ?? null
  )

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
      toast.showToast(editPromptItem.value ? '模板已更新' : '模板已创建')
    } catch {
      toast.showToast('保存失败，请重试', 'error')
    } finally {
      promptSaving.value = false
    }
  }

  async function handleDeletePrompt(item: PromptTemplate) {
    if (!confirm(`确定删除模板「${item.name}」？此操作不可恢复。`)) return
    try {
      await adminApi.deletePromptTemplate(item.id)
      loadPromptTemplates()
      toast.showToast('模板已删除', 'info')
    } catch {
      toast.showToast('删除失败，请重试', 'error')
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

  function handleBackToList() {
    showPromptList.value = true
    currentTemplateId.value = null
    versions.value = []
    selectedVersionId.value = null
  }

  async function handleCreateVersion() {
    if (!currentTemplateId.value) return
    const current = versions.value.find(v => v.is_current)
    versionForm.value = { content: current?.content ?? '', remark: '' }
    showVersionModal.value = true
  }

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
      toast.showToast('新版本已创建，已全局生效')
    } catch {
      toast.showToast('创建版本失败，请重试', 'error')
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
      toast.showToast('回滚成功，已全局生效')
    } catch {
      toast.showToast('回滚失败，请重试', 'error')
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

  return {
    promptItems,
    promptTotal,
    promptPage,
    promptPageSize,
    promptLoading,
    promptKeyword,
    showPromptList,
    showPromptModal,
    editPromptItem,
    promptSaving,
    promptErrors,
    promptForm,
    currentTemplateId,
    currentTemplateName,
    versions,
    selectedVersionId,
    versionsLoading,
    showVersionModal,
    versionSaving,
    versionForm,
    showRollbackModal,
    rollbackTarget,
    rollbackLoading,
    promptVariables,
    promptModalTextareaRef,
    versionModalTextareaRef,
    versionFullscreen,
    showPreview,
    previewContent,
    previewVersionId,
    variableExamples,
    selectedVersion,
    /* functions */
    insertVariableToPromptModal,
    insertVariableToVersionModal,
    computeCharCount,
    toggleVersionFullscreen,
    togglePreview,
    generatePreview,
    loadPromptTemplates,
    handleAddPrompt,
    handleEditPrompt,
    handleSavePrompt,
    handleDeletePrompt,
    handleViewVersions,
    loadVersions,
    handleBackToList,
    handleCreateVersion,
    handleCopyAsNewVersion,
    handleSaveVersion,
    handleRollback,
    confirmRollback,
    handlePromptBackdropClick,
    handleVersionBackdropClick,
    handleRollbackBackdropClick,
    handlePromptSearch,
    formatDate,
    formatDateTime,
  }
}
