"""
Unit tests for the Network Automation Framework
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import MagicMock, patch, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from device_manager import DeviceManager, load_devices_from_yaml
from config_backup import ConfigBackup
from config_deploy import ConfigDeploy
from config_compliance import ComplianceChecker, ComplianceRule


class TestDeviceManager(unittest.TestCase):
    """Tests for DeviceManager"""

    def setUp(self):
        self.device_config = {
            'device_type': 'cisco_ios',
            'host': '192.168.1.1',
            'username': 'admin',
            'password': 'admin',
            'port': 22,
        }

    @patch('device_manager.ConnectHandler')
    def test_connect_success(self, mock_handler):
        mock_handler.return_value = MagicMock()
        dm = DeviceManager(self.device_config)
        result = dm.connect()
        self.assertTrue(result)
        self.assertTrue(dm.connected)

    @patch('device_manager.ConnectHandler', side_effect=Exception("Connection refused"))
    def test_connect_failure(self, mock_handler):
        dm = DeviceManager(self.device_config)
        result = dm.connect()
        self.assertFalse(result)
        self.assertFalse(dm.connected)

    @patch('device_manager.ConnectHandler')
    def test_disconnect(self, mock_handler):
        mock_conn = MagicMock()
        mock_handler.return_value = mock_conn
        dm = DeviceManager(self.device_config)
        dm.connect()
        dm.disconnect()
        mock_conn.disconnect.assert_called_once()
        self.assertFalse(dm.connected)

    @patch('device_manager.ConnectHandler')
    def test_send_command_success(self, mock_handler):
        mock_conn = MagicMock()
        mock_conn.send_command.return_value = 'show output'
        mock_handler.return_value = mock_conn
        dm = DeviceManager(self.device_config)
        dm.connect()
        result = dm.send_command('show version')
        self.assertEqual(result, 'show output')

    def test_send_command_no_connection(self):
        dm = DeviceManager(self.device_config)
        result = dm.send_command('show version')
        self.assertIsNone(result)

    @patch('device_manager.ConnectHandler')
    def test_send_config_success(self, mock_handler):
        mock_conn = MagicMock()
        mock_conn.send_config_set.return_value = 'config output'
        mock_handler.return_value = mock_conn
        dm = DeviceManager(self.device_config)
        dm.connect()
        result = dm.send_config(['interface Gi0/1', 'no shutdown'])
        self.assertEqual(result, 'config output')

    def test_send_config_no_connection(self):
        dm = DeviceManager(self.device_config)
        result = dm.send_config(['interface Gi0/1'])
        self.assertIsNone(result)

    @patch('device_manager.ConnectHandler')
    def test_get_running_config_cisco(self, mock_handler):
        mock_conn = MagicMock()
        mock_conn.send_command.return_value = 'running config'
        mock_handler.return_value = mock_conn
        dm = DeviceManager(self.device_config)
        dm.connect()
        result = dm.get_running_config()
        mock_conn.send_command.assert_called_with('show running-config')
        self.assertEqual(result, 'running config')

    @patch('device_manager.ConnectHandler')
    def test_get_running_config_juniper(self, mock_handler):
        mock_conn = MagicMock()
        mock_conn.send_command.return_value = 'juniper config'
        mock_handler.return_value = mock_conn
        config = dict(self.device_config, device_type='juniper_junos')
        dm = DeviceManager(config)
        dm.connect()
        dm.get_running_config()
        mock_conn.send_command.assert_called_with('show configuration')

    def test_load_devices_from_yaml(self):
        yaml_content = (
            "devices:\n"
            "  - device_type: cisco_ios\n"
            "    host: 10.0.0.1\n"
            "    username: admin\n"
            "    password: secret\n"
            "    port: 22\n"
        )
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            tmp_path = f.name
        try:
            devices = load_devices_from_yaml(tmp_path)
            self.assertEqual(len(devices), 1)
            self.assertEqual(devices[0]['host'], '10.0.0.1')
        finally:
            os.unlink(tmp_path)

    def test_load_devices_from_yaml_missing_file(self):
        devices = load_devices_from_yaml('/nonexistent/path.yaml')
        self.assertEqual(devices, [])


class TestConfigBackup(unittest.TestCase):
    """Tests for ConfigBackup"""

    def test_backup_dir_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup_dir = os.path.join(tmp, 'backups')
            cb = ConfigBackup(backup_dir=backup_dir)
            self.assertTrue(os.path.exists(backup_dir))

    @patch('config_backup.DeviceManager')
    def test_backup_device_success(self, mock_dm_class):
        mock_dm = MagicMock()
        mock_dm.connect.return_value = True
        mock_dm.get_running_config.return_value = 'hostname router1'
        mock_dm_class.return_value = mock_dm

        with tempfile.TemporaryDirectory() as tmp:
            cb = ConfigBackup(backup_dir=tmp)
            device_config = {
                'device_type': 'cisco_ios',
                'host': '10.0.0.1',
                'username': 'admin',
                'password': 'admin',
                'port': 22,
            }
            result = cb.backup_device(device_config)
            self.assertTrue(result)
            saved_files = [f for f in os.listdir(tmp) if f.endswith('.txt')]
            self.assertEqual(len(saved_files), 1)
            self.assertIn('10.0.0.1', saved_files[0])

    @patch('config_backup.DeviceManager')
    def test_backup_device_connect_failure(self, mock_dm_class):
        mock_dm = MagicMock()
        mock_dm.connect.return_value = False
        mock_dm_class.return_value = mock_dm

        with tempfile.TemporaryDirectory() as tmp:
            cb = ConfigBackup(backup_dir=tmp)
            result = cb.backup_device({'host': '10.0.0.1'})
            self.assertFalse(result)

    @patch('config_backup.DeviceManager')
    def test_backup_device_no_config(self, mock_dm_class):
        mock_dm = MagicMock()
        mock_dm.connect.return_value = True
        mock_dm.get_running_config.return_value = None
        mock_dm_class.return_value = mock_dm

        with tempfile.TemporaryDirectory() as tmp:
            cb = ConfigBackup(backup_dir=tmp)
            result = cb.backup_device({'host': '10.0.0.1'})
            self.assertFalse(result)


class TestConfigDeploy(unittest.TestCase):
    """Tests for ConfigDeploy"""

    @patch('config_deploy.DeviceManager')
    def test_deploy_commands_success(self, mock_dm_class):
        mock_dm = MagicMock()
        mock_dm.connect.return_value = True
        mock_dm.send_config.return_value = 'output'
        mock_dm_class.return_value = mock_dm

        with tempfile.TemporaryDirectory() as tmp:
            cd = ConfigDeploy(template_dir=tmp)
            result = cd.deploy_commands({'host': '10.0.0.1'}, ['no shutdown'])
            self.assertTrue(result)

    @patch('config_deploy.DeviceManager')
    def test_deploy_commands_connect_failure(self, mock_dm_class):
        mock_dm = MagicMock()
        mock_dm.connect.return_value = False
        mock_dm_class.return_value = mock_dm

        with tempfile.TemporaryDirectory() as tmp:
            cd = ConfigDeploy(template_dir=tmp)
            result = cd.deploy_commands({'host': '10.0.0.1'}, ['no shutdown'])
            self.assertFalse(result)

    def test_deploy_from_file(self):
        commands_executed = []

        with tempfile.TemporaryDirectory() as tmp:
            config_file = os.path.join(tmp, 'test.cfg')
            with open(config_file, 'w') as f:
                f.write('interface Gi0/1\nno shutdown\n')

            cd = ConfigDeploy(template_dir=tmp)
            cd.deploy_commands = lambda cfg, cmds: commands_executed.extend(cmds) or True
            result = cd.deploy_from_file({'host': '10.0.0.1'}, config_file)
            self.assertTrue(result)
            self.assertIn('interface Gi0/1', commands_executed)

    def test_rollback_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup_file = os.path.join(tmp, 'backup.cfg')
            with open(backup_file, 'w') as f:
                f.write('hostname router1\n')

            cd = ConfigDeploy(template_dir=tmp)
            called_with = {}
            cd.deploy_from_file = lambda cfg, bf: called_with.update({'file': bf}) or True
            result = cd.rollback_config({'host': '10.0.0.1'}, backup_file)
            self.assertTrue(result)
            self.assertEqual(called_with['file'], backup_file)


class TestComplianceRule(unittest.TestCase):
    """Tests for ComplianceRule"""

    def test_must_contain_pass(self):
        rule = ComplianceRule('NTP', 'NTP test', 'must_contain', pattern='ntp server')
        result = rule.check('ntp server 10.0.0.1')
        self.assertTrue(result['compliant'])

    def test_must_contain_fail(self):
        rule = ComplianceRule('NTP', 'NTP test', 'must_contain', pattern='ntp server')
        result = rule.check('hostname router1')
        self.assertFalse(result['compliant'])

    def test_must_not_contain_pass(self):
        rule = ComplianceRule('NoTelnet', 'No telnet', 'must_not_contain', pattern='transport input telnet')
        result = rule.check('transport input ssh')
        self.assertTrue(result['compliant'])

    def test_must_not_contain_fail(self):
        rule = ComplianceRule('NoTelnet', 'No telnet', 'must_not_contain', pattern='transport input telnet')
        result = rule.check('transport input telnet')
        self.assertFalse(result['compliant'])

    def test_regex_pass(self):
        rule = ComplianceRule('SSH2', 'SSH v2', 'regex', pattern=r'ip ssh version 2')
        result = rule.check('ip ssh version 2\nhostname router1')
        self.assertTrue(result['compliant'])

    def test_regex_fail(self):
        rule = ComplianceRule('SSH2', 'SSH v2', 'regex', pattern=r'ip ssh version 2')
        result = rule.check('hostname router1')
        self.assertFalse(result['compliant'])

    def test_command_rule_pass(self):
        mock_dm = MagicMock()
        mock_dm.send_command.return_value = 'NTP: synchronized'
        rule = ComplianceRule('NTPSync', 'NTP sync', 'command',
                              command='show ntp status', required_value='synchronized')
        result = rule.check('', device_manager=mock_dm)
        self.assertTrue(result['compliant'])

    def test_command_rule_no_device_manager(self):
        rule = ComplianceRule('NTPSync', 'NTP sync', 'command',
                              command='show ntp status', required_value='synchronized')
        result = rule.check('')
        self.assertFalse(result['compliant'])


class TestComplianceChecker(unittest.TestCase):
    """Tests for ComplianceChecker"""

    def _make_rules_file(self, tmp_dir):
        rules = {
            "rules": [
                {
                    "name": "NTP Server",
                    "description": "NTP must be configured",
                    "type": "must_contain",
                    "pattern": "ntp server"
                }
            ]
        }
        rules_file = os.path.join(tmp_dir, 'rules.json')
        with open(rules_file, 'w') as f:
            json.dump(rules, f)
        return rules_file

    def test_load_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            rules_file = self._make_rules_file(tmp)
            checker = ComplianceChecker(rules_file=rules_file)
            self.assertEqual(len(checker.rules), 1)
            self.assertEqual(checker.rules[0].name, 'NTP Server')

    def test_creates_default_rules_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            rules_file = os.path.join(tmp, 'nonexistent.json')
            checker = ComplianceChecker(rules_file=rules_file)
            self.assertTrue(len(checker.rules) > 0)
            self.assertTrue(os.path.exists(rules_file))

    def test_check_device_from_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            rules_file = self._make_rules_file(tmp)
            backup_dir = tmp

            config_text = 'ntp server 10.0.0.1\nhostname router1'
            backup_file = os.path.join(backup_dir, '10.0.0.1_20240101_120000.txt')
            with open(backup_file, 'w') as f:
                f.write(config_text)

            checker = ComplianceChecker(rules_file=rules_file)

            with patch('config_compliance.os.listdir', return_value=['10.0.0.1_20240101_120000.txt']):
                with patch('config_compliance.os.path.join', side_effect=os.path.join):
                    with patch('builtins.open', mock_open(read_data=config_text)):
                        result = checker.check_device({'host': '10.0.0.1'}, check_live=False)

            self.assertEqual(result['passed'], 1)
            self.assertEqual(result['compliance_score'], 100.0)

    def test_generate_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            rules_file = self._make_rules_file(tmp)
            checker = ComplianceChecker(rules_file=rules_file)

            results = {
                'timestamp': '2024-01-01T12:00:00',
                'total_devices': 1,
                'overall_compliance': 100.0,
                'device_results': [
                    {
                        'device': '10.0.0.1',
                        'compliance_score': 100.0,
                        'passed': 1,
                        'total_rules': 1,
                        'rule_results': [
                            {
                                'compliant': True,
                                'rule': 'NTP Server',
                                'message': 'Found',
                                'details': None,
                            }
                        ]
                    }
                ]
            }

            report_file = os.path.join(tmp, 'report.txt')
            checker.generate_report(results, output_file=report_file)

            self.assertTrue(os.path.exists(report_file))
            with open(report_file) as f:
                content = f.read()
            self.assertIn('NETWORK COMPLIANCE REPORT', content)
            self.assertIn('10.0.0.1', content)


if __name__ == '__main__':
    unittest.main()

