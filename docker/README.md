# Docker 部署说明

## 快速部署

### 1. 开发环境部署

```bash
# 启动基础服务（不包含 Nginx）
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

访问地址：
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000

### 2. 生产环境部署

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，修改 SECRET_KEY 等配置
vim .env

# 启动所有服务（包含 Nginx）
docker-compose --profile production up -d --build

# 查看服务状态
docker-compose ps
```

访问地址：
- 网站: http://localhost (Nginx 代理)

## 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| redis | 6379 | 消息队列 |
| backend | 8000 | Django 后端 |
| celery-worker | - | 异步任务处理 |
| celery-beat | - | 定时任务调度 |
| frontend | 3000 | Vue 前端 |
| nginx | 80 | 反向代理（生产环境） |

## 常用命令

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重启单个服务
docker-compose restart backend

# 查看特定服务日志
docker-compose logs -f backend

# 进入容器
docker exec -it photo-manager-backend bash

# 执行 Django 命令
docker exec photo-manager-backend python manage.py createsuperuser
```

## 数据持久化

数据存储在 Docker volumes 中：

- `redis_data`: Redis 数据
- `media_data`: 上传的图片文件
- `static_data`: Django 静态文件

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| SECRET_KEY | Django 密钥 | 必须修改 |
| DEBUG | 调试模式 | False |
| ALLOWED_HOSTS | 允许的主机 | localhost |
| CELERY_BROKER_URL | Celery 消息代理 | redis://redis:6379/0 |

## 故障排查

### 1. 容器启动失败

```bash
# 查看日志
docker-compose logs backend

# 检查容器状态
docker-compose ps
```

### 2. 数据库迁移失败

```bash
# 手动执行迁移
docker exec photo-manager-backend python manage.py migrate
```

### 3. 静态文件未加载

```bash
# 重新收集静态文件
docker exec photo-manager-backend python manage.py collectstatic --noinput
```

### 4. Celery 任务不执行

```bash
# 检查 Redis 连接
docker exec photo-manager-redis redis-cli ping

# 查看 Worker 日志
docker-compose logs celery-worker
```
