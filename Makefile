# ============================================================
# 用友产业案例教学课程定制系统 — 服务管理 Makefile
# ============================================================
# 用法:
#   make dev-start     开发模式启动（带热重载）
#   make dev-stop      停止开发模式进程
#   make dev-restart   重启开发模式
#   make dev-status    查看开发模式进程状态
#
#   make deploy        一键部署（构建前端 + 重启后端 + 重载 Nginx）
#   make start         生产模式启动（通过 systemd）
#   make stop          生产模式停止（通过 systemd）
#   make restart       生产模式重启（通过 systemd）
#   make status        查看生产服务状态
#
#   make setup         首次部署：创建 conda 环境、安装依赖、初始化数据库
#   make build-frontend 构建前端
#   make backup-db     备份数据库
#   make logs          查看后端日志（实时）
#   make health        健康检查
# ============================================================

# ---------- 可覆盖变量 ----------
PROJECT_ROOT   := $(shell pwd)
BACKEND_DIR    := $(PROJECT_ROOT)/backend
FRONTEND_DIR   := $(PROJECT_ROOT)/frontend
LOG_DIR        := $(BACKEND_DIR)/logs
PID_FILE       := $(BACKEND_DIR)/uvicorn.pid

# conda 环境配置（线上 Miniforge3）
CONDA_DIR      ?= $(HOME)/miniforge3
CONDA_ENV_NAME ?= yonyou-case
CONDA_ENV      := $(CONDA_DIR)/envs/$(CONDA_ENV_NAME)
PYTHON         := $(CONDA_ENV)/bin/python
PIP            := $(CONDA_ENV)/bin/pip
CONDA_RUN      := conda run -n $(CONDA_ENV_NAME) --no-capture-output

HOST           ?= 0.0.0.0
PORT           ?= 8000
WORKERS        ?= 4

SERVICE_NAME   := yonyou-case
DB_NAME        ?= yonyou_case
DB_USER        ?= yonyou
BACKUP_DIR     := $(BACKEND_DIR)/data

