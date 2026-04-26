/**
 * Date formatting utilities.
 * All functions expect UTC ISO 8601 strings from the API
 * and convert to the browser's local timezone for display.
 */

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '-'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '-'
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}`
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return '-'
  // Handle both full ISO datetime and plain YYYY-MM-DD
  const d = iso.includes('T') ? new Date(iso) : new Date(iso + 'T00:00:00Z')
  if (isNaN(d.getTime())) return '-'
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export function formatMonthDay(dateStr: string | null | undefined): string {
  if (!dateStr) return ''
  // Handle both full ISO datetime and plain YYYY-MM-DD
  const d = dateStr.includes('T') ? new Date(dateStr) : new Date(dateStr + 'T00:00:00Z')
  if (isNaN(d.getTime())) return ''
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${m}-${day}`
}

export function formatDateForInput(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}
