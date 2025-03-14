from datetime import datetime
import json
import os
from pathlib import Path
from typing import Dict, Optional, List, Any
from .content_fetcher import ContentFetcher
from .rate_limiter import RateLimiter
from ..utils.config import Config
from ..utils.logger import Logger

logger = Logger.get_logger()

class WebsiteMonitor:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize website monitor.
        
        Args:
            config_path: Optional path to config file
        """
        self.config = Config(config_path)
        self.content_fetcher = ContentFetcher()
        self.rate_limiter = RateLimiter()
        self.data_dir = Path('data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def start_monitoring(self) -> List[Dict[str, Any]]:
        """Start monitoring all configured websites.
        
        Returns:
            List[Dict[str, Any]]: List of changes detected
        """
        websites = self.config.get_websites()
        if not websites:
            logger.warning("No websites configured for monitoring")
            return []
        
        changes = []
        for website in websites:
            try:
                site_changes = self._check_website(website)
                if site_changes:
                    changes.append(site_changes)
            except Exception as e:
                logger.error(f"Error monitoring {website.get('name', 'Unknown')}: {str(e)}")
                continue
        
        return changes
    
    def _check_website(self, website: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check a single website for changes.
        
        Args:
            website: Website configuration
            
        Returns:
            Optional[Dict[str, Any]]: Changes detected, if any
        """
        name = website.get('name', 'Unknown')
        url = website.get('url')
        selectors = website.get('content', {}).get('selectors', [])
        
        if not url or not selectors:
            logger.error(f"Invalid configuration for website {name}")
            return None
        
        try:
            # Fetch current content
            content, timestamp = self.content_fetcher.fetch_content(url, selectors)
            
            # Load previous content
            previous_data = self._load_previous_content(name)
            
            # Save current content
            self._save_content(name, content, timestamp)
            
            # If no previous content, just save current and return
            if not previous_data:
                logger.info(f"Initial content saved for {name}")
                return None
            
            # Compare content and detect changes
            changes = self._detect_changes(
                name,
                previous_data['content'],
                content,
                previous_data['timestamp'],
                timestamp
            )
            
            return changes if changes['changes'] else None
            
        except Exception as e:
            logger.error(f"Error checking website {name}: {str(e)}")
            return None
    
    def _load_previous_content(self, website_name: str) -> Optional[Dict[str, Any]]:
        """Load previous content for a website.
        
        Args:
            website_name: Name of the website
            
        Returns:
            Optional[Dict[str, Any]]: Previous content data if exists
        """
        file_path = self.data_dir / f"{website_name.lower().replace(' ', '_')}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'content': data['content'],
                    'timestamp': datetime.fromisoformat(data['timestamp'])
                }
        except Exception as e:
            logger.error(f"Error loading previous content for {website_name}: {str(e)}")
            return None
    
    def _save_content(self, website_name: str, content: str, timestamp: datetime) -> None:
        """Save current content for a website.
        
        Args:
            website_name: Name of the website
            content: Current content
            timestamp: Current timestamp
        """
        file_path = self.data_dir / f"{website_name.lower().replace(' ', '_')}.json"
        try:
            data = {
                'content': content,
                'timestamp': timestamp.isoformat()
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving content for {website_name}: {str(e)}")
    
    def _detect_changes(
        self,
        website_name: str,
        previous_content: str,
        current_content: str,
        previous_timestamp: datetime,
        current_timestamp: datetime
    ) -> Dict[str, Any]:
        """Detect changes between previous and current content.
        
        Args:
            website_name: Name of the website
            previous_content: Previous content
            current_content: Current content
            previous_timestamp: Previous timestamp
            current_timestamp: Current timestamp
            
        Returns:
            Dict[str, Any]: Changes detected
        """
        # Split content into lines for comparison
        prev_lines = set(previous_content.splitlines())
        curr_lines = set(current_content.splitlines())
        
        # Find added and removed lines
        added = curr_lines - prev_lines
        removed = prev_lines - curr_lines
        
        # Calculate change percentage
        total_lines = len(prev_lines | curr_lines)
        changes = len(added) + len(removed)
        change_percentage = (changes / total_lines * 100) if total_lines > 0 else 0
        
        return {
            'website': website_name,
            'timestamp': current_timestamp.isoformat(),
            'previous_check': previous_timestamp.isoformat(),
            'changes': bool(added or removed),
            'added': list(added),
            'removed': list(removed),
            'change_percentage': round(change_percentage, 2)
        }
    
    def close(self) -> None:
        """Clean up resources."""
        self.content_fetcher.close()