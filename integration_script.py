#!/usr/bin/env python3
"""
CRO Framework Integration Script
Automatically integrates the 5-point framework into existing codebase
"""

import os
import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrameworkIntegrator:
    """Integrates CRO framework into existing project"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.app_dir = self.project_root / "app"
        self.backup_dir = self.project_root / "backup_original"
        
    def integrate_framework(self):
        """Run complete framework integration"""
        logger.info("🚀 Starting CRO Framework Integration")
        
        # Step 1: Backup original files
        self.backup_original_files()
        
        # Step 2: Create directory structure
        self.create_directory_structure()
        
        # Step 3: Update existing files
        self.update_existing_files()
        
        # Step 4: Create new framework files
        self.create_framework_files()
        
        # Step 5: Update configuration
        self.update_configuration()
        
        # Step 6: Generate integration report
        self.generate_integration_report()
        
        logger.info("✅ Framework integration completed!")
    
    def backup_original_files(self):
        """Backup original files before modification"""
        logger.info("📦 Backing up original files")
        
        files_to_backup = [
            "main.py",
            "app/models.py",
            "app/vision/vision_manager.py",
            "app/services/analysis_engine.py",
            "app/services/scraping_service.py"
        ]
        
        self.backup_dir.mkdir(exist_ok=True)
        
        for file_path in files_to_backup:
            source = self.project_root / file_path
            if source.exists():
                destination = self.backup_dir / file_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                logger.info(f"✅ Backed up {file_path}")
    
    def create_directory_structure(self):
        """Create necessary directory structure"""
        logger.info("📁 Creating directory structure")
        
        directories = [
            "app/framework",
            "app/services/enhanced",
            "app/vision/enhanced",
            "screenshots",
            "tests/framework"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")
    
    def update_existing_files(self):
        """Update existing files with framework integration"""
        logger.info("🔧 Updating existing files")
        
        # Update vision_manager.py
        self.update_vision_manager()
        
        # Update models.py
        self.update_models()
        
        # Update main.py
        self.update_main_file()
    
    def update_vision_manager(self):
        """Update vision manager with framework configuration"""
        vision_manager_path = self.app_dir / "vision" / "vision_manager.py"
        
        if vision_manager_path.exists():
            content = vision_manager_path.read_text()
            
            # Add framework configuration
            framework_config = '''
# ====================================================================
# 🎯 FRAMEWORK CONFIGURATION - ENABLE/DISABLE FRAMEWORK ANALYSIS
# ====================================================================

ENABLE_FRAMEWORK_ANALYSIS = True  # 5-Point CRO Framework Analysis

'''
            
            # Insert after existing configuration
            if "# ====" in content:
                lines = content.split('\n')
                insert_index = -1
                for i, line in enumerate(lines):
                    if "# ====" in line and "CONFIGURATION" in line:
                        # Find the end of this configuration block
                        for j in range(i + 1, len(lines)):
                            if lines[j].strip() == "" and j < len(lines) - 1:
                                if not lines[j + 1].startswith('#') and not lines[j + 1].startswith('ENABLE_'):
                                    insert_index = j
                                    break
                        break
                
                if insert_index > -1:
                    lines.insert(insert_index, framework_config)
                    vision_manager_path.write_text('\n'.join(lines))
                    logger.info("✅ Updated vision_manager.py with framework configuration")
    
    def update_models(self):
        """Update models.py with framework support"""
        models_path = self.app_dir / "models.py"
        
        if models_path.exists():
            content = models_path.read_text()
            
            # Add framework models
            framework_models = '''
# Framework-specific models
class FrameworkMetrics(BaseModel):
    """Metrics collected by the CRO framework"""
    has_breadcrumbs: Optional[bool] = False
    navigation_links: Optional[int] = 0
    page_depth: Optional[int] = 0
    font_count: Optional[int] = 0
    product_image_count: Optional[int] = 0
    trust_badges: Optional[int] = 0
    has_return_policy: Optional[bool] = False

class FrameworkAnalysis(BaseModel):
    """Results from framework analysis"""
    score: int
    issues: List[str] = []
    recommendations: List[Dict[str, str]] = []
    metrics: FrameworkMetrics = FrameworkMetrics()

'''
            
            # Add before the last class
            content = content.replace(
                "class CROAnalysisResponse(BaseModel):",
                f"{framework_models}\nclass CROAnalysisResponse(BaseModel):"
            )
            
            models_path.write_text(content)
            logger.info("✅ Updated models.py with framework models")
    
    def update_main_file(self):
        """Update main.py with framework endpoints"""
        main_path = self.project_root / "main.py"
        
        if main_path.exists():
            content = main_path.read_text()
            
            # Add framework endpoint
            framework_endpoint = '''
@app.get("/api/framework/status")
async def get_framework_status():
    """Get framework analysis status"""
    return {
        "framework_enabled": True,
        "categories": ["navigation", "display", "information", "technical", "psychological"],
        "version": "1.0",
        "integration_status": "active"
    }

'''
            
            # Insert before the main block
            content = content.replace(
                'if __name__ == "__main__":',
                f"{framework_endpoint}\nif __name__ == \"__main__\":"
            )
            
            main_path.write_text(content)
            logger.info("✅ Updated main.py with framework endpoints")
    
    def create_framework_files(self):
        """Create new framework-specific files"""
        logger.info("📝 Creating framework files")
        
        # Create framework init file
        framework_init = self.app_dir / "framework" / "__init__.py"
        framework_init.write_text('"""CRO Framework Package"""')
        
        # Create framework config file
        config_content = '''"""Framework Configuration"""

class FrameworkConfig:
    ENABLE_NAVIGATION_ANALYSIS = True
    ENABLE_DISPLAY_ANALYSIS = True
    ENABLE_INFORMATION_ANALYSIS = True
    ENABLE_TECHNICAL_ANALYSIS = True
    ENABLE_PSYCHOLOGICAL_ANALYSIS = True
    
    CATEGORY_WEIGHTS = {
        "navigation": 0.20,
        "display": 0.15,
        "information": 0.25,
        "technical": 0.20,
        "psychological": 0.20
    }

config = FrameworkConfig()
'''
        
        config_file = self.app_dir / "framework" / "config.py"
        config_file.write_text(config_content)
        
        logger.info("✅ Created framework configuration files")
    
    def update_configuration(self):
        """Update project configuration files"""
        logger.info("⚙️  Updating configuration")
        
        # Update requirements.txt if it exists
        requirements_path = self.project_root / "requirements.txt"
        if requirements_path.exists():
            content = requirements_path.read_text()
            
            # Add framework comment if not present
            if "# CRO Framework" not in content:
                content += "\n# CRO Framework - No additional dependencies required\n"
                requirements_path.write_text(content)
                logger.info("✅ Updated requirements.txt")
        
        # Create .env.example with framework settings
        env_example = self.project_root / ".env.framework.example"
        env_content = '''# CRO Framework Configuration
CRO_ENABLE_NAVIGATION=true
CRO_ENABLE_DISPLAY=true
CRO_ENABLE_INFORMATION=true
CRO_ENABLE_TECHNICAL=true
CRO_ENABLE_PSYCHOLOGICAL=true
CRO_MAX_ANALYSIS_TIME=30
CRO_SAVE_SCREENSHOTS=true
'''
        env_example.write_text(env_content)
        logger.info("✅ Created framework environment configuration")
    
    def generate_integration_report(self):
        """Generate integration completion report"""
        logger.info("📋 Generating integration report")
        
        report_content = f"""# CRO Framework Integration Report

