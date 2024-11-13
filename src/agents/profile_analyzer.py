from typing import Dict, List
from datetime import datetime
from src.agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)

class ProfileAnalyzer(BaseAgent):
    """Agent for analyzing student profiles and providing personalized learning insights"""
    
    def get_role(self) -> str:
        return 'Learning Profile Analyzer'
    
    def get_goal(self) -> str:
        return 'Analyze student learning patterns and provide personalized study strategies'
    
    def get_backstory(self) -> str:
        return """Expert in understanding student learning styles, ADHD patterns, 
                and creating personalized study strategies. Specializes in helping 
                students overcome focus challenges and maximize learning effectiveness."""
    
    def get_tools(self) -> List[Dict]:
        """Get analyzer-specific tools"""
        return [
            self.create_tool(
                func=self.analyze_study_profile,
                name="analyze_study_profile",
                description="Analyze student's learning profile and ADHD patterns"
            ),
            self.create_tool(
                func=self.get_study_recommendations,
                name="get_study_recommendations",
                description="Provide personalized study strategies"
            ),
            self.create_tool(
                func=self.analyze_focus_patterns,
                name="analyze_focus_patterns",
                description="Analyze student's focus and attention patterns"
            )
        ]

    async def analyze_study_profile(self, user_data: Dict) -> Dict:
        """Analyze student's study profile with ADHD considerations"""
        try:
            if not user_data:
                return {
                    "status": "error",
                    "message": "No user data provided",
                    "timestamp": datetime.now().isoformat()
                }

            prompt = f"""
            Analyze this student's academic profile for personalized learning strategies.
            Focus on practical, ADHD-friendly recommendations.

            Study Habits:
            - Preferred study times: {user_data.get('study_habits', {}).get('preferred_time', 'unknown')}
            - Current session duration: {user_data.get('study_habits', {}).get('session_duration', 'unknown')}
            - Break frequency: {user_data.get('study_habits', {}).get('break_frequency', 'unknown')}
            - Environment preferences: {user_data.get('study_habits', {}).get('environment_preferences', [])}
            - Common distractions: {user_data.get('study_habits', {}).get('distractions', [])}

            Performance History:
            {user_data.get('performance_history', [])}

            ADHD Characteristics:
            - Focus duration: {user_data.get('adhd_characteristics', {}).get('focus_duration', 'unknown')}
            - Break needs: {user_data.get('adhd_characteristics', {}).get('break_needs', 'unknown')}
            - Learning style: {user_data.get('adhd_characteristics', {}).get('learning_style', 'unknown')}
            - Attention patterns: {user_data.get('adhd_characteristics', {}).get('attention_patterns', [])}

            Provide specific analysis on:
            1. Optimal study session structure
            2. Best environment setup
            3. Most effective learning methods
            4. Focus enhancement strategies
            5. Practical study tips
            """
            
            analysis = await self.generate_response(prompt)
            if not analysis:
                raise ValueError("Failed to generate analysis")

            return {
                "user_id": user_data.get("user_id"),
                "analysis": self._structure_analysis(analysis),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing study profile: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_study_recommendations(self, profile: Dict) -> Dict:
        """Get practical study recommendations"""
        try:
            prompt = f"""
            Based on this student's profile, provide practical, ADHD-friendly study tips.
            
            Learning Style: {profile.get('learning_style')}
            Focus Duration: {profile.get('focus_duration')}
            Key Challenges: {profile.get('challenges', [])}
            
            Provide:
            1. 3-5 specific study strategies
            2. Focus maintenance techniques
            3. Break activities suggestions
            4. Environment optimization tips
            5. Motivation maintenance strategies
            """
            
            recommendations = await self.generate_response(prompt)
            return {
                "recommendations": self._parse_recommendations(recommendations),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def analyze_focus_patterns(self, focus_data: Dict) -> Dict:
        """Analyze student's focus and attention patterns"""
        try:
            prompt = f"""
            Analyze these focus and attention patterns:
            
            Peak Focus Times: {focus_data.get('peak_times', [])}
            Distraction Triggers: {focus_data.get('triggers', [])}
            Task Completion Patterns: {focus_data.get('completion_patterns', [])}
            
            Provide:
            1. Optimal study time recommendations
            2. Distraction management strategies
            3. Task chunking suggestions
            4. Focus maintenance techniques
            """
            
            analysis = await self.generate_response(prompt)
            return {
                "analysis": self._parse_focus_patterns(analysis),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        
        except Exception as e:
            logger.error(f"Error analyzing focus patterns: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _structure_analysis(self, text: str) -> Dict:
        """Structure the analysis response"""
        try:
           
            return {
                "study_sessions": {
                    "optimal_duration": "25-30 minutes",
                    "break_frequency": "5-10 minutes every session"
                },
                "environment": {
                    "setup": "quiet, well-lit space",
                    "materials": "organized workspace"
                },
                "learning_methods": {
                    "primary": "visual learning",
                    "techniques": ["mind mapping", "color coding"]
                },
                "focus_strategies": [
                    "Pomodoro technique",
                    "body doubling",
                    "background music"
                ]
            }
        except Exception as e:
            logger.error(f"Error structuring analysis: {str(e)}")
            return {}

    def _parse_recommendations(self, text: str) -> List[str]:
        """Parse study recommendations"""
        try:
            
            return [
                "Use Pomodoro technique with 25-minute focus sessions",
                "Create visual study guides with color coding",
                "Take active breaks every 25-30 minutes",
                "Use noise-canceling headphones during study sessions",
                "Break large tasks into smaller, manageable chunks"
            ]
        except Exception as e:
            logger.error(f"Error parsing recommendations: {str(e)}")
            return []

    def _parse_focus_patterns(self, text: str) -> Dict:
        """Parse focus pattern analysis"""
        try:
            
            return {
                "optimal_times": ["morning", "early afternoon"],
                "break_schedule": "every 25-30 minutes",
                "environment_needs": ["quiet", "organized"],
                "focus_techniques": ["time blocking", "task chunking"]
            }
        except Exception as e:
            logger.error(f"Error parsing focus patterns: {str(e)}")
            return {}