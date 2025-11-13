"""
Performance Monitoring and Metrics
Simple in-memory metrics for tracking API performance
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Metrics storage
request_metrics: Dict[str, List[dict]] = defaultdict(list)
endpoint_stats: Dict[str, dict] = defaultdict(lambda: {
    "total_requests": 0,
    "total_time": 0,
    "min_time": float('inf'),
    "max_time": 0,
    "errors": 0,
    "success": 0
})

def record_request(endpoint: str, method: str, status_code: int, process_time: float, api_key: str = "anonymous"):
    """
    Record a request metric
    
    Args:
        endpoint: API endpoint path
        method: HTTP method
        status_code: Response status code
        process_time: Request processing time in seconds
        api_key: API key used (masked)
    """
    metric = {
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "process_time": process_time,
        "api_key": api_key[:10] + "..." if len(api_key) > 10 else api_key,
        "timestamp": datetime.now()
    }
    
    # Store individual request
    request_metrics[endpoint].append(metric)
    
    # Update endpoint statistics
    stats = endpoint_stats[endpoint]
    stats["total_requests"] += 1
    stats["total_time"] += process_time
    stats["min_time"] = min(stats["min_time"], process_time)
    stats["max_time"] = max(stats["max_time"], process_time)
    
    if 200 <= status_code < 300:
        stats["success"] += 1
    else:
        stats["errors"] += 1
    
    # Clean old metrics (keep last hour)
    clean_old_metrics(endpoint)

def clean_old_metrics(endpoint: str, hours: int = 1):
    """Remove metrics older than specified hours"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    request_metrics[endpoint] = [
        m for m in request_metrics[endpoint]
        if m["timestamp"] > cutoff_time
    ]

def get_endpoint_stats(endpoint: str = None) -> dict:
    """
    Get statistics for an endpoint or all endpoints
    
    Args:
        endpoint: Specific endpoint or None for all
        
    Returns:
        dict: Statistics including avg time, request count, error rate
    """
    if endpoint:
        stats = endpoint_stats.get(endpoint, {})
        if not stats or stats["total_requests"] == 0:
            return {}
        
        return {
            "endpoint": endpoint,
            "total_requests": stats["total_requests"],
            "success_rate": stats["success"] / stats["total_requests"] * 100,
            "error_rate": stats["errors"] / stats["total_requests"] * 100,
            "avg_time": stats["total_time"] / stats["total_requests"],
            "min_time": stats["min_time"] if stats["min_time"] != float('inf') else 0,
            "max_time": stats["max_time"]
        }
    
    # Return all endpoints
    return {
        ep: get_endpoint_stats(ep)
        for ep in endpoint_stats.keys()
        if endpoint_stats[ep]["total_requests"] > 0
    }

def get_recent_requests(endpoint: str = None, limit: int = 10) -> List[dict]:
    """
    Get recent requests for an endpoint
    
    Args:
        endpoint: Specific endpoint or None for all
        limit: Maximum number of requests to return
        
    Returns:
        List of recent request metrics
    """
    if endpoint:
        requests = request_metrics.get(endpoint, [])
        return sorted(requests, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    # Get from all endpoints
    all_requests = []
    for requests in request_metrics.values():
        all_requests.extend(requests)
    
    return sorted(all_requests, key=lambda x: x["timestamp"], reverse=True)[:limit]

def get_slow_requests(threshold_seconds: float = 5.0, limit: int = 10) -> List[dict]:
    """
    Get slowest requests above threshold
    
    Args:
        threshold_seconds: Minimum processing time
        limit: Maximum number of requests to return
        
    Returns:
        List of slow requests
    """
    all_requests = []
    for requests in request_metrics.values():
        all_requests.extend([r for r in requests if r["process_time"] > threshold_seconds])
    
    return sorted(all_requests, key=lambda x: x["process_time"], reverse=True)[:limit]

def get_error_requests(limit: int = 10) -> List[dict]:
    """
    Get recent error requests
    
    Args:
        limit: Maximum number of requests to return
        
    Returns:
        List of error requests
    """
    all_requests = []
    for requests in request_metrics.values():
        all_requests.extend([r for r in requests if r["status_code"] >= 400])
    
    return sorted(all_requests, key=lambda x: x["timestamp"], reverse=True)[:limit]

def get_metrics_summary() -> dict:
    """Get overall metrics summary"""
    total_requests = sum(stats["total_requests"] for stats in endpoint_stats.values())
    total_success = sum(stats["success"] for stats in endpoint_stats.values())
    total_errors = sum(stats["errors"] for stats in endpoint_stats.values())
    
    if total_requests == 0:
        return {
            "total_requests": 0,
            "success_rate": 0,
            "error_rate": 0,
            "endpoints": 0
        }
    
    return {
        "total_requests": total_requests,
        "success_rate": total_success / total_requests * 100,
        "error_rate": total_errors / total_requests * 100,
        "endpoints": len([ep for ep in endpoint_stats if endpoint_stats[ep]["total_requests"] > 0]),
        "top_endpoints": sorted(
            endpoint_stats.items(),
            key=lambda x: x[1]["total_requests"],
            reverse=True
        )[:5]
    }

def reset_metrics():
    """Reset all metrics (for testing or periodic cleanup)"""
    request_metrics.clear()
    endpoint_stats.clear()
    logger.info("All metrics have been reset")
