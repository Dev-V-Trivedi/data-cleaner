#!/usr/bin/env python3
"""
Quick verification script for production deployment
"""

import sys
import importlib

def check_dependencies():
    """Check if all required dependencies are available."""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_classifiers():
    """Check if classifiers can be imported."""
    try:
        from enhanced_column_classifier import EnhancedColumnClassifier
        print("✅ Enhanced Column Classifier - OK")
        enhanced_available = True
    except ImportError as e:
        print(f"⚠️  Enhanced Column Classifier - UNAVAILABLE ({e})")
        enhanced_available = False
    
    try:
        from column_classifier import ColumnClassifier
        print("✅ Basic Column Classifier - OK")
        basic_available = True
    except ImportError as e:
        print(f"❌ Basic Column Classifier - MISSING ({e})")
        basic_available = False
    
    return enhanced_available or basic_available

def check_main_app():
    """Check if main app can be imported."""
    try:
        from main_simple import app
        print("✅ Main FastAPI App - OK")
        return True
    except ImportError as e:
        print(f"❌ Main FastAPI App - ERROR ({e})")
        return False

def main():
    print("🔍 Data Cleaner Backend - Deployment Verification")
    print("=" * 50)
    
    all_good = True
    
    print("\n📦 Checking Dependencies...")
    if not check_dependencies():
        all_good = False
    
    print("\n🧠 Checking Classifiers...")
    if not check_classifiers():
        all_good = False
    
    print("\n🚀 Checking Main Application...")
    if not check_main_app():
        all_good = False
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 All checks passed! Ready for deployment.")
        print("\n📋 Next Steps:")
        print("1. Push to GitHub")
        print("2. Deploy to Render")
        print("3. Update frontend API URL")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n🔧 Possible Solutions:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Check file paths and imports")
        print("3. Verify all files are in the correct location")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
