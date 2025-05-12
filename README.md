# Wake-on-LAN MCP Server

## Overview

A Model Context Protocol (MCP) server that allows you to remotely wake up devices on your local network. This MCP server is intentionally designed to be simple, straightforward, and requires minimal setup. The core implementation is less than 100 lines of code.

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
    "wake_on_lans": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/repo",
        "run",
        "mcp-wake-on-lan"
      ]
    }
  }
}
```

