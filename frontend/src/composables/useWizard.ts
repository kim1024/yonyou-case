import { reactive, computed } from 'vue'
import { wizardApi } from '@/api/wizard'
import type { WizardState, CascadeData, CoursePlan } from '@/types'

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

  // 所有必选项是否已选完
  const canSubmit = computed(() => {
    return state.major !== null
      && state.industry !== null
      && state.region !== null
      && state.enterprise !== null
      && state.hour !== null
  })

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

  // 生成课程方案
  async function generate(): Promise<{ data: CoursePlan; source: string; llm_error?: string } | null> {
    if (!canSubmit.value) return null

    loading.generating = true
    try {
      const res = await wizardApi.generate({
        major: state.major!,
        industry: state.industry!,
        enterprise: state.enterprise!,
        hour: state.hour!,
      })
      return res.data
    } catch (e) {
      console.error('生成失败:', e)
      return null
    } finally {
      loading.generating = false
    }
  }

  // 重置全部
  function reset() {
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
  }

  return {
    state,
    cascade,
    loading,
    unlocked,
    canSubmit,
    init,
    selectMajor,
    selectIndustry,
    selectRegion,
    selectEnterprise,
    selectHour,
    generate,
    reset,
  }
}
