# Photo Manager 图片管理系统

一个功能完善的在线图片管理网站，支持图片上传、EXIF 解析、标签管理、图片编辑和 AI 智能描述生成。

## 功能特性

- **用户系统**: 注册、登录、个人资料管理
- **图片上传**: 拖拽上传、多图上传、格式校验
- **EXIF 解析**: 自动提取拍摄信息（相机、时间、GPS 等）
- **标签系统**: 自动标签、用户标签、热门标签
- **图片编辑**: 裁剪、旋转、翻转、亮度/对比度调整
- **AI 描述**: 接入视觉大模型自动生成图片描述
- **响应式**: PC、平板、手机多端适配
- **权限控制**: 公开/私有图片、API Key 加密存储

## 技术栈

| 前端 | 后端 | 其他 |
|------|------|------|
| Vue 3 | Django 3.2 | Redis |
| Element Plus | Django REST Framework | Celery |
| Pinia | djoser | SQLite |
| Vite | Pillow | Docker |

## 快速开始

### 开发环境

```bash
# 克隆项目
git clone https://github.com/Hoshinopb/photo-manager.git
cd photo-manager

# 启动所有服务（后端 + 前端 + Redis + Celery）
./start.sh start

# 访问
# 前端: http://localhost:5173
# 后端: http://localhost:8000
```

### Docker 部署

```bash
# 构建并启动
docker-compose up -d --build

# 访问
# 前端: http://localhost:3000
# 后端: http://localhost:8000
```

## 项目结构

```
photo-manager/
├── backend/                # Django 后端
│   ├── apps/
│   │   ├── users/         # 用户管理
│   │   ├── images/        # 图片管理
│   │   └── tags/          # 标签管理
│   ├── config/            # 配置文件
│   └── requirements.txt
├── frontend/              # Vue 前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 公共组件
│   │   └── stores/        # 状态管理
│   └── package.json
├── docs/                  # 项目文档
│   ├── 设计文档.md        # 系统架构、数据库设计、API 设计
│   ├── 使用手册.md        # 功能操作指南
│   ├── 项目搭建.md        # 环境配置、项目启动指南
│   └── 实验报告.md        # 功能完成情况、问题解决、总结
├── docker-compose.yml
└── start.sh               # 启动脚本
```

## API 接口

### 用户认证
- `POST /api/auth/users/` - 用户注册
- `POST /api/auth/token/login/` - 用户登录
- `GET /api/auth/users/me/` - 获取当前用户

### 图片管理
- `GET /api/images/` - 图片列表
- `POST /api/images/` - 上传图片
- `GET /api/images/{id}/` - 图片详情
- `PATCH /api/images/{id}/` - 更新图片
- `DELETE /api/images/{id}/` - 删除图片
- `POST /api/images/{id}/edit/` - 编辑图片
- `POST /api/images/{id}/generate_ai_description/` - AI 生成描述

### 标签管理
- `GET /api/tags/` - 标签列表
- `GET /api/tags/hot/` - 热门标签

## 本地开发

### 后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

### Celery Worker

```bash
# 确保 Redis 已启动
cd backend
celery -A config worker -l INFO
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 配置

### 环境变量

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### AI 功能配置

1. 访问 [SiliconFlow](https://siliconflow.cn) 获取 API Key
2. 在「个人资料」→「AI 设置」中配置 Key
3. 即可使用 AI 图片描述生成功能

## 常见问题

### Q1: 上传图片失败怎么办？

- 检查文件格式是否支持（JPG/PNG/GIF/WebP/BMP）
- 检查文件大小是否超过限制（默认 10MB）
- 确保网络连接正常

### Q2: 图片上传等功能失效？

请确保 Celery Worker 已启动，稍后刷新页面。


### Q3: AI 生成描述失败？

- 确认已在个人资料中配置有效的 API Key
- 检查 API Key 是否有余额
- 图片过大可能导致超时，建议使用小于 5MB 的图片

### Q4: 忘记密码怎么办？

点击登录页面的「忘记密码」链接，输入注册邮箱，系统会发送重置密码链接。

### Q5: 如何批量删除图片？

1. 进入「我的图片」页面
2. 切换到网格视图
3. 点击图片右上角的复选框选择要删除的图片
4. 点击底部的「批量删除」按钮

