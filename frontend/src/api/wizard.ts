import http from './http'

export const wizardApi = {
  getMajors() { return http.get('/api/majors') },
  getIndustries() { return http.get('/api/industries') },
  getRegions(industry: string) { return http.post('/api/regions', { industry }) },
  getEnterprises(industry: string, province: string) {
    return http.post('/api/enterprises', { industry, province })
  },
  getEnterpriseInfo(industry: string, province: string, name: string) {
    return http.post('/api/enterprise-info', { industry, province, name })
  },
  getHours() { return http.get('/api/hours') },
  getConfig() { return http.get('/api/config') },
  generate(data: { major: string; industry: string; enterprise: string; hour: number }) {
    return http.post('/api/generate', data)
  },
}
