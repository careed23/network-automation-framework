"""
Configuration Backup Script
Automatically backs up network device configurations
"""

import os
from datetime import datetime
from device_manager import DeviceManager, load_devices_from_yaml
import logging

logger = logging.getLogger(__name__)


class ConfigBackup:
    """Handles backup operations for network devices"""
    
    def __init__(self, backup_dir='backups'):
        """
        Initialize backup manager
        
        Args:
            backup_dir (str): Directory to store backups
        """
        self.backup_dir = backup_dir
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            logger.info(f"Created backup directory: {self.backup_dir}")
    
    def backup_device(self, device_config):
        """
        Backup configuration for a single device
        
        Args:
            device_config (dict): Device configuration
            
        Returns:
            bool: True if backup successful, False otherwise
        """
        device_manager = DeviceManager(device_config)
        
        if not device_manager.connect():
            return False
        
        try:
            # Get running configuration
            config = device_manager.get_running_config()
            
            if not config:
                logger.error(f"Failed to retrieve config from {device_config['host']}")
                return False
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            hostname = device_config.get('host', 'unknown')
            filename = f"{hostname}_{timestamp}.txt"
            filepath = os.path.join(self.backup_dir, filename)
            
            # Save to file
            with open(filepath, 'w') as f:
                f.write(config)
            
            logger.info(f"Backup saved: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed for {device_config['host']}: {str(e)}")
            return False
        finally:
            device_manager.disconnect()
    
    def backup_all_devices(self, devices_yaml='config/devices.yaml'):
        """
        Backup configurations for all devices in YAML file
        
        Args:
            devices_yaml (str): Path to devices YAML file
            
        Returns:
            dict: Results summary
        """
        devices = load_devices_from_yaml(devices_yaml)
        
        results = {
            'total': len(devices),
            'successful': 0,
            'failed': 0,
            'devices': []
        }
        
        for device in devices:
            hostname = device.get('host', 'unknown')
            logger.info(f"Starting backup for {hostname}")
            
            success = self.backup_device(device)
            
            if success:
                results['successful'] += 1
                results['devices'].append({
                    'host': hostname,
                    'status': 'success'
                })
            else:
                results['failed'] += 1
                results['devices'].append({
                    'host': hostname,
                    'status': 'failed'
                })
        
        return results


def main():
    """Main function to run backup script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup network device configurations')
    parser.add_argument('--devices', default='config/devices.yaml',
                       help='Path to devices YAML file')
    parser.add_argument('--backup-dir', default='backups',
                       help='Directory to store backups')
    
    args = parser.parse_args()
    
    # Create backup manager
    backup_manager = ConfigBackup(backup_dir=args.backup_dir)
    
    # Run backup
    logger.info("=" * 50)
    logger.info("Starting backup process")
    logger.info("=" * 50)
    
    results = backup_manager.backup_all_devices(args.devices)
    
    # Print summary
    logger.info("=" * 50)
    logger.info("Backup Summary")
    logger.info("=" * 50)
    logger.info(f"Total devices: {results['total']}")
    logger.info(f"Successful: {results['successful']}")
    logger.info(f"Failed: {results['failed']}")
    
    for device in results['devices']:
        logger.info(f"  {device['host']}: {device['status']}")


if __name__ == '__main__':
    main()
