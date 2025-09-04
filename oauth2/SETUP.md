# OAuth2 Demo Setup

## Quick Start

1. **Configure your IP address:**
   ```bash
   cp .env.example .env
   # Edit .env and set HOST_IP to your desired IP
   ```

2. **create the virtual environment** (If not already done)
   ```bash
   uv init && uv sync
   ```
   
3. **Start the demo:**
   ```bash
   python3 start_oauth_demo.py
   ```

4. **Access the application:**
   - Open your browser to: `http://YOUR_IP:5052`
   - Click "Login with OAuth2" to test the flow

## Configuration Examples

### For Local Development
```env
HOST_IP=localhost
```

### For Public Server
```env
HOST_IP=your.server.ip.address
```

### For Tailscale/VPN
```env
HOST_IP=100.x.x.x
```

### Auto-detection
```env
HOST_IP=
# Leave blank to auto-detect server IP
```

## Services

- **Client App**: `http://YOUR_IP:5052` (main interface)
- **Auth Server**: `http://YOUR_IP:5050` (handles OAuth flow)
- **Resource Server**: `http://YOUR_IP:5051` (protected resources)

## Alternative Launchers

- **With uv**: `uv run run_demo.py` (after setting `export HOST_IP=your.ip`)
- **Direct**: `python3 run_demo.py` (after setting environment variables)
