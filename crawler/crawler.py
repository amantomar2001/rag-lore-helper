from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import re
import os
from bs4 import BeautifulSoup
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use relative path
RAW_DATA_DIR = "../data/raw"

# Get credentials from environment variables
EMAIL = os.getenv("FANDOM_EMAIL")
PASSWORD = os.getenv("FANDOM_PASSWORD")

def navigate_to_target(query, query2):
    print(f"Line {__line__()}: Starting navigate_to_target with query={query}, query2={query2}")
    
    if not EMAIL or not PASSWORD:
        print("CRITICAL ERROR: FANDOM_EMAIL and FANDOM_PASSWORD not found. Please check your .env file.")
        return None, None, None

    options = Options()
    print(f"Line {__line__()}: Setting Chrome options")
    # options.add_argument('--headless')  # Comment out for debugging
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--enable-unsafe-swiftshader')
    # Add user-agent to mimic a real browser
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    print(f"Line {__line__()}: Initializing Chrome driver")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Navigate to login page
        print(f"Line {__line__()}: Navigating to Fandom login page")
        driver.get('https://auth.fandom.com/signin?source=signin&metadata=&redirect=https%3A%2F%2Fauth.fandom.com%2Fauth%2Fredirect%3Fredirect%3Dhttps%25253A%25252F%25252Fwww.fandom.com%25252F%26metadata%3D%26redirected_from%3Dsignin%26source%3Dmw')
        time.sleep(random.uniform(2, 4))  # Random delay to mimic human behavior

        # Wait for email input field
        print(f"Line {__line__()}: Waiting for email input")
        email_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='identifier'][data-test='signin-username-field']"))
        )
        print(f"Line {__line__()}: Sending email")
        email_input.clear()  # Clear any pre-filled value
        email_input.send_keys(EMAIL)
        time.sleep(random.uniform(0.5, 1.5))  # Small delay for typing

        # Wait for password input field
        print(f"Line {__line__()}: Waiting for password input")
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password'][data-test='signin-password-field']"))
        )
        print(f"Line {__line__()}: Sending password")
        password_input.send_keys(PASSWORD)
        time.sleep(random.uniform(0.5, 1.5))

        # Submit the login form
        print(f"Line {__line__()}: Submitting login form")
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='signin-password-submit']"))
        )
        driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(random.uniform(3, 5))  # Wait for login to process and redirect

        # Verify login success by checking for redirect
        print(f"Line {__line__()}: Verifying login")
        WebDriverWait(driver, 10).until(
            EC.url_contains("www.fandom.com")  # Adjust based on redirect URL
        )
        print(f"Line {__line__()}: Login successful, proceeding to search")

        # Proceed to search
        print(f"Line {__line__()}: Navigating to Fandom search")
        driver.get('https://www.fandom.com')
        time.sleep(random.uniform(2, 4))
        print(f"Line {__line__()}: Waiting for search box")
        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='query'], input[placeholder*='Search']"))
        )
        print(f"Line {__line__()}: Sending query to search box")
        search_box.send_keys(query)
        time.sleep(random.uniform(0.5, 1.5))
        search_box.send_keys(Keys.RETURN)
        
        print(f"Line {__line__()}: Waiting for wiki links")
        wiki_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='.fandom.com']"))
        )
        print(f"Line {__line__()}: Selecting wiki link")
        target_url = None
        query_lower = query.lower().replace(" ", "")
        for link in wiki_links:
            href = link.get_attribute('href')
            text = link.text.lower()
            if re.search(query_lower, href.lower()) or 'wiki' in text:
                target_url = href
                break
        if not target_url and wiki_links:
            target_url = wiki_links[0].get_attribute('href')
        if not target_url:
            raise Exception("No relevant wiki found")
        print(f"Line {__line__()}: Target URL: {target_url}")
        driver.get(target_url)
        time.sleep(random.uniform(2, 4))
        
        print(f"Line {__line__()}: Waiting for wiki search box")
        try:
            wiki_search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-app__input, input[type='search'], input[type='text']"))
            )
        except:
            print(f"Line {__line__()}: Fallback to generic text input")
            wiki_search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
        print(f"Line {__line__()}: Sending query2 to wiki search box")
        wiki_search_box.send_keys(query2)
        time.sleep(random.uniform(0.5, 1.5))
        wiki_search_box.send_keys(Keys.RETURN)
        time.sleep(random.uniform(2, 4))
        
        print(f"Line {__line__()}: Waiting for first search result")
        try:
            first_result = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.unified-search__result__title"))
            )
        except:
            print(f"Line {__line__()}: Fallback to generic wiki link")
            first_result = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "main a[href*='/wiki/']"))
            )
        result_url = first_result.get_attribute('href')
        print(f"Line {__line__()}: Navigating to result URL: {result_url}")
        driver.get(result_url)
        time.sleep(random.uniform(2, 4))
        
        print(f"Line {__line__()}: Expanding buttons")
        expandable_elements = driver.find_elements(By.CSS_SELECTOR, 'main button, main [role="button"], main a[data-tracking-label="expand"], main .mw-collapsible-toggle, main .navbox-title, main [data-expandtext], main [data-toggle]')
        if expandable_elements:
            for element in expandable_elements:
                try:
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(random.uniform(0.1, 0.3))
                except:
                    pass
        
        print(f"Line {__line__()}: Extracting main content")
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        main_content = soup.find('main')
        content_html = str(main_content) if main_content else html
        title_elem = soup.find('h1') or soup.find('title')
        title = title_elem.get_text().strip() if title_elem else 'page'
        title = re.sub(r'[^\w\s-]', '_', title)
        title = re.sub(r'\s+', '_', title).strip('_')
        
        print(f"Line {__line__()}: Saving HTML with title: {title}")
        game_folder = re.sub(r'[^\w\s-]', '_', query).strip()
        game_folder = re.sub(r'\s+', '_', game_folder).strip('_')
        game_dir = os.path.join(RAW_DATA_DIR, game_folder)
        os.makedirs(game_dir, exist_ok=True)
        file_path = os.path.join(game_dir, f'{title}.html')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_html)
        print(f"Line {__line__()}: HTML saved at {file_path}")
        return result_url, content_html, file_path
    except Exception as e:
        print(f"Line {__line__()}: Error: {e}")
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        driver.save_screenshot('debug.png')
        return None, None, None
    finally:
        print(f"Line {__line__()}: Closing driver")
        driver.quit()

def __line__():
    import inspect
    return inspect.currentframe().f_back.f_lineno