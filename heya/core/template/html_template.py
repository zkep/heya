from __future__ import annotations

__all__ = ["DEFAULT_CSS", "HTML_TEMPLATE", "render_html"]

DEFAULT_CSS = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background: #fff;
    padding: 40px;
    max-width: 800px;
    margin: 0 auto;
}

h1, h2, h3, h4, h5, h6 {
    margin: 1.5em 0 0.5em;
    font-weight: 600;
    line-height: 1.3;
}

h1 {
    font-size: 2em;
    border-bottom: 2px solid #eee;
    padding-bottom: 0.3em;
    margin-top: 0;
}

h2 {
    font-size: 1.5em;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.3em;
}

h3 {
    font-size: 1.25em;
}

p {
    margin: 1em 0;
}

ul, ol {
    margin: 1em 0;
    padding-left: 2em;
}

li {
    margin: 0.5em 0;
}

blockquote {
    margin: 1em 0;
    padding: 0.5em 1em;
    border-left: 4px solid #ddd;
    background: #f9f9f9;
    color: #666;
}

code {
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    background: #f4f4f4;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-size: 0.9em;
}

pre {
    background: #282c34;
    color: #abb2bf;
    padding: 1em;
    border-radius: 6px;
    overflow-x: auto;
    margin: 1em 0;
}

pre code {
    background: transparent;
    padding: 0;
    color: inherit;
    font-size: 0.875em;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 0.5em 1em;
    text-align: left;
}

th {
    background: #f5f5f5;
    font-weight: 600;
}

tr:nth-child(even) {
    background: #f9f9f9;
}

a {
    color: #0066cc;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 2em 0;
}

img {
    max-width: 100%;
    height: auto;
}

@media print {
    body {
        padding: 20px;
        max-width: none;
    }
}
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""


def render_html(title: str, content: str, css: str | None = None) -> str:
    if css is None:
        css = DEFAULT_CSS
    return HTML_TEMPLATE.format(title=title, css=css, content=content)
