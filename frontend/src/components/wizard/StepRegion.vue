<script setup lang="ts">
import { ref, computed } from 'vue'
import { MapPin, Search } from 'lucide-vue-next'

const props = defineProps<{
  regions: string[]
  loading: boolean
  selectedRegion: string | null
}>()
const emit = defineEmits<{ select: [region: string] }>()

const poppedKey = ref<string | null>(null)
const searchQuery = ref('')

const filteredRegions = computed(() => {
  if (!searchQuery.value.trim()) return props.regions
  const q = searchQuery.value.trim().toLowerCase()
  return props.regions.filter((r) => r.toLowerCase().includes(q))
})

function handleSelect(region: string) {
  poppedKey.value = region
  setTimeout(() => {
    emit('select', region)
    poppedKey.value = null
  }, 250)
}
</script>

<template>
  <div>
    <!-- 搜索框 -->
    <div class="relative mb-5">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 pointer-events-none" />
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索地区..."
        class="input-macos pl-10 w-full md:w-80"
      />
    </div>

    <!-- 骨架屏 -->
    <div v-if="loading" class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
      <div
        v-for="i in 18"
        :key="i"
        class="h-12 rounded-xl bg-neutral-100 animate-pulse"
      />
    </div>

    <!-- 地区网格 -->
    <div
      v-else
      class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 max-h-[360px] overflow-y-auto pr-1 custom-scrollbar"
    >
      <button
        v-for="region in filteredRegions"
        :key="region"
        :class="[
          'h-12 rounded-xl flex items-center justify-center gap-2 border text-sm font-medium',
          'transition-all duration-200 cursor-pointer',
          selectedRegion === region
            ? 'bg-primary-50 border-primary-400 text-primary-700 shadow-sm -translate-y-0.5'
            : 'bg-white border-neutral-200 text-neutral-600 hover:border-primary-300 hover:text-primary-600 hover:-translate-y-0.5',
          poppedKey === region ? 'animate-select-pop' : '',
        ]"
        @click="handleSelect(region)"
      >
        <MapPin class="w-3.5 h-3.5 shrink-0" :stroke-width="1.5" />
        <span>{{ region }}</span>
      </button>
    </div>

    <!-- 空状态 -->
    <div
      v-if="!loading && filteredRegions.length === 0 && regions.length > 0"
      class="text-center py-8 text-neutral-400 text-sm"
    >
      未找到匹配的地区
    </div>
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
</style>
