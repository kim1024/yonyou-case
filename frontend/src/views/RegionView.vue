<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Plus, Inbox, Pencil, Trash2, ChevronDown, MapPin } from 'lucide-vue-next'
import { adminApi } from '@/api/admin'
import type { Province, City } from '@/types'

/* ── 省份列表 ── */
const provinces = ref<Province[]>([])
const provinceTotal = ref(0)
const loading = ref(false)

/* ── 展开行 ── */
const expandedId = ref<number | null>(null)
const cityLoading = ref(false)
const cities = ref<City[]>([])
const cityTotal = ref(0)

/* ── 省份弹窗 ── */
const showProvinceModal = ref(false)
const editProvince = ref<Province | null>(null)
const provinceForm = ref({ name: '', sort_order: 0 })
const provinceSaving = ref(false)
const provinceErrors = ref<Record<string, string>>({})
const provinceNameRef = ref<HTMLInputElement | null>(null)

/* ── 城市弹窗 ── */
const showCityModal = ref(false)
const editCity = ref<City | null>(null)
const cityForm = ref({ name: '', sort_order: 0 })
const citySaving = ref(false)
const cityErrors = ref<Record<string, string>>({})
const cityNameRef = ref<HTMLInputElement | null>(null)

/* ── 加载省份列表 ── */
async function loadProvinces() {
  loading.value = true
  try {
    const res = await adminApi.getProvinces({})
    provinces.value = res.data.items
    provinceTotal.value = res.data.total
  } finally {
    loading.value = false
  }
}

/* ── 加载城市列表 ── */
async function loadCities(provinceId: number) {
  cityLoading.value = true
  cities.value = []
  try {
    const res = await adminApi.getCities(provinceId, { province_id: provinceId })
    cities.value = res.data.items
    cityTotal.value = res.data.total
  } finally {
    cityLoading.value = false
  }
}

/* ── 展开/折叠 ── */
async function toggleExpand(province: Province) {
  if (expandedId.value === province.id) {
    expandedId.value = null
    cities.value = []
    return
  }
  expandedId.value = province.id
  await loadCities(province.id)
}

/* ──────────────────────────────────
   省份 CRUD
   ────────────────────────────────── */

function handleAddProvince() {
  editProvince.value = null
  provinceForm.value = { name: '', sort_order: 0 }
  provinceErrors.value = {}
  showProvinceModal.value = true
}

function handleEditProvince(item: Province) {
  editProvince.value = item
  provinceErrors.value = {}
  provinceForm.value = { name: item.name, sort_order: item.sort_order }
  showProvinceModal.value = true
}

function validateProvince(): boolean {
  provinceErrors.value = {}
  if (!provinceForm.value.name.trim()) provinceErrors.value.name = '请输入省份名称'
  return Object.keys(provinceErrors.value).length === 0
}

async function handleSaveProvince() {
  if (!validateProvince()) {
    await nextTick()
    provinceNameRef.value?.focus()
    return
  }
  provinceSaving.value = true
  try {
    if (editProvince.value) {
      await adminApi.updateProvince(editProvince.value.id, {
        name: provinceForm.value.name,
        sort_order: provinceForm.value.sort_order,
      })
    } else {
      await adminApi.createProvince({
        name: provinceForm.value.name,
        sort_order: provinceForm.value.sort_order,
      })
    }
    showProvinceModal.value = false
    loadProvinces()
  } catch {
    alert('保存省份失败')
  } finally {
    provinceSaving.value = false
  }
}

async function handleDeleteProvince(item: Province) {
  if (!confirm(`确定删除省份「${item.name}」？\n\n注意：删除省份将同时删除其下所有关联城市，此操作不可恢复。`)) return
  try {
    await adminApi.deleteProvince(item.id)
    if (expandedId.value === item.id) {
      expandedId.value = null
      cities.value = []
    }
    loadProvinces()
  } catch {
    alert('删除省份失败（可能存在企业引用）')
  }
}

/* ──────────────────────────────────
   城市 CRUD
   ────────────────────────────────── */

function handleAddCity() {
  editCity.value = null
  cityForm.value = { name: '', sort_order: 0 }
  cityErrors.value = {}
  showCityModal.value = true
}

