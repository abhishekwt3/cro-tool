"""Enhanced Pydantic models for CRO Analysis with Framework Support"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, HttpUrl

class CROAnalysisRequest(BaseModel):
    url: HttpUrl
    client_name: Optional[str] = None
    enable_framework_analysis: Optional[bool] = True
    analysis_depth: Optional[str] = "comprehensive"  # basic, standard, comprehensive

class ElementPosition(BaseModel):
    x: int
    y: int
    width: int
    height: int

class CROElement(BaseModel):
    type: str
    text: str
    position: ElementPosition
    attributes: Dict[str, str] = {}
    visible: bool = True
    score: int = 0

class TrustSignal(BaseModel):
    type: str
    text: str
    position: ElementPosition
    visible: bool
    effectiveness: int

class CTAButton(BaseModel):
    text: str
    color: str
    size: str
    position: ElementPosition
    prominent: bool
    persuasiveness: int

class CROData(BaseModel):
    trust_signals: List[TrustSignal] = []
    cta_buttons: List[CTAButton] = []
    forms: List[CROElement] = []
    cart_elements: List[CROElement] = []
    product_images: List[CROElement] = []
    coupon_fields: List[CROElement] = []
    delivery_info: List[CROElement] = []

# Framework-specific models
class FrameworkMetrics(BaseModel):
    """Metrics collected by the CRO framework"""
    # Navigation metrics
    has_breadcrumbs: Optional[bool] = False
    navigation_links: Optional[int] = 0
    page_depth: Optional[int] = 0
    
    # Display metrics
    font_count: Optional[int] = 0
    fonts_used: Optional[List[str]] = []
    positioned_elements: Optional[int] = 0
    empty_containers: Optional[int] = 0
    unique_colors: Optional[int] = 0
    
    # Information metrics
    product_titles: Optional[int] = 0
    has_descriptions: Optional[bool] = False
    description_count: Optional[int] = 0
    product_image_count: Optional[int] = 0
    has_offers: Optional[bool] = False
    offer_count: Optional[int] = 0
    
    # Technical metrics
    has_viewport_meta: Optional[bool] = False
    large_images: Optional[int] = 0
    total_images: Optional[int] = 0
    performance: Optional[Dict[str, Any]] = {}
    
    # Psychological metrics
    trust_badges: Optional[int] = 0
    has_return_policy: Optional[bool] = False
    has_faq: Optional[bool] = False

class FrameworkAnalysis(BaseModel):
    """Results from framework analysis"""
    score: int
    issues: List[str] = []
    recommendations: List[Dict[str, str]] = []
    metrics: FrameworkMetrics = FrameworkMetrics()

class FrameworkResults(BaseModel):
    """Complete framework analysis results"""
    navigation: FrameworkAnalysis
    display: FrameworkAnalysis
    information: FrameworkAnalysis
    technical: FrameworkAnalysis
    psychological: FrameworkAnalysis
    overall_framework_score: int

# Enhanced AI model results
class YOLODetection(BaseModel):
    class_name: str
    confidence: float
    bounding_box: ElementPosition
    label: str

class YOLOResults(BaseModel):
    detections: List[YOLODetection] = []
    total_elements: int = 0
    button_count: int = 0
    form_count: int = 0
    image_count: int = 0
    text_count: int = 0
    processing_time: float = 0.0

class ClaudeAnalysis(BaseModel):
    textual_insights: List[str] = []
    design_suggestions: List[str] = []
    ux_recommendations: List[str] = []
    conversion_issues: List[str] = []
    processing_time: float = 0.0

class Recommendation(BaseModel):
    category: str
    priority: str  # high, medium, low
    issue: str
    solution: str
    impact: str
    source: str  # claude, yolo, framework, combined, fallback

# Enhanced category scores supporting both legacy and framework categories
class CategoryScores(BaseModel):
    # Legacy categories (for compatibility)
    product_page: int = 0
    cart_page: int = 0
    mobile: int = 0
    trust_signals: int = 0
    coupons: int = 0
    delivery: int = 0
    
    # Framework categories (new)
    navigation: Optional[int] = None
    display: Optional[int] = None
    information: Optional[int] = None
    technical: Optional[int] = None
    psychological: Optional[int] = None

class EnhancedAIInsights(BaseModel):
    """Enhanced AI insights with framework integration"""
    overall_score: int = 0
    category_scores: Dict[str, int] = {}
    recommendations: List[Recommendation] = []
    visual_issues: List[str] = []
    mobile_issues: List[str] = []
    
    # AI model results
    claude_analysis: Optional[ClaudeAnalysis] = None
    yolo_analysis: Optional[YOLOResults] = None
    
    # Framework results
    framework_results: Optional[FrameworkResults] = None
    framework_metrics: Optional[FrameworkMetrics] = None
    
    # Analysis metadata
    analysis_methods: List[str] = []
    coverage_score: Optional[int] = None
    quality_indicators: List[str] = []

# Keep original AIInsights for compatibility
class AIInsights(BaseModel):
    overall_score: int = 0
    category_scores: Dict[str, int] = {}
    recommendations: List[Recommendation] = []
    visual_issues: List[str] = []
    mobile_issues: List[str] = []
    claude_analysis: Optional[ClaudeAnalysis] = None
    yolo_analysis: Optional[YOLOResults] = None

class CROAnalysisResponse(BaseModel):
    id: str
    url: str
    overall_score: int
    category_scores: CategoryScores
    visual_analysis: Union[AIInsights, EnhancedAIInsights]
    element_analysis: CROData
    recommendations: List[Recommendation]
    models_used: List[str]
    analysis_date: datetime
    
    # Enhanced fields
    framework_analysis: Optional[FrameworkResults] = None
    analysis_metadata: Optional[Dict[str, Any]] = None

# New response models for enhanced endpoints
class FrameworkOnlyResponse(BaseModel):
    """Response for framework-only analysis"""
    id: str
    url: str
    framework_results: FrameworkResults
    recommendations: List[Recommendation]
    analysis_date: datetime

class ComparisonAnalysisResponse(BaseModel):
    """Response comparing framework vs AI analysis"""
    id: str
    url: str
    framework_analysis: FrameworkResults
    ai_analysis: AIInsights
    combined_analysis: EnhancedAIInsights
    agreement_score: int  # How much framework and AI agree (0-100)
    analysis_date: datetime

# Enhanced analysis request for different analysis types
class EnhancedAnalysisRequest(BaseModel):
    url: HttpUrl
    client_name: Optional[str] = None
    analysis_type: str = "comprehensive"  # framework_only, ai_only, comprehensive
    enable_claude: Optional[bool] = True
    enable_yolo: Optional[bool] = True
    enable_framework: Optional[bool] = True
    focus_areas: Optional[List[str]] = None  # Specific framework areas to focus on

# Health check models
class ModelStatus(BaseModel):
    enabled: bool
    initialized: bool
    ready: bool
    categories: Optional[List[str]] = None
    error: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    models: Dict[str, ModelStatus]
    database: str
    cache: str
    framework_enabled: bool
    total_analysis_methods: int

# Analytics models for reporting
class AnalysisStats(BaseModel):
    total_analyses: int
    avg_score: float
    common_issues: List[str]
    improvement_areas: List[str]
    analysis_methods_used: Dict[str, int]

class CategoryBreakdown(BaseModel):
    category: str
    avg_score: float
    common_issues: List[str]
    improvement_rate: float  # How much scores improved over time

class AnalyticsResponse(BaseModel):
    overall_stats: AnalysisStats
    category_breakdown: List[CategoryBreakdown]
    trend_data: Dict[str, List[float]]  # Scores over time
    recommendations_impact: Dict[str, float]  # Which recommendations work best