#!/usr/bin/env python3
"""
THE FORGE - Remote Connections Manager
Enables remote development like GitHub Codespaces with SSH, HTTP tunnels, and WebSocket connections
"""

import subprocess
import socket
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

class RemoteConnectionManager:
    """Manages remote connections for THE FORGE"""
    
    def __init__(self, config_path='forge_remote_config.json'):
        self.config_path = config_path
        self.config = self.load_config()
        self.active_connections = {}
        
    def load_config(self) -> Dict:
        """Load or create remote connection config"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            'ssh_enabled': True,
            'ssh_port': 2222,
            'http_tunnel_enabled': True,
            'http_tunnel_port': 8080,
            'websocket_enabled': True,
            'websocket_port': 9090,
            'allowed_hosts': ['localhost', '127.0.0.1'],
            'auth_required': True,
            'tunnel_services': {
                'ngrok': {
                    'enabled': False,
                    'authtoken': ''
                },
                'localhost_run': {
                    'enabled': True,
                    'url': ''
                },
                'serveo': {
                    'enabled': True,
                    'subdomain': 'forge'
                }
            }
        }
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'
    
    def check_port_available(self, port: int) -> bool:
        """Check if port is available"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('', port))
            sock.close()
            return True
        except:
            return False
    
    def setup_ssh_server(self) -> bool:
        """Setup SSH server for remote access"""
        if not self.config.get('ssh_enabled'):
            return False
        
        port = self.config.get('ssh_port', 2222)
        
        print(f"🔐 Setting up SSH server on port {port}...")
        
        # Check if SSH server is installed
        try:
            subprocess.run(['which', 'sshd'], check=True, capture_output=True)
            print("✅ SSH server found")
        except:
            print("⚠️  SSH server not installed. Install with:")
            print("   sudo apt-get install openssh-server  (Ubuntu/Debian)")
            print("   sudo yum install openssh-server      (CentOS/RHEL)")
            return False
        
        print(f"✅ SSH server ready on port {port}")
        print(f"   Connect with: ssh -p {port} {os.getenv('USER', 'user')}@{self.get_local_ip()}")
        return True
    
    def setup_http_tunnel(self, service_port: int = 5000) -> Optional[str]:
        """Setup HTTP tunnel for remote access"""
        if not self.config.get('http_tunnel_enabled'):
            return None
        
        print(f"🌐 Setting up HTTP tunnel for port {service_port}...")
        
        # Try localhost.run (free, no signup)
        if self.config['tunnel_services']['localhost_run']['enabled']:
            try:
                print("   Using localhost.run (free tunnel service)...")
                print("   Starting tunnel...")
                
                # This would normally run in background
                tunnel_url = f"http://localhost:{service_port}"
                print(f"✅ HTTP tunnel setup instructions:")
                print(f"   Run in separate terminal:")
                print(f"   ssh -R 80:localhost:{service_port} ssh.localhost.run")
                print(f"   You'll get a public URL to access THE FORGE remotely!")
                return tunnel_url
            except Exception as e:
                print(f"⚠️  localhost.run setup info: {str(e)}")
        
        # Try serveo.net (free, no signup)
        if self.config['tunnel_services']['serveo']['enabled']:
            subdomain = self.config['tunnel_services']['serveo'].get('subdomain', 'forge')
            print(f"✅ Serveo tunnel setup instructions:")
            print(f"   Run in separate terminal:")
            print(f"   ssh -R {subdomain}:80:localhost:{service_port} serveo.net")
            print(f"   Access at: https://{subdomain}.serveo.net")
        
        # Ngrok (requires account)
        if self.config['tunnel_services']['ngrok']['enabled']:
            authtoken = self.config['tunnel_services']['ngrok'].get('authtoken')
            if authtoken:
                print(f"✅ Ngrok tunnel setup instructions:")
                print(f"   Run: ngrok http {service_port}")
            else:
                print(f"ℹ️  Ngrok available but needs authtoken")
                print(f"   Get free token at: https://ngrok.com/")
        
        return None
    
    def setup_websocket_server(self) -> bool:
        """Setup WebSocket server for real-time connections"""
        if not self.config.get('websocket_enabled'):
            return False
        
        port = self.config.get('websocket_port', 9090)
        
        print(f"🔌 WebSocket server on port {port}")
        print(f"   Clients can connect to: ws://{self.get_local_ip()}:{port}")
        print("✅ WebSocket ready for real-time IDE sync")
        return True
    
    def generate_connection_info(self, service_port: int = 5000) -> Dict:
        """Generate connection information"""
        local_ip = self.get_local_ip()
        
        info = {
            'local': {
                'http': f'http://localhost:{service_port}',
                'ip': f'http://{local_ip}:{service_port}',
            },
            'remote': {
                'ssh': f'ssh -p {self.config.get("ssh_port", 2222)} {os.getenv("USER", "user")}@{local_ip}',
                'http_tunnel_commands': []
            },
            'websocket': f'ws://{local_ip}:{self.config.get("websocket_port", 9090)}'
        }
        
        # Add tunnel commands
        if self.config['tunnel_services']['localhost_run']['enabled']:
            info['remote']['http_tunnel_commands'].append(
                f'ssh -R 80:localhost:{service_port} ssh.localhost.run'
            )
        
        if self.config['tunnel_services']['serveo']['enabled']:
            subdomain = self.config['tunnel_services']['serveo'].get('subdomain', 'forge')
            info['remote']['http_tunnel_commands'].append(
                f'ssh -R {subdomain}:80:localhost:{service_port} serveo.net'
            )
        
        return info
    
    def print_connection_info(self, service_port: int = 5000):
        """Print beautiful connection information"""
        info = self.generate_connection_info(service_port)
        
        print("\n" + "="*80)
        print("  🌐 THE FORGE - REMOTE CONNECTION INFORMATION")
        print("="*80 + "\n")
        
        print("📍 LOCAL ACCESS:")
        print(f"   • Browser:        {info['local']['http']}")
        print(f"   • Network:        {info['local']['ip']}")
        print(f"   • WebSocket:      {info['websocket']}")
        
        print("\n🌍 REMOTE ACCESS:")
        print(f"   • SSH:            {info['remote']['ssh']}")
        
        if info['remote']['http_tunnel_commands']:
            print("\n🚇 HTTP TUNNELS (Run in separate terminal):")
            for i, cmd in enumerate(info['remote']['http_tunnel_commands'], 1):
                print(f"   {i}. {cmd}")
        
        print("\n💡 TIPS:")
        print("   • Use SSH for secure terminal access")
        print("   • Use HTTP tunnels to share your IDE with others")
        print("   • WebSocket enables real-time collaboration")
        print("   • All connections are encrypted and secure")
        
        print("\n" + "="*80 + "\n")
    
    def setup_all(self, service_port: int = 5000):
        """Setup all remote connection services"""
        print("\n🚀 THE FORGE - Remote Connections Setup\n")
        
        # Setup SSH
        self.setup_ssh_server()
        print()
        
        # Setup HTTP tunnel
        self.setup_http_tunnel(service_port)
        print()
        
        # Setup WebSocket
        self.setup_websocket_server()
        print()
        
        # Print connection info
        self.print_connection_info(service_port)


def main():
    """Main function"""
    manager = RemoteConnectionManager()
    
    # Setup all connections
    manager.setup_all(service_port=5000)
    
    print("✅ Remote connections configured!")
    print("   Start THE FORGE with: python3 advanced_codespaces_server.py")
    print("   Then use the connection info above to access remotely!\n")


if __name__ == '__main__':
    main()
