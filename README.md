<div align="center">

# 🚀 Network Automation Framework

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge&logo=python&logoColor=white)](https://github.com/psf/black)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/careed23/network-automation-framework/graphs/commit-activity)

<br>

**A Python-based network automation framework for managing and configuring network devices at scale.**
<br>
**Automate backups, deployments, and provisioning across multi-vendor environments.**

<br>

![Cisco IOS](https://img.shields.io/badge/Cisco-IOS-1BA0D7?style=for-the-badge&logo=cisco&logoColor=white)
![Juniper Junos](https://img.shields.io/badge/Juniper-Junos-84B135?style=for-the-badge&logo=juniper-networks&logoColor=white)
![Arista EOS](https://img.shields.io/badge/Arista-EOS-FF6A00?style=for-the-badge&logo=arista&logoColor=white)

</div>

---

## 🆕 New Features!

Check out our latest additions:
- ✅ [Configuration Compliance Checker](NEW_FEATURES.md#1️⃣-configuration-compliance-checker)
- 📧 [Email & Slack Notifications](NEW_FEATURES.md#2️⃣-email--slack-notifications)
- 🌐 [Web Dashboard](NEW_FEATURES.md#3️⃣-web-dashboard)

See [NEW_FEATURES.md](NEW_FEATURES.md) for complete setup instructions!

---

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Architecture](#%EF%B8%8F-architecture)
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

## 🏗️ Architecture

The framework follows a modular architecture for flexibility and maintainability:

```mermaid
graph TB
    subgraph User["👤 Network Engineer"]
        CLI[Command Line Interface]
    end
    
    subgraph Framework["🐍 Network Automation Framework"]
        subgraph Core["Core Modules"]
            DM[Device Manager<br/>Connection Handler]
        end
        
        subgraph Features["Features"]
            Backup[Config Backup<br/>Module]
            Deploy[Config Deploy<br/>Module]
        end
        
        subgraph Storage["Storage & Templates"]
            Templates[Jinja2 Templates<br/>config/templates/]
            BackupDir[Backup Storage<br/>backups/]
            Logs[Logs<br/>logs/]
        end
    end
    
    subgraph Devices["🌐 Network Infrastructure"]
        R1[Router 1<br/>Cisco IOS]
        R2[Router 2<br/>Cisco IOS]
        SW1[Switch 1<br/>Arista EOS]
        SW2[Switch 2<br/>Juniper]
        FW[Firewall<br/>Palo Alto]
    end
    
    subgraph Config["⚙️ Configuration"]
        YAML[devices.yaml<br/>Device Inventory]
    end
    
    CLI -->|Run Scripts| Backup
    CLI -->|Run Scripts| Deploy
    
    Backup --> DM
    Deploy --> DM
    
    DM -->|SSH/Netmiko| R1
    DM -->|SSH/Netmiko| R2
    DM -->|SSH/Netmiko| SW1
    DM -->|SSH/Netmiko| SW2
    DM -->|SSH/Netmiko| FW
    
    Backup -->|Save configs| BackupDir
    Deploy -->|Load templates| Templates
    DM -->|Write logs| Logs
    
    YAML -.->|Device Info| DM
    Templates -.->|Config Templates| Deploy
    
    style Framework fill:#e1f5ff
    style Devices fill:#fff4e1
    style Config fill:#f0f0f0
    style User fill:#e8f5e9
