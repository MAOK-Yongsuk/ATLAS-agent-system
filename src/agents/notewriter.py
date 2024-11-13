from typing import Dict, List, Any
from crewai import Agent
#from langchain.tools.base import BaseTool
from utils.logger import get_logger
import datetime
from src.agents.base_agent import BaseAgent
logger = get_logger(__name__)

class NotewriterAgent(BaseAgent):
    def get_role(self) -> str:
        return "Study Material Specialist"
    
    def get_goal(self) -> str:
        return "Create comprehensive and effective study materials"
    
    def get_backstory(self) -> str:
        return """Expert in creating educational content with deep 
                understanding of learning methodologies."""
    
    def get_tools(self) -> List[Dict]:
        """Keep your existing tools but use the new format"""
        return [
            self.create_tool(
                func=self.summarize_content,
                name="summarize_content",
                description="Create a comprehensive summary of study materials"
            ),
            self.create_tool(
                func=self.extract_concepts,
                name="extract_concepts",
                description="Extract and organize key concepts"
            ),
            self.create_tool(
                func=self.create_study_guide,
                name="create_study_guide",
                description="Create a structured study guide"
            ),
            self.create_tool(
                func=self.analyze_complexity,
                name="analyze_complexity",
                description="Analyze content complexity and structure"
            )
        ]

    def create_agent(self) -> Agent:
        """Create CrewAI agent"""
        return Agent(
            role='Study Material Specialist',
            goal='Create comprehensive and effective study materials',
            backstory="""Expert in creating educational content with deep 
                        understanding of learning methodologies.""",
            tools=self.get_tools(),
            verbose=True,
            llm=self.llm
        )

    async def summarize_content(self, content: Dict) -> Dict:
        """Keep your existing implementation"""
        try:
            if not content or 'text' not in content:
                return {
                    "summary": "No content provided",
                    "type": "error",
                    "timestamp": datetime.now().isoformat()
                }

            prompt = f"""
            Create a comprehensive summary of:
            {content['text']}
            
            Focus on:
            1. Main concepts
            2. Key points
            3. Important relationships
            """
            
            response = await self.generate_response(prompt)
            return {
                "summary": response,
                "type": "summary",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in summarize_content: {str(e)}")
            return {
                "summary": f"Error: {str(e)}",
                "type": "error",
                "timestamp": datetime.now().isoformat()
            }

    async def extract_concepts(self, content: Dict) -> List[Dict]:
        """Extract key concepts"""
        try:
            prompt = f"""
            Extract key concepts from:
            {content.get('text', '')}
            
            For each concept provide:
            1. Name
            2. Brief definition
            3. Importance level
            4. Related concepts
            """
            
            response = await self.generate_response(prompt)
            return self._parse_concepts(response)
        except Exception as e:
            logger.error(f"Error in extract_concepts: {str(e)}")
            raise

    async def create_study_guide(self, content: Dict) -> Dict:
        """Create study guide"""
        try:
            prompt = f"""
            Create a study guide for:
            {content.get('text', '')}
            
            Include:
            1. Learning objectives
            2. Key concepts
            3. Examples
            4. Practice questions
            """
            
            response = await self.generate_response(prompt)
            return {
                "guide": response,
                "type": "study_guide",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in create_study_guide: {str(e)}")
            raise

    async def analyze_complexity(self, content: Dict) -> Dict:
        """Analyze content complexity and structure"""
        try:
            prompt = f"""
            Analyze the complexity of:
            Content: {content.get('text', '')}
            
            Evaluate:
            1. Conceptual difficulty (1-5)
            2. Technical complexity (1-5)
            3. Prerequisites required
            4. Potential challenging areas
            5. Recommended background knowledge
            """
            
            response = await self.generate_response(prompt)
            return self._parse_complexity(response)
        except Exception as e:
            logger.error(f"Error in analyze_complexity: {str(e)}")
            raise
    
    def _parse_concepts(self, text: str) -> List[Dict]:
        """Parse concept extraction response"""
        # Implement concept parsing logic
        return []
    
    def _parse_complexity(self, text: str) -> Dict:
        """Parse complexity analysis response"""
        # Implement complexity parsing logic
        return {
            "conceptual_difficulty": 3,
            "technical_complexity": 3,
            "prerequisites": [],
            "challenging_areas": [],
            "recommended_background": []
        }