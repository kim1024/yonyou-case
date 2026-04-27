<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Building2, Search, ChevronDown, X, Check } from 'lucide-vue-next'
import EnterpriseInfoPanel from '@/components/wizard/EnterpriseInfoPanel.vue'
import type { MajorEnterpriseInfo } from '@/types'

const props = defineProps<{
  enterprises: string[]
  loading: boolean
  enterpriseInfo: MajorEnterpriseInfo | null
  selectedEnterprise: string | null
  infoLoading: boolean
}>()
const emit = defineEmits<{ select: [name: string | null] }>()

const isOpen = ref(false)
const searchQuery = ref('')
const highlightedIndex = ref(-1)
const containerRef = ref<HTMLDivElement | null>(null)
const searchInputRef = ref<HTMLInputElement | null>(null)
const optionsRef = ref<HTMLDivElement | null>(null)

const filteredEnterprises = computed(() => {
  if (!searchQuery.value.trim()) return props.enterprises
  const q = searchQuery.value.trim().toLowerCase()
  return props.enterprises.filter((n) => n.toLowerCase().includes(q))
})

const displayText = computed(() => props.selectedEnterprise ?? '请选择企业...')

function toggle() {
  if (isOpen.value) {
    close()
  } else {
    open()
  }
}

function open() {
  isOpen.value = true
  searchQuery.value = ''
  highlightedIndex.value = -1
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

function close() {
  isOpen.value = false
  searchQuery.value = ''
  highlightedIndex.value = -1
}

function selectItem(name: string) {
  emit('select', name)
  close()
}

function clearSelection(e: Event) {
  e.stopPropagation()
  emit('select', null)
  close()
}

function onClickOutside(e: MouseEvent) {
  if (containerRef.value && !containerRef.value.contains(e.target as Node)) {
    close()
  }
}

function onKeyDown(e: KeyboardEvent) {
  const items = filteredEnterprises.value
  if (e.key === 'Escape') {
    close()
    return
  }
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    highlightedIndex.value = Math.min(highlightedIndex.value + 1, items.length - 1)
    scrollToHighlighted()
  }
  if (e.key === 'ArrowUp') {
    e.preventDefault()
    highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0)
    scrollToHighlighted()
  }
  if (e.key === 'Enter') {
    e.preventDefault()
    if (highlightedIndex.value >= 0 && highlightedIndex.value < items.length) {
      selectItem(items[highlightedIndex.value])
    }
  }
}

function scrollToHighlighted() {
  nextTick(() => {
    if (!optionsRef.value) return
    const el = optionsRef.value.querySelector(`[data-index="${highlightedIndex.value}"]`) as HTMLElement | null
    el?.scrollIntoView({ block: 'nearest' })
  })
}

watch(filteredEnterprises, () => {
  highlightedIndex.value = -1
})

onMounted(() => {
  document.addEventListener('mousedown', onClickOutside)
})
onUnmounted(() => {
  document.removeEventListener('mousedown', onClickOutside)
})
</script>

