<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Upload, Search, Inbox, Pencil, Trash2, Building2 } from 'lucide-vue-next'
import { adminApi } from '@/api/admin'
import EnterpriseForm from '@/components/admin/EnterpriseForm.vue'
import ImportDialog from '@/components/admin/ImportDialog.vue'
import type { Enterprise } from '@/types'

const enterprises = ref<Enterprise[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const filterIndustry = ref('')
const filterProvince = ref('')
const filterKeyword = ref('')

const showForm = ref(false)
const showImport = ref(false)
const editItem = ref<Enterprise | null>(null)

async function loadData() {
  const res = await adminApi.getEnterprises({
    page: page.value,
    page_size: pageSize,
    industry: filterIndustry.value || undefined,
    province: filterProvince.value || undefined,
    keyword: filterKeyword.value || undefined,
  })
  enterprises.value = res.data.items
  total.value = res.data.total
}

function handleSearch() {
  page.value = 1
  loadData()
}

function handleAdd() {
  editItem.value = null
  showForm.value = true
}

function handleEdit(item: Enterprise) {
  editItem.value = item
  showForm.value = true
}

async function handleDelete(id: number) {
  if (confirm('确定删除？')) {
    await adminApi.deleteEnterprise(id)
    loadData()
  }
}

function handleSaved() {
  showForm.value = false
  loadData()
}

function handleImported() {
  showImport.value = false
  loadData()
}

onMounted(() => loadData())
</script>

<template>
  <div class="animate-fade-up">
    <!-- 页面标题区 -->
    <div class="page-header flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-xl flex items-center justify-center"
          style="background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);"
        >
          <Building2 :size="20" color="#fff" :stroke-width="1.8" />
        </div>
        <div>
          <h1>企业管理</h1>
          <p>管理企业信息与案例数据</p>
        </div>
      </div>
      <div class="flex gap-3">
        <button class="btn-secondary" @click="showImport = true">
          <Upload :size="16" />
          Excel 导入
        </button>
        <button class="btn-primary" @click="handleAdd">
          <Plus :size="16" />
          新增企业
        </button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="flex gap-3 mb-6">
      <input v-model="filterIndustry" placeholder="行业" class="input-macos w-40" @keyup.enter="handleSearch" />
      <input v-model="filterProvince" placeholder="省份" class="input-macos w-40" @keyup.enter="handleSearch" />
      <input v-model="filterKeyword" placeholder="企业名称关键词" class="input-macos w-60" @keyup.enter="handleSearch" />
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
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">客户名称</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">省份</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">城市</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">行业</th>
            <th class="px-4 py-3 text-center text-neutral-500 font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, idx) in enterprises" :key="item.id" class="border-t border-neutral-100 transition-colors duration-100" :class="idx % 2 === 1 ? 'bg-neutral-50/50' : ''">
            <td class="px-4 py-3 text-neutral-800">{{ item.customer_name }}</td>
            <td class="px-4 py-3 text-neutral-600">{{ item.province }}</td>
            <td class="px-4 py-3 text-neutral-600">{{ item.city }}</td>
            <td class="px-4 py-3 text-neutral-600">{{ item.industry }}</td>
            <td class="px-4 py-3 text-center">
              <button class="btn-ghost text-primary-500" @click="handleEdit(item)">
                <Pencil :size="14" />
              </button>
              <button class="btn-ghost text-danger" @click="handleDelete(item.id)">
                <Trash2 :size="14" />
              </button>
            </td>
          </tr>
          <tr v-if="enterprises.length === 0">
            <td colspan="5" class="px-4 py-12 text-center">
              <div class="flex flex-col items-center gap-2 text-neutral-400">
                <Inbox :size="32" />
                <span>暂无数据</span>
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
        <button :disabled="page <= 1" class="btn-ghost" @click="page--; loadData()">上一页</button>
        <span class="px-3 py-1 text-neutral-600">第 {{ page }} 页</span>
        <button :disabled="page * pageSize >= total" class="btn-ghost" @click="page++; loadData()">下一页</button>
      </div>
    </div>

    <!-- 弹窗 -->
    <EnterpriseForm v-if="showForm" :item="editItem" @close="showForm = false" @saved="handleSaved" />
    <ImportDialog v-if="showImport" @close="showImport = false" @imported="handleImported" />
  </div>
</template>
