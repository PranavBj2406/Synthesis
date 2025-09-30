#!/usr/bin/env python3
"""
Application entry point
Run this file to start the Flask development server
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress PyMongo DEBUG logs
logging.getLogger("pymongo").setLevel(logging.WARNING)
# Load environment variables
load_dotenv()

from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment variables
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("🚀 SYNTHESIS SERVER STARTING")
    print("=" * 60)
    print(f"📍 Server URL: http://{host}:{port}")
    print(f"🔧 Debug Mode: {debug}")
    print(f"🗄️  Database: {app.config.get('DATABASE_NAME', 'Not configured')}")
    print(f"🌍 Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    print("=" * 60)
    print("📋 Available Endpoints:")
    print("   GET  /api/health                    - Server health check")
    print("   GET  /api/auth/health               - Auth service health")
    print("   POST /api/auth/signup               - User registration")
    print("   POST /api/auth/signin               - User login")
    print("   POST /api/auth/check-email          - Check email availability")
    print("   POST /api/auth/check-username       - Check username availability")
    print("   POST /api/auth/validate-password    - Password validation")
    print("   GET  /api/auth/profile              - Get user profile (protected)")
    print("   POST /api/auth/logout               - User logout")
    print("   POST /api/auth/forgot-password      - Password reset request")
    print("   GET /api/healthcare-gan/health      - Health check")
    print("   GET /api/healthcare-gan/metrics     - Get training metrics")
    print("   POST /api/healthcare-gan/train      - Train GAN models")
    print("   POST /api/healthcare-gan/generate   - Generate synthetic healthcare")
    print("   GET  /api/healthcare-gan/status     - Integration status")
    print("   GET  /api/healthcare-gan/test       - Integration Test")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        sys.exit(1)