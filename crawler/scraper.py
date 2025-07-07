import os
import re
from bs4 import BeautifulSoup
from markdownify import markdownify as md

PROCESSED_DATA_DIR = "../data/processed"

# Add character_name to the function signature
def scrape_html(html_file_path, game_name, character_name):
    """
    Reads raw HTML, cleans it, and saves it as a markdown file
    with a standardized name.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Your existing scraping and cleaning logic goes here...
        # For example:
        # for tag in soup.find_all(['nav', 'aside', 'footer', 'script', 'style']):
        #     tag.decompose()
        # markdown_content = md(str(soup), heading_style="ATX")
        
        # This is an example, replace with your actual scraping logic
        if soup.body:
            markdown_content = md(str(soup.body), heading_style="ATX")
        else:
            markdown_content = md(html_content, heading_style="ATX")


        # --- STANDARDIZED FILE NAMING ---
        # Sanitize game name for the folder
        game_folder = re.sub(r'[^\w\s-]', '_', game_name.strip()).strip('_')
        game_folder = re.sub(r'\s+', '_', game_folder)
        processed_game_dir = os.path.join(PROCESSED_DATA_DIR, game_folder)
        os.makedirs(processed_game_dir, exist_ok=True)

        # Sanitize character name for the filename
        char_filename = re.sub(r'[^\w\s-]', '_', character_name.strip()).strip('_')
        char_filename = re.sub(r'\s+', '_', char_filename)

        markdown_path = os.path.join(processed_game_dir, f"{char_filename}.md")
        print(f"Saving markdown to standardized path: {markdown_path}")

        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return markdown_content

    except Exception as e:
        print(f"Error during scraping: {e}")
        return None