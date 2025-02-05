import argparse
import os
from webcrawler import WebCrawler
from utils.validurl import validate_url
from utils.filenamesanatizer import sanitize_filename


# Parsing the command-line arguments
parser = argparse.ArgumentParser(description="Web Crawler")
parser.add_argument("-m", "--max_urls", type=int, default=50, help="Maximum number of URLs to crawl")
parser.add_argument("-b", "--base_url", type=str, default="https://web-scraping.dev/products", help="Base URL to start crawling from")
parser.add_argument("-o", "--output_path", type=str, help="Path to the JSON output file (optional, auto-generated if not provided)")
parser.add_argument("-t", "--n_threads", type=int, default=5, help="Number of threads to use")
parser.add_argument("-p", "--politeness_delay", type=int, default=5, help="Politeness delay in seconds")
args = parser.parse_args()

# Validate the base URL
if not validate_url(args.base_url):
    print(f"Invalid or unreachable base URL: {args.base_url}")
    exit(1)

# Generate the output path if not provided
if args.output_path is None:
    sanitized_name = sanitize_filename(args.base_url)
    args.output_path = f"output/crawled_data_{sanitized_name}.json"

# Ensure the output directory exists
os.makedirs(os.path.dirname(args.output_path), exist_ok=True)

# Create an instance of the WebCrawler class and start crawling
print(f"Starting crawl for base URL: {args.base_url}")
web_crawler = WebCrawler(
    args.base_url, 
    max_urls=args.max_urls, 
    n_threads=args.n_threads,
    politeness_delay=args.politeness_delay
)
web_crawler.crawl()

# Save the crawled data to a JSON file
print(f"Saving crawled data to {args.output_path}")
web_crawler.save_crawled_data(args.output_path)
