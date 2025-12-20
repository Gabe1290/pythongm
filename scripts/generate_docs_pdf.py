#!/usr/bin/env python3
"""
Generate PDF-ready HTML documents from Markdown files.

This script converts Markdown documentation to HTML with print-friendly styling.
The HTML files can be opened in a browser and printed to PDF using Ctrl+P.

Usage:
    python scripts/generate_docs_pdf.py

Output:
    docs/TESTING_CHECKLIST.html - Print-ready HTML version
"""

import os
import sys
from pathlib import Path

# Try to import markdown-it, fall back to simple conversion if not available
try:
    from markdown_it import MarkdownIt
    from markdown_it.extensions.tables import tables_plugin
    HAS_MARKDOWN_IT = True
except ImportError:
    HAS_MARKDOWN_IT = False
    print("Warning: markdown-it not available, using basic conversion")


# CSS for print-ready PDF output
PDF_STYLES = """
<style>
    @page {
        size: A4;
        margin: 2cm;
    }

    * {
        box-sizing: border-box;
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 11pt;
        line-height: 1.5;
        color: #333;
        max-width: 210mm;
        margin: 0 auto;
        padding: 20px;
        background: white;
    }

    h1 {
        font-size: 24pt;
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        margin-top: 0;
        page-break-after: avoid;
    }

    h2 {
        font-size: 16pt;
        color: #2980b9;
        border-bottom: 1px solid #bdc3c7;
        padding-bottom: 5px;
        margin-top: 25px;
        page-break-after: avoid;
    }

    h3 {
        font-size: 13pt;
        color: #27ae60;
        margin-top: 20px;
        page-break-after: avoid;
    }

    h4 {
        font-size: 11pt;
        color: #8e44ad;
        margin-top: 15px;
        page-break-after: avoid;
    }

    p {
        margin: 10px 0;
    }

    em {
        color: #7f8c8d;
        font-style: italic;
    }

    code {
        font-family: 'Consolas', 'Monaco', monospace;
        background-color: #f8f9fa;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 10pt;
        color: #c7254e;
    }

    pre {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        border: 1px solid #e9ecef;
        page-break-inside: avoid;
    }

    pre code {
        background: none;
        padding: 0;
        color: #333;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 10pt;
        page-break-inside: avoid;
    }

    th {
        background-color: #3498db;
        color: white;
        padding: 10px 8px;
        text-align: left;
        font-weight: 600;
    }

    td {
        padding: 8px;
        border-bottom: 1px solid #e9ecef;
        vertical-align: top;
    }

    tr:nth-child(even) {
        background-color: #f8f9fa;
    }

    tr:hover {
        background-color: #e8f4f8;
    }

    /* Checkbox styling */
    td:first-child {
        width: 60px;
        text-align: center;
        font-family: monospace;
    }

    /* Status indicators */
    .status-pending { color: #e74c3c; }
    .status-done { color: #27ae60; }
    .status-issue { color: #f39c12; }

    hr {
        border: none;
        border-top: 2px solid #bdc3c7;
        margin: 30px 0;
    }

    ul, ol {
        margin: 10px 0;
        padding-left: 25px;
    }

    li {
        margin: 5px 0;
    }

    /* Print-specific styles */
    @media print {
        body {
            padding: 0;
        }

        h1, h2, h3, h4 {
            page-break-after: avoid;
        }

        table, pre, blockquote {
            page-break-inside: avoid;
        }

        tr {
            page-break-inside: avoid;
        }
    }

    /* Legend box */
    .legend {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }

    /* Phase headers */
    h2:contains("PHASE") {
        background-color: #2c3e50;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
    }
</style>
"""


def convert_table_to_html(table_lines: list) -> str:
    """Convert markdown table lines to HTML table."""
    if len(table_lines) < 2:
        return '\n'.join(table_lines)

    html = ['<table>']

    # Process header row
    header_cells = [cell.strip() for cell in table_lines[0].split('|')[1:-1]]
    html.append('<thead><tr>')
    for cell in header_cells:
        html.append(f'<th>{cell}</th>')
    html.append('</tr></thead>')

    # Skip separator row (index 1), process data rows
    html.append('<tbody>')
    for row in table_lines[2:]:
        if '|' in row:
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            html.append('<tr>')
            for cell in cells:
                html.append(f'<td>{cell}</td>')
            html.append('</tr>')
    html.append('</tbody>')
    html.append('</table>')

    return '\n'.join(html)


