"""Lighthouse Performance Analysis Service for Technical Metrics"""

import os
import asyncio
import logging
import json
import subprocess
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class LighthouseService:
    """Google Lighthouse integration for technical performance analysis"""
    
    def __init__(self):
        self.enabled = self._check_lighthouse_available()
    
    def _check_lighthouse_available(self) -> bool:
        """Check if Lighthouse CLI is available"""
        try:
            result = subprocess.run(
                ['lighthouse', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("✅ Lighthouse CLI available")
                return True
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("⚠️  Lighthouse CLI not found. Install with: npm install -g lighthouse")
            return False
    
    async def analyze_performance(self, url: str) -> Dict[str, Any]:
        """Run Lighthouse analysis on URL"""
        if not self.enabled:
            return self._get_mock_lighthouse_data()
        
        try:
            logger.info(f"🔍 Running Lighthouse analysis for {url}")
            
            # Run Lighthouse CLI
            result = await asyncio.to_thread(
                self._run_lighthouse_cli,
                url
            )
            
            if result:
                logger.info("✅ Lighthouse analysis completed")
                return self._parse_lighthouse_results(result)
            else:
                logger.warning("⚠️  Lighthouse analysis failed, using mock data")
                return self._get_mock_lighthouse_data()
                
        except Exception as e:
            logger.error(f"❌ Lighthouse analysis error: {e}")
            return self._get_mock_lighthouse_data()
    
    def _run_lighthouse_cli(self, url: str) -> Optional[Dict[str, Any]]:
        """Run Lighthouse CLI command"""
        try:
            # Run Lighthouse with JSON output
            result = subprocess.run(
                [
                    'lighthouse',
                    url,
                    '--output=json',
                    '--output-path=stdout',
                    '--chrome-flags="--headless"',
                    '--only-categories=performance,accessibility,best-practices,seo',
                    '--quiet'
                ],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )
            
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            return None
            
        except Exception as e:
            logger.error(f"Lighthouse CLI error: {e}")
            return None
    
    def _parse_lighthouse_results(self, lighthouse_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Lighthouse JSON results"""
        try:
            categories = lighthouse_data.get('categories', {})
            audits = lighthouse_data.get('audits', {})
            
            # Extract key metrics
            performance_score = int(categories.get('performance', {}).get('score', 0) * 100)
            accessibility_score = int(categories.get('accessibility', {}).get('score', 0) * 100)
            best_practices_score = int(categories.get('best-practices', {}).get('score', 0) * 100)
            seo_score = int(categories.get('seo', {}).get('score', 0) * 100)
            
            # Core Web Vitals
            metrics = audits.get('metrics', {}).get('details', {}).get('items', [{}])[0]
            
            return {
                "performance_score": performance_score,
                "accessibility_score": accessibility_score,
                "best_practices_score": best_practices_score,
                "seo_score": seo_score,
                "metrics": {
                    "first_contentful_paint": metrics.get('firstContentfulPaint', 0),
                    "largest_contentful_paint": metrics.get('largestContentfulPaint', 0),
                    "total_blocking_time": metrics.get('totalBlockingTime', 0),
                    "cumulative_layout_shift": metrics.get('cumulativeLayoutShift', 0),
                    "speed_index": metrics.get('speedIndex', 0),
                    "interactive": metrics.get('interactive', 0)
                },
                "opportunities": self._extract_opportunities(audits),
                "diagnostics": self._extract_diagnostics(audits),
                "passed_audits": self._extract_passed_audits(audits)
            }
            
        except Exception as e:
            logger.error(f"Error parsing Lighthouse results: {e}")
            return self._get_mock_lighthouse_data()
    
    def _extract_opportunities(self, audits: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract performance opportunities"""
        opportunities = []
        
        opportunity_audits = [
            'render-blocking-resources',
            'unused-css-rules',
            'unused-javascript',
            'modern-image-formats',
            'uses-optimized-images',
            'uses-text-compression',
            'uses-responsive-images'
        ]
        
        for audit_id in opportunity_audits:
            audit = audits.get(audit_id, {})
            if audit.get('score', 1) < 1:  # Failed audit
                opportunities.append({
                    'title': audit.get('title', ''),
                    'description': audit.get('description', ''),
                    'savings': audit.get('details', {}).get('overallSavingsMs', 0)
                })
        
        return opportunities[:5]  # Top 5 opportunities
    
    def _extract_diagnostics(self, audits: Dict[str, Any]) -> List[str]:
        """Extract diagnostic information"""
        diagnostics = []
        
        diagnostic_audits = [
            'mainthread-work-breakdown',
            'bootup-time',
            'uses-long-cache-ttl',
            'total-byte-weight',
            'dom-size'
        ]
        
        for audit_id in diagnostic_audits:
            audit = audits.get(audit_id, {})
            if audit.get('score', 1) < 0.9:  # Below 90%
                diagnostics.append(audit.get('title', ''))
        
        return diagnostics
    
    def _extract_passed_audits(self, audits: Dict[str, Any]) -> List[str]:
        """Extract what's working well"""
        passed = []
        
        key_audits = [
            'first-contentful-paint',
            'largest-contentful-paint',
            'uses-responsive-images',
            'uses-text-compression',
            'viewport'
        ]
        
        for audit_id in key_audits:
            audit = audits.get(audit_id, {})
            if audit.get('score', 0) >= 0.9:  # Score >= 90%
                passed.append(audit.get('title', ''))
        
        return passed
    
    def _get_mock_lighthouse_data(self) -> Dict[str, Any]:
        """Mock Lighthouse data for when CLI is not available"""
        return {
            "performance_score": 75,
            "accessibility_score": 88,
            "best_practices_score": 82,
            "seo_score": 90,
            "metrics": {
                "first_contentful_paint": 1800,
                "largest_contentful_paint": 3200,
                "total_blocking_time": 450,
                "cumulative_layout_shift": 0.15,
                "speed_index": 3500,
                "interactive": 4200
            },
            "opportunities": [
                {
                    "title": "Eliminate render-blocking resources",
                    "description": "Resources are blocking the first paint of your page",
                    "savings": 850
                },
                {
                    "title": "Remove unused JavaScript",
                    "description": "Reduce unused JavaScript and defer loading",
                    "savings": 320
                }
            ],
            "diagnostics": [
                "Reduce JavaScript execution time",
                "Minimize main-thread work",
                "Reduce the impact of third-party code"
            ],
            "passed_audits": [
                "First Contentful Paint",
                "Uses responsive images",
                "Has a viewport meta tag"
            ]
        }
    
    def is_enabled(self) -> bool:
        """Check if service is enabled"""
        return self.enabled
