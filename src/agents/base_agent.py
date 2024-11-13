from typing import Dict, List, Callable, Any
from crewai import Agent
from utils.logger import get_logger
#from langchain.tools import Tool, BaseTool
logger = get_logger(__name__)

# class ToolWrapper(BaseTool):
#     """Wrapper class for tool functions that implements BaseTool properly"""
    
#     def __init__(self, name: str, func: Callable, description: str):
#         super().__init__(name=name, description=description)
#         self._func = func

#     def _run(self, *args: Any, **kwargs: Any) -> Any:
#         """Required implementation of abstract _run method"""
#         return self._func(*args, **kwargs)
class BaseAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_tool(self, func: Callable, name: str, description: str) -> Dict:
        """Create a tool in the format CrewAI expects"""
        return {
            "name": name,
            "description": description,
            "function": func.__name__,  # Just use the function name
            "coroutine": func  # Store the actual coroutine
        }
    
    
    async def generate_response(self, prompt: str) -> str:
        try:
            completion = await self.llm.chat.completions.create(
                model="nvidia/llama-3.1-nemotron-70b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return None

 
    def create_agent(self) -> Agent:
        """Create agent with appropriate configuration"""
        try:
            return Agent(
                role=self.get_role(),
                goal=self.get_goal(),
                backstory=self.get_backstory(),
                tools=self.get_tools(),
                verbose=True,
                llm=self.llm
            )
        except Exception as e:
            logger.error(f"Failed to create agent: {str(e)}")
            raise

    def get_role(self) -> str:
        raise NotImplementedError
        
    def get_goal(self) -> str:
        raise NotImplementedError
        
    def get_backstory(self) -> str:
        raise NotImplementedError
        
    def get_tools(self) -> List[Dict]:
        raise NotImplementedError
