# Web Scraper with AI Content Extraction

This project implements an intelligent web scraper that not only collects data from websites but also uses AI to extract and summarize meaningful content. It's designed with anti-detection measures and respects website crawling policies.

## Features

- **Smart Web Scraping**: Uses Playwright for dynamic website rendering and content extraction
- **Anti-Detection Measures**:
  - Random user agent rotation
  - Randomized mouse movements and scrolling
  - Configurable wait times between requests
  - Custom HTTP headers
- **Content Processing**:
  - Structured extraction of headings, paragraphs, lists, and tables
  - Markdown formatting of extracted content
  - AI-powered content summarization using Google's Gemini AI
- **Error Handling**:
  - Automatic retry mechanism for failed requests
  - Comprehensive error logging

## Requirements

```
playwright
beautifulsoup4
google-generativeai
python-dotenv
fake-useragent
```

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root and add your Gemini API key:
   ```
   GEMINI_KEY=your_api_key_here
   ```

## Usage

The scraper can be run directly from the command line:

```bash
python main.py
```

By default, it will scrape the sample URLs included in the script. To scrape different URLs, modify the `sample_urls` list in the `main.py` file.

## How It Works

1. **Web Scraping (`scrape_url` function)**:
   - Initializes a browser session with randomized user agent
   - Performs human-like interactions (mouse movements, scrolling)
   - Extracts content and converts it to markdown format
   - Saves raw content to dated files

2. **Content Processing (`extract_meaningful_text` function)**:
   - Uses Gemini AI to analyze and extract meaningful content
   - Summarizes content if it exceeds 4000 words
   - Saves processed content to separate files

3. **Output Structure**:
   ```
   data/
   ├── domain_name/
   │   ├── DD-MM-YYYY.md           # Raw scraped content
   │   └── distilled_DD-MM-YYYY.md # AI-processed content
   ```

## Anti-Detection Features

- Random wait times between requests (5-15 seconds)
- 3-8 random mouse movements per page
- Randomized scrolling behavior
- Custom HTTP headers including:
  - User-Agent rotation
  - Accept headers
  - DNT (Do Not Track)
  - Sec-Fetch parameters

## Error Handling

The scraper includes a retry mechanism that:
- Attempts each URL up to 3 times
- Implements exponential backoff between retries
- Logs all errors with detailed information

## Limitations

- Requires a valid Gemini API key
- Some websites may block automated access
- Processing very large pages may require additional memory

## Contributing

Feel free to submit issues and enhancement requests!
