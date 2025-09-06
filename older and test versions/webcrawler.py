#libraries needed, mostly specified by this tutorial: https://platform.openai.com/docs/tutorials/web-qa-embeddings
import certifi #except this one, used to certify python, for troubleshooting
import requests
import re
import urllib.request
from bs4 import BeautifulSoup #for getting the text content out of websites
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os #for creating directories and files
import hashlib #to better encode website page names so they fit into OS naming conventions
from pydantic_core.core_schema import none_schema

# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^http[s]*://.+'

#url name
domain = "leuphana.de"
full_url = "https://www.leuphana.de/"

#because the urls gave me so many errors
def safe_filename(url):
    parsed = urlparse(url)  #parsing the url name
    base = os.path.basename(parsed.path)   #looking up the end of its directory path ("text/01230/../example.txt")
    if not base:    #if the path ends with "/" or is empty, call the file index by default
        base = "index"
        # Replace all characters that are not letters, numbers, dots, underscores, or dashes with "_" to make it more readable:
    base = "".join(c if c.isalnum() or c in "._-" else "_" for c in base)
    #if filename still longer than 50 characters, cut it down
    if len(base) > 50:
        base = base[:50]
# Create an 8-character hash out of  full URL (otherwise too long)
    hash_part = hashlib.md5(url.encode('utf-8')).hexdigest()[:8]
    #return cleaned filename
    return f"{base}_{hash_part}.txt"

##The following classes are from the aforementioned tutorial

# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has a href attribute, add the href attribute to the list of hyperlinks
        if tag == 'a' and 'href' in attrs:
            self.hyperlinks.append(attrs['href'])

def get_hyperlinks(url):
    # Try to open the URL and read the HTML
    try:
        # Open the URL and read the HTML
        with urllib.request.urlopen(url) as response:

            # If the response is not HTML, return an empty list
            if not response.info().get('Content-Type').startswith("text/html"):
                return []

            # Decode the HTML
            html = response.read().decode('utf-8')
    except Exception as e:
        print(e)
        return []

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks

def get_domain_hyperlinks(local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks(url)):
        clean_link = None

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif link.startswith("#") or link.startswith("mailto:"):
                continue
            clean_link = "https://" + local_domain + "/" + link

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

        # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))

#main crawl function
def crawl(url):
    local_domain = urlparse(url).netloc
    queue = deque([url])
    seen = set([url])

    os.makedirs(f"text/{local_domain}", exist_ok=True)
    os.makedirs("../processed", exist_ok=True)

    while queue:
        url = queue.pop()
        print(url)


        filename = safe_filename(url)
        filepath = f"text/{local_domain}/{filename}"


        if os.path.exists(filepath):
            print(f"File {filepath} already exists, skipping.")
            continue

        try:
            response = requests.get(url, verify=certifi.where())
            content_type = response.headers.get('Content-Type', '')


            if 'text/html' not in content_type:
                print(f"Skipping non-HTML content at {url}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()

            if "You need to enable JavaScript to run this app." in text:
                print(f"Unable to parse page {url} due to JavaScript requirement.")
                continue

            with open(filepath, "w", encoding="UTF-8") as f:
                f.write(text)

        except Exception as e:
            print(f"Error while parsing {url}: {e}")
            continue

        for link in get_domain_hyperlinks(local_domain, url):
            if link not in seen:
                queue.append(link)
                seen.add(link)

crawl(full_url)
