"""地区管理路由 —— 已废弃，请使用 /api/admin/provinces 路由。"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/admin/regions", tags=["admin-regions"])

# 所有地区管理接口已迁移至：
# - GET/POST        /api/admin/provinces             —— 省份列表 / 新增省份
# - PUT/DELETE      /api/admin/provinces/{id}        —— 编辑 / 删除省份（含企业数据同步）
# - GET/POST        /api/admin/provinces/{id}/cities  —— 城市列表 / 新增城市
# - PUT/DELETE      /api/admin/cities/{id}           —— 编辑 / 删除城市（含企业数据同步）
