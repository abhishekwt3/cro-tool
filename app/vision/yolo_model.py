"""YOLOv8 Vision Model for UI Element Detection"""

import os
import time
import logging
import asyncio
from typing import List, Optional
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import io

from app.models import AIInsights, CROData, YOLOResults, YOLODetection, ElementPosition, Recommendation

logger = logging.getLogger(__name__)

class YOLOVisionModel:
    """YOLOv8 computer vision model for UI element detection"""
    
    def __init__(self):
        self.model = None
        self.enabled = False
    
    async def initialize(self):
        """Initialize YOLOv8 model"""
        try:
            # Try to load a custom UI model, fallback to general model
            try:
                self.model = YOLO('yolov8n-ui.pt')  # Custom UI model
                logger.info("✅ Loaded custom YOLOv8 UI model")
            except:
                self.model = YOLO('yolov8n.pt')  # General model
                logger.info("✅ Loaded general YOLOv8 model")
            
            # Warm up the model
            dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
            await asyncio.to_thread(self.model, dummy_image, verbose=False)
            
            self.enabled = True
            logger.info("🔥 YOLOv8 model warmed up and ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize YOLOv8: {e}")
            self.enabled = False
    
    async def analyze_screenshot(self, screenshot: bytes, html_data: CROData) -> AIInsights:
        """Analyze screenshot using YOLOv8"""
        if not self.enabled:
            return self._get_mock_analysis()
        
        start_time = time.time()
        
        try:
            # Convert screenshot to image
            image = Image.open(io.BytesIO(screenshot))
            image_array = np.array(image)
            
            # Run YOLOv8 detection
            results = await asyncio.to_thread(
                self.model, 
                image_array, 
                conf=0.3,  # Lower confidence for UI elements
                verbose=False
            )
            
            # Process results
            detections = self._process_detections(results)
            insights = self._convert_to_cro_insights(detections, html_data)
            
            # Add YOLO-specific analysis
            insights.yolo_analysis = YOLOResults(
                detections=detections,
                total_elements=len(detections),
                button_count=self._count_elements_by_class(detections, ['button', 'ui_element']),
                form_count=self._count_elements_by_class(detections, ['textbox', 'form']),
                image_count=self._count_elements_by_class(detections, ['image', 'picture']),
                text_count=self._count_elements_by_class(detections, ['text', 'label']),
                processing_time=time.time() - start_time
            )
            
            # Mark recommendations as from YOLO
            for rec in insights.recommendations:
                rec.source = "yolo"
            
            logger.info(f"🎯 YOLOv8 detected {len(detections)} elements in {insights.yolo_analysis.processing_time:.2f}s")
            return insights
            
        except Exception as e:
            logger.error(f"YOLOv8 analysis failed: {e}")
            return self._get_mock_analysis()
    
    def _process_detections(self, results) -> List[YOLODetection]:
        """Process YOLOv8 detection results"""
        detections = []
        
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Get confidence and class
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    # Map to UI element type
                    ui_type = self._map_to_ui_element(class_name)
                    
                    detection = YOLODetection(
                        class_name=ui_type,
                        confidence=confidence,
                        bounding_box=ElementPosition(
                            x=int(x1),
                            y=int(y1),
                            width=int(x2 - x1),
                            height=int(y2 - y1)
                        ),
                        label=f"{class_name} ({ui_type})"
                    )
                    
                    detections.append(detection)
        
        return detections
    
    def _map_to_ui_element(self, class_name: str) -> str:
        """Map YOLO classes to UI element types"""
        ui_mapping = {
            "person": "user_avatar",
            "book": "text_content",
            "laptop": "device",
            "cell phone": "mobile_device",
            "mouse": "pointer",
            "tv": "screen",
            "bottle": "product",
            "cup": "product",
            "scissors": "tool",
            "remote": "controller"
        }
        
        return ui_mapping.get(class_name, "ui_element")
    
    def _convert_to_cro_insights(self, detections: List[YOLODetection], html_data: CROData) -> AIInsights:
        """Convert YOLO detections to CRO insights"""
        insights = AIInsights()
        
        # Count elements by type
        button_count = self._count_elements_by_class(detections, ['button', 'ui_element'])
        form_count = self._count_elements_by_class(detections, ['form', 'textbox'])
        image_count = self._count_elements_by_class(detections, ['image', 'product'])
        
        # Calculate category scores
        insights.category_scores = {
            "product_page": self._calculate_product_page_score(detections, html_data),
            "cart_page": self._calculate_cart_page_score(detections, html_data),
            "mobile": self._calculate_mobile_score(detections, html_data),
            "trust_signals": self._calculate_trust_signals_score(detections, html_data),
            "coupons": self._calculate_coupons_score(detections, html_data),
            "delivery": self._calculate_delivery_score(detections, html_data)
        }
        
        # Calculate overall score
        insights.overall_score = sum(insights.category_scores.values()) // len(insights.category_scores)
        
        # Generate recommendations
        recommendations = []
        
        if button_count < 3:
            recommendations.append(Recommendation(
                category="cta_buttons",
                priority="high",
                issue=f"Only {button_count} buttons detected by computer vision",
                solution="Add more prominent call-to-action buttons",
                impact="Could increase conversions by 10-15%",
                source="yolo"
            ))
        
        if form_count == 0:
            recommendations.append(Recommendation(
                category="forms",
                priority="medium",
                issue="No forms detected in visual analysis",
                solution="Ensure contact/signup forms are visually prominent",
                impact="Could improve lead generation by 5-10%",
                source="yolo"
            ))
        
        if image_count < 5:
            recommendations.append(Recommendation(
                category="product_page",
                priority="medium",
                issue="Limited product images detected",
                solution="Add more product images and visual content",
                impact="Could improve engagement by 8-12%",
                source="yolo"
            ))
        
        insights.recommendations = recommendations
        
        # Analyze layout distribution
        self._analyze_layout_distribution(detections, insights)
        
        return insights
    
    def _count_elements_by_class(self, detections: List[YOLODetection], classes: List[str]) -> int:
        """Count elements by class type"""
        count = 0
        for detection in detections:
            if any(cls in detection.class_name.lower() for cls in classes):
                count += 1
        return count
    
    def _calculate_product_page_score(self, detections: List[YOLODetection], html_data: CROData) -> int:
        """Calculate product page score based on detections"""
        score = 60
        
        image_count = self._count_elements_by_class(detections, ['image', 'product'])
        button_count = self._count_elements_by_class(detections, ['button', 'ui_element'])
        
        if image_count >= 6:
            score += 20
        elif image_count >= 3:
            score += 10
        
        if button_count >= 2:
            score += 15
        
        # Combine with HTML data
        if html_data.product_images:
            score += 5
        
        return min(score, 100)
    
    def _calculate_cart_page_score(self, detections: List[YOLODetection], html_data: CROData) -> int:
        """Calculate cart page score"""
        score = 65
        
        form_count = self._count_elements_by_class(detections, ['form', 'textbox'])
        button_count = self._count_elements_by_class(detections, ['button', 'ui_element'])
        
        if form_count > 0:
            score += 15
        if button_count >= 3:
            score += 15
        
        return min(score, 100)
    
    def _calculate_mobile_score(self, detections: List[YOLODetection], html_data: CROData) -> int:
        """Calculate mobile experience score"""
        score = 70
        
        # Analyze button sizes (basic heuristic)
        large_buttons = 0
        for detection in detections:
            if 'button' in detection.class_name.lower():
                area = detection.bounding_box.width * detection.bounding_box.height
                if area > 5000:  # Large enough for mobile
                    large_buttons += 1
        
        if large_buttons > 0:
            score += 20
        
        return min(score, 100)
    
    def _calculate_trust_signals_score(self, detections: List[YOLODetection], html_data: CROData) -> int:
        """Calculate trust signals score"""
        score = 60
        
        if html_data.trust_signals:
            score += 25
        
        # Images could be trust badges
        image_count = self._count_elements_by_class(detections, ['image'])
        if image_count >= 3:
            score += 15
        
        return min(score, 100)
    
    def _calculate_coupons_score(self, detections: List[YOLODetection], html_data: CROData) -> int:
        """Calculate coupons score"""
        score = 50
        
        textbox_count = self._count_elements_by_class(detections, ['textbox'])
        if textbox_count > 0:
            score += 20
        
        if html_data.coupon_fields:
            score += 30
        
        return min(score, 100)
    
    def _calculate_delivery_score(self, detections: List[YOLODetection], html_data: CROData) -> int:
        """Calculate delivery score"""
        score = 75
        
        if html_data.delivery_info:
            score += 20
        
        return min(score, 100)
    
    def _analyze_layout_distribution(self, detections: List[YOLODetection], insights: AIInsights):
        """Analyze element layout distribution"""
        if not detections:
            return
        
        # Calculate distribution
        top_half = 0
        bottom_half = 0
        
        for detection in detections:
            center_y = detection.bounding_box.y + (detection.bounding_box.height // 2)
            if center_y < 400:  # Assuming ~800px height
                top_half += 1
            else:
                bottom_half += 1
        
        # Add layout issues
        if top_half < 2:
            insights.visual_issues.append("Most elements detected below the fold")
        
        if bottom_half == 0:
            insights.visual_issues.append("No elements detected in lower page area")
    
    def _get_mock_analysis(self) -> AIInsights:
        """Mock analysis when YOLOv8 is not available"""
        return AIInsights(
            overall_score=72,
            category_scores={
                "product_page": 70,
                "cart_page": 75,
                "mobile": 68,
                "trust_signals": 75,
                "coupons": 65,
                "delivery": 80
            },
            recommendations=[
                Recommendation(
                    category="system",
                    priority="low",
                    issue="YOLOv8 model not available",
                    solution="Install ultralytics package for computer vision analysis",
                    impact="Would provide detailed UI element detection",
                    source="yolo"
                )
            ],
            visual_issues=["Computer vision analysis unavailable"],
            mobile_issues=["YOLOv8 analysis requires model installation"],
            yolo_analysis=YOLOResults(
                detections=[],
                total_elements=0,
                button_count=0,
                form_count=0,
                image_count=0,
                text_count=0,
                processing_time=0.1
            )
        )
    
    def is_enabled(self) -> bool:
        """Check if YOLOv8 model is enabled"""
        return self.enabled
    
    def get_model_name(self) -> str:
        """Get model name"""
        return "YOLOv8 Vision"