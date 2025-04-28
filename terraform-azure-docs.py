import os
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

# Define repository details
repo_url = 'https://github.com/Azure/terraform.git'
repo_name = 'terraform'
output_dir = 'output'

os.makedirs(output_dir, exist_ok=True)

if not os.path.exists(repo_name):
    subprocess.run(['git', 'clone', repo_url])

def markdown_to_text(markdown_content):
    try:
        import markdown
        html = markdown.markdown(markdown_content)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    except ImportError:
        print("Please install the 'markdown' and 'beautifulsoup4' packages.")
        return markdown_content

for root, _, files in os.walk(repo_name):
    for file in files:
        if file.endswith('.md'):
            md_path = Path(root) / file

            with open(md_path, 'r', encoding='utf-8') as md_file:
                md_content = md_file.read()
                plain_text = markdown_to_text(md_content)

                relative_path = md_path.relative_to(repo_name).with_suffix('.txt')
                output_path = Path(output_dir) / relative_path.parent
                os.makedirs(output_path, exist_ok=True)

                output_file = output_path / relative_path.name
                with open(output_file, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(plain_text)

                print(f'Converted {md_path} -> {output_file}')
