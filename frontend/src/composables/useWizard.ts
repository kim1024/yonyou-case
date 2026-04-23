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

  function selectMajor(major: string) {
    state.major = major
    state.industry = null
    state.region = null
    state.enterprise = null
    state.hour = null
    cascade.regions = []
    cascade.enterprises = []
    cascade.enterpriseInfo = null
    state.currentStep = 2
  }

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

  async function selectEnterprise(name: string) {
    state.enterprise = name
    // 不自动跳转到 Step 5，停留在 Step 4 等待用户确认

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

  function confirmEnterprise() {
    if (state.enterprise) {
      state.currentStep = 5
    }
  }

  function goToStep(targetStep: number) {
    if (targetStep >= state.currentStep) return
    if (targetStep < 1) return

    // 按目标步骤清除级联数据
    if (targetStep === 1) {
      state.major = null
      state.industry = null
      state.region = null
      state.enterprise = null
      state.hour = null
      cascade.regions = []
      cascade.enterprises = []
      cascade.enterpriseInfo = null
    } else if (targetStep === 2) {
      state.industry = null
      state.region = null
      state.enterprise = null
      state.hour = null
      cascade.regions = []
      cascade.enterprises = []
      cascade.enterpriseInfo = null
    } else if (targetStep === 3) {
      state.region = null
      state.enterprise = null
      state.hour = null
      cascade.enterprises = []
      cascade.enterpriseInfo = null
    } else if (targetStep === 4) {
      state.hour = null
    }

    state.currentStep = targetStep
  }

  function selectHour(hour: number) {
    state.hour = hour
  }

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
    confirmEnterprise,
    goToStep,
    selectHour,
    generate,
    reset,
  }
}
