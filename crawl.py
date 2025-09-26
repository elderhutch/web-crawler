from urllib.parse import urlparse, urljoin
import urllib.parse
import requests
from bs4 import BeautifulSoup

''' html = """<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><h1><b>The Dormouse's story</b></h1></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""
'''

def normalize_url(url):
    parsed_url = urlparse(url)
    full_path = f"{parsed_url.netloc}{parsed_url.path}"
    full_path = full_path.rstrip("/")
    return full_path.lower()

def get_h1_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.h1.string if soup.h1 else ""

def get_first_paragraph_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    if not soup.main:
        return soup.p.string if soup.p else ""
    return soup.main.p.string if soup.main.p else ""

def get_urls_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        links.add(urllib.parse.urljoin(base_url, link['href']))
    return sorted(list(links)) if links else []

def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    images = set()
    for img in soup.find_all('img', src=True):
        images.add(urllib.parse.urljoin(base_url, img['src']))
    return sorted(list(images)) if images else []

def extract_page_data(html, page_url):
    return {
        "url": page_url,
        "h1": get_h1_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url)
        
    }

def get_html(url):
    try:
        response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error: Received status code {response.status_code} for URL: {url}")
            return None
    except requests.RequestException as e:
        print(f"Error: An exception occurred while trying to fetch the URL: {url}\n{e}")
        return None

def crawl_page(base_url, current_url=None, page_data=None):
    if page_data is None:
        page_data = {}
    if current_url is None:
        current_url = base_url

    if normalize_url(current_url) in page_data:
        return page_data

    print(f"Crawling: {current_url}")
    html = get_html(current_url)
    if html is None:
        return page_data

    data = extract_page_data(html, current_url)
    page_data[normalize_url(current_url)] = data

    for link in data["outgoing_links"]:
        if normalize_url(link).startswith(normalize_url(base_url)):
            crawl_page(base_url, link, page_data)

    return page_data
