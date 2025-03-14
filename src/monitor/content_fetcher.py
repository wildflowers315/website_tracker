import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from typing import Dict, Optional, Tuple
from ..utils.logger import Logger
from tenacity import retry, stop_after_attempt, wait_exponential

logger = Logger.get_logger()

class ContentFetcher:
    def __init__(self, headers: Optional[Dict[str, str]] = None):
        """Initialize the content fetcher.
        
        Args:
            headers: Optional custom headers for requests
        """
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self._last_request_time: Dict[str, float] = {}
        self._min_request_interval = 1.0  # Minimum seconds between requests to same domain
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def fetch_content(self, url: str, selectors: list) -> Tuple[str, datetime]:
        """Fetch and extract content from a website.
        
        Args:
            url: Website URL
            selectors: List of CSS selectors to extract content from
            
        Returns:
            Tuple[str, datetime]: Extracted content and timestamp
            
        Raises:
            requests.RequestException: If request fails after retries
        """
        self._respect_rate_limit(url)
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            content = []
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    # Remove script and style elements
                    for script in element.find_all(['script', 'style']):
                        script.decompose()
                    # Get text and normalize whitespace
                    text = ' '.join(element.get_text().split())
                    if text:
                        content.append(text)
            
            timestamp = datetime.now()
            return '\n'.join(content), timestamp
            
        except requests.RequestException as e:
            logger.error(f"Error fetching content from {url}: {str(e)}")
            raise
    
    def _respect_rate_limit(self, url: str) -> None:
        """Ensure we don't exceed rate limits for a domain.
        
        Args:
            url: Website URL
        """
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        current_time = time.time()
        if domain in self._last_request_time:
            elapsed = current_time - self._last_request_time[domain]
            if elapsed < self._min_request_interval:
                time.sleep(self._min_request_interval - elapsed)
        
        self._last_request_time[domain] = time.time()
    
    def close(self) -> None:
        """Close the requests session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager enter."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()