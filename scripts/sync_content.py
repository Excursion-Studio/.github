#!/usr/bin/env python3
"""
Sync content from excursion-studio.github.io to .github profile README
"""

import json
import argparse
import re
from pathlib import Path


def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def convert_z_tags(text):
    """Convert <z> and <zi> tags to Markdown bold (**text**)"""
    text = re.sub(r'<z>(.*?)</z>', r'**\1**', text)
    text = re.sub(r'<zi>(.*?)</zi>', r'**\1**', text)
    return text


def generate_courses_table(sections, lang='en'):
    """Generate courses markdown table"""
    lines = []
    access_text = "Access" if lang == 'en' else "访问"
    
    for section in sections:
        title = convert_z_tags(section['title'])
        lines.append(f"### {title}\n")
        lines.append("")
        lines.append("| Course | Status | Link |")
        lines.append("|--------|--------|------|")
        
        for item in section.get('items', []):
            status = "✅ Available" if item.get('available', False) else "❌ Not Available"
            link = f"[{access_text}]({item['link']})"
            item_title = convert_z_tags(item['title'])
            lines.append(f"| {item_title} | {status} | {link} |")
        
        lines.append("")
    
    return "\n".join(lines)


def generate_products_table(sections, lang='en'):
    """Generate products markdown table"""
    lines = []
    preview_text = "Preview" if lang == 'en' else "预览"
    
    for section in sections:
        title = convert_z_tags(section['title'])
        lines.append(f"### {title}\n")
        lines.append("")
        lines.append("| Product | Status | Link |")
        lines.append("|---------|--------|------|")
        
        for item in section.get('items', []):
            status = "✅ Available" if item.get('available', False) else "❌ Not Available"
            link = f"[{preview_text}]({item['link']})"
            item_title = convert_z_tags(item['title'])
            lines.append(f"| {item_title} | {status} | {link} |")
        
        lines.append("")
    
    return "\n".join(lines)


def generate_digests_table(sections, lang='en'):
    """Generate digests markdown table with top 3 latest items"""
    lines = []
    read_text = "Read" if lang == 'en' else "阅读"
    latest_text = "**🔥 Latest!**" if lang == 'en' else "**🔥 最新！**"
    title_header = "Title" if lang == 'en' else "标题"
    link_header = "Link" if lang == 'en' else "链接"
    
    all_items = []
    for section in sections:
        for item in section.get('items', []):
            all_items.append(item)
    
    all_items.sort(key=lambda x: x.get('digestPubTime', ''), reverse=True)
    top_items = all_items[:3]
    
    lines.append(f"| {title_header} | {link_header} |")
    lines.append("|-------|------|")
    
    for i, item in enumerate(top_items):
        title = convert_z_tags(item.get('title', ''))
        if i == 0:
            title = f"{title} {latest_text}"
        
        # Parse sourcePath to build correct URL if available
        source_path = item.get('sourcePath')
        if source_path:
            # Extract paperName: take last two elements after split, then first one
            parts = source_path.split('/')
            if len(parts) >= 2:
                paper_name = parts[-2]
                # Extract categoryPath: first two parts (e.g., paper-guide or paper-express)
                category_path = parts[0]
                url = f"https://excursion-studio.github.io/ES-digests/{category_path}/index.html?paper={paper_name}"
            else:
                url = item.get('pdfUrl', '#')
        else:
            url = item.get('pdfUrl', '#')
        
        link = f"[{read_text}]({url})"
        lines.append(f"| {title} | {link} |")
    
    lines.append("")
    
    return "\n".join(lines)


def update_readme_section(readme_content, section_name, new_content):
    """Update a section in README between markers"""
    start_marker = f"<!-- {section_name}_START -->"
    end_marker = f"<!-- {section_name}_END -->"
    
    pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
    replacement = f"{start_marker}\n{new_content}\n{end_marker}"
    
    return re.sub(pattern, replacement, readme_content, flags=re.DOTALL)


def sync_content(source_dir, target_dir):
    """Main sync function"""
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Load data files
    courses_en = load_json(source_path / 'data' / 'en' / 'courses.json')
    courses_zh = load_json(source_path / 'data' / 'zh' / 'courses.json')
    products_en = load_json(source_path / 'data' / 'en' / 'products.json')
    products_zh = load_json(source_path / 'data' / 'zh' / 'products.json')
    digests_en = load_json(source_path / 'data' / 'en' / 'digests.json')
    digests_zh = load_json(source_path / 'data' / 'zh' / 'digests.json')
    
    # Read current README files
    readme_en_path = target_path / 'profile' / 'README.md'
    readme_zh_path = target_path / 'profile' / 'README_zh.md'
    
    readme_en = readme_en_path.read_text(encoding='utf-8')
    readme_zh = readme_zh_path.read_text(encoding='utf-8')
    
    # Generate new content
    courses_en_content = generate_courses_table(courses_en.get('sections', []), 'en')
    courses_zh_content = generate_courses_table(courses_zh.get('sections', []), 'zh')
    products_en_content = generate_products_table(products_en.get('sections', []), 'en')
    products_zh_content = generate_products_table(products_zh.get('sections', []), 'zh')
    digests_en_content = generate_digests_table(digests_en.get('sections', []), 'en')
    digests_zh_content = generate_digests_table(digests_zh.get('sections', []), 'zh')
    
    # Update READMEs
    readme_en = update_readme_section(readme_en, 'COURSES', courses_en_content)
    readme_zh = update_readme_section(readme_zh, 'COURSES', courses_zh_content)
    readme_en = update_readme_section(readme_en, 'PRODUCTS', products_en_content)
    readme_zh = update_readme_section(readme_zh, 'PRODUCTS', products_zh_content)
    readme_en = update_readme_section(readme_en, 'DIGESTS', digests_en_content)
    readme_zh = update_readme_section(readme_zh, 'DIGESTS', digests_zh_content)
    
    # Write updated READMEs
    readme_en_path.write_text(readme_en, encoding='utf-8')
    readme_zh_path.write_text(readme_zh, encoding='utf-8')
    
    print("Sync completed successfully!")


def main():
    parser = argparse.ArgumentParser(description='Sync content from excursion-studio.github.io')
    parser.add_argument('--source', required=True, help='Path to source repo (excursion-studio.github.io)')
    parser.add_argument('--target', required=True, help='Path to target repo (.github)')
    
    args = parser.parse_args()
    sync_content(args.source, args.target)


if __name__ == '__main__':
    main()
