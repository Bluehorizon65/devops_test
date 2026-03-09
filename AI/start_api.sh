#!/bin/bash

echo "🔋 ROOFTOP DETECTION API STARTUP"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing API requirements..."
pip install -r api_requirements.txt

# Start the API server
echo "🚀 Starting FastAPI server..."
echo "📡 API will be available at: http://localhost:8000"
echo "📚 API docs will be available at: http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

uvicorn rooftop_api:app --host 0.0.0.0 --port 8000 --reload