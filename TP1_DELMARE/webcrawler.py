import time
from bs4 import BeautifulSoup
from threading import Thread
from urllib import robotparser, error, parse
from queue import PriorityQueue
import json
from utils.pagedownloader import download_page


class WebCrawler:
    def __init__(self, base_url, max_urls=50, n_threads=1, politeness_delay=3, max_url_per_page=5):
        self.base_url = base_url
        self.max_urls = max_urls
        self.visited_urls = set()  # Utilisation d'un set pour les URL visitées
        self.urls_to_crawl = PriorityQueue()
        self.urls_to_crawl.put((0, base_url))
        self.visited_sitemaps = set()
        self.n_threads = n_threads
        self.robots_parsers = {}
        self.politeness_delay = politeness_delay
        self.max_url_per_page = max_url_per_page
        self.crawled_data = [] 

    def can_parse_url(self, url):
        robots_url = parse.urljoin(url, "/robots.txt")
        if robots_url in self.robots_parsers:
            rp = self.robots_parsers[robots_url]
        else:
            rp = robotparser.RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
                self.robots_parsers[robots_url] = rp
            except error.URLError:
                return True  # Assume parsing is allowed if robots.txt is inaccessible.
        return rp.can_fetch("*", url)

    def parse_html_content(self, url, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        title = soup.title.string.strip() if soup.title else "No Title"
        first_paragraph = soup.find('p').text.strip() if soup.find('p') else "No First Paragraph"
        links = [
            a_tag['href'] if a_tag['href'].startswith("http") else parse.urljoin(url, a_tag['href'])
            for a_tag in soup.find_all('a', href=True)
        ]

        return {
            "url": url,
            "title": title,
            "first_paragraph": first_paragraph,
            "links": links
        }

    def add_url_to_crawl(self, url):
        # Normaliser l'URL pour éviter les doublons
        normalized_url = parse.urljoin(self.base_url, url)

        # Assurez-vous que l'URL n'est ni déjà visitée ni déjà dans la queue de crawl
        if normalized_url not in self.visited_urls and normalized_url not in [u[1] for u in self.urls_to_crawl.queue]:
            priority = 0 if 'product' in url else 1
            self.urls_to_crawl.put((priority, normalized_url))

    def process_page(self, current_url):
        if not self.can_parse_url(current_url):
            return

        html_content = download_page(current_url)
        if html_content:
            parsed_data = self.parse_html_content(current_url, html_content)
            self.crawled_data.append(parsed_data)

            for link in parsed_data["links"]:
                if link not in self.visited_urls:
                    self.add_url_to_crawl(link)

            # Mise à jour de visited_urls pour inclure l'URL visité
            self.visited_urls.add(current_url)

            # Retirer l'URL des liens à explorer
            self.urls_to_crawl.queue = [item for item in self.urls_to_crawl.queue if item[1] != current_url]

    def crawl(self):
        while not self.urls_to_crawl.empty() and len(self.visited_urls) < self.max_urls:
            n_current_threads = min(self.n_threads, self.urls_to_crawl.qsize())
            n_current_threads = min(n_current_threads, self.max_urls - len(self.visited_urls))

            current_urls = [self.urls_to_crawl.get()[1] for _ in range(n_current_threads)]
            threads = [Thread(target=self.process_page, args=(current_url,)) for current_url in current_urls]

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            time.sleep(self.politeness_delay)

    def save_crawled_data(self, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.crawled_data, f, indent=4, ensure_ascii=False)


# Example usage
if __name__ == '__main__':
    example_base_url = "https://web-scraping.dev/products"
    web_crawler = WebCrawler(example_base_url, max_urls=10)
    web_crawler.crawl()
    web_crawler.save_crawled_data("output/crawled_data.json")
