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


def load_devices_from_yaml(yaml_file):
    """
    Load device configurations from YAML file
    
    Args:
        yaml_file (str): Path to YAML file
        
    Returns:
        list: List of device configurations
    """
    try:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('devices', [])
    except Exception as e:
        logger.error(f"Failed to load devices from {yaml_file}: {str(e)}")
        return []
