"""
Notification System
Send email and Slack notifications for automation events
"""

import smtplib
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications"""
    
    def __init__(self, smtp_server, smtp_port, username, password, 
                 from_email, use_tls=True):
        """
        Initialize email notifier
        
        Args:
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP port
            username (str): SMTP username
            password (str): SMTP password
            from_email (str): From email address
            use_tls (bool): Whether to use TLS
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.use_tls = use_tls
    
    def send_email(self, to_emails, subject, body, html=False):
        """
        Send an email
        
        Args:
            to_emails (list): List of recipient email addresses
            subject (str): Email subject
            body (str): Email body
            html (bool): Whether body is HTML
            
        Returns:
            bool: True if sent successfully
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent to {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_backup_notification(self, results, to_emails):
        """
        Send backup completion notification
        
        Args:
            results (dict): Backup results
            to_emails (list): Recipient emails
        """
        subject = f"Network Backup Report - {results['successful']}/{results['total']} Successful"
        
        body = f"""
Network Configuration Backup Report
{'=' * 50}

Total Devices: {results['total']}
Successful: {results['successful']}
Failed: {results['failed']}

Device Details:
"""
        for device in results['devices']:
            status_symbol = '✓' if device['status'] == 'success' else '✗'
            body += f"\n{status_symbol} {device['host']}: {device['status']}"
        
        body += f"\n\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_email(to_emails, subject, body)
    
    def send_compliance_notification(self, results, to_emails):
        """
        Send compliance check notification
        
        Args:
            results (dict): Compliance check results
            to_emails (list): Recipient emails
        """
        subject = f"Network Compliance Report - {results['overall_compliance']}% Compliant"
        
        body = f"""
Network Compliance Report
{'=' * 50}

Overall Compliance Score: {results['overall_compliance']}%
Total Devices Checked: {results['total_devices']}

Device Breakdown:
"""
        for device_result in results['device_results']:
            body += f"\n{device_result['device']}: {device_result['compliance_score']}% "
            body += f"({device_result['passed']}/{device_result['total_rules']} rules passed)"
            
            # Add failed rules
            failed_rules = [r for r in device_result['rule_results'] if not r['compliant']]
            if failed_rules:
                body += "\n  Failed Rules:"
                for rule in failed_rules[:3]:  # Top 3 failures
                    body += f"\n    - {rule['rule']}: {rule['message']}"
        
        body += f"\n\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        body += "\n\nFull report available in compliance_report.txt"
        
        return self.send_email(to_emails, subject, body)
    
    def send_deployment_notification(self, device, success, to_emails):
        """
        Send deployment notification
        
        Args:
            device (str): Device hostname
            success (bool): Whether deployment was successful
            to_emails (list): Recipient emails
        """
        status = "Successful" if success else "Failed"
        subject = f"Configuration Deployment {status} - {device}"
        
        body = f"""
Configuration Deployment Notification
{'=' * 50}

Device: {device}
Status: {status}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'Configuration has been successfully applied to the device.' if success else 'Configuration deployment failed. Please check logs for details.'}
"""
        
        return self.send_email(to_emails, subject, body)


class SlackNotifier:
    """Send Slack notifications"""
    
    def __init__(self, webhook_url):
        """
        Initialize Slack notifier
        
        Args:
            webhook_url (str): Slack webhook URL
        """
        self.webhook_url = webhook_url
    
    def send_message(self, text, blocks=None):
        """
        Send a Slack message
        
        Args:
            text (str): Message text (fallback)
            blocks (list): Slack blocks for rich formatting
            
        Returns:
            bool: True if sent successfully
        """
        try:
            payload = {'text': text}
            if blocks:
                payload['blocks'] = blocks
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info("Slack notification sent")
                return True
            else:
                logger.error(f"Slack notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Slack message: {str(e)}")
            return False
    
    def send_backup_notification(self, results):
        """
        Send backup notification to Slack
        
        Args:
            results (dict): Backup results
        """
        success_emoji = '✅' if results['failed'] == 0 else '⚠️'
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{success_emoji} Network Backup Report"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Devices:*\n{results['total']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Successful:*\n{results['successful']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failed:*\n{results['failed']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Timestamp:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]
        
        # Add device details
        device_text = ""
        for device in results['devices']:
            emoji = '✅' if device['status'] == 'success' else '❌'
            device_text += f"{emoji} {device['host']}\n"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Device Status:*\n{device_text}"
            }
        })
        
        return self.send_message("Network Backup Report", blocks)
    
    def send_compliance_notification(self, results):
        """
        Send compliance notification to Slack
        
        Args:
            results (dict): Compliance results
        """
        score = results['overall_compliance']
        emoji = '✅' if score >= 90 else '⚠️' if score >= 70 else '❌'
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Network Compliance Report"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Overall Score:*\n{score}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Devices Checked:*\n{results['total_devices']}"
                    }
                ]
            }
        ]
        
        # Add device breakdown
        device_text = ""
        for device_result in results['device_results']:
            score_emoji = '✅' if device_result['compliance_score'] >= 90 else '⚠️'
            device_text += f"{score_emoji} *{device_result['device']}*: {device_result['compliance_score']}%\n"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Device Scores:*\n{device_text}"
            }
        })
        
        return self.send_message("Network Compliance Report", blocks)
    
    def send_deployment_notification(self, device, success):
        """
        Send deployment notification to Slack
        
        Args:
            device (str): Device hostname
            success (bool): Whether deployment was successful
        """
        emoji = '✅' if success else '❌'
        status = "Successful" if success else "Failed"
        color = "good" if success else "danger"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Configuration Deployment {status}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Device:*\n{device}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{status}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Timestamp:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]
        
        return self.send_message(f"Deployment {status} - {device}", blocks)


def load_notification_config(config_file='config/notifications.json'):
    """
    Load notification configuration from JSON file
    
    Args:
        config_file (str): Path to config file
        
    Returns:
        dict: Notification configuration
    """
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Notification config not found: {config_file}")
        return {}
    except Exception as e:
        logger.error(f"Error loading notification config: {str(e)}")
        return {}


def get_email_notifier(config=None):
    """Create and return EmailNotifier from config"""
    if not config:
        config = load_notification_config()
    
    email_config = config.get('email', {})
    if not email_config.get('enabled', False):
        return None
    
    return EmailNotifier(
        smtp_server=email_config['smtp_server'],
        smtp_port=email_config['smtp_port'],
        username=email_config['username'],
        password=email_config['password'],
        from_email=email_config['from_email'],
        use_tls=email_config.get('use_tls', True)
    )


def get_slack_notifier(config=None):
    """Create and return SlackNotifier from config"""
    if not config:
        config = load_notification_config()
    
    slack_config = config.get('slack', {})
    if not slack_config.get('enabled', False):
        return None
    
    return SlackNotifier(webhook_url=slack_config['webhook_url'])