function handleEditCity(item: City) {
  editCity.value = item
  cityErrors.value = {}
  cityForm.value = { name: item.name, sort_order: item.sort_order }
  showCityModal.value = true
}

function validateCity(): boolean {
  cityErrors.value = {}
  if (!cityForm.value.name.trim()) cityErrors.value.name = '请输入城市名称'
  return Object.keys(cityErrors.value).length === 0
}

async function handleSaveCity() {
  if (!validateCity()) {
    await nextTick()
    cityNameRef.value?.focus()
    return
  }
  if (!expandedId.value) return
  citySaving.value = true
  try {
    if (editCity.value) {
      await adminApi.updateCity(editCity.value.id, {
        name: cityForm.value.name,
        sort_order: cityForm.value.sort_order,
      })
    } else {
      await adminApi.createCity({
        name: cityForm.value.name,
        province_id: expandedId.value,
        sort_order: cityForm.value.sort_order,
      })
    }
    showCityModal.value = false
    loadCities(expandedId.value)
    loadProvinces()
  } catch {
    alert('保存城市失败')
  } finally {
    citySaving.value = false
  }
}

async function handleDeleteCity(item: City) {
  if (!confirm(`确定删除城市「${item.name}」？此操作不可恢复。`)) return
  try {
    await adminApi.deleteCity(item.id)
    if (expandedId.value) {
      loadCities(expandedId.value)
      loadProvinces()
    }
  } catch {
    alert('删除城市失败（可能存在企业引用）')
  }
}

/* ── 启用/禁用省份 ── */
async function handleToggleProvinceActive(item: Province) {
  await adminApi.updateProvince(item.id, { is_active: !item.is_active })
  loadProvinces()
}

/* ── 启用/禁用城市 ── */
async function handleToggleCityActive(item: City) {
  await adminApi.updateCity(item.id, { is_active: !item.is_active })
  if (expandedId.value) loadCities(expandedId.value)
}

/* ── 初始化 ── */
onMounted(() => loadProvinces())

function handleProvinceBackdrop(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('ef-overlay')) {
    showProvinceModal.value = false
  }
}

