import logging
from webcrawler import WebCrawler
import os
from utils.validurl import validate_url
from utils.filenamesanatizer import sanitize_filename

# Testing configurations
test_configurations = [
    {
        "base_url": "https://quotes.toscrape.com",
        "max_urls": 15,
        "n_threads": 5,
        "politeness_delay": 1,
        "output_path": "output/test_crawled_data_quotes.json",
    },
    {
        "base_url": "https://books.toscrape.com",
        "max_urls": 20,
        "n_threads": 4,
        "politeness_delay": 3,
        "output_path": None,
    },
    {
        "base_url": "https://thisurldoesnotexist12345.com",  # URL qui n'existe pas
        "max_urls": 10,
        "n_threads": 2,
        "politeness_delay": 2,
        "output_path": "output/test_crawled_data_invalid_url.json",
    }
]

for idx, config in enumerate(test_configurations):
    # Validate the base URL
    if not validate_url(config["base_url"]):
        logging.error(f"Invalid or unreachable base URL: {config['base_url']}")
        continue

    # Generate the output path if not provided
    if config["output_path"] is None:
        sanitized_name = sanitize_filename(config["base_url"])
        config["output_path"] = f"output/test_crawled_data_{sanitized_name}.json"

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(config["output_path"]), exist_ok=True)

    web_crawler = WebCrawler(
        config["base_url"],
        max_urls=config["max_urls"],
        n_threads=config["n_threads"],
        politeness_delay=config["politeness_delay"]
    )
    web_crawler.crawl()

    # Save the crawled data to a JSON file
    logging.info(f"Saving crawled data to {config['output_path']}")
    web_crawler.save_crawled_data(config["output_path"])

    print(f"Test {idx + 1} completed for base URL: {config['base_url']}. Data saved to {config['output_path']}. ")
