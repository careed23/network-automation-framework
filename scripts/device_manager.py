import yaml
import logging
# Netmiko is used for network connectivity, which is implied by the framework design.
from netmiko import ConnectHandler 

logger = logging.getLogger(__name__)


class DeviceManager:
    """Handles secure SSH connections and basic operations using Netmiko"""
    
    def __init__(self, device_config):
        """
        Initialize Device Manager
        
        Args:
            device_config (dict): Device configuration dictionary
        """
        self.device_config = device_config
        self.connection = None
        self.connected = False
        
    def connect(self):
        """Establish connection to the network device"""
        try:
            # We use a copy of the config to avoid modifying the original dictionary
            connect_config = self.device_config.copy()
            
            # Netmiko requires 'host' instead of 'ip' in some contexts, but 'host' is safer
            connect_config['host'] = connect_config.pop('host') 
            
            logger.info(f"Connecting to {connect_config['host']}")
            
            self.connection = ConnectHandler(**connect_config)
            self.connected = True
            logger.info(f"Successfully connected to {connect_config['host']}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {self.device_config['host']}: {str(e)}")
            self.connected = False
            return False

    def disconnect(self):
        """Close the connection to the network device"""
        if self.connection:
            self.connection.disconnect()
            self.connected = False
            logger.info(f"Disconnected from {self.device_config['host']}")

    def send_command(self, command):
        """Send a single command to the device"""
        if not self.connection:
            logger.error("No active connection")
            return None
        
        try:
            output = self.connection.send_command(command)
            return output
        except Exception as e:
            logger.error(f"Failed to send command: {str(e)}")
            return None

    # START OF THE CODE YOU PROVIDED, NOW CORRECTLY INDENTED

    def send_config(self, config_commands):
        """
        Send configuration commands to device
        
        Args:
            config_commands (list): List of configuration commands
            
        Returns:
            str: Configuration output
        """
        if not self.connection:
            logger.error("No active connection")
            return None
        
        try:
            output = self.connection.send_config_set(config_commands)
            logger.info(f"Configuration applied: {len(config_commands)} commands")
            return output
        except Exception as e:
            logger.error(f"Failed to apply configuration: {str(e)}")
            return None
    
    def get_running_config(self):
        """
        Retrieve running configuration from device
        
        Returns:
            str: Running configuration
        """
        device_type = self.device_config.get('device_type', '')
        
        if 'cisco' in device_type:
            command = 'show running-config'
        elif 'juniper' in device_type:
            command = 'show configuration'
        elif 'arista' in device_type:
            command = 'show running-config'
        else:
            command = 'show running-config'
        
        return self.send_command(command)
    
    def save_config(self):
        """Save configuration on device"""
        device_type = self.device_config.get('device_type', '')
        
        try:
            if 'cisco' in device_type:
                self.connection.save_config()
            elif 'juniper' in device_type:
                self.send_command('commit')
            else:
                self.connection.save_config()
            
            logger.info(f"Configuration saved on {self.device_config['host']}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            return False

# END OF THE CLASS DEFINITION

def load_devices_from_yaml(yaml_file):
    # ... (code for try block)
    try:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('devices', [])
    except Exception as e: # Note the 'as e' for error message use
        logger.error(f"Failed to load devices from {yaml_file}: {str(e)}")
        return [] # This return statement must be indented

# ... rest of the file
