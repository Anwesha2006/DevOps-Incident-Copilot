import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Path to MCP server
SERVER_PATH = Path(__file__).resolve().parent.parent / "mcp" / "server.py"


async def call_mcp_tool(tool_name: str, arguments: dict):

    server_params = StdioServerParameters(
        command="python",
        args=[str(SERVER_PATH)],
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # Initialize MCP connection
            await session.initialize()

            # Call requested MCP tool
            result = await session.call_tool(
                tool_name,
                arguments
            )

            return result


async def search_logs_async(
    service: str,
    query: str,
    time_range: str
):

    return await call_mcp_tool(
        "search_logs",
        {
            "service": service,
            "query": query,
            "time_range": time_range
        }
    )


async def get_metrics_async(
    service: str,
    time_range: str
):

    return await call_mcp_tool(
        "get_metrics",
        {
            "service": service,
            "time_range": time_range
        }
    )


async def get_recent_deployments_async(
    service: str,
    time_range: str
):

    return await call_mcp_tool(
        "get_recent_deployments",
        {
            "service": service,
            "time_range": time_range
        }
    )


# Test the connection
async def main():

    print("\nTesting MCP connection...")
    print("=" * 50)

    result = await search_logs_async(
        "checkout",
        "timeout",
        "last_30_minutes"
    )

    print("\nSearch logs result:")
    print(result)

    result = await get_metrics_async(
        "checkout",
        "last_30_minutes"
    )

    print("\nMetrics result:")
    print(result)

    result = await get_recent_deployments_async(
        "checkout",
        "last_24_hours"
    )

    print("\nDeployment result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())