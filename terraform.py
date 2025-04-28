import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import markdown

# Define repo details
repo_owner = "hashicorp"
repo_name = "terraform-provider-azurerm"
output_dir = "output-terraform-provider-azurerm"

api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/website/docs/"

# TODO: add ur github token here
headers = {"Authorization": ""}

os.makedirs(output_dir, exist_ok=True)

target_dirs = [
    "website/docs/r",
    "website/docs/ephemeral-resources",
    "website/docs/functions",
    "website/docs/guides"
]

target_file = "website/docs/index.html.markdown"

def markdown_to_text(markdown_content):
    html = markdown.markdown(markdown_content)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


def fetch_and_process_markdown(api_url, current_path=""):

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        items = response.json()

        for item in items:

            if item["type"] == "dir" and any(item["path"].startswith(dir_path) for dir_path in target_dirs):
                fetch_and_process_markdown(item["url"], current_path + "/" + item["name"])

            elif item["type"] == "file":
                if item["path"] == target_file or any(item["path"].startswith(dir_path) for dir_path in target_dirs):
                    print(f"Processing file: {item['path']}")
                    file_url = item["download_url"]
                    md_response = requests.get(file_url, headers=headers)

                    if md_response.status_code == 200:
                        md_content = md_response.text
                        plain_text = markdown_to_text(md_content)

                        relative_path = Path(current_path) / item["name"]
                        output_path = Path(output_dir) / relative_path

                        os.makedirs(output_path.parent, exist_ok=True)

                        output_path = output_path.with_suffix(".txt")
                        with open(output_path, "w", encoding="utf-8") as txt_file:
                            txt_file.write(plain_text)

                        print(f"Processed {item['path']} -> {output_path}")

                    else:
                        print(f"Failed to download {file_url}")

    else:
        print(f"Failed to fetch {api_url}, status code: {response.status_code}")


fetch_and_process_markdown(api_url)
