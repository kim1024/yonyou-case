<script setup lang="ts">
import { ref, computed } from 'vue'
import { adminApi } from '@/api/admin'

const emit = defineEmits<{ close: []; imported: [] }>()

const file = ref<File | null>(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const result = ref('')
const isError = ref(false)
const isDragOver = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const isReady = computed(() => file.value !== null && !uploading.value)

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  file.value = input.files?.[0] || null
  if (file.value) {
    result.value = ''
    isError.value = false
  }
}

function clearFile() {
  file.value = null
  result.value = ''
  isError.value = false
  if (fileInput.value) fileInput.value.value = ''
}

function triggerFileInput() {
  fileInput.value?.click()
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  isDragOver.value = true
}

function onDragLeave() {
  isDragOver.value = false
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  isDragOver.value = false
  const dropped = e.dataTransfer?.files?.[0]
  if (dropped) {
    file.value = dropped
    result.value = ''
    isError.value = false
  }
}

async function handleUpload() {
  if (!file.value) return
  uploading.value = true
  uploadProgress.value = 0
  isError.value = false
  result.value = ''

  // 模拟进度条（实际上传期间平滑推进）
  const progressTimer = setInterval(() => {
    if (uploadProgress.value < 90) {
      uploadProgress.value += Math.random() * 12
      if (uploadProgress.value > 90) uploadProgress.value = 90
    }
  }, 200)

  try {
    const res = await adminApi.importExcel(file.value)
    clearInterval(progressTimer)
    uploadProgress.value = 100
    result.value = res.data.message
    setTimeout(() => emit('imported'), 1500)
  } catch (e) {
    clearInterval(progressTimer)
    uploadProgress.value = 0
    result.value = '导入失败，请检查文件格式后重试'
    isError.value = true
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div class="id-overlay" @click.self="emit('close')">
      <div class="id-dialog">
        <!-- 标题栏 -->
        <div class="id-header">
          <h2 class="id-title">导入企业数据</h2>
          <button class="id-close-btn" @click="emit('close')" type="button">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>

        <!-- 内容区 -->
        <div class="id-body">
          <!-- 拖拽上传区域 -->
          <div
            class="id-dropzone"
            :class="{ 'id-dropzone--active': isDragOver }"
            @dragover="onDragOver"
            @dragleave="onDragLeave"
            @drop="onDrop"
            @click="triggerFileInput"
          >
            <input
              ref="fileInput"
              type="file"
              accept=".xlsx,.xls"
              class="id-file-input"
              @change="onFileChange"
            />
            <!-- 上传图标 -->
            <div class="id-dropzone-icon">
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="6" y="10" width="28" height="22" rx="3" stroke="currentColor" stroke-width="1.5" fill="none"/>
                <path d="M14 20L20 14L26 20" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M20 14V28" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </div>
            <p class="id-dropzone-text">拖拽文件到此处，或点击选择</p>
            <p class="id-dropzone-hint">支持 .xlsx 格式</p>
          </div>

          <!-- 已选文件信息 -->
          <div v-if="file && !uploading && !result" class="id-file-info">
            <div class="id-file-icon">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="1" width="14" height="16" rx="2" stroke="currentColor" stroke-width="1.2" fill="none"/>
                <path d="M6 6H12M6 9H12M6 12H9" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="id-file-details">
              <span class="id-file-name">{{ file.name }}</span>
              <span class="id-file-size">{{ formatFileSize(file.size) }}</span>
            </div>
            <button class="id-file-clear" @click.stop="clearFile" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 3L11 11M11 3L3 11" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <!-- 导入进度 -->
          <div v-if="uploading" class="id-progress-section">
            <div class="id-progress-bar">
              <div
                class="id-progress-fill"
                :style="{ width: Math.min(uploadProgress, 100) + '%' }"
              />
            </div>
            <p class="id-progress-text">导入中...</p>
          </div>

          <!-- 导入结果 -->
          <div v-if="result && !uploading" class="id-result" :class="isError ? 'id-result--error' : 'id-result--success'">
            <svg v-if="!isError" class="id-result-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.2"/>
              <path d="M5 8L7 10L11 6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else class="id-result-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.2"/>
              <path d="M5.5 5.5L10.5 10.5M10.5 5.5L5.5 10.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
            <span>{{ result }}</span>
          </div>
        </div>

        <!-- 底部操作栏 -->
        <div class="id-footer">
          <button type="button" class="btn-secondary" @click="emit('close')">取消</button>
          <button
            type="button"
            class="btn-primary"
            :disabled="!isReady"
            @click="handleUpload"
          >
            {{ uploading ? '导入中...' : '开始导入' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* ── 遮罩层 ── */
.id-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  animation: id-fade-in 200ms ease-out forwards;
}

/* ── 模态框卡片 ── */
.id-dialog {
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  background: #FFFFFF;
  border-radius: 14px;
  box-shadow: var(--shadow-overlay);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: id-scale-in 250ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* ── 标题栏 ── */
.id-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 24px;
  border-bottom: 1px solid var(--color-neutral-200);
  flex-shrink: 0;
}

.id-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
  color: var(--color-neutral-900);
  line-height: 1;
}

.id-close-btn {
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

.id-close-btn:hover {
  background-color: var(--color-neutral-100);
  color: var(--color-neutral-700);
}

/* ── 内容区 ── */
.id-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── 拖拽上传区 ── */
.id-dropzone {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 24px;
  border: 2px dashed var(--color-neutral-300);
  border-radius: 12px;
  background: var(--color-neutral-50);
  cursor: pointer;
  transition: border-color var(--duration-normal) ease, background-color var(--duration-normal) ease;
}

.id-dropzone:hover {
  border-color: var(--color-primary-400);
  background: var(--color-primary-50);
}

.id-dropzone--active {
  border-color: var(--color-primary-500) !important;
  background: var(--color-primary-50) !important;
}

.id-file-input {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: -1;
}

.id-dropzone-icon {
  color: var(--color-neutral-400);
  transition: color var(--duration-normal) ease;
}

.id-dropzone:hover .id-dropzone-icon,
.id-dropzone--active .id-dropzone-icon {
  color: var(--color-primary-500);
}

.id-dropzone-text {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-neutral-700);
}

.id-dropzone-hint {
  margin: 0;
  font-size: 12px;
  color: var(--color-neutral-400);
}

/* ── 已选文件信息 ── */
.id-file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--color-neutral-50);
  border: 1px solid var(--color-neutral-200);
  border-radius: 10px;
}

