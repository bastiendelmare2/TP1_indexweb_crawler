
import requests
import logging

def validate_url(url):
    """Validate if the URL is reachable and returns a valid response."""
    try:
        # Effectuer une requête GET pour vérifier l'URL
        response = requests.get(url, allow_redirects=True, timeout=10)
        if 200 <= response.status_code < 300:
            return True
        else:
            logging.error(f"URL validation failed. Status code: {response.status_code} for {url}")
            return False
    except requests.RequestException as e:
        logging.error(f"URL validation error: {e}")
        return False

# Example
if __name__ == "__main__":
    url = "https://example.com"
    is_valid = validate_url(url)
    print(is_valid)  # Output: True or False depending on URL reachability