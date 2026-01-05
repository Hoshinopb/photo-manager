#!/bin/bash

# 图片管理系统启动脚本
# 用法: ./start.sh [command]
# 命令: all | backend | frontend | celery | redis | stop

set -e

# 获取脚本所在目录作为项目根目录（支持相对路径）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
CONDA_ENV="photo"
# 自动检测 conda 安装路径
if [ -d "$HOME/miniconda3" ]; then
    CONDA_PATH="$HOME/miniconda3"
elif [ -d "$HOME/anaconda3" ]; then
    CONDA_PATH="$HOME/anaconda3"
elif [ -d "/opt/conda" ]; then
    CONDA_PATH="/opt/conda"
else
    # 尝试从 conda 命令获取路径
    CONDA_PATH="$(dirname "$(dirname "$(which conda 2>/dev/null)")")" 2>/dev/null || CONDA_PATH=""
fi

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 激活 conda 环境
activate_conda() {
    source "$CONDA_PATH/etc/profile.d/conda.sh"
    conda activate $CONDA_ENV
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 杀掉占用端口的进程
kill_port() {
    local port=$1
    if check_port $port; then
        log_warn "端口 $port 被占用，正在释放..."
        lsof -i :$port | grep LISTEN | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true
        sleep 1
    fi
}

# 启动 Redis
start_redis() {
    log_info "检查 Redis 状态..."
    if systemctl is-active --quiet redis 2>/dev/null; then
        log_info "Redis 已经在运行"
    else
        log_info "启动 Redis..."
        sudo systemctl start redis 2>/dev/null || redis-server --daemonize yes
        sleep 1
        log_info "Redis 已启动"
    fi
}

# 停止 Redis
stop_redis() {
    log_info "停止 Redis..."
    sudo systemctl stop redis 2>/dev/null || pkill redis-server 2>/dev/null || true
}

# 启动后端
start_backend() {
    log_info "启动 Django 后端..."
    kill_port 8000
    
    cd "$BACKEND_DIR"
    activate_conda
    
    # 运行数据库迁移
    log_info "检查数据库迁移..."
    python manage.py migrate --run-syncdb > /dev/null 2>&1 || true
    
    # 启动 Django 开发服务器
    nohup python manage.py runserver 0.0.0.0:8000 > "$PROJECT_ROOT/logs/backend.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/pids/backend.pid"
    
    sleep 2
    if check_port 8000; then
        log_info "Django 后端已启动 (PID: $(cat $PROJECT_ROOT/pids/backend.pid))"
        log_info "后端地址: http://localhost:8000"
    else
        log_error "Django 后端启动失败，请查看日志: $PROJECT_ROOT/logs/backend.log"
    fi
}

# 停止后端
stop_backend() {
    log_info "停止 Django 后端..."
    if [ -f "$PROJECT_ROOT/pids/backend.pid" ]; then
        kill $(cat "$PROJECT_ROOT/pids/backend.pid") 2>/dev/null || true
        rm "$PROJECT_ROOT/pids/backend.pid"
    fi
    kill_port 8000
}

# 启动前端
start_frontend() {
    log_info "启动 Vue 前端..."
    kill_port 5173
    
    cd "$FRONTEND_DIR"
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm install
    fi
    
    # 启动 Vite 开发服务器
    nohup npm run dev -- --host 0.0.0.0 > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/pids/frontend.pid"
    
    sleep 3
    if check_port 5173; then
        log_info "Vue 前端已启动 (PID: $(cat $PROJECT_ROOT/pids/frontend.pid))"
        log_info "前端地址: http://localhost:5173"
    else
        log_error "Vue 前端启动失败，请查看日志: $PROJECT_ROOT/logs/frontend.log"
    fi
}

# 停止前端
stop_frontend() {
    log_info "停止 Vue 前端..."
    if [ -f "$PROJECT_ROOT/pids/frontend.pid" ]; then
        kill $(cat "$PROJECT_ROOT/pids/frontend.pid") 2>/dev/null || true
        rm "$PROJECT_ROOT/pids/frontend.pid"
    fi
    kill_port 5173
}

# 启动 Celery Worker
start_celery() {
    log_info "启动 Celery Worker..."
    
    # 先停止已有的 Celery 进程
    pkill -f "celery -A config worker" 2>/dev/null || true
    sleep 1
    
    cd "$BACKEND_DIR"
    activate_conda
    
    nohup celery -A config worker -l INFO > "$PROJECT_ROOT/logs/celery.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/pids/celery.pid"
    
    sleep 2
    if ps -p $(cat "$PROJECT_ROOT/pids/celery.pid") > /dev/null 2>&1; then
        log_info "Celery Worker 已启动 (PID: $(cat $PROJECT_ROOT/pids/celery.pid))"
    else
        log_warn "Celery Worker 可能启动失败，请查看日志: $PROJECT_ROOT/logs/celery.log"
        log_warn "如果 Redis 未运行，Celery 将无法连接"
    fi
}

# 停止 Celery
stop_celery() {
    log_info "停止 Celery Worker..."
    if [ -f "$PROJECT_ROOT/pids/celery.pid" ]; then
        kill $(cat "$PROJECT_ROOT/pids/celery.pid") 2>/dev/null || true
        rm "$PROJECT_ROOT/pids/celery.pid"
    fi
    pkill -f "celery -A config worker" 2>/dev/null || true
}

# 启动所有服务
start_all() {
    log_info "========== 启动图片管理系统 =========="
    
    # 创建日志和PID目录
    mkdir -p "$PROJECT_ROOT/logs" "$PROJECT_ROOT/pids"
    
    start_redis
    start_backend
    start_celery
    start_frontend
    
    echo ""
    log_info "========== 所有服务已启动 =========="
    echo -e "${BLUE}前端地址:${NC} http://localhost:5173"
    echo -e "${BLUE}后端API:${NC}  http://localhost:8000/api/"
    echo -e "${BLUE}后台管理:${NC} http://localhost:8000/admin/"
    echo ""
    echo -e "${YELLOW}查看日志:${NC}"
    echo "  后端: tail -f $PROJECT_ROOT/logs/backend.log"
    echo "  前端: tail -f $PROJECT_ROOT/logs/frontend.log"
    echo "  Celery: tail -f $PROJECT_ROOT/logs/celery.log"
    echo ""
    echo -e "${YELLOW}停止服务:${NC} ./start.sh stop"
}

# 停止所有服务
stop_all() {
    log_info "========== 停止所有服务 =========="
    stop_celery
    stop_frontend
    stop_backend
    # stop_redis  # Redis 通常保持运行
    log_info "所有服务已停止"
}

# 显示状态
show_status() {
    echo -e "${BLUE}========== 服务状态 ==========${NC}"
    
    # Redis
    if systemctl is-active --quiet redis 2>/dev/null || pgrep redis-server > /dev/null; then
        echo -e "Redis:   ${GREEN}运行中${NC}"
    else
        echo -e "Redis:   ${RED}未运行${NC}"
    fi
    
    # Backend
    if check_port 8000; then
        echo -e "Backend: ${GREEN}运行中${NC} (端口 8000)"
    else
        echo -e "Backend: ${RED}未运行${NC}"
    fi
    
    # Frontend
    if check_port 5173; then
        echo -e "Frontend: ${GREEN}运行中${NC} (端口 5173)"
    else
        echo -e "Frontend: ${RED}未运行${NC}"
    fi
    
    # Celery
    if pgrep -f "celery -A config worker" > /dev/null; then
        echo -e "Celery:  ${GREEN}运行中${NC}"
    else
        echo -e "Celery:  ${RED}未运行${NC}"
    fi
}

# 显示帮助
show_help() {
    echo "图片管理系统启动脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  all       启动所有服务 (默认)"
    echo "  backend   仅启动后端"
    echo "  frontend  仅启动前端"
    echo "  celery    仅启动 Celery Worker"
    echo "  redis     仅启动 Redis"
    echo "  stop      停止所有服务"
    echo "  status    查看服务状态"
    echo "  restart   重启所有服务"
    echo "  help      显示此帮助"
}

# 主入口
case "${1:-all}" in
    all)
        start_all
        ;;
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    celery)
        start_celery
        ;;
    redis)
        start_redis
        ;;
    stop)
        stop_all
        ;;
    status)
        show_status
        ;;
    restart)
        stop_all
        sleep 2
        start_all
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "未知命令: $1"
        show_help
        exit 1
        ;;
esac
