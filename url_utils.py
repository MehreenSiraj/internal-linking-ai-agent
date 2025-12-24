from urllib.parse import urlparse, urlunparse

def normalize_url(url):
    p = urlparse(url)
    return urlunparse((
        p.scheme,
        p.netloc,
        p.path.rstrip("/") or "/",
        "", "", ""
    ))
