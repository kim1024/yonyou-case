# 用友产业案例教学课程定制系统 — 部署运维手册

## 目录

- [1. 项目概览](#1-项目概览)
- [2. 环境要求](#2-环境要求)
- [3. 本地开发](#3-本地开发)
- [4. 配置说明](#4-配置说明)
- [5. 生产部署](#5-生产部署)
  - [5.1 后端部署](#51-后端部署)
  - [5.2 前端构建与 Nginx 部署](#52-前端构建与-nginx-部署)
  - [5.3 systemd 服务管理](#53-systemd-服务管理)
- [6. 数据初始化与迁移](#6-数据初始化与迁移)
- [7. 常用运维操作](#7-常用运维操作)
- [8. 故障排查](#8-故障排查)

---

## 1. 项目概览

| 项目 | 说明 |
|------|------|
| 前端 | Vue 3 + TypeScript + Tailwind CSS，Vite 构建 |
| 后端 | Python 3.12 + FastAPI + SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 14+ |
| 认证 | JWT HS256 + bcrypt 密码哈希 |
| AI 接口 | OpenAI 兼容 API（可选，缺失时自动降级为模板生成） |

---

## 2. 环境要求

**后端：**
- Python 3.12+
- pip
- PostgreSQL 14+
- psycopg2-binary（Python PostgreSQL 驱动，已包含在 requirements.txt 中）

**前端：**
- Node.js 18+
- npm

**生产部署（额外）：**
- Nginx 1.18+
- systemd（Linux）

---

## 3. 本地开发

### 3.1 后端启动

```bash
# 进入项目根目录
cd yonyou-case

# 从模板创建配置文件
cp config.yaml.example config.yaml
# 编辑 config.yaml，至少修改 admin.password 和 admin.jwt_secret

# 进入后端目录，安装依赖
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 初始化数据库（首次运行）
python seed.py

# 启动开发服务器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后访问：
- API 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/api/health`

### 3.2 前端启动

```bash
# 新开终端，进入前端目录
cd yonyou-case/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后访问：`http://localhost:5173`

开发模式下，前端通过 Vite proxy 将 `/api` 请求自动转发至 `http://localhost:8000`。

---

## 4. 配置说明

配置文件位于项目根目录 `config.yaml`，首次使用从模板复制：

```bash
cp config.yaml.example config.yaml
```

### 配置项说明

```yaml
server:
  host: "0.0.0.0"             # 监听地址
  port: 8000                   # 监听端口
  cors_origins:                # 允许的前端跨域地址（生产环境改为实际域名）
    - "http://localhost:5173"

database:
  url: "postgresql://用户名:密码@host:port/数据库名"   # PostgreSQL 连接串

admin:
  username: "admin"            # 管理员用户名
  password: "changeme"         # 管理员密码（首次登录后务必修改）
  jwt_secret: "change-me-in-production"  # JWT 签名密钥（必须修改为随机字符串）

llm:
  api_key: "sk-xxx"            # OpenAI 兼容 API 密钥，填 "sk-xxx" 则使用模板生成
  api_base_url: "https://api.openai.com/v1"  # API 地址
  model: "gpt-4o"              # 模型名称
  temperature: 0.7             # 生成温度
  max_tokens: 2000             # 最大 token 数
  timeout: 60                  # 请求超时（秒）

pricing:
  rate_per_hour: 2000          # 课时单价（元/课时）

frontend:
  title: "用友产业案例教学项目课程定制系统"  # 页面标题
```

### 生产环境必须修改项

| 配置项 | 说明 | 风险 |
|--------|------|------|
| `admin.password` | 默认密码 `changeme` | 未授权访问管理后台 |
| `admin.jwt_secret` | 必须改为随机长字符串 | JWT 可被伪造 |
| `server.cors_origins` | 改为实际前端域名 | 跨域安全 |
| `llm.api_key` | 填入真实 API Key 或保留 `sk-xxx` 跳过 | 影响 AI 生成质量 |

生成随机 JWT 密钥：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 5. 生产部署

### 5.1 后端部署

```bash
# 1. 上传代码到服务器
scp -r yonyou-case/ user@server:/opt/yonyou-case/

# 2. SSH 登录服务器
ssh user@server

# 3. 创建虚拟环境并安装依赖
cd /opt/yonyou-case/backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. 配置
cd /opt/yonyou-case
cp config.yaml.example config.yaml
vim config.yaml   # 修改 admin.password、admin.jwt_secret、server.cors_origins、database.url 等

# 5. 安装 PostgreSQL（如未安装）
sudo apt install postgresql postgresql-contrib

# 6. 创建数据库和用户
sudo -u postgres psql
CREATE USER yonyou WITH PASSWORD 'your_password';
CREATE DATABASE yonyou_case OWNER yonyou;
GRANT ALL PRIVILEGES ON DATABASE yonyou_case TO yonyou;
\q

# 7. 初始化数据库
cd /opt/yonyou-case/backend
python seed.py

# 8. 创建必要目录
mkdir -p logs data

# 9. 测试启动
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# Ctrl+C 停止，确认无报错后继续配置 systemd
```

### 5.2 前端构建与 Nginx 部署

#### 构建前端

```bash
cd /opt/yonyou-case/frontend
npm install
npm run build
# 构建产物在 frontend/dist/ 目录
```

#### Nginx 配置

创建 Nginx 配置文件 `/etc/nginx/sites-available/yonyou-case`：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为实际域名或 IP

    # 前端静态文件
    root /opt/yonyou-case/frontend/dist;
    index index.html;

    # Vue Router history 模式支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理到后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 生成接口可能耗时较长
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

启用站点并重启 Nginx：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/yonyou-case /etc/nginx/sites-enabled/

# 检查配置语法
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

### 5.3 systemd 服务管理

创建服务文件 `/etc/systemd/system/yonyou-case.service`：

```ini
[Unit]
Description=Yonyou Case Teaching Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/yonyou-case/backend
Environment="PATH=/opt/yonyou-case/backend/venv/bin"
ExecStart=/opt/yonyou-case/backend/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

# 安全加固
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/opt/yonyou-case/backend/data /opt/yonyou-case/backend/logs

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

启用并启动：

```bash
sudo systemctl daemon-reload
sudo systemctl enable yonyou-case
sudo systemctl start yonyou-case

# 查看状态
sudo systemctl status yonyou-case

# 查看日志
sudo journalctl -u yonyou-case -f
```

---

## 6. 数据初始化与迁移

### 6.1 首次初始化

```bash
cd /opt/yonyou-case/backend
source venv/bin/activate

python seed.py
```

`seed.py` 做两件事：
1. 从 `old/data/data.xlsx` 导入企业数据到 PostgreSQL（仅在 `enterprises` 表为空时执行）
2. 从 `config.yaml` 创建管理员账号（仅在 `admin_users` 表为空时执行）

### 6.2 重新导入企业数据

如需重新导入（例如 Excel 数据更新）：

```bash
cd /opt/yonyou-case/backend
source venv/bin/activate

# 进入 Python 交互环境
python
```

```python
from app.database import engine
from sqlalchemy import text

# 清空企业表（保留管理员和访问日志）
with engine.connect() as conn:
    conn.execute(text("DELETE FROM enterprises"))
    conn.commit()

# 然后退出，重新运行 seed.py
```

```bash
python seed.py
```

### 6.3 重置管理员密码

修改 `config.yaml` 中的 `admin.password`，然后：

```bash
cd /opt/yonyou-case/backend
source venv/bin/activate

python
```

```python
from app.database import engine
from app.config import settings
from passlib.hash import bcrypt
from sqlalchemy import text

new_hash = bcrypt.hash(settings.admin.password)
with engine.connect() as conn:
    conn.execute(
        text("UPDATE admin_users SET password_hash = :h WHERE username = :u"),
        {"h": new_hash, "u": settings.admin.username}
    )
    conn.commit()
print("密码已更新")
```

### 6.4 数据库备份与恢复

```bash
# 备份
pg_dump -U yonyou -d yonyou_case -f /opt/yonyou-case/backend/data/yonyou_case.bak.$(date +%Y%m%d).sql

# 恢复
psql -U yonyou -d yonyou_case -f /opt/yonyou-case/backend/data/yonyou_case.bak.20260423.sql
sudo systemctl restart yonyou-case
```

### 6.5 数据库结构变更

如需修改表结构：

- **新增表/列**：修改 ORM model 后重启后端，`create_all()` 会自动创建新表，但**不会修改已有表的列**。
- **修改已有列**：需手动执行 `ALTER TABLE` SQL 语句。

---

## 7. 常用运维操作

### 查看服务状态

```bash
sudo systemctl status yonyou-case
```

### 查看后端日志

```bash
# systemd 日志
sudo journalctl -u yonyou-case --since "1 hour ago" -f

# 应用日志（按天滚动，保留 30 天）
tail -f /opt/yonyou-case/backend/logs/app.log
tail -f /opt/yonyou-case/backend/logs/error.log
```

### 重启服务

```bash
sudo systemctl restart yonyou-case
sudo systemctl reload nginx
```

### 更新部署

```bash
# 1. 备份数据库
pg_dump -U yonyou -d yonyou_case -f /opt/yonyou-case/backend/data/yonyou_case.bak.$(date +%Y%m%d).sql

# 2. 拉取最新代码
cd /opt/yonyou-case
git pull

# 3. 更新后端依赖（如有新增）
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 4. 重启后端
sudo systemctl restart yonyou-case

# 5. 重新构建前端
cd /opt/yonyou-case/frontend
npm install        # 如有新增依赖
npm run build

# 6. 重载 Nginx
sudo systemctl reload nginx
```

### 通过管理后台导入 Excel

1. 登录 `http://your-domain.com/login`
2. 进入 `/admin/enterprises` 页面
3. 点击「导入」按钮，上传 `.xlsx` 文件

---

## 8. 故障排查

| 现象 | 排查步骤 |
|------|----------|
| 后端启动失败，提示 `jwt_secret` 错误 | 检查 `config.yaml` 中 `admin.jwt_secret` 是否已修改（不能为 `change-me-in-production`） |
| 前端页面空白，控制台报 404 | 检查 Nginx `try_files` 配置是否正确，`root` 路径是否指向 `frontend/dist` |
| API 请求返回 CORS 错误 | 检查 `config.yaml` 中 `server.cors_origins` 是否包含前端实际访问地址 |
| AI 生成失败，返回模板内容 | 检查 `llm.api_key` 和 `llm.api_base_url` 是否正确，查看 `error.log` |
| 管理后台无法登录 | 确认密码是否正确，可按 [6.3 节](#63-重置管理员密码) 重置 |
| 导入 Excel 失败 | 确认文件为 `.xlsx` 格式，表头需包含：客户名称、省份、城市、行业、公司简介、用友相关内容 |
| PostgreSQL 连接失败 | 检查 PostgreSQL 服务状态 `sudo systemctl status postgresql`，确认连接串正确，检查 `pg_hba.conf` 允许的客户端地址 |
| `npm run build` 类型检查失败 | 运行 `npx vue-tsc --noEmit` 查看具体 TypeScript 错误 |
