import http from './http'
import type {
  Major, Industry, Region, Hour,
  MajorListParams, IndustryListParams, RegionListParams, HourListParams,
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
  getVisitTrends() { return http.get('/api/admin/analytics/visits') },
  getProvinceDistribution() { return http.get('/api/admin/analytics/provinces') },
  getCaseFrequency() { return http.get('/api/admin/analytics/case-frequency') },
  getIndustryDistribution() { return http.get('/api/admin/analytics/industries') },

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

  // ── 课时管理 ──
  getHours(params: HourListParams) {
    return http.get('/api/admin/hours', { params })
  },
  createHour(data: { value: number; label?: string; sort_order?: number }) {
    return http.post('/api/admin/hours', data)
  },
  updateHour(id: number, data: { value?: number; label?: string; is_active?: boolean; sort_order?: number }) {
    return http.put(`/api/admin/hours/${id}`, data)
  },
  deleteHour(id: number) {
    return http.delete(`/api/admin/hours/${id}`)
  },
}
