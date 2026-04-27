import { ref } from 'vue'

export interface ToastItem {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

const toastItems = ref<ToastItem[]>([])
let toastIdCounter = 0

export function useToast() {
  function showToast(message: string, type: ToastItem['type'] = 'success') {
    const id = ++toastIdCounter
    toastItems.value.push({ id, message, type })
    if (toastItems.value.length > 5) toastItems.value.shift()
    setTimeout(() => { removeToast(id) }, 3200)
  }

  function removeToast(id: number) {
    const idx = toastItems.value.findIndex(t => t.id === id)
    if (idx !== -1) toastItems.value.splice(idx, 1)
  }

  return { toastItems, showToast, removeToast }
}
