from urllib import request, error

def download_page(url):
    """
    Downloads the HTML content of a web page.
    """
    try:
        # Sending a request to the URL
        response = request.urlopen(url)
        
        # Reading and decoding the HTML content
        return response.read().decode('utf-8')

    except:
        # Return None if any error occurs
        return None

# Example usage
if __name__ == '__main__':
    # Example URL to download
    example_url = "https://ensai.fr"
    example_html = download_page(example_url)
    print(example_html[:1000])