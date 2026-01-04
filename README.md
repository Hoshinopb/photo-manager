# Photo Manager 图片管理系统

基于 Django + Vue3 的图片管理网站，支持图片上传、EXIF 解析、标签管理和异步处理。

## 功能特性

- ✅ 用户注册/登录/登出
- ✅ 图片上传（支持 jpg/jpeg/png/gif/webp/bmp）
- ✅ 自动 EXIF 解析与标签生成
- ✅ 缩略图异步生成
- ✅ 标签系统（自动标签、用户标签、AI 标签预留）
- ✅ 图片公开/私有设置
- ✅ 多维度筛选（关键词、标签、时间范围）
- ✅ 批量操作（删除、设置公开/私有）

## 技术栈

### 后端
- Django 3.2 + Django REST Framework
- Celery + Redis（异步任务处理）
- Pillow（图片处理）
- ExifRead（EXIF 解析）
- SQLite（数据库）

### 前端
- Vue 3 + Vite
- Element Plus
- Pinia（状态管理）
- Axios（HTTP 请求）

## 项目结构

```
photo-manager/
├── backend/                 # Django 后端
│   ├── apps/
│   │   ├── users/          # 用户管理
│   │   ├── images/         # 图片管理
│   │   └── tags/           # 标签管理
│   ├── config/             # Django 配置
│   │   ├── settings.py
│   │   ├── celery.py       # Celery 配置
│   │   └── urls.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Vue 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── utils/          # API 工具
│   │   └── stores/         # Pinia stores
│   ├── Dockerfile
│   └── nginx.conf
└── docker-compose.yml      # Docker 编排
```

## 本地开发

### 后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

### Celery Worker（异步任务）

```bash
# 确保 Redis 已启动
# 在新终端启动 Celery Worker
cd backend
celery -A config worker -l INFO
```

### 前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## Docker 部署

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## API 接口

详见 [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

### 主要端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/auth/users/` | POST | 用户注册 |
| `/api/auth/token/login/` | POST | 用户登录 |
| `/api/images/` | GET | 获取图片列表 |
| `/api/images/` | POST | 上传图片 |
| `/api/images/{id}/` | PATCH | 更新图片信息 |
| `/api/images/{id}/` | DELETE | 删除图片 |
| `/api/tags/` | GET | 获取标签列表 |
| `/api/tags/hot/` | GET | 获取热门标签 |

## 异步处理架构

```
上传请求 → Django → 保存原图 → 返回响应（即时）
                      ↓
              触发 Celery 任务
                      ↓
            Redis 消息队列
                      ↓
            Celery Worker 处理
            ├── 生成缩略图
            ├── 解析 EXIF
            ├── 自动生成标签
            └── (预留) AI 标注
```

## 配置说明

### 缩略图配置（settings.py）

```python
THUMBNAIL_SIZE = (300, 300)  # 缩略图尺寸
THUMBNAIL_QUALITY = 85       # JPEG 质量
```

### Celery 配置

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

## 许可证

MIT License
