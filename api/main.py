from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import json
from datetime import datetime, timedelta

# Try to import predictor, but handle gracefully if it fails
try:
    from .predictor import predict_temperature
    PREDICTOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import predictor: {e}")
    PREDICTOR_AVAILABLE = False
except Exception as e:
    print(f"Warning: Error importing predictor: {e}")
    PREDICTOR_AVAILABLE = False

app = FastAPI(
    title="Weather Forecasting API",
    description="API for predicting temperature using Transformer model",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variable to store predictions
prediction_cache = None
last_prediction_time = None

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
def api_root():
    return {
        "message": "Weather Forecasting API",
        "endpoints": {
            "/docs": "API documentation",
            "/api/predict": "Get temperature forecast for next 72 hours",
            "/": "Interactive web interface"
        }
    }

@app.get("/api/predict", summary="Get temperature forecast")
def predict():
    """Get temperature forecast for the next 72 hours"""
    global prediction_cache, last_prediction_time
    
    # If we have a recent prediction (within 1 minute), return it
    if prediction_cache and last_prediction_time and (datetime.now() - last_prediction_time).seconds < 60:
        return prediction_cache
    
    # Otherwise generate new prediction
    if not PREDICTOR_AVAILABLE:
        # Generate fallback data
        now = datetime.now()
        prediction = {
            "error": "Model not available",
            "message": "The AI model is not currently available. Please ensure all dependencies are installed.",
            "forecast_hours": 72,
            "temperatures": [20.0] * 72,
            "timestamps": [],
            "unit": "Celsius",
            "generated_at": now.isoformat()
        }
    else:
        try:
            # Get new prediction
            temperatures = predict_temperature()
            
            # Generate timestamps for the next 72 hours
            now = datetime.now()
            timestamps = []
            for i in range(72):
                timestamp = now + timedelta(hours=i)
                timestamps.append(timestamp.strftime("%Y-%m-%d %H:%M"))
            
            prediction = {
                "forecast_hours": 72,
                "temperatures": temperatures,
                "timestamps": timestamps,
                "unit": "Celsius",
                "generated_at": now.isoformat()
            }
        except Exception as e:
            # Fallback data on error
            now = datetime.now()
            prediction = {
                "error": "Prediction failed",
                "message": str(e),
                "forecast_hours": 72,
                "temperatures": [20.0] * 72,
                "timestamps": [],
                "unit": "Celsius",
                "generated_at": now.isoformat()
            }
    
    # Cache the prediction
    prediction_cache = prediction
    last_prediction_time = datetime.now()
    
    return prediction

@app.get("/forecast", response_class=HTMLResponse)
def forecast_page(request: Request):
    return templates.TemplateResponse("forecast.html", {"request": request})

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "predictor_available": PREDICTOR_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }