import http from './http'

export const adminApi = {
  // 认证
  login(username: string, password: string) {
    return http.post('/api/admin/login', { username, password })
  },
  // 企业 CRUD
  getEnterprises(params: { page: number; page_size: number; industry?: string; province?: string; keyword?: string }) {
    return http.get('/api/admin/enterprises', { params })
  },
  createEnterprise(data: any) { return http.post('/api/admin/enterprises', data) },
  updateEnterprise(id: number, data: any) { return http.put(`/api/admin/enterprises/${id}`, data) },
  deleteEnterprise(id: number) { return http.delete(`/api/admin/enterprises/${id}`) },
  importExcel(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return http.post('/api/admin/enterprises/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  // 统计
  getAnalyticsSummary() { return http.get('/api/admin/analytics/summary') },
  getVisitTrends() { return http.get('/api/admin/analytics/visits') },
  getProvinceDistribution() { return http.get('/api/admin/analytics/provinces') },
  getCaseFrequency() { return http.get('/api/admin/analytics/case-frequency') },
  getIndustryDistribution() { return http.get('/api/admin/analytics/industries') },
}
