<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked, type Tokens } from 'marked'
import DOMPurify from 'dompurify'
import { ArrowLeft, RotateCcw, Printer, Sparkles } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// ---------- Data ----------

const content = computed(() => sessionStorage.getItem('resultContent') || '')

const source = computed(() => (route.query.source as string) || 'template')

// ---------- Custom marked renderer ----------

const renderer = new marked.Renderer()

renderer.heading = function (token: unknown) {
  const t = token as Tokens.Heading
  const inner = this.parser.parseInline(t.tokens)

  if (t.depth === 1) {
    return `<h1 style="font-size:38px;font-weight:800;color:var(--color-neutral-900);margin-bottom:8px;text-align:center;line-height:1.3;padding-bottom:16px;border-bottom:2px solid var(--color-primary-300);letter-spacing:0.5px">${inner}</h1>`
  }

  if (t.depth === 2) {
    // Detect if h2 is a pure company name (no "案例/课程/教学/结构/介绍/岗位" keywords)
    const pureCompanyNamePattern = /^[a-zA-Z一-龥　-〿＀-￯ ]+(?:公司|集团|有限|科技|技术|股份|企业)?[\s ]*$/
    const strippedText = inner.replace(/<[^>]*>/g, '').trim()
    const isSubtitle = pureCompanyNamePattern.test(strippedText) &&
      !/案例|课程|教学|结构|介绍|岗位|模块|成果|报价|背景/.test(strippedText)

    if (isSubtitle) {
      return `<h2 style="font-size:24px;font-weight:700;color:var(--color-neutral-600);margin-top:4px;margin-bottom:28px;text-align:center;line-height:1.4;letter-spacing:1px">${inner}</h2>`
    }

    return `<h2 style="font-size:22px;font-weight:700;color:var(--color-neutral-900);margin-top:36px;margin-bottom:14px;padding:10px 18px;border-left:3px solid var(--color-primary-500);background:rgba(99,102,241,0.05);border-radius:0 6px 6px 0;line-height:1.4">${inner}</h2>`
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
  if (t.ordered) {
    return `<ol style="list-style:none;padding:0;margin:8px 0 16px 0;counter-reset:item">${body}</ol>`
  }
  return `<ul style="list-style:none;padding:0;margin:8px 0 16px 0">${body}</ul>`
} as unknown as typeof renderer.list

renderer.listitem = function (token: unknown) {
  const t = token as Tokens.ListItem
  const inner = this.parser.parse(t.tokens)
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
  return `<blockquote style="border-left:4px solid var(--color-neutral-300);background:var(--color-neutral-50);border-radius:0 8px 8px 0;padding:14px 20px;margin:20px 0">${inner}</blockquote>`
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

const html = computed(() => {
  const raw = DOMPurify.sanitize(marked.parse(content.value) as string)
  return raw.replace(
    /<span style="display:block;text-align:center;font-size:48px[^"]*">(.*?)<\/span>/,
    `<div style="text-align:center;margin:32px 0;padding:28px 32px;background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(99,102,241,0.03));border-radius:16px;border:1px solid rgba(99,102,241,0.15)"><span style="display:block;font-size:48px;font-weight:800;color:var(--color-primary-600);letter-spacing:-1px">$1</span></div>`
  )
})

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

    <main class="main-content" style="padding:48px 48px 72px">
      <!-- Markdown content card (sole content area) -->
      <div
        class="content-card"
        style="background:var(--color-neutral-0);border-radius:16px;padding:56px 56px;margin:0 auto;box-shadow:var(--shadow-float);max-width:960px"
        v-html="html"
      />
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
  .content-card {
    padding: 40px 36px !important;
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
  .content-card {
    padding: 28px 20px !important;
    border-radius: 12px !important;
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
  .content-card {
    box-shadow: none !important;
    border: 1px solid #e5e5ea !important;
    max-width: 100% !important;
    padding: 40px !important;
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
