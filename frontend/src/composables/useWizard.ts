import { reactive, computed, ref } from 'vue'
import { wizardApi } from '@/api/wizard'
import type { WizardState, CascadeData, CoursePlan } from '@/types'

const GEN_STAGE_KEY = 'generating_stage'
const GEN_START_KEY = 'generating_start_time'
const GEN_REQUEST_KEY = 'generating_request_id'
const GEN_SELECTIONS_KEY = 'generating_selections'

function generateUUID(): string {
  const bytes = new Uint8Array(16)
  crypto.getRandomValues(bytes)
  bytes[6] = (bytes[6] & 0x0f) | 0x40 // Version 4
  bytes[8] = (bytes[8] & 0x3f) | 0x80 // Variant 1
  const hex = Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('')
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`
}

export function useWizard() {
  const state = reactive<WizardState>({
    major: null,
    majorId: null,
    industry: null,
    region: null,
    enterprise: null,
    hour: null,
  })

  const cascade = reactive<CascadeData>({
    majors: [],
    industries: [],
    regions: [],
    enterprises: [],
    hours: [],
    enterpriseInfo: null,
  })

  const loading = reactive({
    init: false,
    industries: false,
    regions: false,
    enterprises: false,
    enterpriseInfo: false,
    generating: false,
  })

  // 各区域解锁状态
  const unlocked = reactive({
    industry: false,
    region: false,
    enterprise: false,
    hour: false,
  })

  // 生成阶段状态
  const generationStage = ref<1 | 2 | 3 | 4>(1)
  const generationStartTime = ref<number | null>(null)
  const elapsedSeconds = ref(0)
  const currentRequestId = ref<string | null>(null)
  let abortController: AbortController | null = null

  // Rate limit state
  const rateLimited = ref(false)
  const rateLimitMessage = ref('')
  const cooldownRemaining = ref(0)
  let cooldownTimer: ReturnType<typeof setInterval> | null = null

  // Error state
  const error = ref('')

  // 所有必选项是否已选完
  const canSubmit = computed(() => {
    return state.major !== null
      && state.industry !== null
      && state.region !== null
      && state.enterprise !== null
      && state.hour !== null
  })

  function clearGeneration() {
    localStorage.removeItem(GEN_STAGE_KEY)
    localStorage.removeItem(GEN_START_KEY)
    localStorage.removeItem(GEN_REQUEST_KEY)
    localStorage.removeItem(GEN_SELECTIONS_KEY)
    generationStage.value = 1
    generationStartTime.value = null
    elapsedSeconds.value = 0
    currentRequestId.value = null
  }

  function handleRateLimit(info: { detail: string; message: string; retryAfter: number }) {
    rateLimited.value = true
    rateLimitMessage.value = info.message
    cooldownRemaining.value = info.retryAfter

    if (cooldownTimer) clearInterval(cooldownTimer)
    cooldownTimer = setInterval(() => {
      cooldownRemaining.value--
      if (cooldownRemaining.value <= 0) {
        clearRateLimit()
      }
    }, 1000)
  }

  function clearRateLimit() {
    rateLimited.value = false
    rateLimitMessage.value = ''
    cooldownRemaining.value = 0
    if (cooldownTimer) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }

  function updateStage() {
    if (!generationStartTime.value) return
    const elapsed = getElapsedSeconds()
    elapsedSeconds.value = elapsed
    if (elapsed < 2) {
      generationStage.value = 1
    } else if (elapsed < 10) {
      generationStage.value = 2
    } else {
      generationStage.value = 3
    }
  }

  function getElapsedSeconds(): number {
    if (!generationStartTime.value) return 0
    return Math.floor((Date.now() - generationStartTime.value) / 1000)
  }

  // 初始化：加载 majors + hours
  async function init() {
    loading.init = true
    try {
      const [majorsRes, hoursRes] = await Promise.all([
        wizardApi.getMajors(),
        wizardApi.getHours(),
      ])
      cascade.majors = majorsRes.data
      cascade.hours = hoursRes.data
    } catch (e) {
      console.error('初始化失败:', e)
    } finally {
      loading.init = false
    }
  }

  // 选择专业 → 加载该专业关联的行业 → 解锁行业区
  async function selectMajor(majorName: string, majorId: number) {
    state.major = majorName
    state.majorId = majorId
    // 级联重置下游
    state.industry = null
    state.region = null
    state.enterprise = null
    state.hour = null
    cascade.industries = []
    cascade.regions = []
    cascade.enterprises = []
    cascade.enterpriseInfo = null
    unlocked.industry = false
    unlocked.region = false
    unlocked.enterprise = false
    unlocked.hour = false

    // 加载该专业关联的行业
    loading.industries = true
    try {
      const res = await wizardApi.getIndustries(majorId)
      cascade.industries = res.data
      unlocked.industry = true
    } catch (e) {
      console.error('加载行业失败:', e)
    } finally {
      loading.industries = false
    }
  }

  // 选择行业 → 加载地区 → 解锁地区区
  async function selectIndustry(industry: string) {
    state.industry = industry
    // 级联重置下游
    state.region = null
    state.enterprise = null
    state.hour = null
    cascade.regions = []
    cascade.enterprises = []
    cascade.enterpriseInfo = null
    unlocked.region = false
    unlocked.enterprise = false
    unlocked.hour = false

    loading.regions = true
    try {
      const res = await wizardApi.getRegions(industry)
      cascade.regions = res.data
      unlocked.region = true
    } catch (e) {
      console.error('加载省份失败:', e)
    } finally {
      loading.regions = false
    }
  }

  // 选择地区 → 加载企业 → 解锁企业区
  async function selectRegion(region: string | null) {
    state.region = region
    // 清除选择时重置下游
    state.enterprise = null
    state.hour = null
    cascade.enterprises = []
    cascade.enterpriseInfo = null
    unlocked.enterprise = false
    unlocked.hour = false
    if (!region) return

    loading.enterprises = true
    try {
      const res = await wizardApi.getEnterprises(state.industry!, region)
      cascade.enterprises = res.data
      unlocked.enterprise = true
    } catch (e) {
      console.error('加载企业失败:', e)
    } finally {
      loading.enterprises = false
    }
  }

  // 选择企业（加载详情）
  async function selectEnterprise(name: string | null) {
    state.enterprise = name
    cascade.enterpriseInfo = null
    if (!name) {
      unlocked.hour = false
      return
    }

    loading.enterpriseInfo = true
    try {
      const res = await wizardApi.getEnterpriseInfo(
        state.industry!,
        state.region!,
        name
      )
      cascade.enterpriseInfo = res.data
      unlocked.hour = true
    } catch (e) {
      console.error('加载企业详情失败:', e)
    } finally {
      loading.enterpriseInfo = false
    }
  }

  // 选择课时
  function selectHour(hour: number) {
    state.hour = hour
  }

  // 生成课程方案 — POST /api/generate returns 202 immediately (async pattern)
  async function generate(): Promise<{ client_request_id: string } | { templateData: CoursePlan; source: string; llm_error?: string } | null> {
    if (!canSubmit.value) return null

    const clientRequestId = generateUUID()

    generationStage.value = 1
    generationStartTime.value = Date.now()
    currentRequestId.value = clientRequestId

    localStorage.setItem(GEN_STAGE_KEY, '1')
    localStorage.setItem(GEN_START_KEY, String(generationStartTime.value))
    localStorage.setItem(GEN_REQUEST_KEY, clientRequestId)
    localStorage.setItem(GEN_SELECTIONS_KEY, JSON.stringify({
      major: state.major,
      industry: state.industry,
      enterprise: state.enterprise,
      region: state.region,
      hour: state.hour,
    }))

    loading.generating = true
    error.value = ''
    abortController = new AbortController()
    try {
      const res = await wizardApi.generate({
        major: state.major!,
        industry: state.industry!,
        enterprise: state.enterprise!,
        region: state.region!,
        hour: state.hour!,
        client_request_id: clientRequestId,
      }, { signal: abortController.signal })
      // 202 accepted — generation is running in the background, not done yet
      console.log('[generate] 已接受, client_request_id:', res.data?.client_request_id)
      return { client_request_id: res.data.client_request_id }
    } catch (e) {
      if ((e as Error).name === 'CanceledError' || (e as Error).name === 'AbortError') {
        // 请求被取消（用户点击重新开始），不报错
        return null
      }
      // Rate limit detection
      if ((e as { rateLimitInfo?: unknown }).rateLimitInfo) {
        handleRateLimit((e as { rateLimitInfo: { detail: string; message: string; retryAfter: number } }).rateLimitInfo)
        loading.generating = false
        clearGeneration()
        return null
      }
      console.error('[generate] API调用失败，2秒后自动重试:', (e as Error).message, e)
      // 自动重试一次（网络抖动等临时故障）
      await new Promise(r => setTimeout(r, 2000))
      try {
        const retryRes = await wizardApi.generate({
          major: state.major!,
          industry: state.industry!,
          enterprise: state.enterprise!,
          region: state.region!,
          hour: state.hour!,
          client_request_id: clientRequestId,
        })
        console.log('[generate] 重试成功, client_request_id:', retryRes.data?.client_request_id)
        return { client_request_id: retryRes.data.client_request_id }
      } catch (retryErr) {
        console.error('[generate] 重试仍然失败，尝试模板兜底:', (retryErr as Error).message)
        // 最终兜底：调用模板生成接口
        try {
          const templateRes = await wizardApi.generateTemplate({
            major: state.major!,
            industry: state.industry!,
            enterprise: state.enterprise!,
            region: state.region!,
            hour: state.hour!,
          })
          console.log('[generate] 模板兜底成功')
          clearGeneration()
          return {
            templateData: templateRes.data.data,
            source: 'template',
            llm_error: templateRes.data.llm_error,
          }
        } catch (templateErr) {
          console.error('[generate] 模板兜底也失败:', (templateErr as Error).message)
          error.value = '生成失败，请检查网络连接或大模型配置后重试'
          clearGeneration()
          return null
        }
      }
    } finally {
      abortController = null
      // 注意：loading.generating 由调用方管理，不在这里设置 false
    }
  }

  // 恢复进行中的生成
  async function restoreGeneration(): Promise<{ status: 'pending' } | { status: 'failed'; message?: string } | { data: CoursePlan; source: string; llm_error?: string } | null> {
    const requestId = localStorage.getItem(GEN_REQUEST_KEY)
    if (!requestId) return null

    const savedStartTime = localStorage.getItem(GEN_START_KEY)

    try {
      const res = await wizardApi.getGenerateStatus(requestId)
      const statusData = res.data

      if (statusData.status === 'completed') {
        clearGeneration()
        return { data: statusData.data, source: statusData.source, llm_error: statusData.llm_error }
      }

      if (statusData.status === 'failed') {
        clearGeneration()
        return { status: 'failed', message: statusData.message }
      }

      if (statusData.status === 'pending' || statusData.status === 'processing') {
        if (savedStartTime) {
          generationStartTime.value = parseInt(savedStartTime, 10)
          currentRequestId.value = requestId
          elapsedSeconds.value = getElapsedSeconds()
          updateStage()
          loading.generating = true
        }
        return { status: 'pending' }
      }

      // unknown status
      clearGeneration()
      return null
    } catch (e) {
      console.error('恢复生成状态失败:', e)
      clearGeneration()
      return null
    }
  }

  // 重置全部
  function reset() {
    // 如果正在生成，先取消请求
    if (abortController) {
      abortController.abort()
      abortController = null
    }
    state.major = null
    state.majorId = null
    state.industry = null
    state.region = null
    state.enterprise = null
    state.hour = null
    cascade.industries = []
    cascade.regions = []
    cascade.enterprises = []
    cascade.enterpriseInfo = null
    unlocked.industry = false
    unlocked.region = false
    unlocked.enterprise = false
    unlocked.hour = false
    loading.generating = false
    clearGeneration()
    clearRateLimit()
    error.value = ''
  }

  return {
    state,
    cascade,
    loading,
    unlocked,
    canSubmit,
    generationStage,
    generationStartTime,
    elapsedSeconds,
    currentRequestId,
    init,
    selectMajor,
    selectIndustry,
    selectRegion,
    selectEnterprise,
    selectHour,
    generate,
    reset,
    restoreGeneration,
    clearGeneration,
    updateStage,
    getElapsedSeconds,
    rateLimited,
    rateLimitMessage,
    cooldownRemaining,
    clearRateLimit,
    error,
  }
}
