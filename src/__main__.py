"""Main entry point for website tracker."""

import sys
import os
from typing import NoReturn
from .monitor import WebsiteMonitor
from .utils import Logger

logger = Logger.get_logger()

def main() -> NoReturn:
    """Main entry point."""
    try:
        # Get config path from environment or use default
        config_path = os.environ.get('WEBSITE_TRACKER_CONFIG')
        
        # Initialize and run monitor
        logger.info("Starting website content tracker")
        monitor = WebsiteMonitor(config_path)
        
        try:
            changes = monitor.start_monitoring()
            
            # Log results
            if changes:
                logger.info(f"Detected changes in {len(changes)} websites:")
                for change in changes:
                    website = change['website']
                    logger.info(f"\nChanges for {website}:")
                    logger.info(f"Time: {change['timestamp']}")
                    logger.info(f"Change percentage: {change['change_percentage']}%")
                    
                    if change['added']:
                        logger.info("\nAdded content:")
                        for item in change['added']:
                            logger.info(f"+ {item}")
                    
                    if change['removed']:
                        logger.info("\nRemoved content:")
                        for item in change['removed']:
                            logger.info(f"- {item}")
            else:
                logger.info("No changes detected in any monitored websites")
            
            # Exit with success status
            sys.exit(0)
            
        finally:
            monitor.close()
            
    except Exception as e:
        logger.error(f"Error running website tracker: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()