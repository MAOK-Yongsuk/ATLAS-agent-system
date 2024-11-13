import asyncio
from typing import Dict
from datetime import datetime
from openai import OpenAI, AsyncOpenAI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint
import traceback
from src.agents.notewriter import NotewriterAgent
from src.agents.planner import PlannerAgent
from src.agents.advisor import AdvisorAgent
from src.agents.profile_analyzer import ProfileAnalyzer
from src.graphs.study_workflow import GraphNode
from tests.test_utils import MockDataLoader
from utils.config import load_config
from utils.logger import get_logger

console = Console()
logger = get_logger(__name__)

class AcademicAssistant:
    def __init__(self):
        # Load configuration
        self.config = load_config()
        self.mock_data = MockDataLoader()
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Initialize workflow
        self.workflow =GraphNode(
            agents=self.agents
    
        )
        # self.workflow.config.update({
        #     "recursion_limit": self.config.get("workflow", {}).get("recursion_limit", 100),
        #     "max_attempts": self.config.get("workflow", {}).get("max_attempts", 5)
        # })
    
    def _initialize_llm(self):
        try:
            return AsyncOpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=self.config["llm"]["nemotron_70b_key"]
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    def _initialize_agents(self) -> Dict:
        try:
            return {
                "notewriter": NotewriterAgent(self.llm).create_agent(),
                "planner": PlannerAgent(self.llm).create_agent(),
                "advisor": AdvisorAgent(self.llm).create_agent(),
                "profile_analyzer": ProfileAnalyzer(self.llm).create_agent()
            }
        except Exception as e:
            # Log the basic error message at ERROR level
            logger.error(f"Failed to initialize agents: {str(e)}")
            
            # Log detailed stack trace at DEBUG level
            logger.debug(
                "Detailed error information:", 
                exc_info=True,  # This captures the full stack trace
                extra={
                    'error_type': type(e).__name__,
                    'error_details': str(e),
                    'stack_trace': traceback.format_exc()
                }
            )
            

    
    async def generate_llm_response(self, prompt: str) -> str:
        try:
            completion = self.llm.chat.completions.create(
                model="nvidia/llama-3.1-nemotron-70b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config["llm"]["temperature"],
                top_p=1,
                max_tokens=self.config["llm"]["max_tokens"],
                stream=True
            )
            
            response_text = " "
            async for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response_text += chunk.choices[0].delta.content
                    console.print(chunk.choices[0].delta.content, end="")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    async def process_study_request(self, subject: str) -> Dict:
        """Process a study request with enhanced error handling and validation"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(
                description="[cyan]Processing study request...", 
                total=100
            )
            
            try:
                # Validate subject
                if not subject:
                    raise ValueError("Subject is required")
                
                console.print(f"\n[bold blue]Processing study request for: {subject}[/bold blue]")
                
                # Load test data with validation
                user_profile = await self._load_user_profile()
                study_material = await self._load_study_material(subject)
                progress.update(task, advance=20)
                
                # Create initial state with validation
                initial_state = await self._create_initial_state(user_profile, study_material)
                progress.update(task, advance=20)
                console.print("[green]Initial state prepared[/green]")
                
                # Execute workflow with detailed error handling
                console.print("\n[bold]Executing study workflow...[/bold]")
                final_state = await self._execute_workflow(initial_state)
                progress.update(task, advance=40)
                
                # Process and validate final state
                result = await self._process_final_state(final_state)
                
                if result["status"] == "failed":
                    error_msg = result.get("error", "Unknown error occurred")
                    logger.error(f"Study request failed: {error_msg}")
                    raise RuntimeError(f"Study request failed: {error_msg}")
                
                return result
                
            except Exception as e:
                error_msg = f"Error processing study request: {str(e)}"
                logger.error(error_msg, exc_info=True)
                console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
                
                return {
                    "status": "failed",
                    "error": str(e),
                    "step": "process_study_request",
                    "timestamp": datetime.now().isoformat()
                }
    async def _load_user_profile(self) -> Dict:
        """Load and validate user profile with more flexible validation"""
        try:
            profile = self.mock_data.load_adhd_profile("user_001")
            if not profile:
                return {
                    "study_habits": {},
                    "performance_history": [],
                    "adhd_characteristics": {}
                }
            
            required_fields = ["study_habits", "performance_history", "adhd_characteristics"]
            for field in required_fields:
                if field not in profile:
                    profile[field] = {} if field == "study_habits" else (
                        [] if field == "performance_history" else {})
            
            return profile
            
        except Exception as e:
            logger.error(f"Error loading user profile: {str(e)}")
            # Return default profile instead of raising
            return {
                "study_habits": {},
                "performance_history": [],
                "adhd_characteristics": {}
            }

    async def _load_study_material(self, subject: str) -> Dict:
        """Load study material with defaults"""
        try:
            material = self.mock_data.load_study_material(f"{subject}.md")
            if not material:
                return {
                    "text": f"Default content for {subject}",
                    "title": subject,
                    "difficulty_level": "intermediate"
                }
            
            # Ensure text field exists
            if "text" not in material:
                material["text"] = f"Default content for {subject}"
                
            return material
            
        except Exception as e:
            logger.error(f"Error loading study material: {str(e)}")
            return {
                "text": f"Default content for {subject}",
                "title": subject,
                "difficulty_level": "intermediate"
            }

    async def _create_initial_state(self, user_profile: Dict, study_material: Dict) -> Dict:
        """Create and validate initial state"""
        try:
            initial_state = {
                "user_profile": user_profile,
                "study_material": study_material,
                "summaries": [],
                "study_plan": {},
                "progress": {
                    "start_time": datetime.now().isoformat(),
                    "steps_completed": 0,
                    "current_focus_score": 0.0
                },
                "feedback": [],
                "current_step": "start",
                "status": "processing",
                "attempts": 0,
                "iteration_count": 0
            }
            
            # Validate all required fields are present
            required_fields = [
                "user_profile", "study_material", "summaries", "study_plan",
                "progress", "feedback", "current_step", "status"
            ]
            
            missing_fields = [field for field in required_fields if field not in initial_state]
            if missing_fields:
                raise ValueError(f"Missing required state fields: {missing_fields}")
                
            return initial_state
            
        except Exception as e:
            logger.error(f"Error creating initial state: {str(e)}")
            raise

    async def _execute_workflow(self, initial_state: Dict) -> Dict:
        """Execute workflow with enhanced error handling"""
        try:
            return await self.workflow.execute(initial_state)
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
            return {
                **initial_state,
                "status": "failed",
                "error": str(e)
            }

    async def _process_final_state(self, state: Dict) -> Dict:
        """Process and validate final state"""
        try:
            # Validate final state
            if not isinstance(state, dict):
                raise ValueError("Invalid final state format")
                
            if "status" not in state:
                raise ValueError("Final state missing status field")
                
            # Add execution summary
            summary = {
                "completion_time": datetime.now().isoformat(),
                "steps_completed": state.get("progress", {}).get("steps_completed", 0),
                "final_status": state["status"]
            }
            
            return {**state, "summary": summary}
            
        except Exception as e:
            logger.error(f"Error processing final state: {str(e)}")
            return {
                "status": "failed",
                "error": f"Error processing final state: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _display_results(self, state: Dict) -> None:
        """Display execution results"""
        try:
            console.print("\n[bold green]Study Session Results[/bold green]")
            
            if state["status"] == "failed":
                console.print(f"[bold red]Execution failed:[/bold red] {state.get('error', 'Unknown error')}")
                return
            
            summary_text = "\n".join([
                f"[bold]Status:[/bold] {state['status']}",
                f"[bold]Steps Completed:[/bold] {state['progress'].get('steps_completed', 0)}",
                f"[bold]Focus Score:[/bold] {state['progress'].get('current_focus_score', 0):.2f}"
            ])
            
            console.print(Panel(summary_text, title="Session Summary"))
            
        except Exception as e:
            logger.error(f"Error displaying results: {str(e)}")
            console.print("[bold red]Error displaying results[/bold red]")

    
    def visualize_workflow(self):
        try:
            self.workflow.visualize(filename="workflow_graph.png")
            console.print(
                "[green]Workflow graph saved as 'workflow_graph.png'[/green]"
            )
        except Exception as e:
            logger.error(f"Failed to visualize workflow: {str(e)}")
            console.print(
                "[red]Failed to generate workflow visualization[/red]"
            )

async def main():
    console.print("[bold magenta]Starting Academic Life Assistant...[/bold magenta]")
    
    # try:
    assistant = AcademicAssistant()
    assistant.visualize_workflow()
        
        # Process study request
    result = await assistant.process_study_request("machine_learning")
        
    if result["status"] != "failed":
            console.print("\n[bold green]Process completed successfully![/bold green]")
    else:
            console.print("\n[bold red]Process completed with errors![/bold red]")
        
    # except Exception as e:
    #     console.print(f"\n[bold red]Critical error in main execution: {str(e)}[/bold red]")
    #     logger.critical(f"Critical error in main execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())