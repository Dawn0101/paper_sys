# 论文管理系统（Paper Management System）

> 数据库综合实验 · 课程大作业  
> 基于 Flask + 原生 HTML/CSS/JS 的前后端分离系统

[![Python](https://img.shields.io/badge/Python-3.12-blue)]()
[![Flask](https://img.shields.io/badge/Flask-3.x-green)]()
[![Database](https://img.shields.io/badge/Database-SQLite-lightgrey)]()

本系统实现了多角色（学生、学院管理员、校级管理员）的论文管理基础功能，采用轻量级前后端分离架构：后端基于 Flask 提供 RESTful API，前端使用原生 HTML/CSS/JavaScript 构建，无任何构建工具依赖。

---

## 📁 项目结构
```
paper_sys/
├── static/                     # 前端静态资源
│   ├── LoginView.html          # 公共登录页面
│   ├── SearchView.html         # 搜索页面（全局）
│   ├── SettingsView.html       # 个人信息设置页
│   ├── index.css               # 全局样式
│   ├── index.js                # 全局脚本
│   └── icon.svg                # 图标资源
│
│   ├── student/                # 学生端页面
│   │   ├── console.html        # 浏览记录、收藏
│   │   └── overview.html       # 论文统计、词云
│   │
│   ├── college_admin/          # 学院管理员端页面
│   │   ├── console.html        # 论文增删改查、用户管理
│   │   └── overview.html       # 学院内点击排行
│   │
│   └── university_admin/       # 校级管理员端页面
│       ├── console.html        # 全校论文管理、权限控制
│       └── overview.html       # 学院间点击排行
│
├── user/                       # 用户模块（后端）
│   ├── init.py
│   ├── models.py               # 用户数据模型
│   ├── repositories.py         # 数据访问层（DAO）
│   └── views.py                # 登录注册 API 接口
│
├── app.py                      # 应用入口与主路由
├── config.py                   # 配置文件（数据库连接等）
├── sql_script/                 # 数据库脚本
│   ├── create.sql              # 建表语句
│   ├── db_init.py              # 论文数据插入
│   ├── db_init_rest.py         # 剩余数据插入
│   ├── triggers.sql            # 触发器定义
│   └── papers.json             # 外部论文数据源（可选）
│
└── requirements.txt            # Python 依赖
```
---

## 🚀 快速启动

### 1. 克隆项目
```
git clone https://github.com/Dawn0101/paper_sys.git
cd paper_sys
```

### 2. 创建 Conda 虚拟环境（Python 3.12）
```
conda create -n paper_sys python=3.12
conda activate paper_sys
```

### 3. 安装依赖
```
pip install -r requirements.txt
```

### 4. 初始化数据库
```
-- 执行 sql_script/create.sql
-- 执行 sql_script/triggers.sql(触发器）
-- 执行 sql_script/db_init.py（paper表和keyword表）
-- 执行 sql_script/db_init_rest.py（其余表）
```

### 5. 启动服务
```
python app.py
```

> 访问 http://localhost:5000 即可进入系统

---

## 🔐 测试账号

| 角色           | 用户名     | 密码   |
|----------------|------------|--------|
| 学生           | stu_cs_01       | 123456 |
| 学院管理员     | admin_cs   | 123456 |
| 校级管理员     | admin_uni  | 123456 |

⚠️ 注意：当前为开发版本，密码以明文存储于数据库（仅用于调试）。正式场景应使用 werkzeug.security 哈希加密。

---

## 🧩 功能说明

### ✅ Console 页面（控制台）

| 角色       | 功能描述 |
|------------|---------|
| **学生**   | 查看自己的浏览记录、收藏论文（可选） |
| **学院管理员** | 管理学院论文（增删改查）、查看和重置下属用户信息 |
| **校级管理员** | 管理全校论文、所有用户信息及权限分配 |

### ✅ Setting 页面（设置）

- 个人信息增删改查
- 日历组件（展示重要日期）
- 右侧功能说明（红色文字提示）

### ✅ Overview 页面（概览）

| 角色       | 功能描述 |
|------------|---------|
| **学生**   | 论文年份分布、分类统计、词云图 |
| **学院管理员** | 上述内容 + 本学院学生论文点击量排行榜 |
| **校级管理员** | 上述内容 + 各学院论文点击量排行榜 |

---

## 🛠️ 技术说明

### 前端
- 纯 HTML + CSS + JavaScript（无框架）
- 使用 vue.global.js 实现响应式交互（非单文件组件）
- 页面按角色分目录组织，便于维护

### 后端
- Flask 作为 Web 框架
- SQLAlchemy 作为 ORM
- 分层架构：models → repositories → views
- 支持 SQLite 与 MySQL（修改 config.py 即可切换）

### 数据库
- 默认 SQLite，支持扩展至 MySQL
- 使用触发器实现关键词频次自动更新
- 外部导入 papers.json 作为论文数据源

---

## 📌 当前状态

- ✅ 多角色登录认证

---

## 📄 License
本项目为课程教学用途，禁止用于商业场景。
