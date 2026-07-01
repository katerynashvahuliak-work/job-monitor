import logging
import time
import httpx

logger = logging.getLogger(__name__)

JINA_BASE = "https://r.jina.ai/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; JobMonitorBot/1.0)",
    "Accept": "text/plain",
}


HTML_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "uk,en;q=0.9",
}


def fetch_page(url: str) -> str:
    jina_url = JINA_BASE + url
    response = httpx.get(jina_url, headers=HEADERS, timeout=30, follow_redirects=True)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error("HTTP error fetching %s: %s", url, e)
        raise
    finally:
        time.sleep(2)
    return response.text


def fetch_html(url: str) -> str:
    response = httpx.get(url, headers=HTML_HEADERS, timeout=15, follow_redirects=True)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error("HTTP error fetching %s: %s", url, e)
        raise
    finally:
        time.sleep(2)
    return response.text
