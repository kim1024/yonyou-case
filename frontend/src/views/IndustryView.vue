<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Plus, Search, Inbox, Pencil, Trash2, ChevronLeft, ChevronRight, Briefcase } from 'lucide-vue-next'
import { adminApi } from '@/api/admin'
import { formatDate } from '@/utils/date'
import type { Industry, Major } from '@/types'

/* ── 列表数据 ── */
const items = ref<Industry[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const filterKeyword = ref('')
const filterMajorId = ref<number | ''>('')
const loading = ref(false)

/* ── 弹窗 ── */
const showModal = ref(false)
const editItem = ref<Industry | null>(null)
const form = ref({
  name: '',
  major_id: undefined as number | undefined,
})
const saving = ref(false)
const errors = ref<Record<string, string>>({})
const nameRef = ref<HTMLInputElement | null>(null)

/* ── 专业下拉选项 ── */
const majors = ref<Major[]>([])

/* ── 加载数据 ── */
async function loadData() {
  loading.value = true
  try {
    const res = await adminApi.getIndustries({
      page: page.value,
      page_size: pageSize,
      keyword: filterKeyword.value || undefined,
      major_id: typeof filterMajorId.value === 'number' ? filterMajorId.value : undefined,
    })
    items.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadData()
}

/* ── 打开新增弹窗 ── */
function handleAdd() {
  editItem.value = null
  form.value = { name: '', major_id: undefined }
  errors.value = {}
  showModal.value = true
}

/* ── 打开编辑弹窗 ── */
function handleEdit(item: Industry) {
  editItem.value = item
  errors.value = {}
  form.value = {
    name: item.name,
    major_id: item.major_id,
  }
  showModal.value = true
}

/* ── 校验 ── */
function validate(): boolean {
  errors.value = {}
  if (!form.value.name.trim()) errors.value.name = '请输入行业名称'
  return Object.keys(errors.value).length === 0
}

/* ── 保存 ── */
async function handleSave() {
  if (!validate()) {
    await nextTick()
    nameRef.value?.focus()
    return
  }
  saving.value = true
  try {
    if (editItem.value) {
      await adminApi.updateIndustry(editItem.value.id, {
        name: form.value.name,
        major_id: form.value.major_id,
      })
    } else {
      await adminApi.createIndustry({
        name: form.value.name,
        major_id: form.value.major_id,
      })
    }
    showModal.value = false
    loadData()
  } catch {
    alert('保存失败')
  } finally {
    saving.value = false
  }
}

/* ── 删除 ── */
async function handleDelete(id: number) {
  if (!confirm('确定删除该行业？此操作不可恢复。')) return
  try {
    await adminApi.deleteIndustry(id)
    loadData()
  } catch {
    alert('删除失败')
  }
}

/* ── 启用/禁用 ── */
async function handleToggleActive(item: Industry) {
  await adminApi.updateIndustry(item.id, { is_active: !item.is_active })
  loadData()
}

/* ── 初始化 ── */
onMounted(async () => {
  loadData()
  // 加载全部专业（下拉用）
  try {
    const res = await adminApi.getMajors({ page: 1, page_size: 200 })
    majors.value = res.data.items
  } catch { /* ignore */ }
})

function handleBackdropClick(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('ef-overlay')) {
    showModal.value = false
  }
}
</script>

<template>
  <div class="animate-fade-up">
    <!-- 标题栏 -->
    <div class="page-header flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-xl flex items-center justify-center"
          style="background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);"
        >
          <Briefcase :size="20" color="#fff" :stroke-width="1.8" />
        </div>
        <div>
          <h1>行业管理</h1>
          <p>维护行业分类与专业关联</p>
        </div>
      </div>
      <button class="btn-primary" @click="handleAdd">
        <Plus :size="16" />
        新增行业
      </button>
    </div>

    <!-- 筛选栏 -->
    <div class="flex gap-3 mb-6 flex-wrap">
      <input
        v-model="filterKeyword"
        type="text"
        placeholder="搜索行业名称"
        class="input-macos w-60"
        @keyup.enter="handleSearch"
      />
      <select v-model="filterMajorId" class="input-macos w-48">
        <option value="">全部专业</option>
        <option v-for="m in majors" :key="m.id" :value="m.id">{{ m.name }}</option>
      </select>
      <button class="btn-secondary" @click="handleSearch">
        <Search :size="15" />
        搜索
      </button>
    </div>

    <!-- 表格 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-neutral-50">
          <tr class="border-b border-neutral-200">
            <th class="px-4 py-3 text-left text-neutral-500 font-medium w-12">#</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">行业名称</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">所属专业</th>
            <th class="px-4 py-3 text-center text-neutral-500 font-medium">关联企业数</th>
            <th class="px-4 py-3 text-center text-neutral-500 font-medium">状态</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">创建时间</th>
            <th class="px-4 py-3 text-center text-neutral-500 font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in items" :key="item.id" class="border-t border-neutral-100 transition-colors duration-100" :class="index % 2 === 1 ? 'bg-neutral-50/50' : ''">
            <td class="px-4 py-3 text-neutral-400">{{ (page - 1) * pageSize + index + 1 }}</td>
            <td class="px-4 py-3 font-medium text-neutral-800">{{ item.name }}</td>
            <td class="px-4 py-3 text-neutral-500">{{ item.major_name || '-' }}</td>
            <td class="px-4 py-3 text-center">
              <span class="inline-block px-2 py-0.5 rounded-full bg-purple-50 text-purple-600 text-xs font-medium">
                {{ item.enterprise_count ?? 0 }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <button
                class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors duration-200"
                :class="item.is_active ? 'bg-green-500' : 'bg-gray-300'"
                @click="handleToggleActive(item)"
              >
                <span
                  class="inline-block h-3.5 w-3.5 rounded-full bg-white shadow transition-transform duration-200"
                  :class="item.is_active ? 'translate-x-4.5' : 'translate-x-0.5'"
                />
              </button>
            </td>
            <td class="px-4 py-3 text-neutral-500">{{ formatDate(item.created_at) }}</td>
            <td class="px-4 py-3 text-center">
              <button class="btn-ghost text-primary-500" @click="handleEdit(item)">
                <Pencil :size="14" />
              </button>
              <button class="btn-ghost text-danger" @click="handleDelete(item.id)">
                <Trash2 :size="14" />
              </button>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="7" class="px-4 py-12 text-center">
              <div class="flex flex-col items-center gap-2 text-neutral-400">
                <Inbox :size="32" />
                <span>{{ loading ? '加载中...' : '暂无数据' }}</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="mt-4 flex items-center justify-between text-sm text-neutral-500">
      <span>共 <span class="font-medium text-neutral-700">{{ total }}</span> 条</span>
      <div class="flex items-center gap-1">
        <button :disabled="page <= 1" class="btn-ghost" @click="page--; loadData()">
          <ChevronLeft :size="16" />
          上一页
        </button>
        <span class="px-3 py-1 text-neutral-600">第 {{ page }} 页</span>
        <button :disabled="page * pageSize >= total" class="btn-ghost" @click="page++; loadData()">
          下一页
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>

    <!-- 弹窗 -->
    <Teleport to="body">
      <div v-if="showModal" class="ef-overlay" @click="handleBackdropClick">
        <div class="ef-dialog">
          <div class="ef-header">
            <h2 class="ef-title">{{ editItem ? '编辑行业' : '新增行业' }}</h2>
            <button class="ef-close-btn" @click="showModal = false" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleSave" class="ef-body" novalidate>
            <!-- 行业名称 -->
            <div class="ef-field ef-field--full">
              <label class="ef-label">行业名称<span class="ef-required">*</span></label>
              <input
                ref="nameRef"
                v-model="form.name"
                type="text"
                class="input-macos"
                :class="{ 'ef-input-error': errors.name }"
                @input="delete errors.name"
              />
              <span v-if="errors.name" class="ef-error-text">{{ errors.name }}</span>
            </div>

            <!-- 所属专业 -->
            <div class="ef-field ef-field--full">
              <label class="ef-label">所属专业</label>
              <select v-model="form.major_id" class="input-macos">
                <option :value="undefined">-- 未选择 --</option>
                <option v-for="m in majors" :key="m.id" :value="m.id">{{ m.name }}</option>
              </select>
            </div>
          </form>

          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="showModal = false">取消</button>
            <button type="button" class="btn-primary" :disabled="saving" @click="handleSave">
              {{ saving ? '保存中...' : (editItem ? '保存' : '创建') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
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
  gap: 20px;
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
</style>
