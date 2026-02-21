# Heya PDF Converter

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[中文](README-zh.md) | [English](README.md)

A powerful and versatile tool for converting documents to PDF and Word formats. Heya supports converting HTML, Markdown, WeChat articles to PDF, and PDF to Word documents.

Supports three ways to use: Command Line Interface, Web Interface, and Desktop Application.


## Features

- **Multi-format Conversion**: Convert HTML, Markdown, WeChat articles to PDF
- **PDF to Word**: Convert PDF documents to editable Word (.docx) files
- **Batch Processing**: Convert multiple files at once
- **PDF Merging**: Merge multiple PDF files into one
- **Quality Control**: Optional compression with configurable quality levels
- **Three Interfaces**:
  - CLI Tool: Perfect for automation and scripts
  - Web Interface: User-friendly Gradio UI
  - Desktop Application: Native PySide6 application
- **Multi-language Support**: Chinese, English, Korean

## Installation

### Basic Installation

```bash
pip install heya
```

### Install Web Interface

```bash
pip install heya[web]
```

### Install Desktop Application

```bash
pip install heya[app]
```

### Install All Optional Dependencies

```bash
pip install heya[web,app]
```

### Install Playwright Browsers (Required for HTML/WeChat conversion)

```bash
playwright install chromium
```

## Quick Start

### Command Line Interface

```bash
# HTML to PDF
heya html2pdf -i https://example.com -o output.pdf

# Markdown to PDF
heya md2pdf -i README.md -o output.pdf

# WeChat Articles to PDF
heya wechat2pdf -i "https://mp.weixin.qq.com/s/xxx" -o output_dir/

# PDF to Word
heya pdf2word -i document.pdf -o output.docx
```

### Web Interface

```bash
heya web
```

The web server starts on `http://127.0.0.1:7860` by default.

### Desktop Application

```bash
heya app
```

## Usage

### Command Line Options

#### HTML to PDF

```bash
heya html2pdf -i <url or file path> -o <output path> [options]
```

Options:
- `-i, --input`: Source URL or HTML file path (supports multiple inputs)
- `-o, --output`: Output directory path
- `-t, --timeout`: Timeout in seconds (default: 30.0)
- `-q, --quality`: Compression quality: 0=high, 1=medium, 2=low (default: 0)
- `-m, --merge`: Merge all PDFs into one file

Examples:
```bash
# Single file
heya html2pdf -i https://example.com -o output.pdf

# Batch conversion
heya html2pdf -i page1.html -i page2.html -i page3.html -o pdfs/

# Merge output
heya html2pdf -i page1.html -i page2.html -o merged.pdf --merge
```

#### Markdown to PDF

```bash
heya md2pdf -i <file path> -o <output path> [options]
```

Options:
- `-i, --input`: Markdown file path (supports multiple inputs)
- `-o, --output`: Output directory path
- `-t, --timeout`: Timeout in seconds
- `-q, --quality`: Compression quality
- `-m, --merge`: Merge all PDFs into one file

Examples:
```bash
heya md2pdf -i README.md -o output.pdf
heya md2pdf -i *.md -o pdfs/ --merge
```

#### WeChat Articles to PDF

```bash
heya wechat2pdf -i <wechat link> -o <output directory> [options]
```

Options:
- `-i, --input`: WeChat article URL
- `-o, --output`: Output directory path
- `-t, --timeout`: Timeout in seconds
- `-q, --quality`: Compression quality
- `-m, --merge`: Merge all PDFs into one file

Supports:
- Single article URL: `https://mp.weixin.qq.com/s/xxx`
- Article list URL: `https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=xxx`

Examples:
```bash
# Convert single article
heya wechat2pdf -i "https://mp.weixin.qq.com/s/xxx" -o articles/

# Convert article list (batch)
heya wechat2pdf -i "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=xxx" -o articles/
```

#### PDF to Word

```bash
heya pdf2word -i <pdf file> -o <output path>
```

Options:
- `-i, --input`: Source PDF file path
- `-o, --output`: Output Word file path

Example:
```bash
heya pdf2word -i document.pdf -o output.docx
```

### Web Interface Features

- **Multi-tab Interface**: Separate tabs for each conversion type
- **Drag & Drop**: Upload files by dragging and dropping
- **Batch Processing**: Convert multiple files at once
- **PDF Merging**: Merge multiple PDFs into a single file
- **Quality Settings**: Configure compression quality and timeout
- **Multi-language Support**: English, Chinese, and Korean
- **Error Handling**: Clear error messages with issue reporting

### Desktop Application Features

- **Native Interface**: Built with PySide6 for native desktop experience
- **Offline Use**: Core features work without internet
- **Multi-language Support**: Chinese, English, Korean supported
- **Real-time Progress**: Live conversion progress display

## Project Structure

```
heya/
├── heya/                    # Main package
│   ├── app/                 # Desktop application
│   │   ├── components/     # UI components
│   │   ├── core           # Core components
│   │   ├── handlers       # Event handlers
│   │   ├── i18n           # Internationalization
│   │   ├── services       # Service layer
│   │   └── utils          # Utility functions
│   ├── cmd/                # CLI commands
│   │   └── commands        # Command implementations
│   ├── core/               # Core conversion logic
│   │   ├── browser        # Browser management
│   │   ├── cache          # Caching
│   │   ├── config         # Configuration
│   │   ├── converters     # Converters
│   │   ├── exceptions     # Exceptions
│   │   ├── helpers        # Helper functions
│   │   ├── interfaces     # Interfaces
│   │   ├── logging        # Logging
│   │   ├── markdown       # Markdown processing
│   │   ├── models         # Data models
│   │   ├── pdf            # PDF operations
│   │   ├── performance    # Performance optimization
│   │   ├── stream_converters  # Stream converters
│   │   ├── temp           # Temporary files
│   │   ├── template        # Templates
│   │   └── wechat         # WeChat processing
│   └── web/               # Web application
│       ├── components      # UI components
│       ├── config         # Configuration
│       ├── core           # Core
│       ├── handlers       # Event handlers
│       ├── i18n           # Internationalization
│       ├── services       # Service layer
│       └── utils          # Utility functions
├── pyproject.toml          # Project configuration
└── README.md              # This file
```

## Development

### Setup Development Environment

```bash
# Clone the project
git clone https://github.com/zkep/heya.git
cd heya

# Sync dependencies with uv
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### Run Tests

```bash
uv run pytest
```

### Type Checking

```bash
uv run mypy heya
```

### Linting

```bash
uv run ruff check heya
uv run ruff format heya
```

## Dependencies

- **click**: Command-line interface framework
- **playwright**: Browser automation for HTML/WeChat conversion
- **markdown**: Markdown parsing
- **pypdf**: PDF manipulation
- **reportlab**: PDF generation and merging
- **gradio**: Web UI (optional)
- **PySide6**: Desktop application (optional)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/zkep/heya/issues) on GitHub.

## Acknowledgments

- Built with [Playwright](https://playwright.dev/) for reliable browser automation
- Web UI powered by [Gradio](https://www.gradio.app/)
- Desktop application powered by [PySide6](https://doc.qt.io/qtforpython/)
