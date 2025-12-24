import requests
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from url_utils import normalize_url

def get_sitemap_urls(site):
    sitemap = urljoin(site, "/sitemap.xml")
    urls = []

    try:
        r = requests.get(sitemap, timeout=10)
        soup = BeautifulSoup(r.text, "xml")
        for loc in soup.find_all("loc"):
            urls.append(normalize_url(loc.text))
    except:
        pass

    return list(set(urls))

def crawl_pages(site, limit=100):
    domain = urlparse(site).netloc
    visited = set()
    pages = []

    def crawl(url):
        if url in visited or len(visited) >= limit:
            return
        visited.add(url)

        try:
            # Rate-limiting: random delay 0.5-2 seconds between requests
            time.sleep(random.uniform(0.5, 2.0))
            
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "lxml")

            pages.append({
                "url": url,
                "html": r.text
            })

            for a in soup.select("a[href]"):
                link = normalize_url(urljoin(url, a["href"]))
                if urlparse(link).netloc == domain:
                    crawl(link)
        except:
            pass

    crawl(site)
    return pages

