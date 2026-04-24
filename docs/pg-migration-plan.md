# SQLite → PostgreSQL 迁移 + 并发问题修复计划

> 审计日期: 2026-04-24

## 一、背景

项目当前使用 SQLite + FastAPI (uvicorn 单进程) 部署。经全面审计发现：

- **SQLite 单写锁** 是前端高并发写入的核心瓶颈（如 `POST /api/generate`）
- 存在 **Critical 级别事务问题**（中间件写入竞态、wizard 双 commit 无原子性）
- 存在 **Medium 级别问题**（CRUD 缺少事务保护、先删后加无原子性）
- 代码中存在 **SQLite 硬编码**（PRAGMA、strftime、原生 sqlite3 迁移）

决策：**全面切换到 PostgreSQL**，同时修复所有 Critical/Medium 问题。

---

## 二、迁移影响范围

| 级别 | 类别 | 涉及文件 | 问题描述 |
|------|------|----------|----------|
| 🔴 | 数据库引擎 | `database.py` | 硬编码 `sqlite:///` URL、PRAGMA、`check_same_thread` |
| 🔴 | 数据迁移 | `database.py` migrate_db() | 全部使用原生 `sqlite3` + PRAGMA table_info |
| 🔴 | SQLite 函数 | `analytics_service.py`, `admin_llm.py` | `func.strftime()` PostgreSQL 不支持 |
| 🟡 | DateTime | `province_city.py` | `default=datetime.utcnow` 已弃用（Python 3.12+） |
| 🟡 | 事务竞态 | `analytics_middleware.py` | 异步多线程写入无队列化，高并发下争锁 |
| 🟡 | 事务原子性 | `wizard.py` | TokenUsageLog + GeneratedPlan 分两次 commit |
| 🟡 | 事务保护 | `database.py` get_db() | 无显式 rollback 保护 |
| 🟡 | 事务原子性 | `admin_majors.py` | `set_major_industries` 先删后加无 savepoint |
| 🟢 | 部署配置 | `requirements.txt`, `DEPLOY.md`, `config.yaml` | 添加 psycopg2-binary、PG 连接串 |

**ORM 兼容性:** 所有 12 个模型的 Column 类型（Integer, String, Text, Boolean, Float, DateTime）与 PostgreSQL 完全兼容，无需修改模型定义。

---

## 三、实施任务

### Task 1: database.py 重写 — 支持 PostgreSQL + 连接池

**文件:** `backend/app/database.py`

**改动:**

1. 从 `config.yaml` 读取 `database.url`，支持 `postgresql://` 和 `sqlite:///`
2. 根据 URL 前缀条件配置 engine：
   - **SQLite 模式:** `connect_args={"check_same_thread": False}`, 注册 PRAGMA listener
   - **PostgreSQL 模式:** `pool_size=10, max_overflow=20, pool_timeout=30, pool_pre_ping=True`
3. 删除 `migrate_db()` 函数（PG 用 `Base.metadata.create_all()`，种子数据由 `seed.py` 负责）
4. `get_db()` 添加异常时 rollback 保护
5. `recover_visit_logs()` 和 `seed_database()` 保持不变

```python
from app.config import settings

db_url = settings.get("database", {}).get("url", "sqlite:///./data/app.db")

if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    # 注册 PRAGMA listener（WAL + busy_timeout）
else:
    engine = create_engine(db_url, pool_size=10, max_overflow=20, pool_pre_ping=True)
```

---

### Task 2: 消除 SQLite 特定查询语法

**文件:**
- `backend/app/services/analytics_service.py`
- `backend/app/routers/admin_llm.py`

**改动:** `func.strftime('%Y-%m-%d', col)` 替换为数据库无关的 `cast(col, Date)`：

```python
from sqlalchemy import cast, Date

# 之前 (SQLite 专有):
func.strftime('%Y-%m-%d', VisitLog.request_timestamp).label("date")

# 之后 (PG + SQLite 通用):
cast(VisitLog.request_timestamp, Date).label("date")
```

共 6 处替换（analytics_service.py 3 处 + admin_llm.py 3 处）。

---

### Task 3: 修复 province_city.py DateTime 默认值

**文件:** `backend/app/models/province_city.py`

**改动:**

```python
# 之前 (Python 侧默认值，已弃用):
created_at = Column(DateTime, default=datetime.utcnow)

# 之后 (数据库侧默认值):
created_at = Column(DateTime, server_default=func.now())
```

