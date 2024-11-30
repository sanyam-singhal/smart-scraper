from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time
import google.generativeai as genai
import os
from dotenv import load_dotenv
import datetime
from fake_useragent import UserAgent
import random
import pandas as pd

# Initial Setup
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_KEY"))
today_date=datetime.date.today().strftime("%d-%m-%Y")

ua = UserAgent()
random_wait_low=5
random_wait_high=15

random_moves_low=3
random_moves_high=8

extract_instructions="""
You are given the markdown format of a webpage.

Your task is to extract and organize meaningful text from the webpage.
The text should be in a markdown format.

Do not include any other text in your response.

If the content length exceeds 4000 words, then you should summarize the content and extract the most important points.
"""

def perform_random_mouse_movements(page):
    # Generate random number of mouse movements
    num_movements = random.randint(random_moves_low, random_moves_high)
    page_width = page.viewport_size['width']
    page_height = page.viewport_size['height']
    
    for _ in range(num_movements):
        # Generate random coordinates within viewport
        x = random.randint(0, page_width)
        y = random.randint(0, page_height)

        page.mouse.wheel(delta_x=0, delta_y=random.randint(-800, 800))
        
        # Random speed between 1000-3000 milliseconds
        duration = random.randint(1000, 3000)
        
        # Move mouse with random timing
        page.mouse.move(x, y, steps=duration//100)  # steps create a smoother movement
        time.sleep(random.uniform(0.5, 2))

def scrape_url(url: str, storage_path: str, num_retries: int = 3):
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    
    for attempt in range(num_retries):
        try:
            extra_headers={
                'sec-ch-ua': '\'Not A(Brand\';v=\'99\', \'Google Chrome\';v=\'121\', \'Chromium\';v=\'121\'',
                'User-Agent': ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',  # Do Not Track
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            }
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_extra_http_headers(extra_headers)
                page.goto(url)
                
                # Wait for the content to be fully loaded
                page.wait_for_load_state('networkidle')
                page.wait_for_load_state('domcontentloaded')
                
                perform_random_mouse_movements(page)
                
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(random.uniform(1.5, 4))
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Extract content with structure
                content = []
                for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table']):
                    if element.name.startswith('h'):
                        heading_level = element.name[1]  # get the heading level number
                        content.append(f"\n{'#' * int(heading_level)} {element.get_text().strip()}\n")
                    
                    elif element.name == 'ul':
                        content.append("\n")  # Add spacing before list
                        for li in element.find_all('li', recursive=False):
                            content.append(f"* {li.get_text().strip()}\n")
                        content.append("\n")  # Add spacing after list
                    
                    elif element.name == 'ol':
                        content.append("\n")  # Add spacing before list
                        for i, li in enumerate(element.find_all('li', recursive=False), 1):
                            content.append(f"{i}. {li.get_text().strip()}\n")
                        content.append("\n")  # Add spacing after list
                    
                    elif element.name == 'table':
                        content.append("\n")  # Add spacing before table
                        # Process table headers
                        headers = []
                        header_row = element.find('thead')
                        if header_row:
                            headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]
                        else:
                            # If no thead, use first row as header
                            first_row = element.find('tr')
                            if first_row:
                                headers = [th.get_text().strip() for th in first_row.find_all(['th', 'td'])]
                        
                        if headers:
                            # Add header row
                            content.append('| ' + ' | '.join(headers) + ' |\n')
                            # Add markdown separator
                            content.append('| ' + ' | '.join(['---'] * len(headers)) + ' |\n')
                            
                            # Process table rows
                            for row in element.find_all('tr')[1:] if header_row else element.find_all('tr')[1:]:
                                cols = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
                                if cols:  # Only add non-empty rows
                                    content.append('| ' + ' | '.join(cols) + ' |\n')
                        content.append("\n")  # Add spacing after table
                    
                    else:
                        # For paragraphs, preserve the text
                        text = element.get_text().strip()
                        if text:  # Only add non-empty paragraphs
                            content.append(f"{text}\n\n")
                
                # Join all content with proper spacing
                text = '\n'.join(content)
                
                with open(f'{storage_path}/{today_date}.md', 'a') as f:
                    f.write(text)

                time.sleep(random.uniform(random_wait_low, random_wait_high))

                print(f"Successfully scraped {url} on attempt {attempt + 1}")

                return text  # Exit the retry loop
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
            if attempt == num_retries - 1:  # If this was the last attempt
                print(f"Failed to scrape {url} after {num_retries} attempts")
                raise  # Re-raise the last exception
            time.sleep(random.uniform(2, 5))  # Wait before retrying

    return None

def extract_meaningful_text(text,storage_path):
    model=genai.GenerativeModel(
        model_name="gemini-1.5-flash-002",
        system_instruction=extract_instructions
    )
    try:
        result = model.generate_content(text)
        with open(f'{storage_path}/distilled_{today_date}.md', 'w',encoding='utf-8') as f:
            f.write(result.text)

    except Exception as e:
        print(f"Failed to extract meaningful text: {str(e)}")

if __name__ == "__main__":
    sample_urls=[
        'https://www.theguardian.com/uk',
        'https://github.com/fake-useragent/fake-useragent'
    ]
    for url in sample_urls:
        storage_path=f"data/{url.split('//')[-1].replace('/', '-').replace('.', '_')}"
        text=scrape_url(url, storage_path)
        if text:
            extract_meaningful_text(text,storage_path)