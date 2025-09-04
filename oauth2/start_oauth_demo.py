#!/usr/bin/env python3
"""
OAuth2 Demo Launcher

This script loads configuration from .env file for flexible deployment.
Supports local development, public servers, Tailscale, Docker, etc.
"""

import os
import subprocess
import sys
from pathlib import Path

def load_env_file(env_file=".env"):
    """Load environment variables from .env file"""
    env_path = Path(env_file)
    if not env_path.exists():
        print(f"⚠️  No {env_file} file found. Using auto-detection.")
        return {}
    
    env_vars = {}
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"⚠️  Error loading {env_file}: {e}")
    
    return env_vars

def get_server_ip():
    """Get the server's IP address as fallback"""
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            ips = result.stdout.strip().split()
            if ips:
                return ips[0]
    except Exception:
        pass
    return 'localhost'

def main():
    # Load environment variables from .env file
    env_vars = load_env_file()
    
    # Determine HOST_IP
    host_ip = env_vars.get('HOST_IP', '').strip()
    if not host_ip:
        host_ip = get_server_ip()
        print(f"🔍 Auto-detected server IP: {host_ip}")
    else:
        print(f"📝 Using configured IP from .env: {host_ip}")
    
    print(f"🚀 Setting up OAuth2 demo...")
    print(f"📡 Services will be accessible at:")
    print(f"   - Authorization Server: http://{host_ip}:5050")
    print(f"   - Resource Server: http://{host_ip}:5051") 
    print(f"   - Client Application: http://{host_ip}:5052")
    print()
    print("🔥 Starting servers...")
    print("   Press Ctrl+C to stop all servers")
    print()
    
    # Set up environment
    env = os.environ.copy()
    env['HOST_IP'] = host_ip
    
    # Add any other env vars from .env file
    for key, value in env_vars.items():
        env[key] = value
    
    try:
        # Use uv to run the demo
        subprocess.run(['uv', 'run', 'run_demo.py'], env=env)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)
    except FileNotFoundError:
        print("❌ Error: 'uv' command not found.")
        print("💡 Alternatives:")
        print("   1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("   2. Use Python directly: pip install flask requests && python3 run_demo.py")
        sys.exit(1)

if __name__ == '__main__':
    main()