涉及 `Province.created_at` 和 `City.created_at` 两个字段。

---

### Task 4: AnalyticsMiddleware 写入队列化（Critical）

**文件:** `backend/app/middleware/analytics_middleware.py`

**问题:** `asyncio.create_task(asyncio.to_thread(write_log))` 在高并发下多个线程竞争 SQLite 写锁，PostgreSQL 虽无此问题但队列化仍可降低连接池压力。

**改动:**

- 引入 `asyncio.Queue` + 单一消费者协程
- 所有 VisitLog 写入排队串行执行
- 保留重试逻辑和 JSONL 备份
- 应用关闭时优雅排空队列（lifespan/shutdown 事件）

---

### Task 5: wizard.py 双 commit 合并（Critical）

**文件:** `backend/app/routers/wizard.py`（约 508-540 行）

**问题:** TokenUsageLog 和 GeneratedPlan 分两次 `db.commit()`，中间失败导致数据不一致。

**改动:**

```python
# 之前:
db.add(log)
db.commit()           # 第一次 commit
db.add(plan_record)
db.commit()           # 第二次 commit

# 之后:
db.add(log)
db.add(plan_record)
db.commit()           # 单次原子提交
```

模板回退路径（约 555-566 行）同样处理。添加 try/except 保护。

---

### Task 6: set_major_industries savepoint（Medium）

**文件:** `backend/app/routers/admin_majors.py`（约 187-194 行）

**问题:** 先删后加操作，中间异常导致旧关联丢失、新关联未写入。

**改动:**

```python
db.query(MajorIndustry).filter(MajorIndustry.major_id == major_id).delete()
savepoint = db.begin_nested()
try:
    for ind_id in data.industry_ids:
        db.add(MajorIndustry(major_id=major_id, industry_id=ind_id))
    savepoint.commit()
except Exception:
    savepoint.rollback()
    raise
```

---

### Task 7: config.yaml 更新数据库连接

**文件:** `config.yaml`

**改动:**

```yaml
database:
  url: "postgresql://用户名:密码@host:port/数据库名"  # 替换为实际连接信息
```

---

### Task 8: 依赖与部署配置

**文件:**
- `backend/requirements.txt` — 添加 `psycopg2-binary`
- `DEPLOY.md` — 添加 PostgreSQL 创建数据库和用户的说明

---

## 四、执行顺序

```
Phase 1 (基础设施):
  Task 1 (database.py 重写) + Task 7 (config.yaml) + Task 8 (依赖)

Phase 2 (代码兼容，可并行):
  Task 2 (strftime → cast/Date)
  Task 3 (datetime.utcnow → server_default)
  Task 4 (middleware 队列化)
  Task 5 (wizard 双 commit 合并)
  Task 6 (savepoint)

Phase 3 (验证):
  启动应用 → 确认表自动创建 → seed 数据 → 测试所有接口
```

---

## 五、关键文件清单

| 文件 | 操作 |
|------|------|
| `backend/app/database.py` | **重写** — PG engine、连接池、条件 PRAGMA、get_db rollback |
| `backend/app/services/analytics_service.py` | strftime → cast/Date（3 处） |
| `backend/app/routers/admin_llm.py` | strftime → cast/Date（3 处） |
| `backend/app/models/province_city.py` | datetime.utcnow → server_default=func.now()（2 处） |
| `backend/app/middleware/analytics_middleware.py` | 写入队列化重构 |
| `backend/app/routers/wizard.py` | 合并双 commit（2 处） |
| `backend/app/routers/admin_majors.py` | savepoint 保护（1 处） |
| `config.yaml` | PostgreSQL 连接串 |
| `backend/requirements.txt` | 添加 psycopg2-binary |
| `DEPLOY.md` | 更新部署说明 |

---

## 六、验证方式

1. **连接验证:** 启动应用，确认 PostgreSQL 连接成功，所有表通过 `create_all` 自动创建
2. **种子数据:** `python seed.py` 执行成功，数据正确写入 PG
3. **接口功能测试:** 对所有 CRUD 接口（企业、专业、行业、省市、课时、提示词、LLM 配置、方案）执行增删改查
4. **并发压测:** 使用 `ab -n 100 -c 20` 测试只读接口 + 多个 `POST /api/generate` 并发写入
5. **中间件验证:** 确认 visit_logs 写入正常，JSONL 备份正常追加
6. **事务验证:** 验证 wizard.py 原子提交、set_major_industries savepoint 回滚
