from typing import Dict, List
from datetime import datetime, timedelta
from src.agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)

class PlannerAgent(BaseAgent):
    """Agent for academic planning and schedule optimization"""
    
    def get_role(self) -> str:
        return 'Academic Planning Specialist'
    
    def get_goal(self) -> str:
        return 'Create optimized study plans and schedules for ADHD students'
    
    def get_backstory(self) -> str:
        return """Expert in academic planning with deep understanding of 
                learning patterns and ADHD-friendly scheduling. Specializes in 
                creating flexible, engaging study plans that accommodate varying 
                attention spans and energy levels."""
    
    def get_tools(self) -> List[Dict]:
        """Get planner-specific tools"""
        return [
            self.create_tool(
                func=self.create_study_plan,
                name="create_study_plan",
                description="Create personalized ADHD-friendly study plans"
            ),
            self.create_tool(
                func=self.optimize_schedule,
                name="optimize_schedule",
                description="Optimize study schedules based on performance patterns"
            ),
            self.create_tool(
                func=self.analyze_workload,
                name="analyze_workload",
                description="Analyze and balance academic workload"
            ),
            self.create_tool(
                func=self.generate_milestones,
                name="generate_milestones",
                description="Create achievable study milestones and checkpoints"
            ),
            self.create_tool(
                func=self.sync_calendar,
                name="sync_calendar",
                description="Synchronize study plans with calendar"
            )
        ]

    async def create_study_plan(self, params: Dict) -> Dict:
        """Create personalized study plan with enhanced error handling"""
        try:
            if not params or not all(k in params for k in ['subject', 'available_time', 'learning_style', 'adhd_profile']):
                return {
                    "status": "error",
                    "message": "Missing required parameters",
                    "timestamp": datetime.now().isoformat()
                }

            prompt = f"""
            Create a detailed ADHD-friendly study plan considering:
            Subject: {params['subject']}
            Available Time: {params['available_time']}
            Learning Style: {params['learning_style']}
            ADHD Profile: {params['adhd_profile']}
            
            Plan should include:
            1. Session breakdown with durations (20-30 minute focus periods)
            2. Strategic break scheduling (frequent, engaging breaks)
            3. Focus techniques for each session (e.g., Pomodoro, body doubling)
            4. Clear progress checkpoints
            5. Reward system for motivation
            6. Flexibility options for different energy levels
            7. Distraction management strategies
            """
            
            response = await self.generate_response(prompt)
            if not response:
                raise ValueError("Failed to generate study plan")
                
            return self._structure_study_plan(response)
            
        except Exception as e:
            logger.error(f"Error creating study plan: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def optimize_schedule(self, schedule: Dict) -> Dict:
        """Optimize study schedule with ADHD considerations"""
        try:
            prompt = f"""
            Optimize this schedule for ADHD students considering:
            Current Schedule: {schedule.get('current', {})}
            Performance Data: {schedule.get('performance', {})}
            Energy Patterns: {schedule.get('energy_patterns', [])}
            
            Provide:
            1. Optimized time blocks (25-minute focus sessions)
            2. Strategic break distributions (5-15 minute breaks)
            3. Focus technique recommendations
            4. Backup plans for low-energy days
            5. Motivation maintenance strategies
            6. Environment optimization tips
            """
            
            response = await self.generate_response(prompt)
            return self._parse_schedule_optimization(response)
            
        except Exception as e:
            logger.error(f"Error optimizing schedule: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def analyze_workload(self, tasks: List[Dict]) -> Dict:
        """Analyze academic workload with ADHD considerations"""
        try:
            prompt = f"""
            Analyze academic workload for ADHD student:
            Tasks: {tasks}
            
            Provide:
            1. Task breakdown into manageable chunks
            2. Priority ordering with urgency/importance matrix
            3. Effort estimation with focus requirements
            4. Potential challenges and mitigation strategies
            5. Required resources and tools
            6. Recommended focus techniques per task
            7. Alternative approaches for different energy levels
            """
            
            response = await self.generate_response(prompt)
            return self._parse_workload_analysis(response)
            
        except Exception as e:
            logger.error(f"Error analyzing workload: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def generate_milestones(self, plan: Dict) -> List[Dict]:
        """Generate achievable study milestones"""
        try:
            prompt = f"""
            Create ADHD-friendly milestone plan for:
            Study Plan: {plan}
            
            Include:
            1. Small, achievable checkpoints
            2. Clear progress indicators
            3. Specific achievement criteria
            4. Regular review points
            5. Reward systems
            6. Flexibility options
            7. Recovery strategies for missed milestones
            """
            
            response = await self.generate_response(prompt)
            return self._parse_milestones(response)
            
        except Exception as e:
            logger.error(f"Error generating milestones: {str(e)}")
            return []

    async def sync_calendar(self, study_plan: Dict) -> Dict:
        """Synchronize study plan with calendar"""
        try:
            events = self._create_calendar_events(study_plan)
            return {
                "status": "success",
                "events": events,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error syncing calendar: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _structure_study_plan(self, text: str) -> Dict:
        """Parse and structure study plan"""
        try:
            
            return {
                "sessions": [],
                "breaks": [],
                "techniques": [],
                "checkpoints": [],
                "rewards": [],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error structuring study plan: {str(e)}")
            return {"error": str(e)}

    def _parse_schedule_optimization(self, text: str) -> Dict:
        """Parse schedule optimization results"""
        try:
            
            return {
                "time_blocks": [],
                "breaks": [],
                "techniques": [],
                "contingency_plans": []
            }
        except Exception as e:
            logger.error(f"Error parsing schedule: {str(e)}")
            return {"error": str(e)}

    def _parse_workload_analysis(self, text: str) -> Dict:
        """Parse workload analysis results"""
        try:
            
            return {
                "distribution": {},
                "priorities": [],
                "effort_estimates": {},
                "risks": []
            }
        except Exception as e:
            logger.error(f"Error parsing workload: {str(e)}")
            return {"error": str(e)}

    def _parse_milestones(self, text: str) -> List[Dict]:
        """Parse milestone data"""
        try:
           
            return [
                {
                    "checkpoint": "milestone 1",
                    "criteria": [],
                    "rewards": []
                }
            ]
        except Exception as e:
            logger.error(f"Error parsing milestones: {str(e)}")
            return []

    def _create_calendar_events(self, study_plan: Dict) -> List[Dict]:
        """Create calendar events from study plan"""
        try:
            
            return []
        except Exception as e:
            logger.error(f"Error creating calendar events: {str(e)}")
            return []