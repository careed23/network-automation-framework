Network Automation Framework

A Python-based network automation framework for managing and configuring network devices at scale. This tool automates common network administration tasks including configuration backups, deployments, and template-based provisioning.
Features

Automated Configuration Backups: Schedule and execute backups of network device configurations
Template-Based Deployment: Use Jinja2 templates to deploy standardized configurations
Multi-Vendor Support: Works with Cisco, Juniper, Arista, HP, and many other vendors via Netmiko
Centralized Management: Manage all devices from a single YAML configuration file
Logging: Comprehensive logging for audit trails and troubleshooting
Rollback Capability: Easily rollback to previous configurations
Batch Operations: Execute commands across multiple devices simultaneously

Use Cases

Daily automated configuration backups
Standardized device provisioning
Configuration compliance checking
Emergency rollback procedures
Bulk configuration changes
Network disaster recovery

Installation
Prerequisites

Python 3.7 or higher
Network devices accessible via SSH
Valid credentials for your network devices

Setup

Clone this repository:

bashgit clone https://github.com/yourusername/network-automation-framework.git
cd network-automation-framework

Create a virtual environment (recommended):

bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:

bashpip install -r requirements.txt

Create necessary directories:

bashmkdir -p backups logs config/templates

Configure your devices in config/devices.yaml:

yamldevices:
  - device_type: cisco_ios
    host: 192.168.1.1
    username: admin
    password: your_password
    port: 22
Usage
Configuration Backup
Backup all devices defined in your configuration:
bashpython scripts/config_backup.py
Specify custom devices file or backup directory:
bashpython scripts/config_backup.py --devices config/devices.yaml --backup-dir backups
Configuration Deployment
Deploy specific commands to all devices:
bashpython scripts/config_deploy.py --commands "interface GigabitEthernet0/1" "description Uplink to Core"
Deploy commands to a specific device:
bashpython scripts/config_deploy.py --host 192.168.1.1 --commands "ntp server 10.0.0.1"
Deploy from a configuration file:
bashpython scripts/config_deploy.py --file config/my_config.txt
Deploy using a Jinja2 template:
bashpython scripts/config_deploy.py --template interface_config.j2 --vars '{"interface": "GigabitEthernet0/1", "vlan": 100}'
Rollback Configuration
Rollback to a previous backup:
bashpython scripts/config_deploy.py --host 192.168.1.1 --file backups/192.168.1.1_20240115_143022.txt
Project Structure
network-automation-framework/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── config/
│   ├── devices.yaml         # Device inventory
│   └── templates/           # Jinja2 configuration templates
├── scripts/
│   ├── __init__.py
│   ├── device_manager.py    # Core device connection module
│   ├── config_backup.py     # Backup functionality
│   └── config_deploy.py     # Deployment functionality
├── backups/                 # Configuration backups stored here
├── logs/                    # Application logs
└── examples/                # Example configurations and templates
Configuration Templates
Create Jinja2 templates in config/templates/ for standardized deployments:
Example: interface_config.j2
jinjainterface {{ interface }}
 description {{ description }}
 switchport mode {{ mode }}
 switchport access vlan {{ vlan }}
 no shutdown
Security Best Practices

Never commit credentials: Add config/devices.yaml to .gitignore
Use environment variables: Store sensitive data in environment variables
Restrict file permissions: Limit access to configuration files
Use SSH keys: Prefer key-based authentication over passwords
Enable logging: Monitor all automation activities
Test first: Always test on non-production devices first

Supported Platforms
This framework supports any device compatible with Netmiko, including:

Cisco IOS, IOS-XE, IOS-XR, NX-OS, ASA
Juniper Junos
Arista EOS
HP ProCurve
Dell Force10
Palo Alto PAN-OS
Many more...

See the Netmiko documentation for a complete list.
Troubleshooting
Connection Failures
Check the logs in logs/network_automation.log for detailed error messages:

Verify device IP addresses and SSH connectivity
Confirm credentials are correct
Ensure SSH is enabled on devices
Check firewall rules and network ACLs

Authentication Issues

Verify username and password in devices.yaml
For Cisco devices, you may need to specify the secret for enable mode
Check if devices require key-based authentication

Contributing
Contributions are welcome! Please feel free to submit issues or pull requests.
Future Enhancements

 Web-based dashboard for monitoring
 Configuration compliance checking
 Scheduled backup jobs via cron
 Integration with version control (Git)
 Ansible playbook integration
 REST API for remote operations
 Configuration diff and change tracking
 Multi-threading for faster operations

Author
Colten Reed - https://github.com/careed23
Acknowledgments

Built with Netmiko for network device connections
Uses Jinja2 for configuration templating# network-automation-framework
A production-ready network automation tool that streamlines device management across Cisco, Juniper, Arista, and other vendors. Features automated configuration backups, Jinja2 template deployments, rollback capabilities, and comprehensive logging for enterprise network operations.
