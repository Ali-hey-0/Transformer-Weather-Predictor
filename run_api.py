#!/usr/bin/env python3
"""
Weather Forecasting API Server
Enhanced with beautiful web interface and interactive charts
"""

import uvicorn
from api.main import app

if __name__ == "__main__":
    print("🌤️  Starting Weather Forecasting API Server...")
    print("📊 Interactive web interface available at: http://localhost:8000")
    print("📚 API documentation available at: http://localhost:8000/docs")
    print("🔗 Direct API endpoint: http://localhost:8000/api/predict")
    print("\n" + "="*50)
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )