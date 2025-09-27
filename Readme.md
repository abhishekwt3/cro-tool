# README.md
# 🚀 CRO Analyzer - Python Backend

**AI-Powered Conversion Rate Optimization Analysis with Easy Model Switching**

## 🎯 **Why Python?**

✅ **Single Codebase** - No microservices complexity  
✅ **Native AI Integration** - YOLOv8, Claude, future models built-in  
✅ **Faster Development** - 50% less code than Go version  
✅ **Rich AI Ecosystem** - Easy to add new models  
✅ **SQLite Simplicity** - No PostgreSQL setup needed  

## 🔧 **Easy Model Switching**

Edit **one file**: `app/vision/vision_manager.py`

```python
# 🎛️ ENABLE/DISABLE AI MODELS HERE
ENABLE_CLAUDE_VISION = True   # Set to False to disable
ENABLE_YOLO_VISION = True     # Set to False to disable
```

## 🚀 **Quick Start**

```bash
# 1. Setup
git clone <repo> && cd cro-analyzer
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Add your Claude API key to .env

# 3. Run
python main.py

# 4. Test
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## 🐳 **Docker (Recommended)**

```bash
# Quick start with Docker
docker-compose up --build

# Access API
curl http://localhost:8080/api/models
```

## 🎯 **Features**

- **🤖 Dual AI Models**: Claude Vision + YOLOv8 computer vision
- **🔀 Easy Switching**: Change one variable to enable/disable models
- **📱 Complete Analysis**: Screenshots, HTML parsing, AI insights
- **💾 SQLite Database**: Simple file-based storage
- **⚡ Fast Performance**: Async Python with concurrent processing
- **🔄 Real-time Updates**: WebSocket progress tracking
- **📦 Smart Caching**: Redis + in-memory fallback

## 📊 **API Endpoints**

```python
# Check enabled models
GET /api/models

# Run analysis
POST /api/analyze
{
  "url": "https://store.com",
  "client_name": "Client Co"
}

# Real-time analysis
WS /api/analyze/ws?url=https://store.com

# Health check
GET /health
```

## 🔧 **Adding New AI Models**

1. **Create model file**: `app/vision/custom_model.py`
2. **Implement interface**:
```python
class CustomVisionModel:
    async def analyze_screenshot(self, screenshot: bytes, html_data: CROData):
        # Your model logic
        return AIInsights(...)
    
    def get_model_name(self) -> str:
        return "Custom Model"
    
    def is_enabled(self) -> bool:
        return True
```

3. **Add to manager**: Edit `vision_manager.py`
```python
ENABLE_CUSTOM_MODEL = True

# In initialize_models():
if ENABLE_CUSTOM_MODEL:
    self.models.append(CustomVisionModel())
```

## 🎛️ **Configuration Options**

| Model | Purpose | Speed | Accuracy |
|-------|---------|-------|----------|
| **Claude Only** | Design insights, UX analysis | Fast | ⭐⭐⭐⭐⭐ |
| **YOLOv8 Only** | UI detection, layout analysis | Fastest | ⭐⭐⭐⭐ |
| **Both Models** | Maximum accuracy, validation | Medium | ⭐⭐⭐⭐⭐ |
| **HTML Only** | Basic structural analysis | Instant | ⭐⭐⭐ |

## 📁 **Project Structure**

```
app/
├── vision/
│   ├── vision_manager.py    # 🎛️ Model switching
│   ├── claude_model.py      # Claude Vision API
│   └── yolo_model.py        # YOLOv8 computer vision
├── services/
│   ├── analysis_engine.py   # Main analysis logic
│   ├── screenshot_service.py # Playwright screenshots
│   ├── scraping_service.py   # HTML/DOM extraction
│   └── cache_service.py      # Redis caching
├── models.py                 # Pydantic data models
├── database.py               # SQLite + SQLAlchemy
└── main.py                   # FastAPI app
```

## 💡 **Why This Architecture?**

- **🔌 Pluggable Models**: Add GPT-4 Vision, BLIP, or custom models easily
- **⚡ Async Everything**: Non-blocking I/O for better performance  
- **🛡️ Error Resilience**: Graceful fallbacks when models fail
- **📊 Rich Insights**: Combines computer vision + AI text analysis
- **🔄 Live Updates**: Real-time progress via WebSockets

Perfect for agencies who want **powerful AI analysis** with **simple deployment** and **easy customization**! 🎯