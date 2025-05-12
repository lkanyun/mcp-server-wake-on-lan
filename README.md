# Wake-on-LAN MCP Server


## Overview

A Model Context Protocol (MCP) server that allows you to remotely wake up devices on your local network. This MCP server is intentionally designed to be simple, straightforward, and requires minimal setup. The core implementation is less than 100 lines of code.

## Features

* Wake up network devices using MAC addresses
* Support for standard Wake-on-LAN protocol
* Dual transport modes: SSE and stdio
* Simple command-line interface

## Example Prompts

```
Wake up my home desktop (MAC: 00:11:22:33:44:55)
```
## Usage with Claude Desktop

### Python

#### Install uv


```
brew install uv
git clone ...
```

#### Run the server

```
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
