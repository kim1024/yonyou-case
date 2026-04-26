import http from './http'

export const wizardApi = {
  getMajors() { return http.get('/api/majors') },
  getIndustries(majorId?: number) {
    const params = majorId !== undefined ? { major_id: majorId } : undefined
    return http.get('/api/industries', { params })
  },
  getRegions(industry: string) { return http.post('/api/regions', { industry }) },
  getEnterprises(industry: string, province: string) {
    return http.post('/api/enterprises', { industry, province })
  },
  getEnterpriseInfo(industry: string, province: string, name: string) {
    return http.post('/api/enterprise-info', { industry, province, name })
  },
  getHours() { return http.get('/api/hours') },
  getConfig() { return http.get('/api/config') },
  generate(data: { major: string; industry: string; enterprise: string; region: string; hour: number; client_request_id?: string }, config?: { signal?: AbortSignal }) {
    return http.post('/api/generate', data, { ...config, timeout: 120000 })
  },
  getGenerateStatus(client_request_id: string) {
    return http.get(`/api/generate/status/${client_request_id}`)
  },
}
