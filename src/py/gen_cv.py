#!/usr/bin/env python3
import markdown
import jinja2
from pathlib import Path
import re
import sys

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CV</title>
    <style>
        @page {
            size: A4;
            margin: 0.5cm 1cm;
        }
        body {
            font-family: "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
            font-size: 11.5pt;
            line-height: 1.3;
            color: #333;
            max-width: 21cm;
            margin: 0 auto;
            padding: 0.5cm;
        }
        * {
            font-family: "Noto Sans CJK SC", "Microsoft YaHei", Consolas, sans-serif;
        }
        h3 {
            color: #000;
            font-weight: bold;
            font-size: 1.2em;
            margin: 4px 0 4px 0;
            padding-bottom: 2px;
        }
        hr {
            border: none;
            border-top: 1px solid #000;
            margin: -4px 0;
        }
        strong, b {
            color: #000;
            font-weight: bold;
        }
        p {
            margin: 4px 0;
        }
    </style>
</head>
<body>
    {{ content }}
</body>
</html>
"""

def convert_markdown_to_html(md_content):
    md_content = re.sub(r'^(\s{2,})(?=\S)', lambda m: '    ' * (len(m.group(1)) // 2), md_content, flags=re.MULTILINE)
    md_content = re.sub(r'<!--.*?-->', '', md_content, flags=re.DOTALL)
    extensions = ['extra', 'tables']
    html_content = markdown.markdown(md_content, extensions=extensions)
    html_content = html_content.replace('<hr>', '<hr style="border: none; border-top: 1px solid #000000; margin: 6px 0;">')
    bold_style = 'style="color: #000000; font-weight: 900; letter-spacing: 0.02em;"'
    html_content = html_content.replace('<strong>', f'<strong {bold_style}>')
    return f'<div style="font-size: 0.9em;">{html_content}</div>'

def generate_html(md_file_path, output_path):
    md_content = Path(md_file_path).read_text(encoding='utf-8')
    html_content = convert_markdown_to_html(md_content)
    template = jinja2.Template(HTML_TEMPLATE)
    html_output = template.ren