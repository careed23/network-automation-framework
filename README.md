# 🚀 Network Automation Framework

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/yourusername/network-automation-framework/graphs/commit-activity)

> A Python-based network automation framework for managing and configuring network devices at scale. Automate backups, deployments, and provisioning across multi-vendor environments.

<p align="center">
  <img src="https://img.shields.io/badge/Cisco-IOS-1BA0D7?style=for-the-badge&logo=cisco&logoColor=white" alt="Cisco IOS"/>
  <img src="https://img.shields.io/badge/Juniper-Junos-84B135?style=for-the-badge&logo=juniper-networks&logoColor=white" alt="Juniper"/>
  <img src="https://img.shields.io/badge/Arista-EOS-FF6A00?style=for-the-badge&logo=arista&logoColor=white" alt="Arista"/>
</p>

---

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Examples](#-examples)
- [Project Structure](#-project-structure)
- [Security](#-security)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔄 **Automated Backups** | Schedule and execute configuration backups with timestamps |
| 📝 **Template Engine** | Jinja2-powered configuration templates for standardized deployments |
| 🔌 **Multi-Vendor** | Support for Cisco, Juniper, Arista, HP, and 50+ vendors via Netmiko |
| 📊 **Comprehensive Logging** | Detailed audit trails for compliance and troubleshooting |
| ⏮️ **Rollback Support** | One-command rollback to previous configurations |
| 🎯 **Batch Operations** | Execute commands across multiple devices simultaneously |
| 🔐 **Secure by Design** | Credential management best practices built-in |
| 🛠️ **Easy Configuration** | Simple YAML-based device inventory |

---

## 🎬 Demo

```bash
# Backup all devices
$ python scripts/config_backup.py

[INFO] Connecting to 192.168.1.1
[INFO] Successfully connected to 192.168.1.1
[INFO] Backup saved: backups/192.168.1.1_20240115_143022.txt
[INFO] ✓ 5 devices backed up successfully

# Deploy configuration template
$ python scripts/config_deploy.py --template interface_config.j2 \
  --vars '{"interface_name": "GigabitEthernet0/1", "vlan": 10}'

[INFO] Configuration deployed to 192.168.1.1
[INFO] ✓ Deployment successful
```

---

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- SSH access to network devices
- Valid device credentials

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/network-automation-framework.git
cd network-automation-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create required directories
mkdir -p backups logs config/templates
```

---

## ⚡ Quick Start

1. **Configure your devices** in `config/devices.yaml`:

```yaml
devices:
  - device_type: cisco_ios
    host: 192.168.1.1
    username: admin
    password: your_password
    port: 22
```

2. **Run your first backup**:

```bash
python scripts/config_backup.py
```

3. **Deploy a configuration**:

```bash
python scripts/config_deploy.py --host 192.168.1.1 \
  --commands "ntp server 10.0.0.1"
```

📖 See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

---

## 💻 Usage

### Configuration Backup

```bash
# Backup all devices
python scripts/config_backup.py

# Custom backup directory
python scripts/config_backup.py --backup-dir /path/to/backups

# Specific devices file
python scripts/config_backup.py --devices config/prod_devices.yaml
```

### Configuration Deployment

```bash
# Deploy specific commands
python scripts/config_deploy.py --commands \
  "interface GigabitEthernet0/1" \
  "description Uplink to Core"

# Deploy to specific device
python scripts/config_deploy.py --host 192.168.1.1 \
  --file config/my_config.txt

# Use template with variables
python scripts/config_deploy.py --template interface_config.j2 \
  --vars '{"interface_name": "Gi0/1", "vlan": 100}'
```

### Rollback Configuration

```bash
python scripts/config_deploy.py --host 192.168.1.1 \
  --file backups/192.168.1.1_20240115_143022.txt
```

---

## ⚙️ Configuration

### Device Inventory (`config/devices.yaml`)

```yaml
devices:
  - device_type: cisco_ios
    host: 192.168.1.1
    username: admin
    password: secure_password
    secret: enable_password  # Optional
    port: 22
    
  - device_type: juniper_junos
    host: 192.168.1.10
    username: netadmin
    password: secure_password
    port: 22
```

### Supported Device Types

<details>
<summary>Click to expand supported platforms</summary>

- Cisco: `cisco_ios`, `cisco_nxos`, `cisco_xr`, `cisco_asa`
- Juniper: `juniper_junos`
- Arista: `arista_eos`
- HP: `hp_procurve`, `hp_comware`
- Dell: `dell_force10`, `dell_os10`
- Palo Alto: `paloalto_panos`
- And 40+ more via [Netmiko](https://github.com/ktbyers/netmiko)

</details>

---

## 📚 Examples

### Example 1: Bulk Interface Configuration

Create `config/templates/bulk_interface.j2`:

```jinja
{% for interface in interfaces %}
interface {{ interface.name }}
 description {{ interface.description }}
 switchport access vlan {{ interface.vlan }}
 no shutdown
{% endfor %}
```

Deploy:

```bash
python scripts/config_deploy.py --template bulk_interface.j2 \
  --vars '{"interfaces": [
    {"name": "Gi0/1", "description": "Workstation", "vlan": 10},
    {"name": "Gi0/2", "description": "Printer", "vlan": 20}
  ]}'
```

### Example 2: Python Integration

```python
from scripts.device_manager import DeviceManager
from scripts.config_backup import ConfigBackup

# Backup a device programmatically
device_config = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'password'
}

