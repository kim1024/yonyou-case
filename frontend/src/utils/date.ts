/**
 * Date formatting utilities.
 * All functions expect API strings already normalized to server timezone.
 * Prefer direct string formatting to avoid browser-local timezone shifts.
 */

function extractDateTimeParts(value: string): { date: string; time?: string } | null {
  const normalized = value.trim().replace(' ', 'T')
  const match = normalized.match(/^(\d{4}-\d{2}-\d{2})(?:T(\d{2}:\d{2}))?/)
  if (!match) return null
  return { date: match[1], time: match[2] }
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '-'
  const parts = extractDateTimeParts(iso)
  if (parts?.time) return `${parts.date} ${parts.time}`
  if (parts?.date) return `${parts.date} 00:00`
  return '-'
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return '-'
  const parts = extractDateTimeParts(iso)
  return parts?.date ?? '-'
}

export function formatMonthDay(dateStr: string | null | undefined): string {
  if (!dateStr) return ''
  const parts = extractDateTimeParts(dateStr)
  if (!parts?.date) return ''
  return parts.date.slice(5)
}

export function formatDateForInput(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}
