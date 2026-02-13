# Heya PDF Converter

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

English ｜ [中文](README-zh.md) 

A powerful and versatile tool for converting documents to PDF and Word formats. Heya supports converting HTML, Markdown, WeChat articles to PDF, and PDF to Word documents.

![Heya PDF Converter Interface](docs/heya.gif)

## Features

- **HTML to PDF**: Convert web pages or local HTML files to PDF
- **Markdown to PDF**: Convert Markdown files to PDF with batch conversion support
- **WeChat Articles to PDF**: Convert WeChat official account articles to PDF, with support for batch conversion from article lists
- **PDF to Word**: Convert PDF documents to editable Word (.docx) files
- **PDF Compression**: Optional compression to reduce file size with configurable quality levels
- **PDF Merging**: Merge multiple PDF files into one
- **Web Interface**: User-friendly web UI with multi-language support (English, Chinese, Korean)
- **CLI Tool**: Command-line interface for automation and scripting

## Installation

### Basic Installation

```bash
pip install heya
```

### With Web UI Support

```bash
pip install heya[ui]
```

### Install Playwright Browsers (Required for HTML/WeChat conversion)

```bash
playwright install chromium
```

### Optional: PDF to Word Conversion

```bash
pip install pdf2docx
```

## Docker

### Using Docker

You can also run Heya using Docker:

```bash
# Build the Docker image
docker build -t heya-web .

# Run the container
docker run -p 7860:7860 heya-web
```

The web interface will be available at `http://localhost:7860`.

### Docker Compose

For easier management, you can use Docker Compose:

```bash
docker-compose up -d
```

Create a `docker-compose.yml` file:

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

## Usage

### Command Line Interface

#### HTML to PDF

```bash
heya html2pdf -i https://example.com -o output.pdf
heya html2pdf -i file:///path/to/page.html -o output.pdf
```

Options:
- `-i, --source`: Source URL or HTML file path
- `-o, --target`: Output PDF file path
- `-t, --timeout`: Timeout in seconds (default: 3.0)
- `-c, --compress`: Enable PDF compression
- `-q, --quality`: Compression quality: 0=high, 1=medium, 2=low

#### Markdown to PDF

```bash
heya md2pdf -i README.md -o output.pdf
heya md2pdf -i doc.md -o output.pdf -c -q 1
```

#### WeChat Articles to PDF

```bash
heya wechat2pdf -i https://mp.weixin.qq.com/s/xxx -o output_dir/
```

Supports:
- Single article URL: `https://mp.weixin.qq.com/s/xxx`
- Article list URL: `https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=xxx`

#### PDF to Word

```bash
heya pdf2word -i document.pdf -o output.docx
```

#### Web Interface

```bash
heya web
```

By default, the web server starts on `http://127.0.0.1:7860`.

### Web Interface

The web interface provides an easy-to-use UI with the following features:

- **Multi-tab interface**: Separate tabs for each conversion type
- **Drag & drop**: Upload files by dragging and dropping
- **Batch processing**: Convert multiple files at once
- **PDF merging**: Merge multiple PDFs into a single file
- **Quality settings**: Configure compression quality and timeout
- **Multi-language support**: English, Chinese, and Korean
- **Error handling**: Clear error messages with issue reporting

## Project Structure

```
heya/
├── application/          # Core conversion logic
│   ├── converters.py     # Converter implementations
│   └── wechat_converter.py  # WeChat converter
├── cli/                  # Command-line interface
│   ├── commands/         # CLI commands
│   ├── options.py        # Command options
│   └── utils.py         # Utility functions
├── domain/               # Domain models and interfaces
│   ├── models/           # Data models
│   ├── services/         # Domain services
│   ├── exceptions.py     # Exception definitions
│   └── ports.py         # Port interfaces
├── infrastructure/       # Infrastructure implementations
│   ├── browser/          # Browser related
│   ├── markdown/         # Markdown processing
│   ├── pdf/              # PDF processing
│   ├── template/         # Templates
│   └── wechat/           # WeChat parser
├── shared/               # Shared utilities
│   ├── config/           # Configuration management
│   ├── constants.py      # Constants definitions
│   ├── cache.py          # Caching mechanism
│   ├── errors.py         # Error handling
│   ├── logging.py        # Logging
│   └── temp.py           # Temporary file management
└── web/                  # Web interface
    ├── components/       # UI components
    ├── converters/       # Web converters
    ├── handlers/         # Request handlers
    ├── i18n/            # Internationalization
    ├── service.py        # Web service layer
    └── app.py            # Application entry point
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/zkep/heya.git
cd heya
uv sync
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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/zkep/heya/issues) on GitHub.

## Acknowledgments

- Built with [Playwright](https://playwright.dev/) for reliable browser automation
- Web UI powered by [Gradio](https://www.gradio.app/)
