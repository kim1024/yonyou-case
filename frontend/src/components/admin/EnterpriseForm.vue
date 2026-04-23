<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { adminApi } from '@/api/admin'
import type { Enterprise, Province, City, IndustryOption } from '@/types'

const props = defineProps<{ item: Enterprise | null }>()
const emit = defineEmits<{ close: []; saved: [] }>()

const form = ref({
  customer_name: props.item?.customer_name || '',
  province: props.item?.province || '',
  city: props.item?.city || '',
  industry: props.item?.industry || '',
  company_intro: props.item?.company_intro || '',
  yonyou_content: props.item?.yonyou_content || '',
})

const saving = ref(false)
const errors = ref<Record<string, string>>({})
const firstErrorRef = ref<HTMLInputElement | HTMLTextAreaElement | null>(null)

// ── 下拉选择器数据 ──
const provinces = ref<Province[]>([])
const cities = ref<City[]>([])
const industries = ref<IndustryOption[]>([])
const selectedProvinceId = ref<number | null>(null)
const selectedCityId = ref<number | null>(null)
const selectedIndustryId = ref<number | null>(null)
const loadingCities = ref(false)

// ── 加载省份列表 ──
async function loadProvinces() {
  const res = await adminApi.getProvinces({ is_active: true })
  provinces.value = res.data.items
}

// ── 加载城市列表 ──
async function loadCities(provinceId: number) {
  loadingCities.value = true
  try {
    const res = await adminApi.getCities(provinceId, { province_id: provinceId, is_active: true })
    cities.value = res.data.items
  } finally {
    loadingCities.value = false
  }
}

// ── 加载行业列表（接口直接返回数组，无 items 包装）──
async function loadIndustries() {
  const res = await adminApi.getAllIndustries()
  industries.value = res.data as IndustryOption[]
}

// ── 省份变化：加载城市并清空已选城市 ──
watch(selectedProvinceId, async (newId) => {
  cities.value = []
  selectedCityId.value = null
  if (newId !== null) {
    await loadCities(newId)
  }
})

function validate(): boolean {
  errors.value = {}
  if (!form.value.customer_name.trim()) errors.value.customer_name = '请输入客户名称'
  if (selectedProvinceId.value === null) errors.value.province = '请选择省份'
  if (selectedCityId.value === null) errors.value.city = '请选择城市'
  if (selectedIndustryId.value === null) errors.value.industry = '请选择行业'
  return Object.keys(errors.value).length === 0
}

