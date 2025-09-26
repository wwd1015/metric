"""
Posit Connect deployment script for demo_simple_calculator.

This script creates a FastAPI application specifically for this metric
that can be deployed to Posit Connect.
"""

import os
from cap.api import create_api_app

# Import the metric to ensure it's registered
from cap.metrics.demo_simple_calculator import calculate_simple_calculator

# Create the FastAPI app with all registered metrics
app = create_api_app()

# Add custom root endpoint for this specific metric
@app.get("/", tags=["Metric Info"])
async def metric_info():
    """Get information about this specific metric deployment."""
    return {
        "metric_id": "demo_simple_calculator",
        "function_name": "calculate_simple_calculator",
        "status": "active",
        "endpoints": [
            "/metrics",
            "/calculate",
            "/calculate/demo_simple_calculator",
            "/calculate/demo_simple_calculator/html",
            "/calculate/demo_simple_calculator/csv",
            "/docs"
        ],
        "description": "Commercial Analytical Platform (CAP) deployment for demo_simple_calculator"
    }

# For local testing
if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    reload = os.environ.get("RELOAD", "false").lower() == "true"
    
    print(f"Starting demo_simple_calculator deployment...")
    print(f"URL: http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Metric HTML: http://{host}:{port}/calculate/demo_simple_calculator/html")
    
    uvicorn.run("deploy_demo_simple_calculator:app", host=host, port=port, reload=reload)
