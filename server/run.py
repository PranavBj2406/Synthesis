import os
import sys
from dotenv import load_dotenv

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from app import create_app

# Create Flask app
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Flask development server...")
    print(f"📊 Environment: {app.config['FLASK_ENV']}")
    print(f"🔧 Debug mode: {app.config['DEBUG']}")
    print(f"🌐 Server: http://{app.config['HOST']}:{app.config['PORT']}")
    print("=" * 50)
    
    try:
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)