def convert_markdown_to_html(md_content: str) -> str:
    """Convert Markdown to HTML."""
    if HAS_MARKDOWN_IT:
        md = MarkdownIt('commonmark', {'html': True, 'typographer': True})
        md = md.enable('table')
        return md.render(md_content)
    else:
        # Basic fallback conversion with table support
        import re

        lines = md_content.split('\n')
        result = []
        i = 0
        in_table = False
        table_lines = []
        in_list = False
        list_items = []

        while i < len(lines):
            line = lines[i]

            # Check for table start (line with | and next line has |---|)
            if '|' in line and i + 1 < len(lines) and re.match(r'^\|[\s\-:|]+\|$', lines[i + 1]):
                # Start collecting table
                if in_list:
                    result.append('<ul>' + ''.join(list_items) + '</ul>')
                    list_items = []
                    in_list = False

                in_table = True
                table_lines = [line]
                i += 1
                continue

            if in_table:
                if '|' in line:
                    table_lines.append(line)
                    i += 1
                    continue
                else:
                    # End of table
                    result.append(convert_table_to_html(table_lines))
                    table_lines = []
                    in_table = False
                    # Don't increment i, process current line

            # Headers
            if line.startswith('# '):
                if in_list:
                    result.append('<ul>' + ''.join(list_items) + '</ul>')
                    list_items = []
                    in_list = False
                result.append(f'<h1>{line[2:]}</h1>')
                i += 1
                continue
            if line.startswith('## '):
                if in_list:
                    result.append('<ul>' + ''.join(list_items) + '</ul>')
                    list_items = []
                    in_list = False
                result.append(f'<h2>{line[3:]}</h2>')
                i += 1
                continue
            if line.startswith('### '):
                if in_list:
                    result.append('<ul>' + ''.join(list_items) + '</ul>')
                    list_items = []
                    in_list = False
                result.append(f'<h3>{line[4:]}</h3>')
                i += 1
                continue
            if line.startswith('#### '):
                if in_list:
                    result.append('<ul>' + ''.join(list_items) + '</ul>')
                    list_items = []
                    in_list = False
                result.append(f'<h4>{line[5:]}</h4>')
                i += 1
                continue

            # Horizontal rules
            if re.match(r'^---+$', line):
                if in_list:
                    result.append('<ul>' + ''.join(list_items) + '</ul>')
                    list_items = []
                    in_list = False
                result.append('<hr>')
                i += 1
                continue

            # List items
            if line.startswith('- ') or line.startswith('* '):
                in_list = True
                item_text = line[2:]
                # Process inline formatting
                item_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item_text)
                item_text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', item_text)
                item_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', item_text)
                list_items.append(f'<li>{item_text}</li>')
                i += 1
                continue

            # End list if we hit a non-list line
            if in_list and line.strip() and not line.startswith('- ') and not line.startswith('* '):
                result.append('<ul>' + ''.join(list_items) + '</ul>')
                list_items = []
                in_list = False

            # Regular paragraph
            if line.strip():
                # Process inline formatting
                processed = line
                processed = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', processed)
                processed = re.sub(r'\*(.+?)\*', r'<em>\1</em>', processed)
                processed = re.sub(r'`([^`]+)`', r'<code>\1</code>', processed)
                result.append(f'<p>{processed}</p>')

            i += 1

        # Close any remaining table or list
        if in_table and table_lines:
            result.append(convert_table_to_html(table_lines))
        if in_list and list_items:
            result.append('<ul>' + ''.join(list_items) + '</ul>')

        return '\n'.join(result)


def create_html_document(title: str, content: str) -> str:
    """Wrap HTML content in a complete document."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {PDF_STYLES}
</head>
<body>
    {content}
    <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ccc; text-align: center; color: #888; font-size: 9pt;">
        Generated from PyGameMaker documentation | Print this page (Ctrl+P) to save as PDF
    </footer>
</body>
</html>
"""


def process_markdown_file(input_path: Path, output_path: Path):
    """Process a single Markdown file."""
    print(f"Processing: {input_path}")

    # Read markdown content
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Extract title from first heading
    title = "PyGameMaker Documentation"
    for line in md_content.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # Convert to HTML
    html_content = convert_markdown_to_html(md_content)

    # Create complete document
    html_doc = create_html_document(title, html_content)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_doc)

    print(f"Created: {output_path}")
    return output_path


def main():
    """Main entry point."""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_dir = project_root / "docs"

    # Files to convert
    files_to_convert = [
        ("TESTING_CHECKLIST.md", "TESTING_CHECKLIST.html"),
    ]

    # Also check for other markdown files in docs
    if docs_dir.exists():
        for md_file in docs_dir.glob("*.md"):
            html_name = md_file.stem + ".html"
            if (md_file.name, html_name) not in files_to_convert:
                files_to_convert.append((md_file.name, html_name))

    created_files = []

    for md_name, html_name in files_to_convert:
        input_path = docs_dir / md_name
        output_path = docs_dir / html_name

        if input_path.exists():
            created_files.append(process_markdown_file(input_path, output_path))
        else:
            print(f"Warning: {input_path} not found, skipping")

    print("\n" + "=" * 60)
    print("PDF Generation Complete!")
    print("=" * 60)
    print("\nTo create PDF files:")
    print("1. Open the HTML files in a web browser")
    print("2. Press Ctrl+P (or Cmd+P on Mac)")
    print("3. Select 'Save as PDF' as the destination")
    print("4. Click 'Save'")
    print("\nCreated files:")
    for f in created_files:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
