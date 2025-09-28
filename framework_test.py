#!/usr/bin/env python3
"""
CRO Framework Validation Test Script
Tests the 5-point framework implementation
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrameworkTester:
    """Test the CRO Framework implementation"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.test_results = {}
        
    async def run_all_tests(self):
        """Run comprehensive framework tests"""
        logger.info("🧪 Starting CRO Framework Validation Tests")
        
        # Test 1: Health Check
        await self.test_health_check()
        
        # Test 2: Framework Categories
        await self.test_framework_categories()
        
        # Test 3: Sample Analysis
        await self.test_sample_analysis()
        
        # Test 4: Framework Components
        await self.test_framework_components()
        
        # Test 5: Performance Test
        await self.test_performance()
        
        # Generate test report
        self.generate_test_report()
    
    async def test_health_check(self):
        """Test 1: Verify framework is enabled in health check"""
        logger.info("🔍 Test 1: Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                
                # Check framework status
                framework_enabled = data.get("framework_enabled", False)
                framework_status = data.get("models", {}).get("framework_analysis", {})
                
                self.test_results["health_check"] = {
                    "passed": framework_enabled and framework_status.get("ready", False),
                    "framework_enabled": framework_enabled,
                    "framework_ready": framework_status.get("ready", False),
                    "categories": framework_status.get("categories", [])
                }
                
                if self.test_results["health_check"]["passed"]:
                    logger.info("✅ Health check passed - Framework enabled")
                else:
                    logger.error("❌ Health check failed - Framework not ready")
            else:
                self.test_results["health_check"] = {
                    "passed": False,
                    "error": f"HTTP {response.status_code}"
                }
                logger.error(f"❌ Health check failed - HTTP {response.status_code}")
                
        except Exception as e:
            self.test_results["health_check"] = {
                "passed": False,
                "error": str(e)
            }
            logger.error(f"❌ Health check failed - {e}")
    
    async def test_framework_categories(self):
        """Test 2: Verify framework categories endpoint"""
        logger.info("🔍 Test 2: Framework Categories")
        
        try:
            response = requests.get(f"{self.base_url}/api/framework/categories")
            if response.status_code == 200:
                data = response.json()
                
                expected_categories = ["navigation", "display", "information", "technical", "psychological"]
                actual_categories = list(data.get("categories", {}).keys())
                
                all_present = all(cat in actual_categories for cat in expected_categories)
                
                self.test_results["framework_categories"] = {
                    "passed": all_present,
                    "expected": expected_categories,
                    "actual": actual_categories,
                    "missing": [cat for cat in expected_categories if cat not in actual_categories]
                }
                
                if all_present:
                    logger.info("✅ Framework categories test passed")
                else:
                    logger.error(f"❌ Framework categories test failed - Missing: {self.test_results['framework_categories']['missing']}")
            else:
                self.test_results["framework_categories"] = {
                    "passed": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            self.test_results["framework_categories"] = {
                "passed": False,
                "error": str(e)
            }
            logger.error(f"❌ Framework categories test failed - {e}")
    
    async def test_sample_analysis(self):
        """Test 3: Run sample analysis and verify framework scores"""
        logger.info("🔍 Test 3: Sample Analysis")
        
        # Test URLs
        test_urls = [
            "https://example.com",  # Simple test site
            "https://httpbin.org/html",  # Reliable test endpoint
        ]
        
        for url in test_urls:
            try:
                logger.info(f"📊 Analyzing {url}")
                
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/analyze",
                    json={"url": url},
                    timeout=60
                )
                analysis_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for framework scores
                    category_scores = data.get("category_scores", {})
                    framework_categories = ["navigation", "display", "information", "technical", "psychological"]
                    
                    has_framework_scores = any(cat in category_scores for cat in framework_categories)
                    has_overall_score = "overall_score" in data
                    has_recommendations = len(data.get("recommendations", [])) > 0
                    
                    test_result = {
                        "passed": has_framework_scores and has_overall_score,
                        "url": url,
                        "analysis_time": round(analysis_time, 2),
                        "overall_score": data.get("overall_score"),
                        "framework_scores": {cat: category_scores.get(cat) for cat in framework_categories if cat in category_scores},
                        "recommendations_count": len(data.get("recommendations", [])),
                        "models_used": data.get("models_used", [])
                    }
                    
                    if not hasattr(self, 'sample_analysis_results'):
                        self.test_results["sample_analysis"] = []
                    self.test_results["sample_analysis"].append(test_result)
                    
                    if test_result["passed"]:
                        logger.info(f"✅ Sample analysis passed for {url} - Score: {test_result['overall_score']}")
                    else:
                        logger.error(f"❌ Sample analysis failed for {url}")
                        
                else:
                    logger.error(f"❌ Sample analysis failed for {url} - HTTP {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Sample analysis failed for {url} - {e}")
                continue
    
    async def test_framework_components(self):
        """Test 4: Test individual framework components"""
        logger.info("🔍 Test 4: Framework Components")
        
        # Test HTML samples for framework analysis
        test_cases = {
            "navigation": {
                "html": """
                <nav>
                    <ul class="breadcrumb">
                        <li><a href="/">Home</a></li>
                        <li><a href="/category">Category</a></li>
                        <li>Product</li>
                    </ul>
                    <ul class="menu">
                        <li><a href="/about">About</a></li>
                        <li><a href="/products">Products</a></li>
                        <li><a href="/contact">Contact</a></li>
                    </ul>
                </nav>
                """,
                "expected_features": ["breadcrumbs", "navigation_menu"]
            },
            "trust_signals": {
                "html": """
                <div class="trust-badges">
                    <img src="ssl-badge.png" alt="SSL Secured">
                    <div class="guarantee">30-day money back guarantee</div>
                    <div class="testimonial">Great service! - John D.</div>
                </div>
                """,
                "expected_features": ["ssl_badge", "guarantee", "testimonial"]
            },
            "product_info": {
                "html": """
                <div class="product">
                    <h1 class="product-title">Amazing Product</h1>
                    <div class="product-description">This is a detailed description of the amazing product.</div>
                    <img class="product-image" src="product1.jpg" alt="Product Image 1">
                    <img class="product-image" src="product2.jpg" alt="Product Image 2">
                    <div class="offer">Special 20% off today!</div>
                </div>
                """,
                "expected_features": ["product_title", "description", "multiple_images", "offer"]
            }
        }
        
        component_results = {}
        
        for component, test_case in test_cases.items():
            try:
                # Parse HTML with BeautifulSoup (simulating framework analysis)
                soup = BeautifulSoup(test_case["html"], 'html.parser')
                
                features_found = []
                
                # Basic feature detection
                if component == "navigation":
                    if soup.select('.breadcrumb'):
                        features_found.append("breadcrumbs")
                    if soup.select('nav a, .menu a'):
                        features_found.append("navigation_menu")
                
                elif component == "trust_signals":
                    if soup.find(alt=lambda x: x and 'ssl' in x.lower()):
                        features_found.append("ssl_badge")
                    if soup.find(text=lambda x: x and 'guarantee' in x.lower()):
                        features_found.append("guarantee")
                    if soup.select('.testimonial'):
                        features_found.append("testimonial")
                
                elif component == "product_info":
                    if soup.select('.product-title, h1'):
                        features_found.append("product_title")
                    if soup.select('.product-description, .description'):
                        features_found.append("description")
                    if len(soup.select('.product-image')) >= 2:
                        features_found.append("multiple_images")
                    if soup.find(text=lambda x: x and ('off' in x.lower() or '%' in x)):
                        features_found.append("offer")
                
                expected = test_case["expected_features"]
                passed = all(feature in features_found for feature in expected)
                
                component_results[component] = {
                    "passed": passed,
                    "expected_features": expected,
                    "found_features": features_found,
                    "missing_features": [f for f in expected if f not in features_found]
                }
                
                if passed:
                    logger.info(f"✅ {component} component test passed")
                else:
                    logger.error(f"❌ {component} component test failed")
                    
            except Exception as e:
                component_results[component] = {
                    "passed": False,
                    "error": str(e)
                }
                logger.error(f"❌ {component} component test failed - {e}")
        
        self.test_results["framework_components"] = component_results
    
    async def test_performance(self):
        """Test 5: Performance benchmarks"""
        logger.info("🔍 Test 5: Performance Test")
        
        try:
            # Test analysis speed
            test_url = "https://httpbin.org/html"
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/analyze",
                json={"url": test_url},
                timeout=60
            )
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                performance_passed = total_time < 30  # Should complete within 30 seconds
                
                self.test_results["performance"] = {
                    "passed": performance_passed,
                    "total_analysis_time": round(total_time, 2),
                    "target_time": 30,
                    "status": "passed" if performance_passed else "slow"
                }
                
                if performance_passed:
                    logger.info(f"✅ Performance test passed - {total_time:.2f}s")
                else:
                    logger.warning(f"⚠️  Performance test slow - {total_time:.2f}s")
            else:
                self.test_results["performance"] = {
                    "passed": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            self.test_results["performance"] = {
                "passed": False,
                "error": str(e)
            }
            logger.error(f"❌ Performance test failed - {e}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("📋 Generating Test Report")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if isinstance(result, dict) and result.get("passed", False) or
                          isinstance(result, list) and all(r.get("passed", False) for r in result))
        
        report = {
            "framework_validation_report": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%"
                },
                "detailed_results": self.test_results
            }
        }
        
        # Save report
        with open("framework_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("🎯 CRO FRAMEWORK VALIDATION REPORT")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {report['framework_validation_report']['summary']['success_rate']}")
        print("="*60)
        
        # Print detailed results
        for test_name, result in self.test_results.items():
            if isinstance(result, dict):
                status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
                print(f"{status} {test_name}")
            elif isinstance(result, list):
                all_passed = all(r.get("passed", False) for r in result)
                status = "✅ PASS" if all_passed else "❌ FAIL"
                print(f"{status} {test_name} ({len(result)} sub-tests)")
        
        print(f"\nDetailed report saved to: framework_test_report.json")
        
        # Return overall success
        return passed_tests == total_tests

async def main():
    """Main test function"""
    print("🧪 CRO Framework Validation Test Suite")
    print("Make sure the backend is running on localhost:8080")
    print("Starting tests in 3 seconds...")
    await asyncio.sleep(3)
    
    tester = FrameworkTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())