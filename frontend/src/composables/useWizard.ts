import { reactive, computed } from 'vue'
import { wizardApi } from '@/api/wizard'
import type { WizardState, CascadeData } from '@/types'

export function useWizard() {
  const state = reactive<WizardState>({
    currentStep: 1,
    major: null,
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
    regions: false,
    enterprises: false,
    enterpriseInfo: false,
    generating: false,
  })

  const canSubmit = computed(() => {
    return state.major && state.industry && state.region && state.enterprise && state.hour
  })

  // 初始化：并行加载 majors, industries, hours
  async function init() {
    loading.init = true
    try {
      const [majorsRes, industriesRes, hoursRes] = await Promise.all([
        wizardApi.getMajors(),
        wizardApi.getIndustries(),
        wizardApi.getHours(),
      ])
      cascade.majors = majorsRes.data
      cascade.industries = industriesRes.data
      cascade.hours = hoursRes.data
    } catch (e) {
      console.error('初始化失败:', e)
    } finally {
      loading.init = false
    }
  }

  // 选择专业
  function selectMajor(major: string) {
    state.major = major
    state.currentStep = 2
  }

  // 选择行业 → 加载省份
  async function selectIndustry(industry: string) {
    state.industry = industry
    state.region = null
    state.enterprise = null
    cascade.regions = []
    cascade.enterprises = []
    cascade.enterpriseInfo = null
    state.currentStep = 3

    loading.regions = true
    try {
      const res = await wizardApi.getRegions(industry)
      cascade.regions = res.data
    } catch (e) {
      console.error('加载省份失败:', e)
    } finally {
      loading.regions = false
    }
  }

  // 选择省份 → 加载企业
  async function selectRegion(region: string) {
    state.region = region
    state.enterprise = null
    cascade.enterprises = []
    cascade.enterpriseInfo = null
    state.currentStep = 4

    loading.enterprises = true
    try {
      const res = await wizardApi.getEnterprises(state.industry!, region)
      cascade.enterprises = res.data
    } catch (e) {
      console.error('加载企业失败:', e)
    } finally {
      loading.enterprises = false
    }
  }

  // 选择企业 → 加载详情
  async function selectEnterprise(name: string) {
    state.enterprise = name
    state.currentStep = 5

    loading.enterpriseInfo = true
    try {
      const res = await wizardApi.getEnterpriseInfo(
        state.industry!,
        state.region!,
        name
      )
      cascade.enterpriseInfo = res.data
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

  // 提交生成
  async function generate() {
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

  // 重置向导
  function reset() {
    state.currentStep = 1
    state.major = null
    state.industry = null
    state.region = null
    state.enterprise = null
    state.hour = null
    cascade.regions = []
    cascade.enterprises = []
    cascade.enterpriseInfo = null
  }

  return {
    state,
    cascade,
    loading,
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
