<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">企业管理</h1>
      <div class="flex gap-3">
        <button class="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700" @click="showImport = true">
          Excel 导入
        </button>
        <button class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700" @click="handleAdd">
          新增企业
        </button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="flex gap-4 mb-6">
      <input v-model="filterIndustry" placeholder="行业" class="px-3 py-2 border rounded-lg text-sm w-40" @keyup.enter="handleSearch" />
      <input v-model="filterProvince" placeholder="省份" class="px-3 py-2 border rounded-lg text-sm w-40" @keyup.enter="handleSearch" />
      <input v-model="filterKeyword" placeholder="企业名称关键词" class="px-3 py-2 border rounded-lg text-sm w-60" @keyup.enter="handleSearch" />
      <button class="px-4 py-2 bg-gray-600 text-white rounded-lg text-sm hover:bg-gray-700" @click="handleSearch">搜索</button>
    </div>

    <!-- 表格 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-gray-600">客户名称</th>
            <th class="px-4 py-3 text-left text-gray-600">省份</th>
            <th class="px-4 py-3 text-left text-gray-600">城市</th>
            <th class="px-4 py-3 text-left text-gray-600">行业</th>
            <th class="px-4 py-3 text-center text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in enterprises" :key="item.id" class="border-t hover:bg-gray-50">
            <td class="px-4 py-3">{{ item.customer_name }}</td>
            <td class="px-4 py-3">{{ item.province }}</td>
            <td class="px-4 py-3">{{ item.city }}</td>
            <td class="px-4 py-3">{{ item.industry }}</td>
            <td class="px-4 py-3 text-center space-x-2">
              <button class="text-blue-600 hover:text-blue-700" @click="handleEdit(item)">编辑</button>
              <button class="text-red-500 hover:text-red-600" @click="handleDelete(item.id)">删除</button>
            </td>
          </tr>
          <tr v-if="enterprises.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="mt-4 flex items-center justify-between text-sm text-gray-600">
      <span>共 {{ total }} 条</span>
      <div class="flex gap-2">
        <button :disabled="page <= 1" class="px-3 py-1 border rounded disabled:opacity-50" @click="page--; loadData()">上一页</button>
        <span class="px-3 py-1">第 {{ page }} 页</span>
        <button :disabled="page * pageSize >= total" class="px-3 py-1 border rounded disabled:opacity-50" @click="page++; loadData()">下一页</button>
      </div>
    </div>

    <!-- 弹窗 -->
    <EnterpriseForm v-if="showForm" :item="editItem" @close="showForm = false" @saved="handleSaved" />
    <ImportDialog v-if="showImport" @close="showImport = false" @imported="handleImported" />
  </div>
</template>
