# 论文管理系统（Paper Management System）

> 数据库综合实验 · 课程大作业  
> 基于 Flask + 原生 HTML/CSS/JS 的前后端分离系统

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

本系统实现了多角色（学生、学院管理员、校级管理员）的论文管理基础功能，采用轻量级前后端分离架构：后端基于 Flask 提供 RESTful API，前端使用原生 HTML/CSS/JavaScript 构建，无任何构建工具依赖。

---

## 📁 项目结构
main/
├── sql_script/                 # 数据库脚本
│   ├── create_tables.sql       # 建表语句
│   └── update_data.sql         # 初始数据插入
│
├── paper_sys/                  # 核心应用代码
│   ├── static/                 # 前端静态资源（原生 HTML/CSS/JS）
│   │   ├── Loginview/          # 公共登录界面
│   │   ├── student/            # 学生端页面
│   │   ├── college_admin/      # 学院管理员端页面
│   │   └── university_admin/   # 校级管理员端页面
│   │
│   ├── users/                  # 用户模块（后端）
│   │   ├── init.py
│   │   ├── models.py           # 数据模型（User 等）
│   │   ├── repositories.py     # 数据访问层（DAO）
│   │   └── views.py            # API 接口（路由与逻辑）
│   │
│   ├── app.py                  # 应用入口与主路由
│   └── config.py               # 配置文件（数据库连接等）
│
└── README.md

---

## 🚀 快速启动

### 1. 克隆项目
```bash
git clone https://github.com/Dawn0101/paper_sys.git
cd paper_sys

### 2. 创建 Conda 虚拟环境（Python 3.12）

conda create -n paper_sys python=3.12
conda activate paper_sys

### 3. 安装 Python 依赖

pip install -r requirements.txt

### 4. 初始化数据库

-- 执行 sql_script/create_tables.sql
-- 执行 sql_script/update_data.sql（含测试用户）

### 5. 启动服务

python paper_sys/app.py


🔐 测试账号
角色	用户名	密码
学生	lisi	123456
⚠️ 注意：当前为开发版本，密码以明文存储于数据库（仅用于调试）。正式场景应使用 werkzeug.security 哈希加密。

## 🛠️ 技术说明
### 前端：纯 HTML + CSS + JavaScript（无 Vue CLI / Vite / Webpack）
使用 vue.global.js 实现响应式交互（非单文件组件）
页面按角色分目录组织，便于维护
### 后端：
Flask 作为 Web 框架
SQLAlchemy 作为 ORM
分层架构：models → repositories → views
### 数据库：SQLite（默认），支持切换至 MySQL（修改 config.py）

##📌 当前功能
 多角色登录（学生 / 学院管理员 / 校级管理员）
 用户认证 API（/api/login）
 学院信息查询
 论文提交与审核（待实现）
📄 License
本项目为课程教学用途，禁止用于商业场景。

© 2025 Your Name. All rights reserved.
