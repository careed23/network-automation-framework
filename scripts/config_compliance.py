"""
Configuration Compliance Checker
Validates device configurations against defined compliance rules
"""

import re
import json
import logging
from datetime import datetime
from device_manager import DeviceManager, load_devices_from_yaml

logger = logging.getLogger(__name__)


class ComplianceRule:
    """Represents a single compliance rule"""
    
    def __init__(self, name, description, rule_type, pattern=None, 
                 required_value=None, command=None):
        """
        Initialize compliance rule
        
        Args:
            name (str): Rule name
            description (str): Rule description
            rule_type (str): Type of rule (must_contain, must_not_contain, regex, command)
            pattern (str): Pattern to search for
            required_value (str): Required configuration value
            command (str): Command to run for validation
        """
        self.name = name
        self.description = description
        self.rule_type = rule_type
        self.pattern = pattern
        self.required_value = required_value
        self.command = command
    
    def check(self, config_text, device_manager=None):
        """
        Check if configuration complies with this rule
        
        Args:
            config_text (str): Configuration text to check
            device_manager (DeviceManager): Device manager for command-based rules
            
        Returns:
            dict: Result with status, message, and details
        """
        result = {
            'rule': self.name,
            'description': self.description,
            'compliant': False,
            'message': '',
            'details': None
        }
        
        try:
            if self.rule_type == 'must_contain':
                if self.pattern in config_text:
                    result['compliant'] = True
                    result['message'] = f"Required pattern found: {self.pattern}"
                else:
                    result['message'] = f"Missing required pattern: {self.pattern}"
            
            elif self.rule_type == 'must_not_contain':
                if self.pattern not in config_text:
                    result['compliant'] = True
                    result['message'] = f"Forbidden pattern not found (good)"
                else:
                    result['message'] = f"Forbidden pattern found: {self.pattern}"
            
            elif self.rule_type == 'regex':
                matches = re.findall(self.pattern, config_text, re.MULTILINE)
                if matches:
                    result['compliant'] = True
                    result['message'] = f"Pattern matched"
                    result['details'] = matches[:5]  # First 5 matches
                else:
                    result['message'] = f"Pattern not matched: {self.pattern}"
            
            elif self.rule_type == 'command':
                if device_manager:
                    output = device_manager.send_command(self.command)
                    if self.required_value in output:
                        result['compliant'] = True
                        result['message'] = f"Command validation passed"
                    else:
                        result['message'] = f"Command validation failed"
                    result['details'] = output[:200]  # First 200 chars
                else:
                    result['message'] = "No device manager provided for command check"
        
        except Exception as e:
            result['message'] = f"Error checking rule: {str(e)}"
            logger.error(f"Error in rule {self.name}: {str(e)}")
        
        return result


