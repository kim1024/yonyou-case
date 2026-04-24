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

// 向导用课时（API 返回）
export interface WizardHour {
  value: number
  label: string
  unit_price: number
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
  hours: WizardHour[]
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

/** 行业精简项（industries/all 端点返回） */
export interface IndustryOption {
  id: number
  name: string
}

// 地区
export interface Region {
  id: number
  name: string
  is_active: boolean
  sort_order: number
  enterprise_count?: number
  created_at: string
  updated_at: string
}

// 省份
export interface Province {
  id: number
  name: string
  is_active: boolean
  sort_order: number
  city_count?: number
  created_at: string
}

// 城市
export interface City {
  id: number
  name: string
  province_id: number
  is_active: boolean
  sort_order: number
  created_at: string
}

// 课时
export interface Hour {
  id: number
  value: number
  label: string
  unit_price: number
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

// 省份管理 - 列表查询
export interface ProvinceListParams {
  is_active?: boolean
}

// 城市管理 - 列表查询
export interface CityListParams {
  province_id: number
  is_active?: boolean
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

// ── 大模型配置 ──
export interface LlmConfig {
  id: number
  name: string
  api_base_url: string
  api_key_masked: string
  model: string
  temperature: number
  max_tokens: number
  timeout: number
  is_active: boolean
  created_at: string | null
  updated_at: string | null
}

export interface LlmConfigCreate {
  name: string
  api_base_url: string
  api_key: string
  model: string
  temperature: number
  max_tokens: number
  timeout: number
  is_active: boolean
}

export interface LlmConfigUpdate {
  name?: string
  api_base_url?: string
  api_key?: string
  model?: string
  temperature?: number
  max_tokens?: number
  timeout?: number
  is_active?: boolean
}

// ── Token 统计 ──
export interface TokenStats {
  total_tokens: number
  total_calls: number
  today_tokens: number
  today_calls: number
  avg_tokens_per_call: number
  by_model: { model: string; total_tokens: number; calls: number }[]
  daily_trend: { date: string; tokens: number; calls: number }[]
}

// ── 提示词模板 ──
export interface PromptTemplate {
  id: number
  name: string
  description: string | null
  is_active: boolean
  current_version_id: number | null
  current_version_number: number | null
  content_summary: string | null
  created_at: string | null
  updated_at: string | null
}

export interface PromptTemplateDetail {
  id: number
  name: string
  description: string | null
  is_active: boolean
  current_version_id: number | null
  created_at: string | null
  updated_at: string | null
  current_version: PromptVersion | null
}

export interface PromptVersion {
  id: number
  version_number: number
  content: string
  variables: string | null
  remark: string | null
  created_by: string | null
  created_at: string | null
  is_current?: boolean
}

export interface PromptTemplateCreate {
  name: string
  description?: string
  content: string
  variables?: string
  remark?: string
}

export interface PromptVersionCreate {
  content: string
  variables?: string
  remark?: string
  created_by?: string
}

export interface LlmListParams {
  page: number
  page_size: number
}

export interface PromptListParams {
  page: number
  page_size: number
  keyword?: string
}

// ── 课程方案（JSON 结构化） ──
export interface CourseModule {
  name: string
  hours: number
  items: string[]
}

export interface CoursePosition {
  title: string
  description: string[]
}

export interface CoursePricing {
  hour: number
  unit_price: number
  total_cost: number
}

export interface CoursePlan {
  title: string
  subtitle: string
  introduction: string
  modules: CourseModule[]
  positions: CoursePosition[]
  deliverables: string[]
  notes: string
  pricing: CoursePricing
}

// ── 生成方案管理 ──
export interface GeneratedPlanListItem {
  id: number
  major: string
  industry: string
  enterprise: string
  province: string
  hour: number
  source: 'ai' | 'template'
  plan_title: string
  created_at: string
}

export interface GeneratedPlan extends GeneratedPlanListItem {
  plan_data: CoursePlan
}

export interface PlanListParams {
  page: number
  page_size: number
  source?: 'ai' | 'template'
  major?: string
  industry?: string
  province?: string
  keyword?: string
  date_from?: string
  date_to?: string
}
