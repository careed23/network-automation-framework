"""
Web Dashboard for Network Automation
Flask-based dashboard for monitoring and managing network automation tasks
"""

from flask import Flask, render_template, jsonify, request, send_file
import os
import json
import logging
from datetime import datetime
import sys

# Add scripts directory to path
# This allows us to import other modules in the scripts/ folder
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from config_backup import ConfigBackup
from config_deploy import ConfigDeploy
from config_compliance import ComplianceChecker
from device_manager import load_devices_from_yaml

# --- SMART TEMPLATE DETECTION ---
# We check both possible locations for the dashboard.html file
possible_paths = [
    os.path.join(current_dir, '..', 'templates'),          # Standard root templates/
    os.path.join(current_dir, '..', 'config', 'templates') # Original config/templates/
]

template_folder_path = None

print("-" * 60)
print("🔍 Searching for dashboard.html...")

for path in possible_paths:
    full_path = os.path.abspath(path)
    check_file = os.path.join(full_path, 'dashboard.html')
    
    if os.path.exists(check_file):
        template_folder_path = full_path
        print(f"✅ FOUND template at: {check_file}")
        break
    else:
        print(f"❌ Not found at: {check_file}")

if not template_folder_path:
    print("\n⚠️ CRITICAL ERROR: 'dashboard.html' was not found in any expected folder.")
    print("Please ensure the file exists in either 'templates/' or 'config/templates/'.")
    # Fallback to root templates to allow app to initialize (will 404 on load)
    template_folder_path = os.path.join(current_dir, '..', 'templates')
print("-" * 60)

# Initialize Flask with the detected folder
app = Flask(__name__, template_folder=template_folder_path)
app.config['SECRET_KEY'] = 'your-your-secret-key-change-this'

logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/devices')
def get_devices():
    """Get list of devices"""
    try:
        devices = load_devices_from_yaml('config/devices.yaml')
        device_list = []
        
        for device in devices:
            device_list.append({
                'host': device['host'],
                'type': device['device_type'],
                'username': device['username']
            })
        
        return jsonify({'success': True, 'devices': device_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/backups')
def get_backups():
    """Get list of backups"""
    try:
        backup_dir = 'backups'
        backups = []
        
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                if filename.endswith('.txt'):
                    filepath = os.path.join(backup_dir, filename)
                    stat = os.stat(filepath)
                    
                    # Parse filename: host_timestamp.txt
                    parts = filename.replace('.txt', '').rsplit('_', 2)
                    host = parts[0] if len(parts) >= 3 else 'unknown'
                    
                    backups.append({
                        'filename': filename,
                        'host': host,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'path': filepath
                    })
        
        backups.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify({'success': True, 'backups': backups})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/backup/run', methods=['POST'])
def run_backup():
    """Run backup job"""
    try:
        backup_manager = ConfigBackup()
        results = backup_manager.backup_all_devices()
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/compliance/check', methods=['POST'])
def check_compliance():
    """Run compliance check"""
    try:
        checker = ComplianceChecker()
        results = checker.check_all_devices(check_live=False)
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        logger.error(f"Compliance check failed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/compliance/rules')
def get_compliance_rules():
    """Get compliance rules"""
    try:
        with open('config/compliance_rules.json', 'r') as f:
            rules_data = json.load(f)
        
        return jsonify({
            'success': True,
            'rules': rules_data['rules']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/deploy', methods=['POST'])
def deploy_config():
    """Deploy configuration"""
    try:
        data = request.json
        host = data.get('host')
        commands = data.get('commands', [])
        
        if not host or not commands:
            return jsonify({'success': False, 'error': 'Host and commands required'})
        
        # Load device config
        devices = load_devices_from_yaml('config/devices.yaml')
        device_config = next((d for d in devices if d['host'] == host), None)
        
        if not device_config:
            return jsonify({'success': False, 'error': 'Device not found'})
        
        # Deploy
        deploy_manager = ConfigDeploy()
        success = deploy_manager.deploy_commands(device_config, commands)
        
        return jsonify({
            'success': success,
            'message': 'Deployment successful' if success else 'Deployment failed'
        })
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/logs')
def get_logs():
    """Get recent log entries"""
    try:
        log_file = 'logs/network_automation.log'
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Get last 100 lines
                recent_lines = lines[-100:]
                
                for line in recent_lines:
                    logs.append(line.strip())
        
        return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    try:
        # Count devices
        devices = load_devices_from_yaml('config/devices.yaml')
        device_count = len(devices)
        
        # Count backups
        backup_dir = 'backups'
        backup_count = 0
        if os.path.exists(backup_dir):
            backup_count = len([f for f in os.listdir(backup_dir) if f.endswith('.txt')])
        
        # Get latest backup time
        latest_backup = None
        if os.path.exists(backup_dir):
            backups = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith('.txt')]
            if backups:
                latest_backup_file = max(backups, key=os.path.getmtime)
                latest_backup = datetime.fromtimestamp(os.path.getmtime(latest_backup_file)).isoformat()
        
        # Count compliance rules
        rules_count = 0
        try:
            with open('config/compliance_rules.json', 'r') as f:
                rules_data = json.load(f)
                rules_count = len(rules_data.get('rules', []))
        except:
            pass
        
        return jsonify({
            'success': True,
            'stats': {
                'devices': device_count,
                'backups': backup_count,
                'rules': rules_count,
                'latest_backup': latest_backup
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/download/<path:filename>')
def download_backup(filename):
    """Download a backup file"""
    try:
        filepath = os.path.join('backups', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
