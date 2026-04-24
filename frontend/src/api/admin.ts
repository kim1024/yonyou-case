import http from './http'
import type {
  Major, Industry, Region, Hour, Province, City,
  MajorListParams, IndustryListParams, RegionListParams, HourListParams,
  ProvinceListParams, CityListParams,
  LlmConfigCreate, LlmConfigUpdate, LlmListParams,
  PromptTemplateCreate, PromptVersionCreate, PromptListParams,
} from '@/types'

export const adminApi = {
  // 认证
  login(username: string, password: string) {
    return http.post('/api/admin/login', { username, password })
  },

  // ── 企业 CRUD ──
  getEnterprises(params: { page: number; page_size: number; industry?: string; province?: string; keyword?: string }) {
    return http.get('/api/admin/enterprises', { params })
  },
  createEnterprise(data: Record<string, string>) { return http.post('/api/admin/enterprises', data) },
  updateEnterprise(id: number, data: Record<string, string>) { return http.put(`/api/admin/enterprises/${id}`, data) },
  deleteEnterprise(id: number) { return http.delete(`/api/admin/enterprises/${id}`) },
  importExcel(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return http.post('/api/admin/enterprises/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // ── 统计 ──
  getAnalyticsSummary() { return http.get('/api/admin/analytics/summary') },
  getVisitTrends(days: number = 7) { return http.get('/api/admin/analytics/visits', { params: { days } }) },
  getProvinceDistribution(days: number = 7) { return http.get('/api/admin/analytics/provinces', { params: { days } }) },
  getCaseFrequency(days: number = 7) { return http.get('/api/admin/analytics/case-frequency', { params: { days } }) },
  getIndustryDistribution(days: number = 7) { return http.get('/api/admin/analytics/industries', { params: { days } }) },

  // ── 专业管理 ──
  getMajors(params: MajorListParams) {
    return http.get('/api/admin/majors', { params })
  },
  createMajor(data: { name: string; description?: string; icon?: string; sort_order?: number }) {
    return http.post('/api/admin/majors', data)
  },
  updateMajor(id: number, data: { name?: string; description?: string; icon?: string; is_active?: boolean; sort_order?: number }) {
    return http.put(`/api/admin/majors/${id}`, data)
  },
  deleteMajor(id: number) {
    return http.delete(`/api/admin/majors/${id}`)
  },
  getMajorIndustries(id: number) {
    return http.get(`/api/admin/majors/${id}/industries`)
  },
  setMajorIndustries(id: number, industryIds: number[]) {
    return http.post(`/api/admin/majors/${id}/industries`, { industry_ids: industryIds })
  },

  // ── 行业管理 ──
  getIndustries(params: IndustryListParams) {
    return http.get('/api/admin/industries', { params })
  },
  createIndustry(data: { name: string; major_id?: number; sort_order?: number }) {
    return http.post('/api/admin/industries', data)
  },
  updateIndustry(id: number, data: { name?: string; major_id?: number; is_active?: boolean; sort_order?: number }) {
    return http.put(`/api/admin/industries/${id}`, data)
  },
  deleteIndustry(id: number) {
    return http.delete(`/api/admin/industries/${id}`)
  },
  getAllIndustries() {
    return http.get('/api/admin/industries/all')
  },

  // ── 地区管理 ──
  getRegions(params: RegionListParams) {
    return http.get('/api/admin/regions', { params })
  },
  createRegion(data: { name: string; sort_order?: number }) {
    return http.post('/api/admin/regions', data)
  },
  updateRegion(id: number, data: { name?: string; is_active?: boolean; sort_order?: number }) {
    return http.put(`/api/admin/regions/${id}`, data)
  },
  deleteRegion(id: number) {
    return http.delete(`/api/admin/regions/${id}`)
  },

  // ── 省份管理 ──
  getProvinces(params: ProvinceListParams) {
    return http.get('/api/admin/provinces', { params })
  },
  createProvince(data: { name: string; sort_order?: number }) {
    return http.post('/api/admin/provinces', data)
  },
  updateProvince(id: number, data: { name?: string; is_active?: boolean; sort_order?: number }) {
    return http.put(`/api/admin/provinces/${id}`, data)
  },
  deleteProvince(id: number) {
    return http.delete(`/api/admin/provinces/${id}`)
  },

  // ── 城市管理 ──
  getCities(provinceId: number, params: CityListParams) {
    return http.get(`/api/admin/provinces/${provinceId}/cities`, { params })
  },
  createCity(data: { name: string; province_id: number; sort_order?: number }) {
    return http.post('/api/admin/cities', data)
  },
  updateCity(id: number, data: { name?: string; province_id?: number; is_active?: boolean; sort_order?: number }) {
    return http.put(`/api/admin/cities/${id}`, data)
  },
  deleteCity(id: number) {
    return http.delete(`/api/admin/cities/${id}`)
  },

  // ── 课时管理 ──
  getHours(params: HourListParams) {
    return http.get('/api/admin/hours', { params })
  },
  createHour(data: { value: number; label?: string; unit_price?: number; sort_order?: number }) {
    return http.post('/api/admin/hours', data)
  },
  updateHour(id: number, data: { value?: number; label?: string; unit_price?: number; is_active?: boolean; sort_order?: number }) {
    return http.put(`/api/admin/hours/${id}`, data)
  },
  deleteHour(id: number) {
    return http.delete(`/api/admin/hours/${id}`)
  },

  // ── 大模型配置 ──
  getLlmConfigs(params: LlmListParams) {
    return http.get('/api/admin/llm/configs', { params })
  },
  createLlmConfig(data: LlmConfigCreate) {
    return http.post('/api/admin/llm/configs', data)
  },
  updateLlmConfig(id: number, data: LlmConfigUpdate) {
    return http.put(`/api/admin/llm/configs/${id}`, data)
  },
  deleteLlmConfig(id: number) {
    return http.delete(`/api/admin/llm/configs/${id}`)
  },
  activateLlmConfig(id: number) {
    return http.post(`/api/admin/llm/configs/${id}/activate`)
  },
  getTokenStats(days: number = 30) {
    return http.get('/api/admin/llm/token-stats', { params: { days } })
  },
  fetchModels(apiBaseUrl: string, apiKey: string) {
    return http.post('/api/admin/llm/models', { api_base_url: apiBaseUrl, api_key: apiKey })
  },

  // ── 提示词模板 ──
  getPromptTemplates(params: PromptListParams) {
    return http.get('/api/admin/prompts', { params })
  },
  createPromptTemplate(data: PromptTemplateCreate) {
    return http.post('/api/admin/prompts', data)
  },
  getPromptTemplate(id: number) {
    return http.get(`/api/admin/prompts/${id}`)
  },
  updatePromptTemplate(id: number, data: { name?: string; description?: string; scene?: string }) {
    return http.put(`/api/admin/prompts/${id}`, data)
  },
  deletePromptTemplate(id: number) {
    return http.delete(`/api/admin/prompts/${id}`)
  },
  getPromptVersions(templateId: number) {
    return http.get(`/api/admin/prompts/${templateId}/versions`)
  },
  createPromptVersion(templateId: number, data: PromptVersionCreate) {
    return http.post(`/api/admin/prompts/${templateId}/versions`, data)
  },
  getPromptVersion(templateId: number, versionId: number) {
    return http.get(`/api/admin/prompts/${templateId}/versions/${versionId}`)
  },
  rollbackPromptVersion(templateId: number, versionId: number) {
    return http.post(`/api/admin/prompts/${templateId}/versions/${versionId}/rollback`)
  },
}