.id-file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--color-primary-50);
  color: var(--color-primary-500);
  flex-shrink: 0;
}

.id-file-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.id-file-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-neutral-800);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.id-file-size {
  font-size: 12px;
  color: var(--color-neutral-400);
}

.id-file-clear {
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
  flex-shrink: 0;
  padding: 0;
  transition: background-color var(--duration-fast) ease, color var(--duration-fast) ease;
}

.id-file-clear:hover {
  background-color: var(--color-neutral-200);
  color: var(--color-neutral-700);
}

/* ── 导入进度 ── */
.id-progress-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.id-progress-bar {
  height: 6px;
  background: var(--color-neutral-200);
  border-radius: 3px;
  overflow: hidden;
}

.id-progress-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #007AFF, #4DA3FF);
  transition: width 300ms ease;
}

.id-progress-text {
  margin: 0;
  font-size: 13px;
  color: var(--color-neutral-500);
}

/* ── 导入结果 ── */
.id-result {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  padding: 12px 16px;
  border-radius: 10px;
}

.id-result--success {
  color: #1a8a3f;
  background: var(--color-success-light);
}

.id-result--error {
  color: var(--color-danger);
  background: var(--color-danger-light);
}

.id-result-icon {
  flex-shrink: 0;
}

/* ── 底部操作栏 ── */
.id-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-neutral-200);
  flex-shrink: 0;
}

/* ── 入场动画 ── */
@keyframes id-fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes id-scale-in {
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
