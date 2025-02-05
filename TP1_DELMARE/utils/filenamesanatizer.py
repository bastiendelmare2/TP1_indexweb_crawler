import re

def sanitize_filename(url):
    """Sanitize the URL to create a valid filename."""
    # Remove 'http://' or 'https://'
    url = re.sub(r"^https?://", "", url)
    # Replace non-alphanumeric characters with underscores
    sanitized = re.sub(r"[^\w\-_.]", "_", url)
    # Remove trailing underscores
    sanitized = re.sub(r"_+$", "", sanitized)
    return sanitized

# Example
if __name__ == "__main__":
    url = "https://example.com/path/to/page/"
    filename = sanitize_filename(url)
    print(filename)  # Output: example_com_path_to_page