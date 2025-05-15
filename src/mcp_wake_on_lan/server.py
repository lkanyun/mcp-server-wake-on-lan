import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
import socket
import re
from typing import Dict, Optional
import json
from pathlib import Path

# 获取配置文件路径
def get_config_dir() -> Path:
    config_dir = Path.home() / '.config' / 'mcp-wake-on-lan'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

DEVICES_FILE = get_config_dir() / 'devices.json'

# 从文件加载设备信息
def load_device_info() -> Dict[str, str]:
    if DEVICES_FILE.exists():
        with open(DEVICES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 保存设备信息到文件
def save_device_info_to_file(devices: Dict[str, str]) -> None:
    with open(DEVICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(devices, f, ensure_ascii=False, indent=2)

# 初始化设备信息
device_info: Dict[str, str] = load_device_info()

# 全局变量存储广播地址
broadcast_address = "255.255.255.255"

async def wake_device_on_lan(
    mac_address: str
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    # 校验mac_address
    if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$', mac_address):
        raise ValueError("Invalid MAC address format")
    
    # 将MAC地址转换为二进制格式
    mac_bytes = bytes.fromhex(mac_address.replace('-', '').replace(':', ''))
    # 发送wake-on-lan包
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(b'\xff' * 6 + mac_bytes * 16, (broadcast_address, 9))
    sock.close()
    return [types.TextContent(type="text", text=f"Wake-on-LAN packet sent successfully to {broadcast_address}")]

async def save_device_info(
    mac_address: str,
    device_name: str
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    # 校验mac_address
    if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$', mac_address):
        raise ValueError("Invalid MAC address format")
    
    # 判断是更新还是新增
    is_update = mac_address in device_info
    
    # 保存或更新设备信息
    device_info[mac_address] = device_name
    
    # 保存到文件
    save_device_info_to_file(device_info)
    
    action = "更新" if is_update else "保存"
    return [types.TextContent(type="text", text=f"成功{action}设备信息：{device_name} ({mac_address})")]

async def list_devices() -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if not device_info:
        return [types.TextContent(type="text", text="当前没有保存任何设备信息")]
    
    # 构建设备列表信息
    device_list = ["已保存的设备列表："]
    for mac_address, name in device_info.items():
        device_list.append(f"- {name} ({mac_address})")
    
    return [types.TextContent(type="text", text="\n".join(device_list))]

async def delete_device(
    mac_address: str
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    # 校验mac_address
    if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$', mac_address):
        raise ValueError("Invalid MAC address format")
    
    # 检查设备是否存在
    if mac_address not in device_info:
        return [types.TextContent(type="text", text=f"设备记录不存在：{mac_address}")]
    
    # 获取设备名称并删除记录
    device_name = device_info[mac_address]
    del device_info[mac_address]
    
    # 保存更新后的设备信息到文件
    save_device_info_to_file(device_info)
    
    return [types.TextContent(type="text", text=f"成功删除设备记录：{device_name} ({mac_address})")]

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
@click.option(
    "--broadcast-addr",
    default="255.255.255.255",
    help="Default broadcast address for Wake-on-LAN packets",
)
def main(port: int, transport: str, broadcast_addr: str) -> int:
    global broadcast_address
    broadcast_address = broadcast_addr

    app = Server("mcp-wake-on-lan")

    @app.call_tool()
    async def call_tool(
        name: str, 
        arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name == "wake_device":
            return await wake_device_on_lan(arguments["mac_address"])
        elif name == "save_device_info":
            return await save_device_info(arguments["mac_address"], arguments["device_name"])
        elif name == "list_devices":
            return await list_devices()
        elif name == "delete_device":
            return await delete_device(arguments["mac_address"])
        else:
            raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="wake_device",
                description="Wake up a device by sending a Wake-on-LAN (WOL) magic packet. If you don't know the MAC address, use the list_devices command first to find the device information",
                inputSchema={
                    "type": "object",
                    "required": ["mac_address"],
                    "properties": {
                        "mac_address": {
                            "type": "string",
                            "description": "The MAC address of the device to wake up. If you don't know the MAC address, use list_devices command to check saved devices",
                        }
                    },
                },
            ),
            types.Tool(
                name="save_device_info",
                description="Save or update device information",
                inputSchema={
                    "type": "object",
                    "required": ["mac_address", "device_name"],
                    "properties": {
                        "mac_address": {
                            "type": "string",
                            "description": "The MAC address of the device",
                        },
                        "device_name": {
                            "type": "string",
                            "description": "The name of the device",
                        }
                    },
                },
            ),
            types.Tool(
                name="list_devices",
                description="List all saved devices",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="delete_device",
                description="Delete a device record by MAC address",
                inputSchema={
                    "type": "object",
                    "required": ["mac_address"],
                    "properties": {
                        "mac_address": {
                            "type": "string",
                            "description": "The MAC address of the device to delete",
                        }
                    },
                },
            )
        ]

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.responses import Response
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
            return Response()

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="::", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0