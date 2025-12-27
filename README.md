# 健身打卡系统 - 项目文档

## 项目概述

这是一个基于Vue3 + Python + SQLite的现代化健身打卡系统，集成了AI大模型技术（阿里云通义千问），为用户提供个性化的健身方案和全方位的健康管理体验。

### 核心功能
- 用户认证系统（登录/注册/个人资料管理）
- 用户头像上传与展示
- 饮食记录与营养分析（214+种食物数据库）
- 运动库与训练记录
- AI智能健身方案生成（基于阿里云通义千问）
- 数据统计与健康趋势分析
- 连续打卡奖励称号系统

---

## 技术架构

### 前端技术栈
- **框架**: Vue 3.x + TypeScript
- **UI库**: Bootstrap 5.x + Bootstrap Icons
- **构建工具**: Vite 6.x
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios

### 后端技术栈
- **语言**: Python 3.12+
- **框架**: 自定义HTTP服务器（基于http.server）
- **数据库**: SQLite 3
- **AI集成**: 阿里云通义千问 (Qwen-Plus)
- **认证**: 简单令牌机制

---

## 功能特性

### 1. 用户系统
- 用户注册与登录
- 个人资料管理（身高、体重、年龄、性别、健身目标）
- 头像上传与展示
- BMI自动计算与健康评估

### 2. 饮食管理
- 214+种食物数据库（主食、肉类、蔬菜、水果、饮品等）
- 饮食记录（早餐、午餐、晚餐、加餐）
- 营养成分追踪（卡路里、蛋白质、碳水、脂肪）
- 每日/每周饮食统计

### 3. 运动管理
- 丰富的运动库（有氧、力量、柔韧性等分类）
- 运动记录与统计
- 卡路里消耗计算
- 运动强度记录

### 4. AI健身方案
- 基于用户画像的个性化方案生成
- 支持多种健身目标（减脂塑形、增肌强体、提升耐力等）
- 详细的周训练计划
- 专业的营养建议

### 5. 数据统计
- 今日统计（摄入卡路里、运动时间、消耗卡路里）
- 本周统计（运动次数、运动天数）
- 连续打卡天数追踪
- 今日活动时间线

### 6. 奖励称号系统
根据连续打卡天数获得不同称号：

| 连续打卡 | 称号 | 描述 |
|---------|------|------|
| 0天 | 健身小白 | 每个人都是从零开始 |
| 3天 | 初露锋芒 | 坚持3天，好的开始 |
| 7天 | 周冠达人 | 坚持一周，养成习惯 |
| 14天 | 毅力新星 | 两周坚持，毅力可嘉 |
| 30天 | 月度冠军 | 一个月！了不起的成就 |
| 60天 | 钢铁意志 | 60天，意志如钢 |
| 90天 | 健身达人 | 90天，真正的达人 |
| 180天 | 传奇人物 | 半年坚持，堪称传奇 |
| 365天 | 年度王者 | 一整年！你就是王者 |

---

## 快速开始

### 环境要求
- Node.js 18.x 或更高版本
- Python 3.12 或更高版本
- 现代浏览器（Chrome/Firefox/Safari/Edge）

### 安装步骤

#### 1. 克隆项目
```bash
cd fitness-tracker
```

#### 2. 后端设置
```bash
cd backend

# 初始化数据库
python standalone_init_db.py

# 启动后端服务器
python enhanced_server.py
```

#### 3. 前端设置
```bash
cd frontend

# 安装Node.js依赖
npm install

# 启动开发服务器
npm run dev
```

### 访问地址
- **前端开发服务器**: http://localhost:3000
- **后端API服务器**: http://localhost:5000
- **默认管理员账号**: admin / admin123

---

## 项目结构

```
fitness-tracker/
├── backend/                    # 后端代码
│   ├── uploads/                # 上传文件目录
│   │   └── avatars/            # 用户头像
│   ├── enhanced_server.py      # 主服务器文件
│   ├── standalone_init_db.py   # 数据库初始化脚本
│   ├── fitness.db              # SQLite数据库
│   └── requirements.txt        # Python依赖
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/         # Vue组件
│   │   │   ├── AppNavbar.vue   # 导航栏
│   │   │   ├── AppFooter.vue   # 页脚
│   │   │   └── ...
│   │   ├── views/              # 页面视图
│   │   │   ├── HomeView.vue    # 首页
│   │   │   ├── ProfileView.vue # 个人中心
│   │   │   ├── DietRecordView.vue    # 饮食记录
│   │   │   ├── ExerciseLibraryView.vue # 运动库
│   │   │   ├── AIPlanView.vue  # AI健身方案
│   │   │   └── ...
│   │   ├── stores/             # Pinia状态管理
│   │   │   └── auth.ts         # 用户认证状态
│   │   ├── utils/              # 工具函数
│   │   │   └── api.ts          # API请求封装
│   │   ├── types/              # TypeScript类型定义
│   │   └── router/             # 路由配置
│   ├── public/                 # 静态资源
│   ├── package.json            # Node.js依赖
│   └── vite.config.ts          # Vite配置
└── README.md                   # 项目文档
```

