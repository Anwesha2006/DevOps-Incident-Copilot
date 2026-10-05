from mcp.server.mcpserver import MCPServer

mcp = MCPServer("DevOps Incident Copilot")


@mcp.tool()
def search_logs(service: str, query: str, time_range: str) -> list:
    """Search through service logs."""
    logs = [
        {
            "timestamp": "2026-10-05 10:21:43",
            "service": "checkout",
            "level": "ERROR",
            "message": "Database connection timeout"
        },
        {
            "timestamp": "2026-10-05 10:22:10",
            "service": "checkout",
            "level": "ERROR",
            "message": "Request timeout after 5000ms"
        },
        {
            "timestamp": "2026-10-05 10:23:01",
            "service": "payment",
            "level": "INFO",
            "message": "Payment request completed"
        }
    ]
    results=[]
    for log in logs:
        if log["service"] != service:
            continue
        if query.lower() in log["message"].lower():
            results.append(log)
    return results

@mcp.tool()
def get_metrics(service: str, time_range: str) -> dict:
    """retrieve operational metrics."""
    metrices={
        "service": service,
        "time_range": time_range,
        "latency_ms": 850,
        "error_rate": 0.08,
        "request_count": 12500,
        "cpu_usage_percent": 72,
        "memory_usage_percent": 68
    }
    return metrices

@mcp.tool()
def get_recent_deployments(service: str, time_range: str) -> list:
    """Find recent deployments or code changes."""
    deployments = [
        {
            "service": "checkout",
            "version": "2.4.1",
            "commit": "a82f91c",
            "deployment_timestamp": "2026-10-05 09:45:00"
        },
        {
            "service": "checkout",
            "version": "2.4.0",
            "commit": "71bc42a",
            "deployment_timestamp": "2026-10-03 14:20:00"
        }
    ]
    results=[]
    for deployment in deployments:
        if deployment["service"] == service:
            results.append(deployment)
    return results

if __name__ == "__main__":
    mcp.run()