function handleCityBackdrop(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('ef-overlay')) {
    showCityModal.value = false
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
          style="background: linear-gradient(135deg, #10B981 0%, #34D399 100%);"
        >
          <MapPin :size="20" color="#fff" :stroke-width="1.8" />
        </div>
        <div>
          <h1>地区管理</h1>
          <p>管理省份城市与区域信息</p>
        </div>
      </div>
      <button class="btn-primary" @click="handleAddProvince">
        <Plus :size="16" />
        新增省份
      </button>
    </div>

    <!-- 统计 -->
    <div class="flex gap-4 mb-6">
      <div class="flex items-center gap-2 px-4 py-2.5 bg-white rounded-xl shadow-sm text-sm">
        <span class="text-neutral-500">省份总数</span>
        <span class="font-semibold text-neutral-800">{{ provinceTotal }}</span>
      </div>
    </div>

    <!-- 表格 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-neutral-50">
          <tr class="border-b border-neutral-200">
            <th class="px-4 py-3 text-left text-neutral-500 font-medium w-12">#</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">省份名称</th>
            <th class="px-4 py-3 text-center text-neutral-500 font-medium">关联城市数</th>
            <th class="px-4 py-3 text-center text-neutral-500 font-medium">状态</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">排序</th>
            <th class="px-4 py-3 text-left text-neutral-500 font-medium">创建时间</th>
            <th class="px-4 py-3 text-center text-neutral-500 font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(province, index) in provinces" :key="province.id">
            <!-- 省份行 -->
            <tr
              class="border-t border-neutral-100 transition-colors duration-100"
              :class="[
                index % 2 === 1 ? 'bg-neutral-50/50' : '',
                expandedId === province.id ? 'bg-emerald-50/30' : ''
              ]"
            >
              <td class="px-4 py-3 text-neutral-400">{{ index + 1 }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <button
                    class="province-expand-btn flex items-center justify-center w-5 h-5 rounded transition-all duration-200"
                    :class="expandedId === province.id ? 'text-emerald-600 bg-emerald-50' : 'text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100'"
                    @click="toggleExpand(province)"
                  >
                    <ChevronDown
                      :size="14"
                      class="transition-transform duration-200"
                      :class="expandedId === province.id ? 'rotate-0' : '-rotate-90'"
                    />
                  </button>
                  <span class="font-medium text-neutral-800">{{ province.name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <span class="inline-block px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 text-xs font-medium">
                  {{ province.city_count ?? 0 }}
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <button
                  class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors duration-200"
                  :class="province.is_active ? 'bg-green-500' : 'bg-gray-300'"
                  @click="handleToggleProvinceActive(province)"
                >
                  <span
                    class="inline-block h-3.5 w-3.5 rounded-full bg-white shadow transition-transform duration-200"
                    :class="province.is_active ? 'translate-x-4.5' : 'translate-x-0.5'"
                  />
                </button>
              </td>
              <td class="px-4 py-3 text-neutral-500">{{ province.sort_order }}</td>
              <td class="px-4 py-3 text-neutral-500">{{ province.created_at?.slice(0, 10) }}</td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-0.5">
                  <button class="btn-ghost text-primary-500" @click="handleEditProvince(province)">
                    <Pencil :size="14" />
                  </button>
                  <button class="btn-ghost text-danger" @click="handleDeleteProvince(province)">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </td>
            </tr>

            <!-- 展开的城市子列表 -->
            <tr v-if="expandedId === province.id" class="city-expanded-row">
              <td colspan="7" class="city-expanded-cell">
                <div class="city-panel">
                  <div class="city-panel-header">
                    <div class="flex items-center gap-2 text-xs text-neutral-500">
                      <span class="inline-block w-1 h-1 rounded-full bg-emerald-400" />
                      <span>{{ province.name }} · 共 <strong class="text-neutral-700">{{ cityTotal }}</strong> 个城市</span>
                    </div>
                    <button class="btn-secondary text-xs" style="padding: 4px 12px; gap: 4px;" @click="handleAddCity">
                      <Plus :size="12" />
                      新增城市
                    </button>
                  </div>

                  <!-- 城市表格 -->
                  <table class="w-full text-xs city-table">
                    <thead>
                      <tr class="border-b border-neutral-200/60">
                        <th class="px-3 py-2 text-left text-neutral-400 font-medium w-8">#</th>
                        <th class="px-3 py-2 text-left text-neutral-400 font-medium">城市名称</th>
                        <th class="px-3 py-2 text-center text-neutral-400 font-medium">状态</th>
                        <th class="px-3 py-2 text-left text-neutral-400 font-medium">排序</th>
                        <th class="px-3 py-2 text-left text-neutral-400 font-medium">创建时间</th>
                        <th class="px-3 py-2 text-center text-neutral-400 font-medium">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(city, ci) in cities"
                        :key="city.id"
                        class="border-t border-neutral-100/60 transition-colors duration-100"
                        :class="ci % 2 === 1 ? 'bg-neutral-50/30' : ''"
                      >
                        <td class="px-3 py-2 text-neutral-400">{{ ci + 1 }}</td>
                        <td class="px-3 py-2 font-medium text-neutral-700">{{ city.name }}</td>
                        <td class="px-3 py-2 text-center">
                          <button
                            class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors duration-200"
                            :class="city.is_active ? 'bg-green-500' : 'bg-gray-300'"
                            @click="handleToggleCityActive(city)"
                          >
                            <span
                              class="inline-block h-2.5 w-2.5 rounded-full bg-white shadow transition-transform duration-200"
                              :class="city.is_active ? 'translate-x-3.5' : 'translate-x-0.5'"
                            />
                          </button>
                        </td>
                        <td class="px-3 py-2 text-neutral-500">{{ city.sort_order }}</td>
                        <td class="px-3 py-2 text-neutral-500">{{ city.created_at?.slice(0, 10) }}</td>
                        <td class="px-3 py-2 text-center">
                          <div class="flex items-center justify-center gap-0.5">
                            <button class="btn-ghost text-primary-500" @click="handleEditCity(city)">
                              <Pencil :size="12" />
                            </button>
                            <button class="btn-ghost text-danger" @click="handleDeleteCity(city)">
                              <Trash2 :size="12" />
                            </button>
                          </div>
                        </td>
                      </tr>
                      <tr v-if="cities.length === 0 && !cityLoading">
                        <td colspan="6" class="px-3 py-6 text-center text-neutral-400">
                          暂无城市数据，点击上方「新增城市」添加
                        </td>
                      </tr>
                      <tr v-if="cityLoading">
                        <td colspan="6" class="px-3 py-6 text-center text-neutral-400">
                          加载中...
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </td>
            </tr>
          </template>

          <!-- 空状态 -->
          <tr v-if="provinces.length === 0">
            <td colspan="7" class="px-4 py-12 text-center">
              <div class="flex flex-col items-center gap-2 text-neutral-400">
                <Inbox :size="32" />
                <span>{{ loading ? '加载中...' : '暂无省份数据' }}</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 省份弹窗 -->
    <Teleport to="body">
      <div v-if="showProvinceModal" class="ef-overlay" @click="handleProvinceBackdrop">
        <div class="ef-dialog">
          <div class="ef-header">
            <h2 class="ef-title">{{ editProvince ? '编辑省份' : '新增省份' }}</h2>
            <button class="ef-close-btn" @click="showProvinceModal = false" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleSaveProvince" class="ef-body" novalidate>
            <div class="ef-field ef-field--full">
              <label class="ef-label">省份名称<span class="ef-required">*</span></label>
              <input
                ref="provinceNameRef"
                v-model="provinceForm.name"
                type="text"
                class="input-macos"
                :class="{ 'ef-input-error': provinceErrors.name }"
                @input="delete provinceErrors.name"
              />
              <span v-if="provinceErrors.name" class="ef-error-text">{{ provinceErrors.name }}</span>
            </div>
            <div class="ef-field ef-field--full">
              <label class="ef-label">排序</label>
              <input v-model.number="provinceForm.sort_order" type="number" min="0" class="input-macos" />
            </div>
          </form>

          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="showProvinceModal = false">取消</button>
            <button type="button" class="btn-primary" :disabled="provinceSaving" @click="handleSaveProvince">
              {{ provinceSaving ? '保存中...' : (editProvince ? '保存' : '创建') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 城市弹窗 -->
    <Teleport to="body">
      <div v-if="showCityModal" class="ef-overlay" @click="handleCityBackdrop">
        <div class="ef-dialog">
          <div class="ef-header">
            <h2 class="ef-title">{{ editCity ? '编辑城市' : '新增城市' }}</h2>
            <button class="ef-close-btn" @click="showCityModal = false" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleSaveCity" class="ef-body" novalidate>
            <div class="ef-field ef-field--full">
              <label class="ef-label">城市名称<span class="ef-required">*</span></label>
              <input
                ref="cityNameRef"
                v-model="cityForm.name"
                type="text"
                class="input-macos"
                :class="{ 'ef-input-error': cityErrors.name }"
                @input="delete cityErrors.name"
              />
              <span v-if="cityErrors.name" class="ef-error-text">{{ cityErrors.name }}</span>
            </div>
            <div class="ef-field ef-field--full">
              <label class="ef-label">排序</label>
              <input v-model.number="cityForm.sort_order" type="number" min="0" class="input-macos" />
            </div>
          </form>

          <div class="ef-footer">
            <button type="button" class="btn-secondary" @click="showCityModal = false">取消</button>
            <button type="button" class="btn-primary" :disabled="citySaving" @click="handleSaveCity">
              {{ citySaving ? '保存中...' : (editCity ? '保存' : '创建') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
/* ── 展开行过渡动画 ── */
.city-expanded-row {
  animation: city-slide-in 250ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.city-expanded-cell {
  padding: 0 !important;
  background: linear-gradient(180deg, rgba(16, 185, 129, 0.02) 0%, transparent 100%);
}

.city-panel {
  margin: 0 16px 12px;
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(4px);
  overflow: hidden;
}

.city-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(16, 185, 129, 0.1);
  background: rgba(249, 250, 251, 0.6);
}

.city-table thead tr {
  background: transparent;
}

.city-table th {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.city-table tbody tr:last-child {
  border-bottom: none;
}

@keyframes city-slide-in {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── 展开按钮 ── */
.province-expand-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

/* ── 弹窗 ── */
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
