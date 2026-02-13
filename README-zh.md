# Heya PDF 转换器

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

中文 ｜ [English](README.md) 

一个功能强大的文档转换工具，支持将 HTML、Markdown、微信公众号文章转换为 PDF，以及 PDF 转 Word 文档。

![Heya PDF 转换器界面](docs/heya.gif)

## 功能特性

- **HTML 转 PDF**：将网页或本地 HTML 文件转换为 PDF
- **Markdown 转 PDF**：将 Markdown 文件转换为 PDF，支持批量转换
- **微信公众号文章转 PDF**：将微信公众号文章转换为 PDF，支持从文章列表批量转换
- **PDF 转 Word**：将 PDF 文档转换为可编辑的 Word (.docx) 文件
- **PDF 压缩**：可选的压缩功能以减小文件大小，支持可配置的质量级别
- **PDF 合并**：将多个 PDF 文件合并为一个
- **Web 界面**：用户友好的 Web UI，支持多语言（中文、英文、韩文）
- **CLI 工具**：命令行界面，支持自动化和脚本

## 安装

### 基础安装

```bash
pip install heya
```

### 安装 Web UI 支持

```bash
pip install heya[ui]
```

### 安装 Playwright 浏览器（HTML/微信转换必需）

```bash
playwright install chromium
```

### 可选：PDF 转 Word 功能

```bash
pip install pdf2docx
```

## Docker

### 使用 Docker

您也可以使用 Docker 运行 Heya：

```bash
# 构建 Docker 镜像
docker build -t heya-web .

# 运行容器
docker run -p 7860:7860 heya-web
```

Web 界面将在 `http://localhost:7860` 可用。

### Docker Compose

为了更方便的管理，您可以使用 Docker Compose：

```bash
docker-compose up -d
```

创建一个 `docker-compose.yml` 文件：

```yaml
version: '3.8'
services:
  heya:
    build: .
    ports:
      - "7860:7860"
    environment:
      - PYTHONUNBUFFERED=1
```

## 使用方法

### 命令行界面

#### HTML 转 PDF

```bash
heya html2pdf -i https://example.com -o output.pdf
heya html2pdf -i file:///path/to/page.html -o output.pdf
```

选项：
- `-i, --source`：源 URL 或 HTML 文件路径
- `-o, --target`：输出 PDF 文件路径
- `-t, --timeout`：超时时间（秒）（默认：3.0）
- `-c, --compress`：启用 PDF 压缩
- `-q, --quality`：压缩质量：0=高质量，1=中等，2=低质量

#### Markdown 转 PDF

```bash
heya md2pdf -i README.md -o output.pdf
heya md2pdf -i doc.md -o output.pdf -c -q 1
```

#### 微信公众号文章转 PDF

```bash
heya wechat2pdf -i https://mp.weixin.qq.com/s/xxx -o output_dir/
```

支持：
- 单篇文章链接：`https://mp.weixin.qq.com/s/xxx`
- 文章列表链接：`https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=xxx`

#### PDF 转 Word

```bash
heya pdf2word -i document.pdf -o output.docx
```

#### Web 界面

```bash
heya web
```

默认情况下，Web 服务器启动在 `http://127.0.0.1:7860`。

### Web 界面

Web 界面提供易于使用的 UI，具有以下功能：

- **多标签界面**：每种转换类型都有独立的标签页
- **拖放上传**：通过拖放上传文件
- **批量处理**：一次转换多个文件
- **PDF 合并**：将多个 PDF 合并为一个文件
- **质量设置**：配置压缩质量和超时时间
- **多语言支持**：中文、英文和韩文
- **错误处理**：清晰的错误消息和问题报告

## 项目结构

```
heya/
├── application/          # 核心转换逻辑
│   ├── converters.py     # 转换器实现
│   └── wechat_converter.py  # 微信转换器
├── cli/                  # 命令行界面
│   ├── commands/         # CLI 命令
│   ├── options.py        # 命令选项
│   └── utils.py         # 工具函数
├── domain/               # 领域模型和接口
│   ├── models/           # 数据模型
│   ├── services/         # 领域服务
│   ├── exceptions.py     # 异常定义
│   └── ports.py         # 端口接口
├── infrastructure/       # 基础设施实现
│   ├── browser/          # 浏览器相关
│   ├── markdown/         # Markdown 处理
│   ├── pdf/              # PDF 处理
│   ├── template/         # 模板
│   └── wechat/           # 微信解析
├── shared/               # 共享工具
│   ├── config/           # 配置管理
│   ├── constants.py      # 常量定义
│   ├── cache.py          # 缓存机制
│   ├── errors.py         # 错误处理
│   ├── logging.py        # 日志
│   └── temp.py           # 临时文件管理
└── web/                  # Web 界面
    ├── components/       # UI 组件
    ├── converters/       # Web 转换器
    ├── handlers/         # 请求处理器
    ├── i18n/            # 国际化
    ├── service.py        # Web 服务层
    └── app.py            # 应用入口
```

## 开发

### 设置开发环境

```bash
git clone https://github.com/zkep/heya.git
cd heya
uv sync
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

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 支持

如果您遇到任何问题或有疑问，请在 GitHub 上[提出问题](https://github.com/zkep/heya/issues)。

## 致谢

- 使用 [Playwright](https://playwright.dev/) 构建可靠的浏览器自动化
- Web UI 由 [Gradio](https://www.gradio.app/) 提供支持
