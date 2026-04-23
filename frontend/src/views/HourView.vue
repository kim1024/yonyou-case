<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Plus, Inbox, Pencil, Trash2, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { adminApi } from '@/api/admin'
import type { Hour } from '@/types'

/* ── 列表数据 ── */
const items = ref<Hour[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)

/* ── 弹窗 ── */
const showModal = ref(false)
const editItem = ref<Hour | null>(null)
const form = ref({
  value: 0,
})
const saving = ref(false)
const errors = ref<Record<string, string>>({})
const valueRef = ref<HTMLInputElement | null>(null)

/* ── 计算约周数 ── */
function estimateWeeks(h: Hour): string {
  const weeks = Math.round(h.value / 16)
  return weeks >= 1 ? `约 ${weeks} 周` : '< 1 周'
}

/* ── 加载数据 ── */
async function loadData() {
  loading.value = true
  try {
    const res = await adminApi.getHours({
      page: page.value,
      page_size: pageSize,
    })
    items.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

/* ── 打开新增弹窗 ── */
function handleAdd() {
  editItem.value = null
  form.value = { value: 0 }
  errors.value = {}
  showModal.value = true
}

/* ── 打开编辑弹窗 ── */
function handleEdit(item: Hour) {
  editItem.value = item
  errors.value = {}
  form.value = { value: item.value }
  showModal.value = true
}

/* ── 校验 ── */
function validate(): boolean {
  errors.value = {}
  if (!form.value.value || form.value.value <= 0) {
    errors.value.value = '请输入有效的课时数'
  }
  return Object.keys(errors.value).length === 0
}

/* ── 保存 ── */
async function handleSave() {
  if (!validate()) {
    await nextTick()
    valueRef.value?.focus()
    return
  }
  saving.value = true
  try {
    const label = `${form.value.value} 课时`
    if (editItem.value) {
      await adminApi.updateHour(editItem.value.id, {
        value: form.value.value,
        label,
      })
    } else {
      await adminApi.createHour({
        value: form.value.value,
        label,
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
  if (!confirm('确定删除该课时？此操作不可恢复。')) return
  try {
    await adminApi.deleteHour(id)
    loadData()
  } catch {
    alert('删除失败')
  }
}

/* ── 启用/禁用 ── */
async function handleToggleActive(item: Hour) {
  await adminApi.updateHour(item.id, { is_active: !item.is_active })
  loadData()
}

/* ── 初始化 ── */
onMounted(() => loadData())

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
      <div>
        <h1>课时管理</h1>
        <p>配置课时及换算周数</p>
      </div>
      <button class="btn-primary" @click="handleAdd">
        <Plus :size="16" />
        新增课时
      </button>
    </div>

    <!-- 表格 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-neutral-50">
          <tr class="border-b border-neutral-200">
            <th class="px-4 py-3 text-left text-neutral-500 font-medium w-12">#</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">课时数</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">约周数</th>
            <th class="px-4 py-3 text-center text-neutral-500 font-medium">状态</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">创建时间</th>
            <th class="px-4 py-3 text-center text-neutral-500 font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in items" :key="item.id" class="border-t border-neutral-100 transition-colors duration-100" :class="index % 2 === 1 ? 'bg-neutral-50/50' : ''">
            <td class="px-4 py-3 text-neutral-400">{{ (page - 1) * pageSize + index + 1 }}</td>
            <td class="px-4 py-3 font-medium text-neutral-800">{{ item.value }} 课时</td>
            <td class="px-4 py-3 text-neutral-500">{{ estimateWeeks(item) }}</td>
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
            <td class="px-4 py-3 text-neutral-500">{{ item.created_at?.slice(0, 10) }}</td>
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
            <td colspan="6" class="px-4 py-12 text-center">
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
            <h2 class="ef-title">{{ editItem ? '编辑课时' : '新增课时' }}</h2>
            <button class="ef-close-btn" @click="showModal = false" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleSave" class="ef-body" novalidate>
            <div class="ef-field ef-field--full">
              <label class="ef-label">课时数<span class="ef-required">*</span></label>
              <input
                ref="valueRef"
                v-model.number="form.value"
                type="number"
                min="1"
                class="input-macos"
                :class="{ 'ef-input-error': errors.value }"
                @input="delete errors.value"
              />
              <span v-if="errors.value" class="ef-error-text">{{ errors.value }}</span>
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
  max-width: 480px;
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
