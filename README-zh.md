# Heya PDF 转换器

[![Python 版本](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![许可证](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[中文](README-zh.md) | [English](README.md)

一个功能强大的文档转换工具，支持将 HTML、Markdown、微信公众号文章转换为 PDF，以及 PDF 转 Word 文档。

支持三种使用方式：命令行界面、Web 界面和桌面应用。


## 功能特性

- **多格式转换**：支持 HTML、Markdown、微信公众号文章转换为 PDF
- **PDF 转 Word**：将 PDF 文档转换为可编辑的 Word (.docx) 文件
- **批量处理**：支持一次性转换多个文件
- **PDF 合并**：将多个 PDF 文件合并为一个
- **质量控制**：可选的压缩功能，支持配置压缩质量级别
- **三种界面**：
  - CLI 工具：适合自动化和脚本
  - Web 界面：用户友好的 Gradio UI
  - 桌面应用：原生 PySide6 应用
- **多语言支持**：中文、英文、韩文

## 安装

### 基础安装

```bash
pip install heya
```

### 安装 Web 界面

```bash
pip install heya[web]
```

### 安装桌面应用

```bash
pip install heya[app]
```

### 安装所有可选依赖

```bash
pip install heya[web,app]
```

### 安装 Playwright 浏览器（HTML/微信转换必需）

```bash
playwright install chromium
```

## 快速开始

### 命令行界面

```bash
# HTML 转 PDF
heya html2pdf -i https://example.com -o output.pdf

# Markdown 转 PDF
heya md2pdf -i README.md -o output.pdf

# 微信公众号文章转 PDF
heya wechat2pdf -i "https://mp.weixin.qq.com/s/xxx" -o output_dir/

# PDF 转 Word
heya pdf2word -i document.pdf -o output.docx
```

### Web 界面

```bash
heya web
```

Web 服务器默认启动在 `http://127.0.0.1:7860`。

### 桌面应用

```bash
heya app
```

## 使用方法

### 命令行选项

#### HTML 转 PDF

```bash
heya html2pdf -i <url 或文件路径> -o <输出路径> [选项]
```

选项：
- `-i, --input`：源 URL 或 HTML 文件路径（支持多个输入）
- `-o, --output`：输出目录路径
- `-t, --timeout`：超时时间（秒）（默认：30.0）
- `-q, --quality`：压缩质量：0=高质量，1=中等，2=低质量（默认：0）
- `-m, --merge`：将所有 PDF 合并为一个文件

示例：
```bash
# 单个文件
heya html2pdf -i https://example.com -o output.pdf

# 批量转换
heya html2pdf -i page1.html -i page2.html -i page3.html -o pdfs/

# 合并输出
heya html2pdf -i page1.html -i page2.html -o merged.pdf --merge
```

#### Markdown 转 PDF

```bash
heya md2pdf -i <文件路径> -o <输出路径> [选项]
```

选项：
- `-i, --input`：Markdown 文件路径（支持多个输入）
- `-o, --output`：输出目录路径
- `-t, --timeout`：超时时间（秒）
- `-q, --quality`：压缩质量
- `-m, --merge`：将所有 PDF 合并为一个文件

示例：
```bash
heya md2pdf -i README.md -o output.pdf
heya md2pdf -i *.md -o pdfs/ --merge
```

#### 微信公众号文章转 PDF

```bash
heya wechat2pdf -i <微信链接> -o <输出目录> [选项]
```

选项：
- `-i, --input`：微信公众号文章链接
- `-o, --output`：输出目录路径
- `-t, --timeout`：超时时间（秒）
- `-q, --quality`：压缩质量
- `-m, --merge`：将所有 PDF 合并为一个文件

支持：
- 单篇文章链接：`https://mp.weixin.qq.com/s/xxx`
- 文章列表链接：`https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=xxx`

示例：
```bash
# 转换单篇文章
heya wechat2pdf -i "https://mp.weixin.qq.com/s/xxx" -o articles/

# 转换文章列表（批量）
heya wechat2pdf -i "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=xxx" -o articles/
```

#### PDF 转 Word

```bash
heya pdf2word -i <PDF文件> -o <输出路径>
```

选项：
- `-i, --input`：源 PDF 文件路径
- `-o, --output`：输出 Word 文件路径

示例：
```bash
heya pdf2word -i document.pdf -o output.docx
```

### Web 界面功能

- **多标签界面**：每种转换类型都有独立的标签页
- **拖放上传**：通过拖放上传文件
- **批量处理**：一次转换多个文件
- **PDF 合并**：将多个 PDF 合并为一个文件
- **质量设置**：配置压缩质量和超时时间
- **多语言支持**：中文、英文和韩文
- **错误处理**：清晰的错误消息和问题报告

### 桌面应用功能

- **原生界面**：使用 PySide6 构建的原生桌面应用
- **离线使用**：无需网络即可使用核心功能
- **多语言支持**：支持中文、英文和韩文
- **实时进度**：转换进度实时显示

## 项目结构

```
heya/
├── heya/                    # 主包
│   ├── app/                 # 桌面应用
│   │   ├── components/     # UI 组件
│   │   ├── core/           # 核心组件
│   │   ├── handlers/       # 事件处理
│   │   ├── i18n/           # 国际化
│   │   ├── services/      # 服务层
│   │   └── utils/         # 工具函数
│   ├── cmd/                # CLI 命令
│   │   └── commands/       # 命令实现
│   ├── core/               # 核心转换逻辑
│   │   ├── browser/        # 浏览器管理
│   │   ├── cache/         # 缓存
│   │   ├── config/        # 配置
│   │   ├── converters/    # 转换器
│   │   ├── exceptions/    # 异常
│   │   ├── helpers/       # 辅助函数
│   │   ├── interfaces/    # 接口
│   │   ├── logging/      # 日志
│   │   ├── markdown/     # Markdown 处理
│   │   ├── models/       # 数据模型
│   │   ├── pdf/          # PDF 操作
│   │   ├── performance/  # 性能优化
│   │   ├── stream_converters/  # 流式转换
│   │   ├── temp/         # 临时文件
│   │   ├── template/     # 模板
│   │   └── wechat/       # 微信处理
│   └── web/               # Web 应用
│       ├── components/    # UI 组件
│       ├── config/        # 配置
│       ├── core/          # 核心
│       ├── handlers/      # 事件处理
│       ├── i18n/          # 国际化
│       ├── services/      # 服务层
│       └── utils/         # 工具函数
├── pyproject.toml         # 项目配置
└── README.md              # 本文件
```

## 开发

### 环境设置

```bash
# 克隆项目
git clone https://github.com/zkep/heya.git
cd heya

# 使用 uv 同步依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate
```

### 运行测试

```bash
uv run pytest
```

### 类型检查

```bash
uv run mypy heya
```

### 代码检查

```bash
uv run ruff check heya
uv run ruff format heya
```

## 依赖项

- **click**：命令行界面框架
- **playwright**：用于 HTML/微信转换的浏览器自动化
- **markdown**：Markdown 解析
- **pypdf**：PDF 操作
- **reportlab**：PDF 生成和合并
- **gradio**：Web UI（可选）
- **PySide6**：桌面应用（可选）

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 支持

如果您遇到任何问题或有疑问，请在 GitHub 上[提出问题](https://github.com/zkep/heya/issues)。

## 致谢

- 使用 [Playwright](https://playwright.dev/) 构建可靠的浏览器自动化
- Web UI 由 [Gradio](https://www.gradio.app/) 提供支持
- 桌面应用由 [PySide6](https://doc.qt.io/qtforpython/) 提供支持
