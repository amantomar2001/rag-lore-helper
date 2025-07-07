# Lore Helper: A RAG-Powered Game Wiki Assistant

This project is a web-based assistant that uses a Retrieval-Augmented Generation (RAG) pipeline to answer questions about video game characters. It automatically crawls and scrapes Fandom wikis, stores the information in a vector database, and uses a Large Language Model to provide detailed summaries based on user queries.

## ✨ Features

-   **Automated Web Crawling:** Uses Selenium to navigate Fandom, log in, and find the correct character pages.
-   **Intelligent Scraping:** Employs BeautifulSoup to parse the raw HTML and extract relevant lore, cleaning it into a structured Markdown format.
-   **Efficient Caching:** Automatically caches scraped data to avoid re-running the expensive crawling and scraping processes for characters that have already been processed.
-   **RAG Pipeline:** Leverages LangChain and FAISS to create a vector database from the scraped lore for fast and relevant information retrieval.
-   **Interactive UI:** A simple and effective web interface built with Streamlit for easy interaction.
-   **Secure:** Uses environment variables (`.env` file) to keep sensitive credentials safe and out of the source code.

## ⚙️ How It Works

The application follows a three-stage pipeline:

1.  **Crawl:** Given a game and character name, Selenium launches a browser, finds the correct wiki, and saves the raw HTML of the character's page.
2.  **Scrape:** BeautifulSoup reads the raw HTML, cleans it, extracts the main content, and saves it as a clean Markdown file. This step is skipped if a Markdown file for the character already exists.
3.  **Query (RAG):** The Markdown file is loaded, split into chunks, and embedded into a FAISS vector store. The user's query is used to find the most relevant chunks of text, which are then fed to an LLM to generate a final, coherent answer.

## 🚀 Getting Started

Follow these instructions to set up and run the project locally.

### 1. Prerequisites

-   Python 3.9+
-   Git
-   Google Chrome browser installed

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/amantomar2001/rag-lore-helper.git
    cd rag-lore-helper
    ```

2.  **Create a virtual environment:**
    ```bash
    # For Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    *(Note: You will need to create a `requirements.txt` file first if you haven't already. You can do this with `pip freeze > requirements.txt`)*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a new file named `.env` in the root of the project directory. Copy the contents of the example below and fill in your own credentials.

    **.env.example**
    ```env
    # Fandom Wiki Credentials
    FANDOM_EMAIL="your_fandom_email@example.com"
    FANDOM_PASSWORD="your_fandom_password"

    # OpenAI API Key for the RAG pipeline
    OPENAI_API_KEY="sk-..."
    ```

### 3. Running the Application

Once the installation is complete, you can start the Streamlit web server with the following command:

```bash
streamlit run crawler/main.py
```

This will open a new tab in your default web browser where you can interact with the Lore Helper.

## 📂 Project Structure

```
rag-lore-helper/
├── crawler/
│   ├── __init__.py
│   ├── main.py         # The Streamlit UI and main pipeline orchestrator
│   ├── crawler.py      # Selenium logic for web crawling and navigation
│   ├── scraper.py      # BeautifulSoup logic for HTML parsing and cleaning
│   └── rag.py          # LangChain/FAISS logic for the RAG pipeline
├── data/
│   ├── processed/      # Stores the clean .md files
│   └── raw/            # Stores the raw .html files
│   └── faiss/          # Stores the FAISS vector indexes
├── .env                # (Not committed) Stores secret keys and credentials
├── .gitignore          # Specifies files for Git to ignore
└── README.md           # This file
```

## 🛠️ Technologies Used

-   **Python**
-   **Streamlit:** For the web interface
-   **Selenium:** For web crawling and browser automation
-   **BeautifulSoup4:** For HTML scraping and parsing
-   **LangChain:** For orchestrating the RAG pipeline
-   **FAISS:** For efficient similarity search in the vector store
-   **OpenAI:** For embeddings and text generation
-   **Dotenv:** For managing environment variables