<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { marked, type Tokens } from 'marked'
import DOMPurify from 'dompurify'
import { ArrowLeft, RotateCcw, Printer } from 'lucide-vue-next'

const router = useRouter()

// ---------- Data ----------

const content = computed(() => sessionStorage.getItem('resultContent') || '')


// ---------- Custom marked renderer ----------

const renderer = new marked.Renderer()

renderer.heading = function (token: unknown) {
  const t = token as Tokens.Heading
  const inner = this.parser.parseInline(t.tokens)

  if (t.depth === 1) {
    return `<h1 style="font-size:38px;font-weight:800;color:#DC2626;margin-bottom:8px;text-align:center;line-height:1.3;padding-bottom:16px;border-bottom:2px solid var(--color-primary-300);letter-spacing:0.5px">${inner}</h1>`
  }

  if (t.depth === 2) {
    // Detect if h2 is a pure company name (no "案例/课程/教学/结构/介绍/岗位" keywords)
    const pureCompanyNamePattern = /^[a-zA-Z一-龥　-〿＀-￯ ]+(?:公司|集团|有限|科技|技术|股份|企业)?[\s ]*$/
    const strippedText = inner.replace(/<[^>]*>/g, '').trim()
    const isSubtitle = pureCompanyNamePattern.test(strippedText) &&
      !/案例|课程|教学|结构|介绍|岗位|模块|成果|报价|背景/.test(strippedText)

    if (isSubtitle) {
      return `<h2 style="font-size:24px;font-weight:700;color:#DC2626;margin-top:4px;margin-bottom:28px;text-align:center;line-height:1.4;letter-spacing:1px">${inner}</h2>`
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
  let result = DOMPurify.sanitize(marked.parse(content.value) as string)

  // 注入报价卡片标题的 SVG 图标
  const titleIcon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.5"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>`

  // 注入成果物 SVG 图标
  const iconMap: Record<string, string> = {
    'PPT': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>`,
    '视频': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5,3 19,12 5,21"/></svg>`,
    '指导书': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>`,
    '数据集': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>`,
    '代码包': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`,
    '实操环境': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`,
  }

  // 将报价标题 span (15px) 和价格 span (56px) 包裹为金色渐变卡片
  // 第一步：标准化报价标题 span（确保 letter-spacing:2px）
  result = result.replace(
    /<span\s[^>]*font-size\s*:\s*15px[^>]*>([^<]*最终报价[^<]*)<\/span>/,
    '<span style="display:block;text-align:center;margin:40px 0 12px;font-size:15px;font-weight:600;color:#888888;letter-spacing:2px">$1</span>'
  )
  // 第二步：标准化报价数字 span（确保 letter-spacing:-1px）
  result = result.replace(
    /<span\s[^>]*font-size\s*:\s*56px[^>]*>(¥[\d,]+)<\/span>/,
    '<span style="display:block;text-align:center;font-size:56px;font-weight:800;letter-spacing:-1px">$1</span>'
  )
  // 第三步：包裹为金色卡片（此时格式已标准化）
  result = result.replace(
    /<span style="[^"]*font-size:15px[^"]*letter-spacing:2px">(.*?)<\/span>\s*<span style="[^"]*font-size:56px[^"]*letter-spacing:-1px">(.*?)<\/span>\s*(<div[^>]*>.*?<\/div>)/,
    `<div style="text-align:center;margin:40px 0;padding:36px 32px 28px;background:linear-gradient(135deg,rgba(255,215,0,0.06),rgba(255,193,37,0.03));border-radius:20px;border:1px solid rgba(212,175,55,0.2)">
      <span style="display:flex;align-items:center;justify-content:center;gap:6px;font-size:15px;font-weight:600;color:#888888;letter-spacing:2px;margin-bottom:16px">${titleIcon}$1</span>
      <span style="display:block;font-size:56px;font-weight:800;color:#D4A017;letter-spacing:-1px;text-shadow:0 2px 4px rgba(212,160,23,0.15)">$2</span>
      <div style="margin-top:20px;padding-top:16px;border-top:1px solid rgba(212,175,55,0.12)">$3</div>
    </div>`
  )

  // 为成果物 div 中的 span 注入 SVG 图标
  for (const [label, svg] of Object.entries(iconMap)) {
    result = result.replace(
      new RegExp(`<span>([^<]*${label}[^<]*)</span>`, 'g'),
      `<span style="display:inline-flex;align-items:center;gap:5px">${svg} ${label}</span>`
    )
  }

  // 优化 AI 声明提示
  result = result.replace(
    /<blockquote[^>]*>[\s\S]*?AI 生成[\s\S]*?<\/blockquote>/,
    `<div style="display:flex;align-items:center;gap:6px;margin-top:24px;padding:0;font-size:12px;color:#999">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 1 4 4v1a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/><path d="M16 14h.01"/><path d="M8 14h.01"/><path d="M12 18v4"/><path d="M9 22h6"/></svg>
      <span>以上内容由 AI 生成，请结合实际教学需求进行调整。</span>
    </div>`
  )

  return result
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
