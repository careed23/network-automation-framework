# Quick Start Guide

Get up and running with the Network Automation Framework in 5 minutes!

## Step 1: Installation (2 minutes)

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

## Step 2: Configure Your Devices (2 minutes)

Edit `config/devices.yaml` with your device information:

```yaml
devices:
  - device_type: cisco_ios
    host: 192.168.1.1
    username: admin
    password: your_password
    port: 22
```

**Important**: Make sure SSH is enabled on your devices and you can reach them from your network.

## Step 3: Test Connection (1 minute)

Run the example script to test connectivity:

```bash
python examples/example_usage.py
```

Or test a simple backup:

```bash
python scripts/config_backup.py
```

## Your First Tasks

### Backup All Devices
```bash
python scripts/config_backup.py
```
Backups will be saved in the `backups/` directory with timestamps.

### Deploy a Simple Command
```bash
python scripts/config_deploy.py --host 192.168.1.1 --commands "ntp server 10.0.0.1"
```

### Deploy Multiple Commands
```bash
python scripts/config_deploy.py --commands \
  "interface GigabitEthernet0/1" \
  "description Uplink Port" \
  "no shutdown"
```

### Use a Configuration Template
```bash
python scripts/config_deploy.py --template interface_config.j2 \
  --vars '{"interface_name": "GigabitEthernet0/1", "mode": "access", "vlan": 10}'
```

## Troubleshooting

### Can't Connect to Device?
- Check IP address in `config/devices.yaml`
- Verify SSH is enabled: `ssh admin@192.168.1.1`
- Check logs: `tail -f logs/network_automation.log`

### Authentication Failed?
- Verify username/password in `config/devices.yaml`
- For Cisco devices, add `secret: enable_password` if needed

### Commands Not Working?
- Check device type is correct (`cisco_ios`, `cisco_nxos`, etc.)
- View logs for detailed error messages
- Test commands manually via SSH first

## Next Steps

1. **Set up scheduled backups** using cron (Linux/Mac) or Task Scheduler (Windows)
2. **Create configuration templates** for common deployment tasks
3. **Add more devices** to your inventory
4. **Implement compliance checking** by comparing backups
5. **Integrate with Git** for version control of configurations

## Need Help?

- Check the main [README.md](README.md) for full documentation
- Review [example_usage.py](examples/example_usage.py) for code examples
- Open an issue on GitHub
- Check logs in `logs/network_automation.log`

## Security Reminder

**Never commit sensitive data to Git!**

```bash
# Make sure .gitignore is working
cat .gitignore  # Should include config/devices.yaml

# Verify devices.yaml won't be committed
git status  # Should NOT show devices.yaml
```

Happy automating! 🚀
