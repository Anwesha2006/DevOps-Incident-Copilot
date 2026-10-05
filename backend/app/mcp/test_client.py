import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # Initialize connection
            await session.initialize()

            # Get available tools
            tools = await session.list_tools()

            print("\nAvailable MCP tools:")
            print("=" * 50)

            for tool in tools.tools:
                print(tool.name)
                print(tool.description)
                print()

            # Test search_logs
            print("\nTesting search_logs...")
            print("=" * 50)

            result = await session.call_tool(
                "search_logs",
                {
                    "service": "checkout",
                    "query": "timeout",
                    "time_range": "last_30_minutes"
                }
            )

            print(result)

            # Test metrics
            print("\nTesting get_metrics...")
            print("=" * 50)

            result = await session.call_tool(
                "get_metrics",
                {
                    "service": "checkout",
                    "time_range": "last_30_minutes"
                }
            )

            print(result)

            # Test deployments
            print("\nTesting get_recent_deployments...")
            print("=" * 50)

            result = await session.call_tool(
                "get_recent_deployments",
                {
                    "service": "checkout",
                    "time_range": "last_24_hours"
                }
            )

            print(result)


if __name__ == "__main__":
    asyncio.run(main())