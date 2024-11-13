import json
import markdown
import os
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class MockDataLoader:
    """Utility class for loading and managing mock data with improved error handling"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent / "mock_data"
        # Ensure mock data directory exists
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(self.base_path / "lecture_notes", exist_ok=True)
        
        # Initialize default data
        self._initialize_default_data()
    
    def _initialize_default_data(self):
        """Initialize default mock data files if they don't exist"""
        # Default ADHD profile
        adhd_profile = {
            "user_id": "default",
            "study_habits": {
                "preferred_time": "morning",
                "session_duration": 25,
                "break_frequency": 5,
                "environment_preferences": ["quiet", "well-lit"],
                "distractions": ["notifications", "noise"]
            },
            "performance_history": [
                {
                    "subject": "math",
                    "average_score": 85,
                    "study_duration": "2 hours",
                    "focus_rating": 7
                }
            ],
            "adhd_characteristics": {
                "focus_duration": "20-30 minutes",
                "break_needs": "frequent",
                "learning_style": "visual",
                "organizational_level": "needs support",
                "attention_patterns": ["hyper-focus", "easily distracted"]
            }
        }
        
        # Default calendar events
        calendar_events = {
            "events": []
        }
        
        # Default tasks
        task = {
            "tasks": []
        }
        
        # Default study material
        default_md = """
# Machine Learning Basics

Machine Learning is a subset of artificial intelligence that focuses on developing systems that can learn from data.

## Key Concepts
1. Supervised Learning
2. Unsupervised Learning
3. Neural Networks
4. Model Evaluation

These concepts form the foundation of modern machine learning applications.
"""
        
        # Save default files if they don't exist
        self._save_json_if_not_exists("adhd_profile.json", adhd_profile)
        self._save_json_if_not_exists("calendar_events.json", calendar_events)
        self._save_json_if_not_exists("task.json", task)
        self._save_md_if_not_exists("lecture_notes/machine_learning.md", default_md)
    
    def _save_json_if_not_exists(self, filename: str, data: Dict):
        """Save JSON file if it doesn't exist"""
        file_path = self.base_path / filename
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
    
    def _save_md_if_not_exists(self, filename: str, content: str):
        """Save markdown file if it doesn't exist"""
        file_path = self.base_path / filename
        if not file_path.exists():
            os.makedirs(file_path.parent, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def load_study_material(self, filename: str) -> Dict[str, Any]:
        """Load study material from markdown files with error handling"""
        try:
            # If no extension provided, add .md
            if not Path(filename).suffix:
                filename = f"{filename}.md"
                
            file_path = self.base_path / "lecture_notes" / filename
            
            if not file_path.exists():
                logger.warning(f"Study material not found: {filename}")
                # Return default content
                return {
                    "content": f"# Default content for {filename}",
                    "html_content": f"<h1>Default content for {filename}</h1>",
                    "filename": filename
                }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                html_content = markdown.markdown(content)
                return {
                    "content": content,
                    "html_content": html_content,
                    "filename": filename
                }
                
        except Exception as e:
            logger.error(f"Error loading study material: {str(e)}")
            return {
                "content": "# Error loading content",
                "html_content": "<h1>Error loading content</h1>",
                "filename": filename
            }

    def load_adhd_profile(self, user_id: str) -> Dict:
        """Load ADHD profile with fallback to default"""
        try:
    
            return {
                "user_id": user_id,
                "study_habits": {
                    "preferred_time": "morning",
                    "session_duration": 25,
                    "break_frequency": 5,
                    "environment_preferences": ["quiet", "well-lit"],
                    "distractions": ["notifications", "noise"]
                },
                "performance_history": [
                    {
                        "subject": "math",
                        "average_score": 85,
                        "study_duration": "2 hours",
                        "focus_rating": 7
                    },
                    {
                        "subject": "science",
                        "average_score": 78,
                        "study_duration": "1.5 hours",
                        "focus_rating": 6
                    }
                ],
                "adhd_characteristics": {
                    "focus_duration": "20-30 minutes",
                    "break_needs": "frequent",
                    "learning_style": "visual",
                    "organizational_level": "needs support",
                    "attention_patterns": ["hyper-focus", "easily distracted"]
                }
            }
        except Exception as e:
            logger.error(f"Error loading ADHD profile: {str(e)}")
            # Return minimal valid profile
            return {
                "user_id": user_id,
                "study_habits": {},
                "performance_history": [],
                "adhd_characteristics": {}
            }

    def load_calendar_events(self) -> Dict[str, Any]:
        """Load calendar events with error handling"""
        try:
            file_path = self.base_path / "calendar_events.json"
            if not file_path.exists():
                return {"events": []}
                
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading calendar events: {str(e)}")
            return {"events": []}

    def load_tasks(self) -> Dict[str, Any]:
        """Load tasks with error handling"""
        try:
            file_path = self.base_path / "task.json"
            if not file_path.exists():
                return {"tasks": []}
                
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading tasks: {str(e)}")
            return {"tasks": []}

def save_test_output(output_type: str, data: Dict[str, Any], filename: str):
    """Save test outputs with error handling"""
    try:
        output_dir = Path(__file__).parent.parent / "data" / "sample_outputs" / output_type
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error saving test output: {str(e)}")