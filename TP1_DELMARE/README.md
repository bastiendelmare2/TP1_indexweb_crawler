# WebCrawler 🕸️

This project is a web crawler designed to automatically browse websites, extract specific information (such as the title, the first paragraph, and links), and save this data into a JSON file. The crawler respects the rules defined in the `robots.txt` file of visited sites and includes features like politeness delay and multithreading for performance optimization.

## Features 🌟

- **Respect for `robots.txt` rules**: The crawler checks permissions before accessing a page.
- **Data extraction**: The crawler extracts the title, the first paragraph, and links from each visited page.
- **Multithreading**: The crawler can use multiple threads to speed up the crawling process.
- **Politeness delay**: A configurable delay is enforced between requests to avoid overloading servers.
- **Data saving**: Extracted data is saved into a JSON file, named according the starting URL.
- **Test URL** : Chekc if the URL in the input is valid.

### Utility Files  🛠️

- **`filenamesanatatizer.py`**: This utility module provides the `sanitize_filename` function, which transforms a given URL into a valid filename. It removes the protocol (`http://` or `https://`), replaces non-alphanumeric characters with underscores, and trims trailing underscores. This is used in `main.py` to generate safe and unique filenames for output files based on URLs.

- **`pagedownloader.py`**: This module contains the `download_page` function, which fetches the HTML content of a given URL. If the URL is reachable, it returns the page content as a decoded string. Otherwise, it gracefully handles errors and returns `None`. This functionality is crucial for extracting and processing data from web pages.

- **`validurl.py`**: This module includes the `validate_url` function, which ensures that a given URL is reachable and returns a valid response (status codes 200–299). It is integrated into `main.py` to validate the base URL before starting the crawling process, preventing unnecessary errors during execution.


## Usage

### Prerequisites

- Python 3.x
- The following libraries must be installed:
  - `requests`
  - `beautifulsoup4`
  - `sqlite3`

### Execution 🎯

To execute the webcrawler, here is the command line to input :

```bash

python main.py -b <base_url> -m <max_urls> -t <n_threads> -p <politeness_delay> -o <output_path>

```

### Parameters 🔧
- `-b` or `--base_url`: Starting URL for crawling (default: `https://web-scraping.dev/products`).
- `-m` or `--max_urls`: Maximum number of URLs to crawl (default: `5`).
- `-t` or `--n_threads`: Number of threads to use (default: `5`).
- `-p` or `--politeness_delay`: Politeness delay in seconds between requests (default: `5`).
- `-o` or `--output_path`: Path to the output JSON file (default: `output/crawled_data.json`).

### Example 📋
To crawl 10 URLs starting from `https://web-scraping.dev/products` with 3 threads and a politeness delay of 3 seconds, use the appropriate command.

```bash

python crawler.py -b https://web-scraping.dev/products -m 10 -t 3 -p 3 -o output/crawled_data.json

```

## Project Structure 🏗️

- `main.py`: Entry point of the program, handles command-line arguments and launches the crawler.
- `webcrawler.py`: Contains the WebCrawler class that implements the crawling logic.
- `utils/filenamesanitizer.py`: Utility module for sanitizing URLs into valid filenames.
- `utils/pagedownloader.py`: Utility module for downloading web page content.
- `utils/validurl.py`: Utility module for validating the reachability of URLs.
- `output/`: Folder containing output files (JSON and logs).
- `test.py`: Script to test the web crawler with various configurations.

## Testing  🧪

The `test.py` script runs the crawler with different configurations and tests the ability of the program to handle valid and invalid URLs.

### Test Cases

1. **Test 1: Valid URL (Quotes Scraper)**  
   - Base URL: `https://quotes.toscrape.com`
   - Expected result: A JSON file containing crawled data (`output/test_crawled_data_quotes.json`) is generated.

2. **Test 2: Valid URL (Books Scraper)**  
   - Base URL: `https://books.toscrape.com`
   - Expected result: A JSON file containing crawled data is generated, and the output file will be saved as `output/test_crawled_data_books_toscrape_com.json` (since the output path is not provided, it will be automatically generated).

3. **Test 3: Invalid URL (Non-existent URL)**  
   - Base URL: `https://thisurldoesnotexist12345.com`  
   - Expected result: The URL is not reachable, and an error message will be displayed in the terminal:
     ```
     ERROR:root:URL validation error: HTTPSConnectionPool(host='thisurldoesnotexist12345.com', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("<urllib3.connection.HTTPSConnection object at 0x7e10638d0800>: Failed to resolve 'thisurldoesnotexist12345.com' ([Errno -2] Name or service not known)"))
     ```
     No output JSON file will be generated for this test.
    
- These are **not unit tests** but rather **usage examples** to demonstrate how the crawler can be used with different configurations.
- The `test.py` script serves as a way to verify the crawler's ability to handle different types of URLs, including invalid ones, and ensure it generates the expected output files or error messages.


## Output Files  📂

- `crawled_data.json`: Contains the extracted data in JSON format.
- `test_crawled_data_books.toscrape.com` : Example of output for another URL.
- `test_crawled_data_quotes` : Same idea as previous one.
- `logs.log`: Contains logs of the crawling process.