class ComplianceChecker:
    """Manages compliance checking for network devices"""
    
    def __init__(self, rules_file='config/compliance_rules.json'):
        """
        Initialize compliance checker
        
        Args:
            rules_file (str): Path to compliance rules JSON file
        """
        self.rules_file = rules_file
        self.rules = []
        self.load_rules()
    
    def load_rules(self):
        """Load compliance rules from JSON file"""
        try:
            with open(self.rules_file, 'r') as f:
                rules_data = json.load(f)
                
            for rule_data in rules_data.get('rules', []):
                rule = ComplianceRule(
                    name=rule_data['name'],
                    description=rule_data['description'],
                    rule_type=rule_data['type'],
                    pattern=rule_data.get('pattern'),
                    required_value=rule_data.get('required_value'),
                    command=rule_data.get('command')
                )
                self.rules.append(rule)
            
            logger.info(f"Loaded {len(self.rules)} compliance rules")
            
        except FileNotFoundError:
            logger.warning(f"Rules file not found: {self.rules_file}")
            self._create_default_rules()
        except Exception as e:
            logger.error(f"Error loading rules: {str(e)}")
    
    def _create_default_rules(self):
        """Create default compliance rules file"""
        default_rules = {
            "rules": [
                {
                    "name": "NTP Server Configured",
                    "description": "Verify NTP server is configured",
                    "type": "must_contain",
                    "pattern": "ntp server"
                },
                {
                    "name": "SSH Version 2",
                    "description": "Ensure SSH version 2 is enabled",
                    "type": "regex",
                    "pattern": "ip ssh version 2"
                },
                {
                    "name": "No Telnet",
                    "description": "Verify telnet is not enabled",
                    "type": "must_not_contain",
                    "pattern": "transport input telnet"
                },
                {
                    "name": "Logging Configured",
                    "description": "Verify logging server is configured",
                    "type": "must_contain",
                    "pattern": "logging"
                },
                {
                    "name": "SNMP Community",
                    "description": "Check for default SNMP community strings",
                    "type": "must_not_contain",
                    "pattern": "snmp-server community public"
                }
            ]
        }
        
        try:
            with open(self.rules_file, 'w') as f:
                json.dump(default_rules, f, indent=2)
            logger.info(f"Created default rules file: {self.rules_file}")
            self.load_rules()
        except Exception as e:
            logger.error(f"Error creating default rules: {str(e)}")
    
    def check_device(self, device_config, check_live=False):
        """
        Check compliance for a single device
        
        Args:
            device_config (dict): Device configuration
            check_live (bool): Whether to connect to device for live checks
            
        Returns:
            dict: Compliance results
        """
        hostname = device_config.get('host', 'unknown')
        logger.info(f"Checking compliance for {hostname}")
        
        results = {
            'device': hostname,
            'timestamp': datetime.now().isoformat(),
            'total_rules': len(self.rules),
            'passed': 0,
            'failed': 0,
            'compliance_score': 0,
            'rule_results': []
        }
        
        device_manager = None
        config_text = None
        
        try:
            if check_live:
                device_manager = DeviceManager(device_config)
                if device_manager.connect():
                    config_text = device_manager.get_running_config()
                else:
                    logger.error(f"Failed to connect to {hostname}")
                    return results
            else:
                # Load from latest backup
                import os
                backup_dir = 'backups'
                backups = [f for f in os.listdir(backup_dir) 
                          if f.startswith(hostname) and f.endswith('.txt')]
                
                if backups:
                    latest_backup = sorted(backups)[-1]
                    backup_path = os.path.join(backup_dir, latest_backup)
                    with open(backup_path, 'r') as f:
                        config_text = f.read()
                    logger.info(f"Using backup: {latest_backup}")
                else:
                    logger.error(f"No backup found for {hostname}")
                    return results
            
            # Check each rule
            for rule in self.rules:
                rule_result = rule.check(config_text, device_manager)
                results['rule_results'].append(rule_result)
                
                if rule_result['compliant']:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
            
            # Calculate compliance score
            if results['total_rules'] > 0:
                results['compliance_score'] = round(
                    (results['passed'] / results['total_rules']) * 100, 2
                )
            
            logger.info(f"{hostname}: {results['compliance_score']}% compliant "
                       f"({results['passed']}/{results['total_rules']} rules)")
            
        except Exception as e:
            logger.error(f"Error checking compliance for {hostname}: {str(e)}")
        finally:
            if device_manager:
                device_manager.disconnect()
        
        return results
    
    def check_all_devices(self, devices_yaml='config/devices.yaml', 
                         check_live=False):
        """
        Check compliance for all devices
        
        Args:
            devices_yaml (str): Path to devices YAML file
            check_live (bool): Whether to connect to devices for live checks
            
        Returns:
            dict: Summary of all compliance checks
        """
        devices = load_devices_from_yaml(devices_yaml)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_devices': len(devices),
            'device_results': [],
            'overall_compliance': 0
        }
        
        total_score = 0
        
        for device in devices:
            result = self.check_device(device, check_live)
            summary['device_results'].append(result)
            total_score += result['compliance_score']
        
        if summary['total_devices'] > 0:
            summary['overall_compliance'] = round(
                total_score / summary['total_devices'], 2
            )
        
        return summary
    
    def generate_report(self, results, output_file='compliance_report.txt'):
        """
        Generate a compliance report
        
        Args:
            results (dict): Compliance check results
            output_file (str): Output file path
        """
        with open(output_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("NETWORK COMPLIANCE REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {results['timestamp']}\n")
            f.write(f"Total Devices: {results['total_devices']}\n")
            f.write(f"Overall Compliance Score: {results['overall_compliance']}%\n")
            f.write("=" * 80 + "\n\n")
            
            for device_result in results['device_results']:
                f.write(f"\nDevice: {device_result['device']}\n")
                f.write(f"Compliance Score: {device_result['compliance_score']}%\n")
                f.write(f"Passed: {device_result['passed']}/{device_result['total_rules']}\n")
                f.write("-" * 80 + "\n")
                
                for rule_result in device_result['rule_results']:
                    status = "✓ PASS" if rule_result['compliant'] else "✗ FAIL"
                    f.write(f"{status} | {rule_result['rule']}\n")
                    f.write(f"       {rule_result['message']}\n")
                    if rule_result['details']:
                        f.write(f"       Details: {rule_result['details']}\n")
                
                f.write("\n")
        
        logger.info(f"Report saved to {output_file}")


def main():
    """Main function to run compliance checker"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check network device compliance')
    parser.add_argument('--devices', default='config/devices.yaml',
                       help='Path to devices YAML file')
    parser.add_argument('--rules', default='config/compliance_rules.json',
                       help='Path to compliance rules JSON file')
    parser.add_argument('--live', action='store_true',
                       help='Check live devices instead of backups')
    parser.add_argument('--report', default='compliance_report.txt',
                       help='Output report file')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Starting Compliance Check")
    logger.info("=" * 60)
    
    # Create compliance checker
    checker = ComplianceChecker(rules_file=args.rules)
    
    # Run compliance checks
    results = checker.check_all_devices(args.devices, check_live=args.live)
    
    # Generate report
    checker.generate_report(results, args.report)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("Compliance Check Summary")
    logger.info("=" * 60)
    logger.info(f"Overall Compliance: {results['overall_compliance']}%")
    logger.info(f"Report saved to: {args.report}")


if __name__ == '__main__':
    main()
