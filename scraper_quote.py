from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def scrape_quotes():
    # Chrome options for headful mode
    chrome_options = Options()
    # Remove headless mode to run in headful
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the page
        driver.get('https://quotes.toscrape.com/')
        time.sleep(2)  # Wait for page to load
        
        # Find all quote containers
        quotes = driver.find_elements(By.CLASS_NAME, 'quote')
        
        print(f"Found {len(quotes)} quotes\n")
        
        # Extract data from each quote
        for i, quote in enumerate(quotes, 1):
            text = quote.find_element(By.CLASS_NAME, 'text').text
            author = quote.find_element(By.CLASS_NAME, 'author').text
            tags = [tag.text for tag in quote.find_elements(By.CLASS_NAME, 'tag')]
            
            print(f"Quote {i}:")
            print(f"Text: {text}")
            print(f"Author: {author}")
            print(f"Tags: {', '.join(tags)}")
            print("-" * 80)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_quotes()