async function handleSave() {
  if (!validate()) {
    await nextTick()
    firstErrorRef.value?.focus()
    return
  }
  saving.value = true
  try {
    const payload = {
      customer_name: form.value.customer_name,
      province: provinces.value.find(p => p.id === selectedProvinceId.value)?.name ?? '',
      city: cities.value.find(c => c.id === selectedCityId.value)?.name ?? '',
      industry: industries.value.find(i => i.id === selectedIndustryId.value)?.name ?? '',
      company_intro: form.value.company_intro,
      yonyou_content: form.value.yonyou_content,
    }
    if (props.item) {
      await adminApi.updateEnterprise(props.item.id, payload)
    } else {
      await adminApi.createEnterprise(payload)
    }
    emit('saved')
  } catch (e) {
    alert('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  document.body.style.overflow = 'hidden'
  // 并行加载省份和行业
  await Promise.all([loadProvinces(), loadIndustries()])
  // 编辑模式：预选省份/行业并加载对应城市
  if (props.item) {
    const province = provinces.value.find(p => p.name === props.item!.province)
    if (province) {
      selectedProvinceId.value = province.id
      await loadCities(province.id)
      const city = cities.value.find(c => c.name === props.item!.city)
      if (city) selectedCityId.value = city.id
    }
    const industry = industries.value.find(i => i.name === props.item!.industry)
    if (industry) selectedIndustryId.value = industry.id
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <div class="ef-overlay" @click.self="emit('close')">
      <div class="ef-dialog">
        <!-- 标题栏 -->
        <div class="ef-header">
          <h2 class="ef-title">{{ item ? '编辑企业' : '新增企业' }}</h2>
          <button class="ef-close-btn" @click="emit('close')" type="button">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>

        <!-- 表单区域 -->
        <form @submit.prevent="handleSave" class="ef-body" novalidate>
          <!-- 客户名称（单列） -->
          <div class="ef-field ef-field--full">
            <label class="ef-label">
              客户名称<span class="ef-required">*</span>
            </label>
            <input
              ref="firstErrorRef"
              v-model="form.customer_name"
              type="text"
              class="input-macos"
              :class="{ 'ef-input-error': errors.customer_name }"
              @input="delete errors.customer_name"
            />
            <span v-if="errors.customer_name" class="ef-error-text">{{ errors.customer_name }}</span>
          </div>

          <!-- 省份 + 城市（双列） -->
          <div class="ef-field-row">
            <div class="ef-field">
              <label class="ef-label">
                省份<span class="ef-required">*</span>
              </label>
              <select
                v-model="selectedProvinceId"
                class="input-macos ef-select"
                :class="{ 'ef-input-error': errors.province }"
                @change="delete errors.province"
              >
                <option :value="null" disabled>请选择省份</option>
                <option v-for="p in provinces" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
              <span v-if="errors.province" class="ef-error-text">{{ errors.province }}</span>
            </div>
            <div class="ef-field">
              <label class="ef-label">
                城市<span class="ef-required">*</span>
              </label>
              <select
                v-model="selectedCityId"
                class="input-macos ef-select"
                :class="{ 'ef-input-error': errors.city }"
                :disabled="selectedProvinceId === null"
                @change="delete errors.city"
              >
                <option :value="null" disabled>
                  {{ selectedProvinceId === null ? '请先选择省份' : loadingCities ? '加载中...' : '请选择城市' }}
                </option>
                <option v-for="c in cities" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
              <span v-if="errors.city" class="ef-error-text">{{ errors.city }}</span>
            </div>
          </div>

          <!-- 行业（单列） -->
          <div class="ef-field ef-field--full">
            <label class="ef-label">
              行业<span class="ef-required">*</span>
            </label>
            <select
              v-model="selectedIndustryId"
              class="input-macos ef-select"
              :class="{ 'ef-input-error': errors.industry }"
              @change="delete errors.industry"
            >
              <option :value="null" disabled>请选择行业</option>
              <option v-for="ind in industries" :key="ind.id" :value="ind.id">{{ ind.name }}</option>
            </select>
            <span v-if="errors.industry" class="ef-error-text">{{ errors.industry }}</span>
          </div>

          <!-- 企业简介（单列 textarea） -->
          <div class="ef-field ef-field--full">
            <label class="ef-label">企业简介</label>
            <textarea
              v-model="form.company_intro"
              rows="3"
              class="input-macos ef-textarea"
            />
          </div>

          <!-- 用友建设内容（单列 textarea） -->
          <div class="ef-field ef-field--full">
            <label class="ef-label">用友建设内容</label>
            <textarea
              v-model="form.yonyou_content"
              rows="3"
              class="input-macos ef-textarea"
            />
          </div>
        </form>

        <!-- 底部操作栏 — 外部按钮手动触发提交 -->
        <div class="ef-footer">
          <button type="button" class="btn-secondary" @click="emit('close')">取消</button>
          <button type="button" class="btn-primary" :disabled="saving" @click="handleSave">
            {{ saving ? '保存中...' : (item ? '保存' : '创建') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* ── 遮罩层 ── */
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

/* ── 模态框卡片 ── */
.ef-dialog {
  width: 100%;
  max-width: 640px;
  max-height: 90vh;
  background: #FFFFFF;
  border-radius: 14px;
  box-shadow: var(--shadow-overlay);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: ef-scale-in 250ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* ── 标题栏 ── */
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

/* ── 表单区域 ── */
.ef-body {
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── 字段行 ── */
.ef-field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.ef-field--full {
  /* 单列字段占满整行 */
}

/* ── 字段 ── */
.ef-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* ── 标签 ── */
.ef-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-neutral-700);
  line-height: 1;
}

/* ── 必填标记 ── */
.ef-required {
  color: var(--color-danger);
  margin-left: 2px;
  font-weight: 500;
}

/* ── 输入框错误态 ── */
.ef-input-error {
  border-color: var(--color-danger) !important;
  box-shadow: 0 0 0 3px rgba(255, 69, 58, 0.12) !important;
}

/* ── 错误文字 ── */
.ef-error-text {
  font-size: 12px;
  color: var(--color-danger);
  line-height: 1;
}

/* ── textarea ── */
.ef-textarea {
  min-height: 80px;
  resize: vertical;
}

/* ── select ── */
.ef-select {
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L5 5L9 1' stroke='%2378716C' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 32px;
  cursor: pointer;
}

.ef-select:disabled {
  background-color: var(--color-neutral-50);
  color: var(--color-neutral-400);
  cursor: not-allowed;
  border-color: var(--color-neutral-200);
}

/* ── 底部操作栏 ── */
.ef-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-neutral-200);
  flex-shrink: 0;
}

/* ── 入场动画 ── */
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
