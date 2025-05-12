import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
import socket
import re


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
    sock.sendto(b'\xff' * 6 + mac_bytes * 16, ('255.255.255.255', 9))
    sock.close()
    return [types.TextContent(type="text", text="Wake-on-LAN packet sent successfully")]
    

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    app = Server("mcp-wake-on-lan")

    @app.call_tool()
    async def call_tool(
        name: str, 
        arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name == "wake_device":
            return await wake_device_on_lan(arguments["mac_address"])
        else:
            raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="wake_device",
                description="Wake up a device by sending a Wake-on-LAN (WOL) magic packet",
                inputSchema={
                    "type": "object",
                    "required": ["mac_address"],
                    "properties": {
                        "mac_address": {
                            "type": "string",
                            "description": "The MAC address of the device to wake up",
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

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0