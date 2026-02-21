# Heya Desktop App

基于 PySide6 的桌面端 PDF 转换工具，支持微信公众号文章、HTML、Markdown 转 PDF，以及 PDF 转 Word。

## 功能特性

- **HTML 转 PDF**: 输入网址，将网页转换为 PDF 文件
- **Markdown 转 PDF**: 上传 Markdown 文件，转换为 PDF 文件（支持批量转换和合并）
- **微信文章转 PDF**: 输入微信公众号文章链接，转换为 PDF 文件（支持批量转换和合并）
- **PDF 转 Word**: 上传 PDF 文件，转换为 Word 文档
- **多语言支持**: 支持中文、英文、韩文
- **可配置设置**: 支持超时时间和压缩级别设置

## 安装

```bash
pip install -e ".[app]"
```

## 运行

```bash
python -m heya.app.main
```

或者直接运行：

```bash
python heya/app/main.py
```

## 项目结构

```
heya/app/
├── __init__.py
├── main.py                 # 主入口文件
├── app.py                  # 应用创建函数
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── component.py        # 组件基类
│   ├── registry.py         # 组件注册器
│   └── main_window.py      # 主窗口
├── components/             # UI 组件
│   ├── __init__.py
│   ├── converter.py        # HTML 转换器组件
│   ├── markdown_converter.py # Markdown 转换器组件
│   ├── wechat.py           # 微信转换器组件
│   ├── pdf_to_word.py      # PDF 转 Word 组件
│   ├── tips.py             # 提示组件
│   └── settings_panel.py   # 设置面板组件
├── handlers/               # 事件处理器
│   ├── __init__.py
│   └── error_handler.py    # 错误处理器
├── services/               # 业务服务
│   ├── __init__.py
│   └── service.py          # 转换服务
├── i18n/                   # 国际化
│   ├── __init__.py
│   ├── core.py             # 国际化管理器
│   └── locales/            # 语言文件
│       ├── zh.json
│       ├── en.json
│       └── ko.json
└── utils/                  # 工具函数
    └── __init__.py
```

## 使用说明

### HTML 转 PDF

1. 选择 "HTML 转 PDF" 标签页
2. 输入网址（支持 http:// 或 https:// 开头的网址）
3. 可选：点击设置调整超时时间和压缩级别
4. 点击 "转PDF" 按钮
5. 等待转换完成，查看输出文件

### Markdown 转 PDF

1. 选择 "Markdown 转 PDF" 标签页
2. 点击 "Upload Markdown Files" 上传 Markdown 文件（支持多选）
3. 可选：点击设置调整超时时间和压缩级别
4. 点击 "转PDF" 按钮
5. 等待转换完成，查看输出文件
6. 如果有多个文件，可以点击 "合并 PDF" 按钮合并所有文件

### 微信文章转 PDF

1. 选择 "微信文章转 PDF" 标签页
2. 输入微信公众号文章链接或文章列表链接
3. 可选：点击设置调整超时时间和压缩级别
4. 点击 "转PDF" 按钮
5. 等待转换完成，查看输出文件
6. 如果有多个文章，可以点击 "合并 PDF" 按钮合并所有文件

### PDF 转 Word

1. 选择 "PDF 转 Word" 标签页
2. 点击 "PDF 文件" 按钮上传 PDF 文件
3. 点击 "转Word" 按钮
4. 等待转换完成，查看输出文件

## 设置说明

- **超时时间**: 设置转换操作的超时时间（秒），默认 60 秒
- **压缩级别**: 设置 PDF 压缩级别
  - 高质量 (0): 不压缩，文件较大
  - 中等 (1): 适度压缩，平衡质量和大小
  - 低质量 (2): 高度压缩，文件较小但可能影响质量

## 依赖项

- PySide6 >= 6.0.0
- playwright >= 1.48.0
- markdown >= 3.5.0
- pypdf >= 4.0.0
- reportlab >= 4.0.0
- pdf2docx (用于 PDF 转 Word)

## 开发

### 代码风格

项目使用 ruff 进行代码格式化和检查：

```bash
ruff check heya/app/
ruff format heya/app/
```

### 类型检查

项目使用 mypy 进行类型检查：

```bash
mypy heya/app/
```

## 许可证

MIT License
