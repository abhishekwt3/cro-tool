"""Pydantic models for CRO Analysis with Framework Feedback"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, HttpUrl

class CROAnalysisRequest(BaseModel):
    url: HttpUrl
    client_name: Optional[str] = None

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
    source: str  # gemini, framework, combined, fallback

class CategoryScores(BaseModel):
    product_page: int = 0
    cart_page: int = 0
    mobile: int = 0
    trust_signals: int = 0
    coupons: int = 0
    delivery: int = 0

# NEW: Framework feedback model
class FrameworkFeedback(BaseModel):
    """Detailed feedback for a framework category"""
    category: str
    score: int
    strengths: List[str] = []  # What's done well (3-4 points)
    improvements: List[str] = []  # What can be improved (3-4 points)
    metrics: Dict[str, Any] = {}

# NEW: Lighthouse performance metrics
class LighthouseMetrics(BaseModel):
    """Lighthouse performance audit results"""
    performance_score: Optional[int] = None  # 0-100
    accessibility_score: Optional[int] = None
    best_practices_score: Optional[int] = None
    seo_score: Optional[int] = None
    first_contentful_paint: Optional[float] = None  # milliseconds
    speed_index: Optional[float] = None
    largest_contentful_paint: Optional[float] = None
    time_to_interactive: Optional[float] = None
    total_blocking_time: Optional[float] = None
    cumulative_layout_shift: Optional[float] = None
    lighthouse_available: bool = False

class AIInsights(BaseModel):
    overall_score: int = 0
    category_scores: Dict[str, int] = {}
    recommendations: List[Recommendation] = []
    visual_issues: List[str] = []
    mobile_issues: List[str] = []
    claude_analysis: Optional[ClaudeAnalysis] = None
    yolo_analysis: Optional[YOLOResults] = None
    
    # NEW: Framework feedback
    framework_feedback: Optional[List[FrameworkFeedback]] = None
    lighthouse_metrics: Optional[LighthouseMetrics] = None

class CROAnalysisResponse(BaseModel):
    id: str
    url: str
    overall_score: int
    category_scores: CategoryScores
    visual_analysis: AIInsights
    element_analysis: CROData
    recommendations: List[Recommendation]
    models_used: List[str]
    analysis_date: datetime