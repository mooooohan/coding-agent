# arXiv CS Daily

一个基于 Flask 框架开发的 arXiv 计算机科学论文每日更新网站，提供分类浏览、论文详情、引用格式等功能。

## 项目功能

### 📚 论文分类浏览
- 支持 11 个 arXiv 计算机科学主要领域分类
- 分类列表：cs.AI (人工智能)、cs.CV (计算机视觉)、cs.SE (软件工程)、cs.TH (计算理论)、cs.SY (系统与控制)、cs.LG (机器学习)、cs.CL (计算语言学)、cs.NE (神经计算)、cs.RO (机器人学)、cs.GT (博弈论)、cs.MM (多媒体)
- 顶部导航栏支持快速分类切换

### 🔄 每日自动更新
- 系统会自动检查论文数据的新鲜度
- 当数据超过 24 小时未更新时，会自动从 arXiv API 获取最新数据
- 也可以手动运行 `data_fetcher.py` 进行数据更新

### 📄 论文详情页面
- 显示论文完整信息：标题、作者、提交/更新日期、分类、摘要
- 提供 arXiv 官方链接和 PDF 直接下载链接
- 支持 BibTeX 和标准学术引用格式的自动生成
- 一键复制引用功能，方便在论文中使用
- 论文导航功能，快速切换上一篇/下一篇

### 🎨 响应式设计
- 适配各种屏幕尺寸（桌面端、平板、手机）
- 现代化的 UI 风格，良好的用户体验

## 项目结构

```
workspace/
├── app/                 # Flask 应用目录
│   ├── static/          # 静态文件目录
│   │   └── css/        # CSS 样式文件
│   ├── templates/       # HTML 模板文件
│   ├── __init__.py      # 应用初始化文件
│   ├── config.py        # 配置文件
│   └── routes.py        # 路由文件
├── data_fetcher.py     # 从 arXiv API 获取数据的脚本
├── papers.json          # 存储论文数据的 JSON 文件
├── requirements.txt     # 项目依赖项
├── run.py               # 应用启动脚本
└── README.md           # 项目说明文档
```

## 快速上手

### 📋 环境要求
- Python 3.7+
- pip 包管理工具

### 🛠️ 安装步骤

1. **克隆或下载项目**
   ```bash
   # 假设项目已下载到本地
   cd workspace
   ```

2. **安装依赖项**
   ```bash
   pip install -r requirements.txt
   ```

3. **获取初始论文数据**
   ```bash
   python data_fetcher.py
   ```

4. **启动应用**
   ```bash
   python run.py
   ```

### 🚀 访问应用

应用启动后，在浏览器中访问以下地址：
- 本地访问：`http://127.0.0.1:5000`
- 局域网访问：`http://192.168.0.xxx:5000`（具体 IP 地址请查看终端输出）

### ⚠️ 注意事项
- 首次启动应用时，需要等待数据获取完成（约 1-2 分钟）
- 应用启动后会自动更新论文数据，无需手动操作
- 如果数据更新失败，可以尝试手动运行 `data_fetcher.py`

## 项目结构

```
workspace/
├── app/                 # Flask 应用核心目录
│   ├── static/          # 静态资源文件
│   │   └── css/        # CSS 样式文件
│   ├── templates/       # HTML 模板文件
│   ├── __init__.py      # 应用初始化
│   ├── config.py        # 配置文件
│   └── routes.py        # 路由和业务逻辑
├── data_fetcher.py     # arXiv API 数据获取脚本
├── papers.json          # 论文数据存储文件
├── requirements.txt     # Python 依赖包列表
├── run.py               # 应用启动脚本
└── README.md           # 项目说明文档
```

## 📝 开发说明

### 项目配置
- 应用配置：`app/config.py`
- arXiv API 配置：`data_fetcher.py`（包括分类列表、最大结果数等）

### 数据更新机制
- 自动更新：应用启动时检查数据新鲜度，超过 24 小时自动更新
- 手动更新：运行 `python data_fetcher.py`

### 模板结构
- 首页：`index.html`
- 论文详情页：`detail.html`
- 错误页面：`404.html`、`500.html`

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature`
5. 提交 Pull Request

## 📄 许可证

本项目仅供学习和研究使用。

## 📧 联系方式

如有问题或建议，请联系项目开发团队。

该脚本会从 arXiv API 获取所有支持分类的最新论文，并将数据保存到 papers.json 文件中。

### 3. 启动应用

运行以下命令启动 Flask 应用：

```bash
python run.py
```

应用启动后，会在终端显示应用的访问地址，默认为：http://127.0.0.1:5000/

在浏览器中打开该地址即可访问 arXiv CS Daily 网站。

## 使用说明

### 1. 浏览论文

- 在网站首页，您可以看到所有分类的最新论文
- 点击导航栏中的分类标签，可以筛选显示特定分类的论文
- 点击论文标题，可以进入论文详情页面

### 2. 获取论文信息

在论文详情页面，您可以：
- 查看论文的完整标题、作者、提交日期、更新日期、分类和摘要
- 点击 "Open on arXiv" 按钮，在新标签页中打开 arXiv 官方页面
- 点击 "Download PDF" 按钮，直接下载论文的 PDF 文件
- 复制 BibTeX 或标准学术引用格式

### 3. 更新论文数据

如果您希望获取最新的论文数据，可以再次运行 data_fetcher.py 脚本：

```bash
python data_fetcher.py
```

脚本会自动更新 papers.json 文件中的数据。

## 技术栈

- **后端框架**: Flask
- **前端技术**: HTML5, CSS3, Bootstrap 5
- **数据获取**: arXiv API
- **数据存储**: JSON
- **模板引擎**: Jinja2

## 注意事项

- 该项目使用 arXiv API 获取数据，需要确保网络连接正常
- 由于 arXiv API 的限制，每次请求最多只能获取 1000 条论文数据
- 为了避免频繁请求 API，建议不要过于频繁地运行 data_fetcher.py 脚本
- 该项目仅供学习和研究使用，不得用于商业用途

## 许可证

MIT License
