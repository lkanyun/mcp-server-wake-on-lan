# Wake-on-LAN MCP Server

## Overview

A Model Context Protocol (MCP) server that allows you to remotely wake up devices on your local network. This MCP server is intentionally designed to be simple, straightforward, and requires minimal setup. 

## Features

* Wake up network devices using MAC addresses
* Save and manage device information (name and MAC address)
* List all saved devices
* Delete device records
* Support for standard Wake-on-LAN protocol
* Dual transport modes: SSE and stdio
* Simple command-line interface

## Example Prompts

```text
# Wake up a device
Wake up my home desktop (MAC: 00:11:22:33:44:55)

# Save device information
Save my desktop PC with MAC address 00:11:22:33:44:55

# List all saved devices
Show me all my saved devices

# Wake up an existing device
Wake up my desktop PC

# Delete a device record
Remove the device with MAC address 00:11:22:33:44:55

# Delete a device record by name
Remove the mac record of my desktop PC
```

## Device Management

The server stores device information in `~/.config/mcp-wake-on-lan/devices.json`. This allows you to:
- Save device names along with their MAC addresses
- List all saved devices
- Delete device records when needed

## Usage with Claude Desktop

### Installation

```bash
brew install uv
git clone ...
```

### Configuration

Add the following configuration to Claude Desktop:

```json
{
  "mcpServers": {
    "mcp-wake-on-lan": {
      "command": "uvx",
      "args": [
        "mcp-wake-on-lan",
        "--broadcast-addr",
        "192.168.1.255"
      ]
    }
  }
}
```
### Docker Deployment

#### Docker Run

```bash
docker run -d --network host lkanyun/mcp-server-wake-on-lan --broadcast-addr 192.168.1.255
```

#### Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3'
services:
  mcp-wake-on-lan:
    image: lkanyun/mcp-server-wake-on-lan
    network_mode: host
    volumes:
      - /your_path:/root/.config/mcp-wake-on-lan
    command:
      - --broadcast-addr
      - 192.168.1.255
    restart: unless-stopped
```

Run:

```bash
docker compose up -d
```

Note: `network_mode: host` is required to ensure Wake-on-LAN magic packets can be properly sent to the local network.

#### Config on Claude Desktop
``` json
{
  "mcpServers": {
    "mcp-server-wake-on-lan": {
      "type": "sse",
      "url": "http://yourip:8000/sse"
    }
  }
}
```