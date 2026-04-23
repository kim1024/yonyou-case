// 企业
export interface Enterprise {
  id: number
  customer_name: string
  province: string
  city: string
  industry: string
  company_intro?: string
  yonyou_content?: string
  created_at?: string
  updated_at?: string
}

// 向导状态
export interface WizardState {
  currentStep: number
  major: string | null
  industry: string | null
  region: string | null
  enterprise: Enterprise | null
  hour: string | null
}

// 级联数据
export interface CascadeData {
  majors: string[]
  industries: string[]
  regions: string[]
  enterprises: Enterprise[]
  hours: string[]
  enterpriseInfo: Enterprise | null
}

// 认证
export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  username: string
}

// 统计
export interface AnalyticsSummary {
  total_visits: number
  total_enterprises: number
  today_visits: number
  week_visits: number
}

export interface VisitTrend {
  date: string
  count: number
}

export interface ProvinceCount {
  province: string
  count: number
}

export interface CaseFrequency {
  enterprise: string
  industry: string
  count: number
}

export interface IndustryCount {
  industry: string
  count: number
}

// 管理后台 - 企业列表
export interface EnterpriseListParams {
  page: number
  page_size: number
  industry?: string
  province?: string
  keyword?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// 前端配置
export interface FrontendConfig {
  title: string
}

// 通用 API 响应
export interface ApiResponse<T> {
  code: number
  data: T
  message?: string
}