<template>
  <div class="space-y-3">
    <!-- 上层：搜索下拉选择器 -->
    <div class="relative" ref="containerRef">
      <!-- 骨架屏 -->
      <div v-if="loading" class="h-10 rounded-lg skeleton w-full max-w-sm" />

      <!-- 触发器 -->
      <button
        v-else
        type="button"
        class="flex items-center gap-2.5 h-10 w-full max-w-sm pl-3.5 pr-4 bg-white/70 backdrop-blur-sm border rounded-lg text-sm text-left transition-all duration-200 cursor-pointer"
        :class="[
          isOpen
            ? 'border-[#C0392B] ring-[3px] ring-[rgba(192,57,43,0.08)] shadow-[0_0_16px_rgba(192,57,43,0.06)]'
            : 'border-neutral-200 hover:border-neutral-300',
          selectedEnterprise ? 'text-neutral-700' : 'text-neutral-400',
        ]"
        @click="toggle"
      >
        <Building2 class="w-4 h-4 shrink-0" :class="selectedEnterprise ? 'text-[#C0392B]' : 'text-neutral-400'" :stroke-width="1.5" />
        <span class="flex-1 truncate">{{ displayText }}</span>
        <X
          v-if="selectedEnterprise"
          class="w-3.5 h-3.5 text-neutral-400 hover:text-neutral-600 shrink-0 transition-colors"
          @click="clearSelection"
        />
        <ChevronDown
          class="w-4 h-4 shrink-0 text-neutral-400 transition-transform duration-200"
          :class="{ 'rotate-180': isOpen }"
        />
      </button>

      <!-- 下拉面板（桌面端） -->
      <Transition name="dropdown">
        <div
          v-if="isOpen"
          class="absolute left-0 z-50 mt-2 bg-white/85 backdrop-blur-xl border border-neutral-200/40 rounded-xl shadow-[0_8px_32px_rgba(0,0,0,0.08)] w-full max-w-sm max-h-[280px] flex-col overflow-hidden hidden md:flex"
        >
          <!-- 搜索框 -->
          <div class="p-2 pb-1.5">
            <div class="relative">
              <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-neutral-400 pointer-events-none" />
              <input
                ref="searchInputRef"
                v-model="searchQuery"
                type="text"
                placeholder="搜索企业..."
                class="h-8 w-full pl-8 pr-8 text-sm bg-neutral-50 border border-neutral-200 rounded-lg text-neutral-700 outline-none placeholder:text-neutral-400 focus:border-[#C0392B] focus:ring-[2px] focus:ring-[rgba(192,57,43,0.08)] focus:shadow-[0_0_12px_rgba(192,57,43,0.04)] transition-all"
                @keydown="onKeyDown"
              />
              <X
                v-if="searchQuery"
                class="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-neutral-400 hover:text-neutral-600 cursor-pointer transition-colors"
                @click="searchQuery = ''"
              />
            </div>
          </div>

          <!-- 分割线 -->
          <div class="h-px bg-neutral-100 mx-2" />

          <!-- 选项列表 -->
          <div ref="optionsRef" class="flex-1 overflow-y-auto py-1.5 custom-scrollbar">
            <button
              v-for="(name, index) in filteredEnterprises"
              :key="name"
              :data-index="index"
              type="button"
              class="flex items-center gap-2.5 h-9 mx-1.5 px-2.5 rounded-lg text-sm cursor-pointer transition-colors duration-100 w-[calc(100%-12px)] text-left border-0"
              :class="[
                selectedEnterprise === name
                  ? 'text-[#991B1B] font-medium pl-[7px]'
                  : highlightedIndex === index
                    ? 'bg-neutral-50 text-neutral-700'
                    : 'text-neutral-700 hover:bg-neutral-50',
              ]"
              :style="selectedEnterprise === name ? 'background: linear-gradient(90deg, rgba(192,57,43,0.06), transparent 40%); border-left: 2px solid; border-image: linear-gradient(to bottom, #C0392B, #D4A06A) 1;' : ''"
              @click="selectItem(name)"
              @mouseenter="highlightedIndex = index"
            >
              <Building2
                class="w-3.5 h-3.5 shrink-0"
                :class="selectedEnterprise === name ? 'text-[#C0392B]' : 'text-neutral-400'"
                :stroke-width="1.5"
              />
              <span class="flex-1 truncate">{{ name }}</span>
              <Check
                v-if="selectedEnterprise === name"
                class="w-3.5 h-3.5 text-[#C0392B] shrink-0"
              />
            </button>

            <!-- 空搜索 -->
            <div
              v-if="filteredEnterprises.length === 0 && !loading && enterprises.length > 0"
              class="text-center py-6 text-neutral-400 text-sm"
            >
              未找到匹配的企业
            </div>
          </div>

          <!-- 底部统计 -->
          <div class="h-px bg-neutral-100 mx-2" />
          <div class="px-3 py-2 text-xs text-neutral-400 text-center">
            共 {{ filteredEnterprises.length }} 家企业
          </div>
        </div>
      </Transition>

      <!-- 移动端 Bottom Sheet 遮罩 -->
      <Transition name="fade">
        <div
          v-if="isOpen"
          class="fixed inset-0 bg-black/20 z-40 md:hidden"
          @click="close"
        />
      </Transition>

      <!-- 移动端 Bottom Sheet -->
      <Transition name="sheet">
        <div
          v-if="isOpen"
          class="fixed bottom-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-xl rounded-t-2xl shadow-overlay max-h-[60vh] flex flex-col md:hidden"
        >
          <!-- 拖拽指示条 -->
          <div class="flex justify-center py-2">
            <div class="w-9 h-1 rounded-full bg-neutral-200" />
          </div>

          <!-- 搜索框 -->
          <div class="px-4 pb-2">
            <div class="relative">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 pointer-events-none" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索企业..."
                class="h-10 w-full pl-10 pr-10 text-sm bg-neutral-50 border border-neutral-200 rounded-lg text-neutral-700 outline-none placeholder:text-neutral-400 focus:border-[#C0392B] focus:ring-[2px] focus:ring-[#C0392B]/15 transition-all"
              />
              <X
                v-if="searchQuery"
                class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 hover:text-neutral-600 cursor-pointer"
                @click="searchQuery = ''"
              />
            </div>
          </div>

          <!-- 选项列表 -->
          <div class="flex-1 overflow-y-auto px-2 pb-4 custom-scrollbar">
            <button
              v-for="name in filteredEnterprises"
              :key="name"
              type="button"
              class="flex items-center gap-3 h-12 mx-2 px-3 rounded-lg text-sm cursor-pointer transition-colors duration-100 w-[calc(100%-16px)] text-left border-0"
              :class="[
                selectedEnterprise === name
                  ? 'bg-[#FEF2F2] text-[#991B1B] font-medium border-l-[3px] border-[#C0392B] pl-[9px]'
                  : 'text-neutral-700 active:bg-neutral-100',
              ]"
              @click="selectItem(name)"
            >
              <Building2
                class="w-4 h-4 shrink-0"
                :class="selectedEnterprise === name ? 'text-[#C0392B]' : 'text-neutral-400'"
                :stroke-width="1.5"
              />
              <span class="flex-1">{{ name }}</span>
              <Check
                v-if="selectedEnterprise === name"
                class="w-4 h-4 text-[#C0392B] shrink-0"
              />
            </button>

            <div
              v-if="filteredEnterprises.length === 0 && !loading && enterprises.length > 0"
              class="text-center py-8 text-neutral-400 text-sm"
            >
              未找到匹配的企业
            </div>
          </div>

          <!-- 底部统计 -->
          <div class="px-4 py-3 border-t border-neutral-100 text-xs text-neutral-400 text-center">
            共 {{ filteredEnterprises.length }} 家企业
          </div>
        </div>
      </Transition>
    </div>

    <!-- 下层：企业详情面板 -->
    <Transition name="fade">
      <EnterpriseInfoPanel
        :info="enterpriseInfo"
        :loading="infoLoading"
      />
    </Transition>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--color-neutral-200);
  border-radius: 9999px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: var(--color-neutral-300);
}

/* Desktop dropdown animation */
.dropdown-enter-active {
  transition: opacity 150ms cubic-bezier(0.16, 1, 0.3, 1), transform 150ms cubic-bezier(0.16, 1, 0.3, 1);
}
.dropdown-leave-active {
  transition: opacity 100ms ease-in, transform 100ms ease-in;
}
.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}

/* Fade for panel and backdrop */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 200ms ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile sheet animation */
.sheet-enter-active {
  transition: transform 250ms cubic-bezier(0.16, 1, 0.3, 1);
}
.sheet-leave-active {
  transition: transform 200ms ease-in;
}
.sheet-enter-from {
  transform: translateY(100%);
}
.sheet-leave-to {
  transform: translateY(100%);
}
</style>
