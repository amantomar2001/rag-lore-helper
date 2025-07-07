import streamlit as st
from crawler import navigate_to_target
from scraper import scrape_html
from rag import run_rag_pipeline
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Hardcoded paths (matching scraper.py)
RAW_DATA_DIR = "../data/raw"
PROCESSED_DATA_DIR = "../data/processed"
FAISS_INDEX_DIR = "../data/faiss"

def get_faiss_index_path(game_name, character_name):
    """Generate path for FAISS index."""
    game_folder = re.sub(r'[^\w\s-]', '_', game_name.strip()).strip('_')
    game_folder = re.sub(r'\s+', '_', game_folder)
    return os.path.join(FAISS_INDEX_DIR, game_folder, f"{character_name.strip()}_faiss")

def get_markdown_path(game_name, base_name):
    """Generate path for markdown file using base_name from HTML file."""
    game_folder = re.sub(r'[^\w\s-]', '_', game_name.strip()).strip('_')
    game_folder = re.sub(r'\s+', '_', game_folder)
    return os.path.join(PROCESSED_DATA_DIR, game_folder, f"{base_name}.md")

def main():
    st.title("Lore Helper")
    
    # Input fields
    game_name = st.text_input("Enter Game Name")
    character_name = st.text_input("Enter Character Name")
    query = st.text_input("Enter Search Query")
    
    if st.button("Run Pipeline"):
        if game_name and character_name and query:
            # Sanitize inputs
            game_name = game_name.strip()
            character_name = character_name.strip()
            st.write(f"Processing game: {game_name}, character: {character_name}, query: {query}")

            # Generate FAISS index path
            faiss_index_path = get_faiss_index_path(game_name, character_name)

            # Run the crawler
            st.write("Running crawler...")
            result_url, content_html, file_path = navigate_to_target(game_name, character_name)
            if not file_path:
                st.error("Failed to retrieve HTML file")
                return
            # Derive base_name from HTML file path
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            markdown_path = get_markdown_path(game_name, base_name)

            # Check if Markdown file already exists
            if os.path.exists(markdown_path):
                st.write("Loading existing markdown...")
            else:
                st.write("Running scraper...")
                scraped_data = scrape_html(file_path, game_name)
                if not scraped_data:
                    st.error("Failed to scrape HTML content")
                    return
                st.write("Scraper output generated.")

            # Verify Markdown file exists
            if os.path.exists(markdown_path):
                st.write("Storing in FAISS vector DB...")
                response = run_rag_pipeline(markdown_path, faiss_index_path, character_name, game_name, query)
                if response:
                    st.success(f"Result: Pipeline completed for {character_name} in {game_name}")
                    st.subheader("Character Summary")
                    st.write(response)
                else:
                    st.error(f"RAG pipeline failed to produce a response")
            else:
                st.error(f"Markdown file not found: {markdown_path}")
                st.write("Ensure scraper saves the markdown file correctly.")
        else:
            st.warning("Please enter Game Name, Character Name, and Query")

if __name__ == "__main__":
    main()