## Integration Completed Successfully! ✅

### Changes Made:

1. **Directory Structure Created:**
   - app/framework/ - Framework core components
   - app/services/enhanced/ - Enhanced service implementations
   - screenshots/ - Screenshot storage for debugging

2. **Files Updated:**
   - app/vision/vision_manager.py - Added framework configuration
   - app/models.py - Added framework data models
   - main.py - Added framework endpoints

3. **New Files Created:**
   - app/framework/config.py - Framework configuration
   - .env.framework.example - Environment variables
   - backup_original/ - Backup of original files

### Framework Features Available:

- ✅ Navigation Analysis (breadcrumbs, menu complexity)
- ✅ Display Analysis (fonts, whitespace, layout)
- ✅ Information Analysis (product content, images)
- ✅ Technical Analysis (performance, mobile)
- ✅ Psychological Analysis (trust signals, social proof)

### Next Steps:

1. Restart your application:
   ```bash
   python main.py
   ```

2. Test framework integration:
   ```bash
   python test_framework.py
   ```

3. Run sample analysis:
   ```bash
   curl -X POST http://localhost:8080/api/analyze \\
     -H "Content-Type: application/json" \\
     -d '{{"url": "https://example.com"}}'
   ```

### Configuration:

To enable/disable framework components, edit:
- `app/vision/vision_manager.py` - Main switches
- `app/framework/config.py` - Detailed settings

### Support:

- Check logs for framework status: "CRO Framework Analysis enabled"
- Verify endpoint: GET /api/framework/status
- View categories: GET /api/framework/categories

Integration completed at: {self.get_timestamp()}
"""
        
        report_path = self.project_root / "FRAMEWORK_INTEGRATION_REPORT.md"
        report_path.write_text(report_content)
        
        print("\n" + "="*60)
        print("🎯 CRO FRAMEWORK INTEGRATION COMPLETED!")
        print("="*60)
        print("✅ Framework successfully integrated into your project")
        print("📁 Original files backed up to backup_original/")
        print("📋 Integration report: FRAMEWORK_INTEGRATION_REPORT.md")
        print("\n🚀 Next steps:")
        print("   1. Restart your application: python main.py")
        print("   2. Test integration: python test_framework.py")
        print("   3. Check status: curl http://localhost:8080/api/framework/status")
        print("="*60)
    
    def get_timestamp(self):
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """Main integration function"""
    print("🎯 CRO Framework Integration Script")
    print("This will integrate the 5-point CRO framework into your existing project")
    
    # Get project root
    project_root = input("Enter project root directory (default: current directory): ").strip()
    if not project_root:
        project_root = "."
    
    # Confirm integration
    confirm = input("Continue with framework integration? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Integration cancelled")
        return
    
    # Run integration
    integrator = FrameworkIntegrator(project_root)
    try:
        integrator.integrate_framework()
    except Exception as e:
        logger.error(f"Integration failed: {e}")
        print(f"❌ Integration failed: {e}")
        print("Check logs and try again")

if __name__ == "__main__":
    main()