backup_manager = ConfigBackup()
backup_manager.backup_device(device_config)
```

More examples in [`examples/example_usage.py`](examples/example_usage.py)

---

## 📁 Project Structure

```
network-automation-framework/
├── 📄 README.md                 # This file
├── 📄 QUICKSTART.md             # Quick start guide
├── 📄 requirements.txt          # Python dependencies
├── 📄 .gitignore               # Git ignore rules
│
├── 📂 config/
│   ├── 📄 devices.yaml         # Device inventory
│   └── 📂 templates/           # Jinja2 templates
│       └── 📄 interface_config.j2
│
├── 📂 scripts/
│   ├── 📄 __init__.py
│   ├── 📄 device_manager.py    # Core device connections
│   ├── 📄 config_backup.py     # Backup functionality
│   └── 📄 config_deploy.py     # Deployment functionality
│
├── 📂 examples/
│   └── 📄 example_usage.py     # Usage examples
│
├── 📂 backups/                 # Configuration backups
└── 📂 logs/                    # Application logs
```

---

## 🔐 Security

### Best Practices Implemented

- ✅ Credentials stored in YAML (excluded from Git)
- ✅ Comprehensive logging for audit trails
- ✅ SSH-based authentication
- ✅ No hardcoded passwords in code
- ✅ File permission recommendations

### Security Recommendations

```bash
# Restrict permissions on sensitive files
chmod 600 config/devices.yaml

# Use environment variables for credentials
export DEVICE_PASSWORD='your_password'

# Consider using SSH keys instead of passwords
```

> ⚠️ **Warning**: Never commit `config/devices.yaml` to version control!

---

## 🗺️ Roadmap

- [ ] 🌐 Web-based dashboard for monitoring
- [ ] ✅ Configuration compliance checking
- [ ] ⏰ Scheduled backup jobs (cron integration)
- [ ] 🔄 Git integration for version control
- [ ] 📡 REST API for remote operations
- [ ] 🔍 Configuration diff and change tracking
- [ ] ⚡ Multi-threading for faster operations
- [ ] 📊 Reporting and analytics dashboard

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🍴 Fork the repository
2. 🌟 Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🎉 Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**

- GitHub: [@careed23](https://github.com/careed23)
- LinkedIn: [Your LinkedIn](https://www.linkedin.com/in/colten-reed-8395b6389/)
- Email: careed23@outlook.com

---

## 🙏 Acknowledgments

- [Netmiko](https://github.com/ktbyers/netmiko) - Network device connectivity
- [Jinja2](https://jinja.palletsprojects.com/) - Configuration templating
- [PyYAML](https://pyyaml.org/) - YAML parsing

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/network-automation-framework?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/network-automation-framework?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/network-automation-framework)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/network-automation-framework)

---

<p align="center">Made with ❤️ for Network Engineers</p>
<p align="center">⭐ Star this repo if you find it helpful!</p>
