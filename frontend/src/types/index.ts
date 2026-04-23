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

// 向导状态（单页渐进式解锁）
export interface WizardState {
  major: string | null
  majorId: number | null
  industry: string | null
  region: string | null
  enterprise: string | null
  hour: number | null
}

// 级联数据（单页模式）
export interface CascadeData {
  majors: WizardMajor[]
  industries: string[]
  regions: string[]
  enterprises: string[]
  hours: number[]
  enterpriseInfo: MajorEnterpriseInfo | null
}

// 向导用专业（API 返回）
export interface WizardMajor {
  id: number
  name: string
  description: string
  icon: string
}

// 向导用企业详情（API 返回）
export interface MajorEnterpriseInfo {
  id: number
  customer_name: string
  province: string
  city: string
  industry: string
  company_intro?: string
  yonyou_content?: string
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

// 专业
export interface Major {
  id: number
  name: string
  description: string
  icon: string
  is_active: boolean
  sort_order: number
  industry_count?: number
  created_at: string
  updated_at: string
}

// 行业
export interface Industry {
  id: number
  name: string
  major_id?: number
  major_name?: string
  is_active: boolean
  sort_order: number
  enterprise_count?: number
  created_at: string
  updated_at: string
}

// 地区
export interface Region {
  id: number
  name: string
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

// 课时
export interface Hour {
  id: number
  value: number
  label: string
  is_active: boolean
  sort_order: number
  created_at: string
}

// 专业管理 - 列表查询
export interface MajorListParams {
  page: number
  page_size: number
  keyword?: string
}

// 行业管理 - 列表查询
export interface IndustryListParams {
  page: number
  page_size: number
  keyword?: string
  major_id?: number
}

// 地区管理 - 列表查询
export interface RegionListParams {
  page: number
  page_size: number
  keyword?: string
}

// 课时管理 - 列表查询
export interface HourListParams {
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
