from app.rag.search import retrieve
import json

def search_incident_docs(query: str):
    """Search historical incident documentation using the RAG pipeline."""
    result= retrieve(query)
    return json.dumps(result, default=str)

def search_logs(service: str, query: str, time_range: str) -> list:
    """Search service logs for matching errors or events."""
    return [
        {
            "timestamp": "2026-10-05 10:21:43",
            "service": service,
            "level": "ERROR",
            "message": "Database connection timeout"
        },
        {
            "timestamp": "2026-10-05 10:22:10",
            "service": service,
            "level": "ERROR",
            "message": "Request timeout after 5000ms"
        }
    ]

def get_metrics(service: str, time_range: str)-> dict:
    """Retrieve operational metrics for a service."""
    return {
        "service": service,
        "time_range": time_range,
        "latency_ms": 850,
        "error_rate": 0.08,
        "request_count": 12500,
        "cpu_usage_percent": 72,
        "memory_usage_percent": 68
    }
    results = []
    for log in logs:
        if log["service"] != service:
            continue
        if query.lower() in log["message"].lower():
            results.append(log)
    return json.dumps(results)
def get_recent_deployments(service: str, time_range: str)-> list:
    """Retrieve recent deployments and code changes for a service."""
    return [
        {
            "service": service,
            "version": "2.4.1",
            "commit": "a82f91c",
            "deployment_timestamp": "2026-10-05 09:45:00"
        },
        {
            "service": service,
            "version": "2.4.0",
            "commit": "71bc42a",
            "deployment_timestamp": "2026-10-03 14:20:00"
        }
    ]
    results = [
        deployment
        for deployment in deployments
        if deployment["service"] == service
    ]
    return json.dumps(results)