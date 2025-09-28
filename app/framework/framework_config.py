"""CRO Framework Configuration Settings"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class FrameworkConfig:
    """Configuration for CRO Framework Analysis"""
    
    # Enable/disable entire categories
    ENABLE_NAVIGATION_ANALYSIS: bool = True
    ENABLE_DISPLAY_ANALYSIS: bool = True  
    ENABLE_INFORMATION_ANALYSIS: bool = True
    ENABLE_TECHNICAL_ANALYSIS: bool = True
    ENABLE_PSYCHOLOGICAL_ANALYSIS: bool = True
    
    # Performance settings
    MAX_ANALYSIS_TIME: int = 30  # seconds
    CONCURRENT_ANALYSIS: bool = True
    SAVE_SCREENSHOTS: bool = True
    
    # Scoring thresholds
    NAVIGATION_THRESHOLDS = {
        "max_nav_links": 15,
        "max_page_depth": 4,
        "breadcrumb_required": True
    }
    
    DISPLAY_THRESHOLDS = {
        "max_font_count": 2,
        "max_positioned_elements": 5,
        "max_unique_colors": 8
    }
    
    INFORMATION_THRESHOLDS = {
        "max_title_length": 60,
        "min_product_images": 2,
        "min_description_length": 50
    }
    
    TECHNICAL_THRESHOLDS = {
        "max_dom_load_time": 3000,  # milliseconds
        "max_first_paint": 2500,    # milliseconds
        "max_image_size": 2000      # pixels
    }
    
    PSYCHOLOGICAL_THRESHOLDS = {
        "min_trust_badges": 2,
        "require_return_policy": True,
        "require_faq": False
    }
    
    # Recommendation priorities
    HIGH_IMPACT_CATEGORIES = ["navigation", "information", "psychological"]
    MEDIUM_IMPACT_CATEGORIES = ["technical", "display"]
    
    # Framework weights for overall score calculation
    CATEGORY_WEIGHTS = {
        "navigation": 0.20,      # 20%
        "display": 0.15,         # 15%
        "information": 0.25,     # 25%
        "technical": 0.20,       # 20%
        "psychological": 0.20    # 20%
    }
    
    # Trust signal keywords for enhanced detection
    TRUST_SIGNAL_KEYWORDS = [
        "ssl", "secure", "verified", "guarantee", "money back",
        "testimonial", "review", "certified", "award", "trusted",
        "paypal", "visa", "mastercard", "norton", "mcafee"
    ]
    
    # High-converting CTA words
    HIGH_CONVERTING_CTA_WORDS = [
        "buy now", "add to cart", "get started", "free trial",
        "download", "sign up", "subscribe", "order now"
    ]
    
    # Mobile-specific settings
    MOBILE_ANALYSIS = {
        "min_touch_target_size": 44,  # pixels
        "max_form_fields": 5,
        "require_viewport_meta": True
    }

# Global configuration instance
config = FrameworkConfig()

def get_framework_config() -> FrameworkConfig:
    """Get the current framework configuration"""
    return config

def update_framework_config(**kwargs) -> None:
    """Update framework configuration"""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

def get_enabled_categories() -> List[str]:
    """Get list of enabled framework categories"""
    categories = []
    if config.ENABLE_NAVIGATION_ANALYSIS:
        categories.append("navigation")
    if config.ENABLE_DISPLAY_ANALYSIS:
        categories.append("display")
    if config.ENABLE_INFORMATION_ANALYSIS:
        categories.append("information")
    if config.ENABLE_TECHNICAL_ANALYSIS:
        categories.append("technical")
    if config.ENABLE_PSYCHOLOGICAL_ANALYSIS:
        categories.append("psychological")
    return categories

def calculate_weighted_score(category_scores: Dict[str, int]) -> int:
    """Calculate weighted overall score based on category importance"""
    total_score = 0
    total_weight = 0
    
    for category, score in category_scores.items():
        if category in config.CATEGORY_WEIGHTS:
            weight = config.CATEGORY_WEIGHTS[category]
            total_score += score * weight
            total_weight += weight
    
    if total_weight == 0:
        return 0
    
    return int(total_score / total_weight)

def get_recommendation_priority(category: str, impact_score: int) -> str:
    """Determine recommendation priority based on category and impact"""
    if category in config.HIGH_IMPACT_CATEGORIES:
        if impact_score >= 80:
            return "high"
        elif impact_score >= 60:
            return "medium"
        else:
            return "low"
    elif category in config.MEDIUM_IMPACT_CATEGORIES:
        if impact_score >= 90:
            return "high"
        elif impact_score >= 70:
            return "medium"
        else:
            return "low"
    else:
        return "medium"  # Default priority

# Environment-based configuration overrides
def load_config_from_env():
    """Load configuration from environment variables"""
    import os
    
    # Performance settings
    if os.getenv("CRO_MAX_ANALYSIS_TIME"):
        config.MAX_ANALYSIS_TIME = int(os.getenv("CRO_MAX_ANALYSIS_TIME"))
    
    if os.getenv("CRO_SAVE_SCREENSHOTS"):
        config.SAVE_SCREENSHOTS = os.getenv("CRO_SAVE_SCREENSHOTS").lower() == "true"
    
    # Category toggles
    if os.getenv("CRO_ENABLE_NAVIGATION"):
        config.ENABLE_NAVIGATION_ANALYSIS = os.getenv("CRO_ENABLE_NAVIGATION").lower() == "true"
    
    if os.getenv("CRO_ENABLE_DISPLAY"):
        config.ENABLE_DISPLAY_ANALYSIS = os.getenv("CRO_ENABLE_DISPLAY").lower() == "true"
    
    if os.getenv("CRO_ENABLE_INFORMATION"):
        config.ENABLE_INFORMATION_ANALYSIS = os.getenv("CRO_ENABLE_INFORMATION").lower() == "true"
    
    if os.getenv("CRO_ENABLE_TECHNICAL"):
        config.ENABLE_TECHNICAL_ANALYSIS = os.getenv("CRO_ENABLE_TECHNICAL").lower() == "true"
    
    if os.getenv("CRO_ENABLE_PSYCHOLOGICAL"):
        config.ENABLE_PSYCHOLOGICAL_ANALYSIS = os.getenv("CRO_ENABLE_PSYCHOLOGICAL").lower() == "true"

# Development presets
def load_development_config():
    """Load development-friendly configuration"""
    config.MAX_ANALYSIS_TIME = 15  # Faster for development
    config.SAVE_SCREENSHOTS = True  # Help with debugging
    config.CONCURRENT_ANALYSIS = True

def load_production_config():
    """Load production-optimized configuration"""
    config.MAX_ANALYSIS_TIME = 30
    config.SAVE_SCREENSHOTS = False  # Save disk space
    config.CONCURRENT_ANALYSIS = True

def load_minimal_config():
    """Load minimal configuration for basic analysis"""
    config.ENABLE_NAVIGATION_ANALYSIS = True
    config.ENABLE_DISPLAY_ANALYSIS = False
    config.ENABLE_INFORMATION_ANALYSIS = True
    config.ENABLE_TECHNICAL_ANALYSIS = False
    config.ENABLE_PSYCHOLOGICAL_ANALYSIS = True
    config.MAX_ANALYSIS_TIME = 10

# Initialize configuration
load_config_from_env()