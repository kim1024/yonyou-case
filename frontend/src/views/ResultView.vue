<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked, type Tokens } from 'marked'
import DOMPurify from 'dompurify'
import { ArrowLeft, RotateCcw, Printer, Sparkles, Coins } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// ---------- Data ----------

const content = computed(() => sessionStorage.getItem('resultContent') || '')

const source = computed(() => (route.query.source as string) || 'template')

interface Selections {
  major?: string
  industry?: string
  region?: string
  enterprise?: string
  hour?: number
}

const selections = computed<Selections>(() => {
  try {
    return JSON.parse(sessionStorage.getItem('resultSelections') || '{}')
  } catch {
    return {}
  }
})

// ---------- Company name extraction ----------

const companyName = computed(() => {
  const text = content.value
  // Try to extract company name from first heading or first line
  const h1Match = text.match(/^#\s+(.+?)(?:案例|课程|教学|方案)/)
  if (h1Match) return h1Match[1].trim()
  // Fallback: extract from line after first heading
  const lines = text.split('\n').filter(l => l.trim())
  if (lines.length > 1) {
    const secondLine = lines[1].trim()
    if (secondLine && !secondLine.startsWith('#') && secondLine.length < 30) {
      return secondLine
    }
  }
  return selections.value.enterprise || ''
})

const courseName = computed(() => {
  const text = content.value
  const h1Match = text.match(/^#\s+(.+)/m)
  if (h1Match) return h1Match[1].trim()
  return '案例教学课程方案'
})

// ---------- Chip summary ----------

interface ChipItem {
  label: string
  active: boolean
}

const chipItems = computed<ChipItem[]>(() => {
  const s = selections.value
  return [
    { label: s.major || '未选专业', active: !!s.major },
    { label: s.industry || '未选行业', active: !!s.industry },
    { label: s.region || '未选区域', active: !!s.region },
    { label: s.enterprise || '未选企业', active: !!s.enterprise },
    { label: s.hour ? `${s.hour}课时` : '未选课时', active: !!s.hour },
  ]
})

// ---------- Cost extraction ----------

const totalCost = computed(() => {
  const text = content.value
  const patterns = [
    /合计[：:]\s*[¥￥]?([\d,]+)/,
    /总费用[：:]\s*[¥￥]?([\d,]+)/,
    /[¥￥]([\d,]+)/,
    /([\d,]+)\s*元/,
  ]
  for (const pattern of patterns) {
    const match = text.match(pattern)
    if (match) {
      return match[1].replace(/,/g, '')
    }
  }
  return null
})

const formattedCost = computed(() => {
  if (!totalCost.value) return null
  const num = parseInt(totalCost.value)
  return num.toLocaleString('zh-CN')
})

// ---------- Custom marked renderer ----------

const renderer = new marked.Renderer()

renderer.heading = function (token: unknown) {
  const t = token as Tokens.Heading
  const inner = this.parser.parseInline(t.tokens)
  if (t.depth === 1) {
    return `<h1 style="font-size:32px;font-weight:700;color:var(--color-neutral-900);margin-bottom:8px;text-align:center;line-height:1.3">${inner}</h1>`
  }
  if (t.depth === 2) {
    return `<h2 style="font-size:22px;font-weight:700;color:var(--color-neutral-900);margin-top:32px;margin-bottom:12px;padding:8px 16px;border-left:3px solid var(--color-primary-500);background:rgba(0,122,255,0.04);border-radius:0 6px 6px 0;line-height:1.4">${inner}</h2>`
  }
  if (t.depth === 3) {
    return `<h3 style="font-size:17px;font-weight:600;color:var(--color-neutral-800);margin-top:28px;margin-bottom:12px;line-height:1.4">${inner}</h3>`
  }
  return `<h${t.depth} style="font-size:16px;font-weight:600;color:var(--color-neutral-800);margin-top:20px;margin-bottom:8px">${inner}</h${t.depth}>`
} as unknown as typeof renderer.heading

renderer.paragraph = function (token: unknown) {
  const t = token as Tokens.Paragraph
  const inner = this.parser.parseInline(t.tokens)
  return `<p style="font-size:15px;color:var(--color-neutral-700);line-height:1.75;margin-bottom:16px">${inner}</p>`
} as unknown as typeof renderer.paragraph

renderer.list = function (token: unknown) {
  const t = token as Tokens.List
  let body = ''
  for (const item of t.items) {
    body += this.listitem(item)
  }
  const tag = t.ordered ? 'ol' : 'ul'
  const startAttr = t.ordered && t.start !== 1 && t.start !== '' ? ` start="${t.start}"` : ''
  if (t.ordered) {
    return `<ol style="list-style:none;padding:0;margin:8px 0 16px 0;counter-reset:item">${body}</ol>`
  }
  return `<ul style="list-style:none;padding:0;margin:8px 0 16px 0">${body}</ul>`
} as unknown as typeof renderer.list

renderer.listitem = function (token: unknown) {
  const t = token as Tokens.ListItem
  const inner = this.parser.parse(t.tokens)
  // Check if parent is ordered by looking at the token structure
  const isOrdered = t.tokens.some(tok => tok.type === 'text' && /^\d+\./.test((tok as Tokens.Text).text))
  return `<li style="display:flex;align-items:flex-start;gap:8px;padding:4px 0;font-size:15px;color:var(--color-neutral-700);line-height:1.75">
    <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--color-primary-400);margin-top:8px;flex-shrink:0"></span>
    <span>${inner}</span>
  </li>`
} as unknown as typeof renderer.listitem

renderer.table = function (token: unknown) {
  const t = token as Tokens.Table
  let headerCells = ''
  for (const cell of t.header) {
    headerCells += this.tablecell(cell)
  }
  const headerRow = this.tablerow({ text: headerCells })

  let bodyRows = ''
  for (const row of t.rows) {
    let cells = ''
    for (const cell of row) {
      cells += this.tablecell(cell)
    }
    bodyRows += this.tablerow({ text: cells })
  }
  if (bodyRows) {
    bodyRows = `<tbody>${bodyRows}</tbody>`
  }
  return `<div style="margin:20px 0;overflow-x:auto;border-radius:10px;border:1px solid var(--color-neutral-200)">
    <table style="width:100%;border-collapse:collapse">
      <thead>${headerRow}</thead>
      ${bodyRows}
    </table>
  </div>`
} as unknown as typeof renderer.table

renderer.tablecell = function (token: unknown) {
  const t = token as Tokens.TableCell
  const inner = this.parser.parseInline(t.tokens)
  const tag = t.header ? 'th' : 'td'
  const alignAttr = t.align ? ` align="${t.align}"` : ''
  if (t.header) {
    return `<${tag}${alignAttr} style="padding:12px 16px;text-align:left;font-size:13px;font-weight:600;color:var(--color-neutral-700);border-bottom:2px solid var(--color-neutral-200);background:var(--color-neutral-50)">${inner}</${tag}>`
  }
  return `<${tag}${alignAttr} style="padding:12px 16px;font-size:14px;color:var(--color-neutral-700);border-bottom:1px solid var(--color-neutral-100)">${inner}</${tag}>`
} as unknown as typeof renderer.tablecell

renderer.blockquote = function (token: unknown) {
  const t = token as Tokens.Blockquote
  const inner = this.parser.parse(t.tokens)
  return `<blockquote style="border-left:4px solid var(--color-primary-400);background:var(--color-primary-50);border-radius:0 10px 10px 0;padding:16px 24px;margin:20px 0">${inner}</blockquote>`
} as unknown as typeof renderer.blockquote

renderer.strong = function (token: unknown) {
  const t = token as Tokens.Strong
  const inner = this.parser.parseInline(t.tokens)
  return `<strong style="color:var(--color-danger);font-weight:600">${inner}</strong>`
} as unknown as typeof renderer.strong

renderer.codespan = function (token: unknown) {
  const t = token as Tokens.Codespan
  return `<code style="background:var(--color-neutral-100);color:var(--color-primary-600);padding:2px 6px;border-radius:4px;font-size:13px;font-family:var(--font-mono)">${t.text}</code>`
} as unknown as typeof renderer.codespan

renderer.em = function (token: unknown) {
  const t = token as Tokens.Em
  const inner = this.parser.parseInline(t.tokens)
  return `<em style="font-style:italic;color:var(--color-neutral-600)">${inner}</em>`
} as unknown as typeof renderer.em

marked.use({ renderer })

// ---------- Sanitized HTML ----------

const html = computed(() => DOMPurify.sanitize(marked.parse(content.value) as string))

// ---------- Print ----------

function handlePrint() {
  window.print()
}
</script>

<template>
  <div class="result-page min-h-screen" style="background:var(--color-neutral-100)">
    <!-- Top bar -->
    <header class="top-bar sticky top-0 z-50" style="background:rgba(255,255,255,0.82);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid var(--color-neutral-200)">
      <div class="top-bar-inner max-w-4xl mx-auto flex items-center justify-between" style="padding:0 48px;height:56px">
        <button
          class="nav-back flex items-center gap-2"
          style="color:var(--color-neutral-600);font-size:14px;font-weight:500;cursor:pointer;background:none;border:none;padding:6px 0;transition:color 0.15s"
          @click="router.push('/')"
        >
          <ArrowLeft style="width:16px;height:16px" />
          <span>返回重新定制</span>
        </button>
        <span
          class="source-badge flex items-center gap-1.5"
          :style="
            source === 'ai'
              ? 'background:var(--color-success-light);color:#1B8C4E;border:1px solid rgba(48,209,88,0.25)'
              : 'background:var(--color-warning-light);color:#B36B00;border:1px solid rgba(255,159,10,0.25)'
          "
          style="padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;letter-spacing:0.02em"
        >
          <Sparkles style="width:12px;height:12px" />
          {{ source === 'ai' ? 'AI 生成' : '模板生成' }}
        </span>
      </div>
    </header>

    <main class="main-content" style="padding:40px 48px 64px">
      <!-- Title card -->
      <div class="title-card" style="background:var(--color-neutral-0);border-radius:16px;padding:40px 32px 28px;margin-bottom:32px;box-shadow:var(--shadow-float);text-align:center">
        <h1 class="course-title" style="font-size:32px;font-weight:700;color:var(--color-neutral-900);margin-bottom:8px;line-height:1.3">
          {{ courseName }}
        </h1>
        <p v-if="companyName" class="company-name" style="font-size:18px;font-weight:400;color:var(--color-neutral-500);margin-bottom:24px">
          {{ companyName }}
        </p>
        <div style="width:60px;height:2px;background:var(--color-neutral-200);margin:0 auto 20px;border-radius:1px" />

        <!-- Chip row -->
        <div class="chip-row" style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px">
          <span
            v-for="(chip, idx) in chipItems"
            :key="idx"
            class="chip"
            :style="
              chip.active
                ? 'background:var(--color-primary-50);color:var(--color-primary-700);border:1px solid var(--color-primary-100)'
                : 'background:var(--color-neutral-100);color:var(--color-neutral-400);border:1px dashed var(--color-neutral-300)'
            "
            style="padding:4px 10px;border-radius:6px;font-size:12px;font-weight:500;white-space:nowrap"
          >
            {{ chip.label }}
          </span>
        </div>
      </div>

      <!-- Markdown content card -->
      <div
        class="content-card"
        style="background:var(--color-neutral-0);border-radius:14px;padding:48px;margin-bottom:32px;box-shadow:var(--shadow-float)"
        v-html="html"
      />

      <!-- Cost card -->
      <div v-if="formattedCost" class="cost-card" style="border-radius:14px;padding:32px;margin-bottom:32px;text-align:center;background:linear-gradient(135deg,#FFFBEB 0%,#FEF3C7 100%);border:2px solid rgba(255,159,10,0.3)">
        <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:12px">
          <Coins style="width:24px;height:24px;color:var(--color-warning)" />
          <span style="font-size:16px;font-weight:600;color:#92400E">课程总费用</span>
        </div>
        <div class="cost-amount" style="font-size:40px;font-weight:700;color:var(--color-warning);font-family:var(--font-mono);line-height:1.2">
          &yen; {{ formattedCost }}
        </div>
        <p style="font-size:13px;color:rgba(146,64,14,0.6);margin-top:8px">以上费用包含课时费、教材费及实践指导费</p>
      </div>

      <!-- AI disclaimer -->
      <div class="ai-disclaimer" style="background:var(--color-neutral-50);border:1px solid var(--color-neutral-200);border-radius:10px;padding:16px 24px;margin-bottom:32px;text-align:center">
        <p style="font-size:13px;color:var(--color-neutral-400);line-height:1.6;margin:0">
          以上内容由 AI 自动生成，仅供参考。具体内容请结合实际教学需求进行调整。
        </p>
      </div>
    </main>

    <!-- Bottom action bar -->
    <footer class="bottom-bar" style="position:sticky;bottom:0;z-40;background:rgba(255,255,255,0.88);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-top:1px solid var(--color-neutral-200)">
      <div class="bottom-bar-inner max-w-4xl mx-auto flex items-center justify-center gap-3" style="padding:16px 48px">
        <button class="btn-secondary flex items-center gap-2" style="padding:10px 24px" @click="router.push('/')">
          <RotateCcw style="width:15px;height:15px" />
          重新定制
        </button>
        <button class="btn-primary flex items-center gap-2" style="padding:10px 24px" @click="handlePrint">
          <Printer style="width:15px;height:15px" />
          打印方案
        </button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Responsive: tablet */
@media (max-width: 1023px) and (min-width: 768px) {
  .top-bar-inner,
  .bottom-bar-inner {
    padding-left: 32px !important;
    padding-right: 32px !important;
  }
  .main-content {
    padding-left: 32px !important;
    padding-right: 32px !important;
  }
}

/* Responsive: mobile */
@media (max-width: 767px) {
  .top-bar-inner,
  .bottom-bar-inner {
    padding-left: 20px !important;
    padding-right: 20px !important;
  }
  .main-content {
    padding: 20px !important;
  }
  .course-title {
    font-size: 24px !important;
  }
  .company-name {
    font-size: 15px !important;
  }
  .title-card {
    padding: 28px 20px 20px !important;
  }
  .content-card {
    padding: 24px 20px !important;
  }
  .cost-amount {
    font-size: 32px !important;
  }
}

/* Print styles */
@media print {
  .top-bar,
  .bottom-bar {
    display: none !important;
  }
  .main-content {
    padding: 0 !important;
    max-width: 100% !important;
  }
  .content-card,
  .title-card,
  .cost-card {
    box-shadow: none !important;
    border: 1px solid #e5e5ea !important;
  }
  .content-card {
    break-inside: avoid;
  }
  h2, h3 {
    break-inside: avoid;
  }
  .result-page {
    background: white !important;
  }
}
</style>