# ---------- 颜色 ----------
C_RESET  := \033[0m
C_GREEN  := \033[32m
C_YELLOW := \033[33m
C_CYAN   := \033[36m
C_RED    := \033[31m

# ============================================================
# 开发模式（本地进程，无 systemd）
# ============================================================

.PHONY: dev-start dev-stop dev-restart dev-status

## 启动开发服务器（单进程 + 热重载）
dev-start:
	@mkdir -p $(LOG_DIR)
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "$(C_YELLOW)[!] 开发服务器已在运行 (PID: $$(cat $(PID_FILE)))$(C_RESET)"; \
		exit 1; \
	fi
	@echo "$(C_GREEN)[>] 启动开发服务器（单进程热重载）...$(C_RESET)"
	cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn app.main:app \
		--host $(HOST) --port $(PORT) --reload &
	@echo $$! > $(PID_FILE)
	@echo "$(C_GREEN)[OK] 开发服务器已启动 (PID: $$!, 端口: $(PORT))$(C_RESET)"

## 停止开发服务器
dev-stop:
	@if [ -f $(PID_FILE) ]; then \
		PID=$$(cat $(PID_FILE)); \
		if kill -0 $$PID 2>/dev/null; then \
			echo "$(C_YELLOW)[>] 停止开发服务器 (PID: $$PID)...$(C_RESET)"; \
			kill $$PID; \
			rm -f $(PID_FILE); \
			echo "$(C_GREEN)[OK] 已停止$(C_RESET)"; \
		else \
			echo "$(C_YELLOW)[!] 进程 $$PID 已不存在，清理 PID 文件$(C_RESET)"; \
			rm -f $(PID_FILE); \
		fi; \
	else \
		echo "$(C_YELLOW)[!] 未找到 PID 文件$(C_RESET)"; \
	fi

## 重启开发服务器
dev-restart: dev-stop
	@sleep 1
	@$(MAKE) dev-start

## 查看开发服务器状态
dev-status:
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "$(C_GREEN)[OK] 开发服务器运行中 (PID: $$(cat $(PID_FILE)), 端口: $(PORT))$(C_RESET)"; \
	else \
		echo "$(C_YELLOW)[-] 开发服务器未运行$(C_RESET)"; \
	fi

# ============================================================
# 生产模式（systemd 管理，多 worker 高并发）
# ============================================================

.PHONY: start stop restart status

## 启动生产服务（systemd，多 worker 高并发）
start:
	@echo "$(C_GREEN)[>] 启动 $(SERVICE_NAME)（$(WORKERS) workers）...$(C_RESET)"
	sudo systemctl start $(SERVICE_NAME)
	@sleep 1
	@sudo systemctl is-active --quiet $(SERVICE_NAME) \
		&& echo "$(C_GREEN)[OK] 服务已启动$(C_RESET)" \
		|| (echo "$(C_RED)[X] 启动失败，查看日志：make logs$(C_RESET)" && exit 1)

## 停止生产服务
stop:
	@echo "$(C_YELLOW)[>] 停止 $(SERVICE_NAME)...$(C_RESET)"
	sudo systemctl stop $(SERVICE_NAME)
	@echo "$(C_GREEN)[OK] 服务已停止$(C_RESET)"

## 重启生产服务（平滑重启，不中断请求）
restart:
	@echo "$(C_GREEN)[>] 重启 $(SERVICE_NAME)...$(C_RESET)"
	sudo systemctl restart $(SERVICE_NAME)
	@sleep 1
	@sudo systemctl is-active --quiet $(SERVICE_NAME) \
		&& echo "$(C_GREEN)[OK] 服务已重启$(C_RESET)" \
		|| (echo "$(C_RED)[X] 重启失败，查看日志：make logs$(C_RESET)" && exit 1)

## 查看生产服务状态
status:
	@echo "$(C_CYAN)--- 服务状态 ---$(C_RESET)"
	@sudo systemctl status $(SERVICE_NAME) --no-pager -l || true
	@echo ""
	@echo "$(C_CYAN)--- 健康检查 ---$(C_RESET)"
	@curl -sf http://127.0.0.1:8000/api/health && echo "" \
		|| echo "$(C_RED)[X] 健康检查失败$(C_RESET)"

# ============================================================
# 部署
# ============================================================

.PHONY: deploy build-frontend

## 一键部署：拉取代码 → 更新依赖 → 构建前端 → 重启后端 → 重载 Nginx
deploy: _preflight
	@echo "$(C_CYAN)========== 开始部署 ==========$(C_RESET)"
	@echo "$(C_GREEN)[1/5] 拉取最新代码...$(C_RESET)"
	cd $(PROJECT_ROOT) && git pull
	@echo "$(C_GREEN)[2/5] 更新后端依赖...$(C_RESET)"
	cd $(BACKEND_DIR) && $(PIP) install -r requirements.txt -q
	@echo "$(C_GREEN)[3/5] 构建前端...$(C_RESET)"
	cd $(FRONTEND_DIR) && npm install --silent && npm run build
	@echo "$(C_GREEN)[4/5] 重启后端服务...$(C_RESET)"
	sudo systemctl restart $(SERVICE_NAME)
	@sleep 2
	@sudo systemctl is-active --quiet $(SERVICE_NAME) \
		|| (echo "$(C_RED)[X] 后端重启失败$(C_RESET)" && exit 1)
	@echo "$(C_GREEN)[5/5] 重载 Nginx...$(C_RESET)"
	sudo nginx -t && sudo systemctl reload nginx
	@echo "$(C_GREEN)========== 部署完成 ==========$(C_RESET)"
	@$(MAKE) health

## 仅构建前端
build-frontend:
	@echo "$(C_GREEN)[>] 构建前端...$(C_RESET)"
	cd $(FRONTEND_DIR) && npm install --silent && npm run build
	@echo "$(C_GREEN)[OK] 前端构建完成 ($(FRONTEND_DIR)/dist)$(C_RESET)"

# ============================================================
# 首次安装
# ============================================================

.PHONY: setup

## 首次部署：创建 conda 环境 → 安装依赖 → 安装前端依赖 → 初始化数据库
setup: _check-config
	@echo "$(C_CYAN)========== 首次安装 ==========$(C_RESET)"
	@echo "$(C_GREEN)[1/4] 创建 conda 环境 ($(CONDA_ENV_NAME), Python 3.12)...$(C_RESET)"
	conda create -n $(CONDA_ENV_NAME) python=3.12 -y
	@echo "$(C_GREEN)[2/4] 安装后端依赖...$(C_RESET)"
	$(PIP) install -r $(BACKEND_DIR)/requirements.txt
	@echo "$(C_GREEN)[3/4] 安装前端依赖...$(C_RESET)"
	cd $(FRONTEND_DIR) && npm install
	@echo "$(C_GREEN)[4/4] 初始化数据库...$(C_RESET)"
	cd $(BACKEND_DIR) && $(PYTHON) seed.py
	@echo ""
	@echo "$(C_GREEN)[OK] 首次安装完成$(C_RESET)"
	@echo "    conda 环境: $(CONDA_ENV)"
	@echo "    后端端口:   $(PORT)"
	@echo "    启动命令:   make start"

# ============================================================
# 数据库
# ============================================================

.PHONY: backup-db

## 备份数据库
backup-db:
	@mkdir -p $(BACKUP_DIR)
	@BACKUP_FILE=$(BACKUP_DIR)/$(DB_NAME).bak.$$(date +%Y%m%d%H%M%S).sql; \
	echo "$(C_GREEN)[>] 备份数据库到 $$BACKUP_FILE ...$(C_RESET)"; \
	pg_dump -U $(DB_USER) -d $(DB_NAME) -f $$BACKUP_FILE; \
	echo "$(C_GREEN)[OK] 备份完成 ($$(du -h $$BACKUP_FILE | cut -f1))$(C_RESET)"

# ============================================================
# 运维
# ============================================================

.PHONY: logs logs-error health

## 查看后端日志（实时跟踪）
logs:
	tail -f $(LOG_DIR)/app.log

## 查看错误日志
logs-error:
	tail -f $(LOG_DIR)/error.log

## 健康检查
health:
	@echo "$(C_CYAN)[>] 健康检查: http://127.0.0.1:$(PORT)/api/health$(C_RESET)"
	@curl -sf http://127.0.0.1:$(PORT)/api/health | $(PYTHON) -m json.tool 2>/dev/null \
		|| echo "$(C_RED)[X] 服务不可达$(C_RESET)"

# ============================================================
# 内部检查
# ============================================================

.PHONY: _preflight _check-config

# 部署前检查：conda 环境、systemd 服务存在
_preflight:
	@test -d $(CONDA_ENV) || (echo "$(C_RED)[X] conda 环境 $(CONDA_ENV_NAME) 不存在，请先运行 make setup$(C_RESET)" && exit 1)
	@systemctl list-unit-files | grep -q $(SERVICE_NAME) \
		|| (echo "$(C_RED)[X] systemd 服务 $(SERVICE_NAME) 不存在，请参考 DEPLOY.md 创建$(C_RESET)" && exit 1)
	@test -f $(PROJECT_ROOT)/config.yaml \
		|| (echo "$(C_RED)[X] config.yaml 不存在，请从 config.yaml.example 复制并修改$(C_RESET)" && exit 1)

# 安装前检查：config.yaml 存在
_check-config:
	@test -f $(PROJECT_ROOT)/config.yaml \
		|| (echo "$(C_RED)[X] config.yaml 不存在，请先执行：$(C_RESET)" \
			&& echo "    cp config.yaml.example config.yaml" \
			&& echo "    # 编辑 config.yaml 后重新运行 make setup" \
			&& exit 1)

# ============================================================
# 帮助
# ============================================================

.PHONY: help

## 显示帮助信息
help:
	@echo ""
	@echo "  $(C_CYAN)用友产业案例教学课程定制系统 — 服务管理$(C_RESET)"
	@echo ""
	@echo "  $(C_GREEN)首次安装:$(C_RESET)"
	@echo "    make setup             创建 conda 环境、安装依赖、初始化数据库"
	@echo ""
	@echo "  $(C_GREEN)开发模式:$(C_RESET)"
	@echo "    make dev-start         启动（单进程热重载，端口 $(PORT)）"
	@echo "    make dev-stop          停止"
	@echo "    make dev-restart       重启"
	@echo "    make dev-status        状态"
	@echo ""
	@echo "  $(C_GREEN)生产模式:$(C_RESET)"
	@echo "    make start             启动（systemd）"
	@echo "    make stop              停止"
	@echo "    make restart           重启"
	@echo "    make status            状态 + 健康检查"
	@echo ""
	@echo "  $(C_GREEN)部署:$(C_RESET)"
	@echo "    make deploy            一键部署（代码 → 依赖 → 前端 → 后端 → Nginx）"
	@echo "    make build-frontend    仅构建前端"
	@echo ""
	@echo "  $(C_GREEN)运维:$(C_RESET)"
	@echo "    make backup-db         备份数据库"
	@echo "    make logs              查看后端日志（实时）"
	@echo "    make logs-error        查看错误日志"
	@echo "    make health            健康检查"
	@echo ""

.DEFAULT_GOAL := help
