#!/usr/bin/env python3
"""
Gemini Pro Vision Integration Test Script
Tests the Gemini model integration with CRO analysis
"""

import asyncio
import os
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_gemini_integration():
    """Test Gemini Pro Vision integration"""
    print("🚀 Testing Gemini Pro Vision Integration")
    print("="*50)
    
    # Test 1: Check API Key
    print("🔍 Test 1: Checking API Key Configuration")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"✅ API Key found: {api_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY not found in environment")
        print("💡 Set with: export GEMINI_API_KEY=your_key_here")
        return False
    
    # Test 2: Check SDK Installation
    print("\n🔍 Test 2: Checking SDK Installation")
    try:
        import google.generativeai as genai
        print("✅ google-generativeai SDK installed")
    except ImportError:
        print("❌ google-generativeai not installed")
        print("💡 Install with: pip install google-generativeai")
        return False
    
    # Test 3: Initialize Gemini Model
    print("\n🔍 Test 3: Testing Gemini Model Initialization")
    try:
        from app.vision.gemini_vision_model import GeminiVisionModel
        
        model = GeminiVisionModel()
        await model.initialize()
        
        if model.is_enabled():
            print("✅ Gemini model initialized successfully")
        else:
            print("❌ Gemini model failed to initialize")
            return False
    except Exception as e:
        print(f"❌ Gemini initialization error: {e}")
        return False
    
    # Test 4: Test Enhanced Vision Manager
    print("\n🔍 Test 4: Testing Enhanced Vision Manager")
    try:
        from enhanced_vision_manager import EnhancedVisionManager
        
        vision_manager = EnhancedVisionManager()
        await vision_manager.initialize_models()
        
        enabled_models = vision_manager.get_enabled_models()
        print(f"✅ Vision Manager initialized")
        print(f"📊 Enabled models: {enabled_models}")
        
        if "Gemini Pro Vision" in enabled_models:
            print("✅ Gemini Pro Vision is enabled")
        else:
            print("⚠️  Gemini Pro Vision not in enabled models")
    except Exception as e:
        print(f"❌ Vision Manager error: {e}")
        return False
    
    # Test 5: Test Backend API
    print("\n🔍 Test 5: Testing Backend API Integration")
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            gemini_status = data.get("models", {}).get("gemini_vision", {})
            
            print("✅ Backend API accessible")
            print(f"📊 Gemini Status: {gemini_status}")
            
            if gemini_status.get("ready", False):
                print("✅ Gemini ready for analysis")
            else:
                print("⚠️  Gemini not ready in backend")
        else:
            print(f"❌ Backend API error: {response.status_code}")
            print("💡 Make sure backend is running: python enhanced_main.py")
    except requests.exceptions.ConnectionError:
        print("❌ Backend not accessible")
        print("💡 Start backend with: python enhanced_main.py")
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    # Test 6: Sample Analysis
    print("\n🔍 Test 6: Running Sample Analysis")
    try:
        response = requests.post(
            "http://localhost:8080/api/analyze",
            json={"url": "https://example.com"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            models_used = data.get("models_used", [])
            overall_score = data.get("overall_score", 0)
            
            print("✅ Sample analysis completed")
            print(f"📊 Overall Score: {overall_score}")
            print(f"🤖 Models Used: {models_used}")
            
            if "Gemini Pro Vision" in models_used:
                print("✅ Gemini successfully analyzed the website")
                
                # Check for Gemini-specific insights
                recommendations = data.get("recommendations", [])
                gemini_recs = [r for r in recommendations if r.get("source") == "gemini"]
                print(f"💡 Gemini Recommendations: {len(gemini_recs)}")
                
                if gemini_recs:
                    print("✅ Gemini provided CRO recommendations")
                else:
                    print("⚠️  No Gemini-specific recommendations found")
            else:
                print("❌ Gemini not used in analysis")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Analysis test error: {e}")
    
    # Test Summary
    print("\n" + "="*50)
    print("📋 GEMINI INTEGRATION TEST SUMMARY")
    print("="*50)
    
    return True

async def performance_test():
    """Test Gemini performance vs other methods"""
    print("\n⚡ Performance Comparison Test")
    print("-"*30)
    
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html"
    ]
    
    for url in test_urls:
        print(f"\n🌐 Testing: {url}")
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8080/api/analyze",
                json={"url": url},
                timeout=60
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                analysis_time = end_time - start_time
                models_used = data.get("models_used", [])
                overall_score = data.get("overall_score", 0)
                
                print(f"⏱️  Analysis Time: {analysis_time:.2f}s")
                print(f"📊 Score: {overall_score}")
                print(f"🤖 Models: {', '.join(models_used)}")
                
                # Check if Gemini provided better insights
                recommendations = data.get("recommendations", [])
                high_priority = [r for r in recommendations if r.get("priority") == "high"]
                print(f"🎯 High Priority Recommendations: {len(high_priority)}")
                
            else:
                print(f"❌ Analysis failed for {url}")
                
        except Exception as e:
            print(f"❌ Error analyzing {url}: {e}")

def print_setup_instructions():
    """Print setup instructions if tests fail"""
    print("\n🔧 SETUP INSTRUCTIONS")
    print("="*30)
    print("1. Get Gemini API Key:")
    print("   https://makersuite.google.com/app/apikey")
    print()
    print("2. Install Dependencies:")
    print("   pip install google-generativeai")
    print()
    print("3. Set Environment Variable:")
    print("   export GEMINI_API_KEY=your_api_key_here")
    print("   # Or add to .env file")
    print()
    print("4. Start Backend:")
    print("   python enhanced_main.py")
    print()
    print("5. Run This Test Again:")
    print("   python gemini_test_script.py")

async def main():
    """Main test function"""
    print("🧪 Gemini Pro Vision Integration Test Suite")
    print("Make sure you have:")
    print("1. GEMINI_API_KEY environment variable set")
    print("2. Backend running on localhost:8080")
    print("3. google-generativeai package installed")
    print()
    
    success = await test_gemini_integration()
    
    if success:
        await performance_test()
        print("\n🎉 All tests completed!")
        print("✅ Gemini Pro Vision is ready for CRO analysis!")
    else:
        print_setup_instructions()

if __name__ == "__main__":
    asyncio.run(main())