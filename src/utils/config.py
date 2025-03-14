import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Optional path to config file. If None, uses default.
        """
        self.config_path = config_path or os.path.join('config', 'websites.yml')
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                self._create_default_config(config_file)
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {str(e)}")
    
    def _create_default_config(self, config_file: Path) -> None:
        """Create default configuration file if it doesn't exist."""
        default_config = {
            'websites': [],
            'email': {
                'service': 'gmail',
                'credentials': {
                    'client_id': '${GMAIL_CLIENT_ID}',
                    'client_secret': '${GMAIL_CLIENT_SECRET}',
                    'refresh_token': '${GMAIL_REFRESH_TOKEN}'
                },
                'from': '${GMAIL_FROM_EMAIL}',
                'batch_interval': 3600,
                'rate_limit': {
                    'max_emails': 50,
                    'period': 3600
                }
            }
        }
        
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False)
    
    def get_websites(self) -> list:
        """Get list of websites to monitor."""
        return self.config.get('websites', [])
    
    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration."""
        return self.config.get('email', {})
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save configuration: {str(e)}")

    def update_website(self, name: str, config: Dict[str, Any]) -> None:
        """Update or add website configuration.
        
        Args:
            name: Website name
            config: Website configuration
        """
        websites = self.get_websites()
        # Find existing website config
        for i, website in enumerate(websites):
            if website.get('name') == name:
                websites[i] = config
                break
        else:
            # Add new website
            websites.append(config)
        
        self.config['websites'] = websites
        self.save_config()
    
    def remove_website(self, name: str) -> bool:
        """Remove website configuration.
        
        Args:
            name: Website name
            
        Returns:
            bool: True if website was removed, False if not found
        """
        websites = self.get_websites()
        for i, website in enumerate(websites):
            if website.get('name') == name:
                websites.pop(i)
                self.config['websites'] = websites
                self.save_config()
                return True
        return False