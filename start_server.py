#!/usr/bin/env python3
"""
Kimi K2 Web Server Launcher
Starts the appropriate server based on environment or user choice
"""

import os
import sys

def main():
    """Launch the appropriate server"""
    
    # Check if we're in production (environment variable set by hosting platforms)
    is_production = os.environ.get('PORT') is not None or '--production' in sys.argv
    use_gui = '--gui' in sys.argv or os.environ.get('USE_GUI') == '1'
    
    print("=" * 80)
    print("🔥 Kimi K2 - THE FORGE AI")
    print("=" * 80)
    
    if use_gui:
        print("\n✨ Starting Web GUI Interface...")
        print("📍 Access at http://localhost:5000")
        from forge_gui import app
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=not is_production)
    else:
        print("\n⚡ Starting REST API Server...")
        print("📍 API at http://localhost:5000")
        print("🔍 Health check: http://localhost:5000/health")
        
        if is_production:
            # In production, use gunicorn (called via Procfile)
            # This script is mainly for local development
            print("\n⚠️  Production mode: Use gunicorn directly")
            print("   gunicorn forge_server:app --bind 0.0.0.0:$PORT")
        else:
            # Development mode
            from forge_server import app, initialize_forge
            initialize_forge()
            port = int(os.environ.get('PORT', 5000))
            app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

if __name__ == '__main__':
    main()