---

## API接口文档

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/profile` - 更新用户资料
- `POST /api/auth/upload-avatar` - 上传用户头像

### 饮食记录接口
- `GET /api/foods` - 获取食物列表
- `GET /api/diet-records` - 获取饮食记录
- `POST /api/diet-records` - 创建饮食记录

### 运动库接口
- `GET /api/exercises` - 获取运动列表
- `GET /api/exercise-logs` - 获取运动记录
- `POST /api/exercise-logs` - 创建运动记录

### AI健身方案接口
- `GET /api/ai-plans` - 获取AI方案列表
- `POST /api/ai-plans/generate` - 生成AI健身方案
- `POST /api/ai-plans/delete/{id}` - 删除AI方案

### 统计数据接口
- `GET /api/stats/today` - 获取今日统计
- `GET /api/stats/week` - 获取本周统计
- `GET /api/stats/recent-activities` - 获取最近活动
- `GET /api/stats/streak-days` - 获取连续打卡天数
- `GET /api/stats/ai-plans-count` - 获取AI方案数量

### 静态文件接口
- `GET /uploads/avatars/{filename}` - 获取用户头像

---

## AI集成说明

### 阿里云通义千问配置
系统集成了阿里云通义千问大模型用于生成个性化健身方案：

```python
# 在 enhanced_server.py 中配置
DASHSCOPE_API_KEY = 'your-api-key-here'
AI_MODEL = 'qwen-plus'  # 可选: qwen-turbo, qwen-plus, qwen-max
```

### AI功能特性
- 基于用户个人信息（年龄、性别、BMI等）生成定制化健身方案
- 结合用户历史运动和饮食数据进行智能调整
- 支持5种健身目标：减脂塑形、增肌强体、提升耐力、增强柔韧性、综合健康
- 支持3种经验水平：初学者、中级、高级
- 提供详细的周训练计划和专业营养建议

---

## 数据库设计

### 核心数据表
- **user** - 用户信息（包含头像字段）
- **food** - 食物数据（214+种食物）
- **diet_record** - 饮食记录
- **exercise** - 运动数据
- **exercise_log** - 运动记录
- **ai_plan** - AI健身方案

### 数据库初始化
```bash
cd backend
python standalone_init_db.py
```

---

## 界面预览

### 首页
- 欢迎横幅（显示用户名、加入天数、当前称号）
- 快速统计卡片（今日摄入、运动时间、消耗卡路里等）
- 功能模块快捷入口
- 今日活动时间线

### 个人中心
- 用户头像上传
- 基本信息管理
- BMI计算与显示
- 称号进度展示
- 快速操作入口

### 饮食记录
- 食物搜索与选择
- 营养成分展示
- 饮食记录列表

### 运动库
- 运动分类浏览
- 运动详情查看
- 快速记录运动

### AI健身方案
- 个性化参数设置
- AI方案生成
- 历史方案查看

---

## 安全特性

- 令牌认证机制
- 密码SHA256加密存储
- CORS跨域保护
- 输入数据验证和过滤
- 文件上传类型和大小限制（头像限制2MB）
- 路径遍历攻击防护

---

## 响应式设计

系统采用Bootstrap 5框架，支持：
- 桌面端（1200px+）
- 平板端（768px-1199px）
- 移动端（<768px）

---

## 部署指南

### 开发环境
```bash
# 后端
cd backend && python enhanced_server.py

# 前端
cd frontend && npm run dev
```

### 生产环境
```bash
# 构建前端
cd frontend && npm run build

# 部署dist文件夹到Web服务器
# 后端服务器可直接运行enhanced_server.py
```

---

## 故障排除

### 常见问题

#### 1. 无法连接后端API
- 检查后端服务器是否启动（端口5000）
- 确认防火墙设置
- 验证API端点URL配置

#### 2. 前端页面空白
- 检查Node.js依赖是否安装完整
- 清除浏览器缓存
- 查看浏览器控制台错误信息

#### 3. 数据库连接失败
- 确认SQLite数据库文件存在
- 检查文件权限
- 重新运行数据库初始化脚本

#### 4. AI功能不可用
- 验证阿里云API密钥配置
- 检查网络连接
- 确认API配额充足

#### 5. 头像上传失败
- 检查图片大小是否超过2MB
- 确认图片格式（支持jpg/png/gif/webp）
- 检查uploads目录权限

---

## 技术支持

如有技术问题，请检查：
1. 控制台错误日志
2. 网络连接状态
3. 服务器运行状态
4. 数据库完整性

---

## 许可证

本项目仅供学习和研究使用。

---

**祝您使用愉快！**

*最后更新时间: 2025-12-27*
