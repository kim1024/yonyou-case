<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked, type Tokens } from 'marked'
import DOMPurify from 'dompurify'
import { ArrowLeft, BookOpen, Factory, Building2, Clock, Coins, RotateCcw, Printer } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// ---------- Data ----------

const content = computed(() => sessionStorage.getItem('resultContent') || '')

const source = computed(() => (route.query.source as string) || 'template')

interface Selections {
  major?: string
  industry?: string
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

// ---------- Summary cards ----------

const summaryItems = computed(() => {
  const s = selections.value
  const items: { label: string; value: string; icon: typeof BookOpen }[] = []
  if (s.major) items.push({ label: '专业方向', value: s.major, icon: BookOpen })
  if (s.industry) items.push({ label: '所属行业', value: s.industry, icon: Factory })
  if (s.enterprise) items.push({ label: '合作企业', value: s.enterprise, icon: Building2 })
  if (s.hour) items.push({ label: '课程课时', value: `${s.hour} 课时`, icon: Clock })
  return items
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
// marked v18 passes token objects to renderer methods, but @types/marked (v5)
// declares the old string-based signatures. We bridge this gap with `as` casts
// while using the real Tokens.* types from marked.d.ts for property access.

const renderer = new marked.Renderer()

renderer.heading = function (token: unknown) {
  const t = token as Tokens.Heading
  const inner = this.parser.parseInline(t.tokens)
  if (t.depth === 1) {
    return `<h1 class="text-3xl font-bold text-gray-900 mb-2 pb-4 border-b-2 border-gray-200">${inner}</h1>`
  }
  if (t.depth === 2) {
    return `<h2 class="text-xl font-semibold text-gray-800 mt-10 mb-4 pl-3 border-l-[3px] border-indigo-500">${inner}</h2>`
  }
  if (t.depth === 3) {
    return `<h3 class="text-lg font-semibold text-gray-700 mt-6 mb-3">${inner}</h3>`
  }
  return `<h${t.depth} class="text-base font-semibold text-gray-700 mt-4 mb-2">${inner}</h${t.depth}>`
} as unknown as typeof renderer.heading

renderer.paragraph = function (token: unknown) {
  const t = token as Tokens.Paragraph
  const inner = this.parser.parseInline(t.tokens)
  return `<p class="text-base text-gray-700 leading-relaxed mb-4">${inner}</p>`
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
    return `<ol class="space-y-2 mb-4 list-decimal pl-5"${startAttr}>${body}</ol>`
  }
  return `<ul class="space-y-2 mb-4">${body}</ul>`
} as unknown as typeof renderer.list

renderer.listitem = function (token: unknown) {
  const t = token as Tokens.ListItem
  const inner = this.parser.parse(t.tokens)
  return `<li class="flex items-start gap-2 py-0.5 text-base text-gray-700">
    <span class="mt-2 w-1.5 h-1.5 rounded-full bg-indigo-500 flex-shrink-0"></span>
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
  return `<div class="my-6 overflow-x-auto rounded-lg border border-gray-200">
    <table class="w-full border-collapse">
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
    return `<${tag}${alignAttr} class="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b-2 border-gray-200">${inner}</${tag}>`
  }
  return `<${tag}${alignAttr} class="px-4 py-3 text-sm text-gray-700 border-b border-gray-100">${inner}</${tag}>`
} as unknown as typeof renderer.tablecell

renderer.blockquote = function (token: unknown) {
  const t = token as Tokens.Blockquote
  const inner = this.parser.parse(t.tokens)
  return `<blockquote class="border-l-4 border-indigo-500 bg-indigo-50 rounded-r-[10px] px-6 py-4 my-6">${inner}</blockquote>`
} as unknown as typeof renderer.blockquote

renderer.strong = function (token: unknown) {
  const t = token as Tokens.Strong
  const inner = this.parser.parseInline(t.tokens)
  return `<strong class="text-indigo-800 font-semibold">${inner}</strong>`
} as unknown as typeof renderer.strong

renderer.codespan = function (token: unknown) {
  const t = token as Tokens.Codespan
  return `<code class="bg-gray-100 text-indigo-700 px-1.5 py-0.5 rounded text-sm font-mono">${t.text}</code>`
} as unknown as typeof renderer.codespan

marked.use({ renderer })

// ---------- Sanitized HTML ----------

const html = computed(() => DOMPurify.sanitize(marked.parse(content.value) as string))
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <button
            class="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition"
            @click="router.push('/')"
          >
            <ArrowLeft class="w-4 h-4" />
            <span class="text-sm font-medium">返回重新定制</span>
          </button>
        </div>
        <div class="flex items-center gap-3">
          <span
            class="text-sm px-3 py-1 rounded-full font-medium"
            :class="
              source === 'ai'
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : 'bg-amber-50 text-amber-700 border border-amber-200'
            "
          >
            {{ source === 'ai' ? '✦ AI 生成' : '✦ 模板生成' }}
          </span>
        </div>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page title -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">课程方案</h1>
        <p class="mt-2 text-gray-500">根据您的选择，系统为您定制了以下课程方案</p>
      </div>

      <!-- Selection summary cards -->
      <div v-if="summaryItems.length" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div
          v-for="item in summaryItems"
          :key="item.label"
          class="bg-white border border-gray-200 rounded-[10px] p-4 flex items-start gap-3"
        >
          <div
            class="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center flex-shrink-0"
          >
            <component :is="item.icon" class="w-5 h-5 text-indigo-500" />
          </div>
          <div>
            <div class="text-xs text-gray-400 font-medium">{{ item.label }}</div>
            <div class="text-sm font-semibold text-gray-900 mt-0.5">{{ item.value }}</div>
          </div>
        </div>
      </div>

      <!-- Markdown content -->
      <div class="bg-white rounded-[14px] shadow-sm p-8" v-html="html" />

      <!-- Cost highlight card -->
      <div v-if="formattedCost" class="mt-8">
        <div
          class="rounded-[14px] p-8 text-center border-2 border-amber-400"
          style="background: linear-gradient(135deg, #FFFBEB, #FEF3C7)"
        >
          <div class="flex items-center justify-center gap-2 mb-2">
            <Coins class="w-6 h-6 text-amber-600" />
            <span class="text-lg font-semibold text-amber-800">课程总费用</span>
          </div>
          <div class="text-4xl font-bold font-mono text-amber-600 my-3">
            &yen; {{ formattedCost }}
          </div>
          <div class="text-sm text-amber-700/70">以上费用包含课时费、教材费及实践指导费</div>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="mt-8 flex items-center justify-center gap-4">
        <button
          class="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-[10px] font-medium hover:bg-indigo-700 transition shadow-sm"
          @click="router.push('/')"
        >
          <RotateCcw class="w-4 h-4" />
          重新定制
        </button>
        <button
          class="flex items-center gap-2 px-6 py-3 bg-white text-gray-700 border border-gray-200 rounded-[10px] font-medium hover:bg-gray-50 transition"
          @click="window.print()"
        >
          <Printer class="w-4 h-4" />
          打印方案
        </button>
      </div>
    </main>
  </div>
</template>
