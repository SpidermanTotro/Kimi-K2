#!/usr/bin/env python3
"""
Simple test to verify the deployment works
Run this before deploying to ensure everything is configured correctly
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import flask
        print("  ✅ Flask imported successfully")
    except ImportError as e:
        print(f"  ❌ Flask import failed: {e}")
        return False
    
    try:
        from flask_cors import CORS
        print("  ✅ Flask-CORS imported successfully")
    except ImportError as e:
        print(f"  ❌ Flask-CORS import failed: {e}")
        return False
    
    try:
        import forge_implementation
        print("  ✅ forge_implementation imported successfully")
    except ImportError as e:
        print(f"  ❌ forge_implementation import failed: {e}")
        return False
    
    try:
        import forge_server
        print("  ✅ forge_server imported successfully")
    except ImportError as e:
        print(f"  ❌ forge_server import failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'forge_server.py',
        'forge_gui.py',
        'forge_implementation.py',
        'requirements.txt',
        'Procfile',
        'render.yaml',
        'runtime.txt',
        'DEPLOYMENT.md',
        'templates/index.html',
        'docs/README.md'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} not found")
            all_exist = False
    
    return all_exist

def test_server_initialization():
    """Test that the server can be initialized"""
    print("\n🔥 Testing server initialization...")
    
    try:
        from forge_implementation import ForgeAI
        forge = ForgeAI()
        forge.initialize()
        print("  ✅ ForgeAI initialized successfully")
        print(f"  ✅ Loaded {len(forge.loader.documents)} documents")
        print(f"  ✅ Total content: {len(forge.loader.all_content):,} characters")
        return True
    except Exception as e:
        print(f"  ❌ Server initialization failed: {e}")
        return False

def test_api_routes():
    """Test that API routes are properly defined"""
    print("\n🛣️  Testing API routes...")
    
    try:
        from forge_server import app
        
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        
        required_routes = [
            '/health',
            '/api/chat',
            '/api/capabilities',
            '/api/system-prompt',
        ]
        
        all_present = True
        for route in required_routes:
            if any(route in r for r in routes):
                print(f"  ✅ {route}")
            else:
                print(f"  ❌ {route} not found")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"  ❌ Route testing failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("🧪 Kimi K2 Deployment Test Suite")
    print("=" * 80)
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("File Structure", test_file_structure()))
    results.append(("Server Initialization", test_server_initialization()))
    results.append(("API Routes", test_api_routes()))
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:30} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("🎉 All tests passed! Ready for deployment.")
        print("\n📝 Next steps:")
        print("  1. Run './setup.sh' to install dependencies")
        print("  2. Test locally: python3 forge_server.py")
        print("  3. Deploy to free hosting - see DEPLOYMENT.md")
        print("=" * 80)
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues before deploying.")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())
