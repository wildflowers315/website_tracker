from datetime import datetime, timedelta
from typing import Dict, Optional
import threading
from ..utils.logger import Logger

logger = Logger.get_logger()

class RateLimiter:
    def __init__(self, requests_per_minute: int = 30):
        """Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum number of requests per minute per domain
        """
        self.requests_per_minute = requests_per_minute
        self.domain_requests: Dict[str, list] = {}
        self._lock = threading.Lock()
    
    def add_request(self, domain: str) -> None:
        """Record a request for a domain.
        
        Args:
            domain: Domain name
        """
        with self._lock:
            now = datetime.now()
            if domain not in self.domain_requests:
                self.domain_requests[domain] = []
            
            # Add current request
            self.domain_requests[domain].append(now)
            
            # Clean up old requests
            self._cleanup_old_requests(domain)
    
    def can_request(self, domain: str) -> bool:
        """Check if a request can be made to a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            bool: True if request is allowed, False otherwise
        """
        with self._lock:
            if domain not in self.domain_requests:
                return True
            
            self._cleanup_old_requests(domain)
            return len(self.domain_requests[domain]) < self.requests_per_minute
    
    def wait_time(self, domain: str) -> Optional[float]:
        """Get time to wait before next request is allowed.
        
        Args:
            domain: Domain name
            
        Returns:
            Optional[float]: Seconds to wait, or None if no wait needed
        """
        with self._lock:
            if self.can_request(domain):
                return None
            
            oldest_allowed = datetime.now() - timedelta(minutes=1)
            next_available = self.domain_requests[domain][0] + timedelta(minutes=1)
            
            if next_available > datetime.now():
                return (next_available - datetime.now()).total_seconds()
            return None
    
    def _cleanup_old_requests(self, domain: str) -> None:
        """Remove requests older than 1 minute.
        
        Args:
            domain: Domain name
        """
        now = datetime.now()
        oldest_allowed = now - timedelta(minutes=1)
        
        self.domain_requests[domain] = [
            req for req in self.domain_requests[domain]
            if req > oldest_allowed
        ]
        
    def reset(self, domain: Optional[str] = None) -> None:
        """Reset rate limiter for a domain or all domains.
        
        Args:
            domain: Optional domain name. If None, resets all domains
        """
        with self._lock:
            if domain:
                self.domain_requests.pop(domain, None)
            else:
                self.domain_requests.clear()