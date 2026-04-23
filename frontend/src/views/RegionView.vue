<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { adminApi } from '@/api/admin'
import type { Region } from '@/types'

/* ── 列表数据 ── */
const items = ref<Region[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const filterKeyword = ref('')
const loading = ref(false)

/* ── 弹窗 ── */
const showModal = ref(false)
const editItem = ref<Region | null>(null)
const form = ref({
  name: '',
})
const saving = ref(false)
const errors = ref<Record<string, string>>({})
const nameRef = ref<HTMLInputElement | null>(null)

/* ── 加载数据 ── */
async function loadData() {
  loading.value = true
  try {
    const res = await adminApi.getRegions({
      page: page.value,
      page_size: pageSize,
      keyword: filterKeyword.value || undefined,
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
  form.value = { name: '' }
  errors.value = {}
  showModal.value = true
}

/* ── 打开编辑弹窗 ── */
function handleEdit(item: Region) {
  editItem.value = item
  errors.value = {}
  form.value = { name: item.name }
  showModal.value = true
}

/* ── 校验 ── */
function validate(): boolean {
  errors.value = {}
  if (!form.value.name.trim()) errors.value.name = '请输入省份名称'
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
      await adminApi.updateRegion(editItem.value.id, { name: form.value.name })
    } else {
      await adminApi.createRegion({ name: form.value.name })
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
  if (!confirm('确定删除该地区？此操作不可恢复。')) return
  try {
    await adminApi.deleteRegion(id)
    loadData()
  } catch {
    alert('删除失败')
  }
}

/* ── 启用/禁用 ── */
async function handleToggleActive(item: Region) {
  await adminApi.updateRegion(item.id, { is_active: !item.is_active })
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
  <div>
    <!-- 标题栏 -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">地区管理</h1>
      <button class="btn-primary" @click="handleAdd">新增地区</button>
    </div>

    <!-- 筛选栏 -->
    <div class="flex gap-4 mb-6">
      <input
        v-model="filterKeyword"
        type="text"
        placeholder="搜索省份名称"
        class="input-macos w-60"
        @keyup.enter="handleSearch"
      />
      <button class="btn-secondary" @click="handleSearch">搜索</button>
    </div>

    <!-- 表格 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-gray-600 w-12">#</th>
            <th class="px-4 py-3 text-left text-gray-600">省份名称</th>
            <th class="px-4 py-3 text-center text-gray-600">状态</th>
            <th class="px-4 py-3 text-left text-gray-600">排序</th>
            <th class="px-4 py-3 text-left text-gray-600">创建时间</th>
            <th class="px-4 py-3 text-center text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in items" :key="item.id" class="border-t hover:bg-gray-50">
            <td class="px-4 py-3 text-gray-500">{{ (page - 1) * pageSize + index + 1 }}</td>
            <td class="px-4 py-3 font-medium">{{ item.name }}</td>
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
            <td class="px-4 py-3 text-gray-500">{{ item.sort_order }}</td>
            <td class="px-4 py-3 text-gray-500">{{ item.created_at?.slice(0, 10) }}</td>
            <td class="px-4 py-3 text-center space-x-2">
              <button class="text-blue-600 hover:text-blue-700 text-xs" @click="handleEdit(item)">编辑</button>
              <button class="text-red-500 hover:text-red-600 text-xs" @click="handleDelete(item.id)">删除</button>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="6" class="px-4 py-12 text-center text-gray-400">
              {{ loading ? '加载中...' : '暂无数据' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="mt-4 flex items-center justify-between text-sm text-gray-600">
      <span>共 {{ total }} 条</span>
      <div class="flex gap-2">
        <button :disabled="page <= 1" class="btn-ghost" @click="page--; loadData()">上一页</button>
        <span class="px-3 py-1">第 {{ page }} 页</span>
        <button :disabled="page * pageSize >= total" class="btn-ghost" @click="page++; loadData()">下一页</button>
      </div>
    </div>

    <!-- 弹窗 -->
    <Teleport to="body">
      <div v-if="showModal" class="ef-overlay" @click="handleBackdropClick">
        <div class="ef-dialog">
          <div class="ef-header">
            <h2 class="ef-title">{{ editItem ? '编辑地区' : '新增地区' }}</h2>
            <button class="ef-close-btn" @click="showModal = false" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleSave" class="ef-body" novalidate>
            <div class="ef-field ef-field--full">
              <label class="ef-label">省份名称<span class="ef-required">*</span></label>
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
