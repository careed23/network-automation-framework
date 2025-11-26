"""
Example Usage Script
Demonstrates how to use the Network Automation Framework
"""

import sys
sys.path.append('scripts')

from device_manager import DeviceManager, load_devices_from_yaml
from config_backup import ConfigBackup
from config_deploy import ConfigDeploy


def example_single_device_backup():
    """Example: Backup a single device"""
    print("\n=== Example 1: Single Device Backup ===")
    
    # Define device configuration
    device_config = {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'admin',
        'port': 22,
    }
    
    # Create backup manager and backup the device
    backup_manager = ConfigBackup(backup_dir='backups')
    success = backup_manager.backup_device(device_config)
    
    print(f"Backup {'successful' if success else 'failed'}")


def example_bulk_backup():
    """Example: Backup all devices from YAML"""
    print("\n=== Example 2: Bulk Backup from YAML ===")
    
    backup_manager = ConfigBackup(backup_dir='backups')
    results = backup_manager.backup_all_devices('config/devices.yaml')
    
    print(f"Total: {results['total']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")


def example_send_commands():
    """Example: Send commands to a device"""
    print("\n=== Example 3: Send Configuration Commands ===")
    
    device_config = {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'admin',
        'port': 22,
    }
    
    commands = [
        'interface GigabitEthernet0/1',
        'description Uplink to Core Switch',
        'no shutdown'
    ]
    
    deploy_manager = ConfigDeploy()
    success = deploy_manager.deploy_commands(device_config, commands)
    
    print(f"Deployment {'successful' if success else 'failed'}")


def example_template_deployment():
    """Example: Deploy configuration using template"""
    print("\n=== Example 4: Template-Based Deployment ===")
    
    device_config = {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'admin',
        'port': 22,
    }
    
    # Variables for template
    template_vars = {
        'interface_name': 'GigabitEthernet0/2',
        'description': 'Access Port - VLAN 10',
        'mode': 'access',
        'vlan': 10,
        'spanning_tree': True
    }
    
    deploy_manager = ConfigDeploy(template_dir='config/templates')
    success = deploy_manager.deploy_from_template(
        device_config, 
        'interface_config.j2', 
        template_vars
    )
    
    print(f"Template deployment {'successful' if success else 'failed'}")


def example_query_device():
    """Example: Query device information"""
    print("\n=== Example 5: Query Device Information ===")
    
    device_config = {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'admin',
        'port': 22,
    }
    
    device_manager = DeviceManager(device_config)
    
    if device_manager.connect():
        # Get various information
        version = device_manager.send_command('show version | include Version')
        interfaces = device_manager.send_command('show ip interface brief')
        
        print("Version Info:")
        print(version)
        print("\nInterfaces:")
        print(interfaces)
        
        device_manager.disconnect()


def example_load_from_yaml():
    """Example: Load devices from YAML and iterate"""
    print("\n=== Example 6: Load and Iterate Devices ===")
    
    devices = load_devices_from_yaml('config/devices.yaml')
    
    print(f"Found {len(devices)} devices:")
    for device in devices:
        print(f"  - {device['host']} ({device['device_type']})")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Network Automation Framework - Usage Examples")
    print("=" * 60)
    print("\nNOTE: These examples will only work if you have:")
    print("1. Configured devices in config/devices.yaml")
    print("2. Network connectivity to your devices")
    print("3. Valid credentials")
    print("\nComment out examples that don't apply to your setup")
    print("=" * 60)
    
    # Uncomment the examples you want to run
    # example_load_from_yaml()
    # example_single_device_backup()
    # example_bulk_backup()
    # example_send_commands()
    # example_template_deployment()
    # example_query_device()
    
    print("\nTo run examples, uncomment them in the main() function")


if __name__ == '__main__':
    main()
