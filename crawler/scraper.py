import os
from bs4 import BeautifulSoup
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - Line %(lineno)d - %(message)s')

# Relative paths
RAW_DATA_DIR = "../data/raw"
PROCESSED_DATA_DIR = "../data/processed"

def scrape_html(html_file_path, game_name):
    logging.info(f"Starting scrape_html for file: {html_file_path}, game_name: {game_name}")

    # Check if input HTML file exists
    if not os.path.exists(html_file_path):
        logging.error(f"Input HTML file not found: {html_file_path}")
        return {}

    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        logging.error(f"Error reading HTML file {html_file_path}: {str(e)}")
        return {}

    soup = BeautifulSoup(html_content, 'html.parser')
    scraped_data = {}
    current_heading = "Introduction"
    scraped_data[current_heading] = []

    main_content = soup.find('main') or soup.find('body')
    if not main_content:
        logging.warning("No main or body content found in HTML")
        return {}

    for element in main_content.find_all(['h1', 'h2', 'h3', 'p', 'table', 'ul', 'ol']):
        if element.name in ['h1', 'h2', 'h3']:
            current_heading = element.get_text(strip=True)
            current_heading = re.sub(r'[^\w\s-]', '_', current_heading).strip('_')  # Sanitize heading
            scraped_data[current_heading] = []
        elif element.name == 'p':
            text = element.get_text(strip=True)
            if text:
                scraped_data[current_heading].append({"type": "text", "content": text})
        elif element.name == 'table':
            table_content = []
            rows = element.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                table_content.append("| " + " | ".join(row_data) + " |")
            if table_content:
                if rows and rows[0].find('th'):
                    headers = rows[0].find_all('th')
                    table_content.insert(1, "| " + " | ".join(["---"] * len(headers)) + " |")
                scraped_data[current_heading].append({"type": "table", "content": table_content})
        elif element.name in ['ul', 'ol']:
            list_items = [li.get_text(strip=True) for li in element.find_all('li') if li.get_text(strip=True)]
            if list_items:
                scraped_data[current_heading].append({"type": "list", "content": list_items})

    # Sanitize file name
    base_name = os.path.splitext(os.path.basename(html_file_path))[0]
    base_name = re.sub(r'[^\w\s-]', '_', base_name).strip('_')  # Remove invalid characters
    base_name = re.sub(r'\s+', '_', base_name)  # Replace spaces with underscores
    game_folder = re.sub(r'[^\w\s-]', '_', game_name).strip('_')
    game_folder = re.sub(r'\s+', '_', game_folder)
    
    game_dir = os.path.join(PROCESSED_DATA_DIR, game_folder)
    os.makedirs(game_dir, exist_ok=True)
    output_file = os.path.join(game_dir, f"{base_name}.md")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {base_name.replace('_', ' ')}\n\n")
            for heading, items in scraped_data.items():
                f.write(f"## {heading}\n\n")
                for item in items:
                    if item['type'] == 'text':
                        f.write(f"{item['content']}\n\n")
                    elif item['type'] == 'table':
                        for row in item['content']:
                            f.write(f"{row}\n")
                        f.write("\n")
                    elif item['type'] == 'list':
                        for li in item['content']:
                            f.write(f"- {li}\n")
                        f.write("\n")
        logging.info(f"Markdown file saved: {output_file}")
    except Exception as e:
        logging.error(f"Error writing Markdown file {output_file}: {str(e)}")
        return scraped_data

    return scraped_data