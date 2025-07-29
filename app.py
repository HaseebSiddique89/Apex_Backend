#!/usr/bin/env python3
"""
Apex Backend - Main Application Entry Point
A comprehensive backend for image processing, 3D model generation, and AR content creation.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quart import Quart
from backend.auth import auth_bp
from backend.image_processing import image_bp
from backend.config import Config

def create_app():
    """Create and configure the Quart application"""
    app = Quart(__name__)
    
    # Configuration
    app.config.from_object(Config)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(image_bp, url_prefix='/image')
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting Apex Backend Server...")
    print("📡 Server will run on http://127.0.0.1:5000")
    print("📚 API Documentation: POSTMAN_TESTING_GUIDE.md")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False
    ) 