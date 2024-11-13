from typing import TypedDict, List, Dict, Literal, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime
import asyncio
from utils.logger import get_logger

logger = get_logger(__name__)

class StudyState(TypedDict):
    """State definition for study workflow"""
    user_profile: Dict
    study_material: Dict
    summaries: List[Dict]
    study_plan: Dict
    progress: Dict
    feedback: List[Dict]
    current_step: str
    status: Literal["processing", "reviewing", "complete", "failed"]
    attempts: int
    iteration_count: int

class GraphNode:
    """Manages the study material processing workflow"""
    
    def __init__(self, agents: Dict):
        """Initialize the workflow graph with agents
        
        Args:
            agents (Dict): Dictionary of initialized agents containing:
                - profile_analyzer: For analyzing user study patterns
                - notewriter: For processing study materials
                - planner: For creating study plans
                - advisor: For providing feedback and recommendations
        """
        self.agents = agents
        self.config = {
            "recursion_limit": 25,  # Reduced from 100
            "max_attempts": 3,      # Reduced from 5
            "min_completion_rate": 0.7,
            "min_understanding_level": 0.6,
            "max_review_attempts": 2,
            "max_plan_adjustments": 2
        }
        self.workflow = self._create_workflow()
    def set_config(self, config: Dict) -> None:
        """Update workflow configuration
        
        Args:
            config (Dict): Configuration parameters to update
        """
        self.config.update(config)
        logger.info(f"Updated workflow configuration: {self.config}")

    def _create_workflow(self) -> StateGraph:
        """Create and configure the workflow graph
        
        Returns:
            StateGraph: Compiled workflow graph
        """
        try:
            workflow = StateGraph(StudyState)
            
            # Add node for each workflow step
            workflow.add_node("analyze_profile", self._sync_analyze_profile)
            workflow.add_node("process_material", self._sync_process_material)
            workflow.add_node("create_plan", self._sync_create_plan)
            workflow.add_node("execute_session", self._sync_execute_session)
            workflow.add_node("evaluate_progress", self._sync_evaluate_progress)
            workflow.add_node("provide_feedback", self._sync_provide_feedback)
            
            # Set the entry point
            workflow.set_entry_point("analyze_profile")
            
            # Add sequential edges
            workflow.add_edge("analyze_profile", "process_material")
            workflow.add_edge("process_material", "create_plan")
            workflow.add_edge("create_plan", "execute_session")
            workflow.add_edge("execute_session", "evaluate_progress")
            
            # Add conditional edges for progress evaluation
            workflow.add_conditional_edges(
                "evaluate_progress",
                self._route_based_on_progress,
                {
                    "complete": "provide_feedback",
                    "adjust_plan": "create_plan",
                    "review_material": "process_material"
                }
            )
            
            # Add conditional edges for feedback
            workflow.add_conditional_edges(
                "provide_feedback",
                self._route_based_on_feedback,
                {
                    "continue": "execute_session",
                    "complete": END
                }
            )
            
            return workflow.compile()
            
        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            raise

    # Synchronous wrapper functions
    def _sync_analyze_profile(self, state: StudyState) -> StudyState:
        """Synchronous wrapper for profile analysis"""
        return asyncio.run(self._analyze_profile(state))
    
    def _sync_process_material(self, state: StudyState) -> StudyState:
        """Synchronous wrapper for material processing"""
        return asyncio.run(self._process_material(state))
    
    def _sync_create_plan(self, state: StudyState) -> StudyState:
        """Synchronous wrapper for plan creation"""
        return asyncio.run(self._create_plan(state))
    
    def _sync_execute_session(self, state: StudyState) -> StudyState:
        """Synchronous wrapper for session execution"""
        return asyncio.run(self._execute_session(state))
    
    def _sync_evaluate_progress(self, state: StudyState) -> StudyState:
        """Synchronous wrapper for progress evaluation"""
        return asyncio.run(self._evaluate_progress(state))
    
    def _sync_provide_feedback(self, state: StudyState) -> StudyState:
        """Synchronous wrapper for feedback provision"""
        return asyncio.run(self._provide_feedback(state))
    def _update_state(self, state: Dict, updates: Dict) -> Dict:
        """Safely update state dictionary"""
        try:
            new_state = state.copy()
            for key, value in updates.items():
                if value is not None:  # Only update if value exists
                    new_state[key] = value
            return new_state
        except Exception as e:
            logger.error(f"Error updating state: {str(e)}")
            return state
    # Async implementation functions
    async def _analyze_profile(self, state: StudyState) -> StudyState:
        """Analyze user profile with better error handling"""
        try:
            if not state.get("user_profile"):
                return self._update_state(state, {
                    "status": "failed",
                    "error": "No user profile provided"
                })

            profile_analysis = await self.agents["profile_analyzer"].analyze_study_profile(
                state["user_profile"]
            )

            if not profile_analysis:
                return self._update_state(state, {
                    "status": "failed",
                    "error": "Profile analysis failed"
                })

            return self._update_state(state, {
                "user_profile": profile_analysis,
                "current_step": "analyze_profile"
            })

        except Exception as e:
            logger.error(f"Profile analysis failed: {str(e)}")
            return self._update_state(state, {
                "status": "failed",
                "error": f"Profile analysis error: {str(e)}"
            })

    
    async def _process_material(self, state: StudyState) -> StudyState:
        """Process and summarize study materials
        
        Args:
            state (StudyState): Current workflow state
            
        Returns:
            StudyState: Updated state with processed materials
        """
        try:
            summary = await self.agents["notewriter"].summarize_content(
                state["study_material"]
            )
            return {
                **state,
                "summaries": state["summaries"] + [summary],
                "current_step": "process_material"
            }
        except Exception as e:
            logger.error(f"Material processing failed: {str(e)}")
            return {**state, "status": "failed"}
    
    async def _create_plan(self, state: StudyState) -> StudyState:
        """Create personalized study plan
        
        Args:
            state (StudyState): Current workflow state
            
        Returns:
            StudyState: Updated state with study plan
        """
        try:
            study_plan = await self.agents["planner"].create_study_plan({
                "profile": state["user_profile"],
                "material": state["study_material"],
                "summaries": state["summaries"]
            })
            return {
                **state,
                "study_plan": study_plan,
                "current_step": "create_plan"
            }
        except Exception as e:
            logger.error(f"Plan creation failed: {str(e)}")
            return {**state, "status": "failed"}
    
    async def _execute_session(self, state: StudyState) -> StudyState:
        """Execute study session tasks
        
        Args:
            state (StudyState): Current workflow state
            
        Returns:
            StudyState: Updated state with session results
        """
        try:
            session = state["study_plan"].get("current_session", {})
            
            progress = {
                "start_time": datetime.now().isoformat(),
                "completed_tasks": 0,
                "focus_scores": []
            }
            
            for task in session.get("tasks", []):
                task_result = {
                    "task_id": task.get("id"),
                    "focus_score": 0.8,
                    "completed": True
                }
                progress["completed_tasks"] += 1
                progress["focus_scores"].append(task_result)
            
            progress["end_time"] = datetime.now().isoformat()
            
            return {
                **state,
                "progress": {
                    **state.get("progress", {}),
                    "latest_session": progress
                },
                "current_step": "execute_session"
            }
            
        except Exception as e:
            logger.error(f"Session execution failed: {str(e)}")
            return {**state, "status": "failed"}
    
    async def _evaluate_progress(self, state: StudyState) -> StudyState:
        """Evaluate study progress
        
        Args:
            state (StudyState): Current workflow state
            
        Returns:
            StudyState: Updated state with progress evaluation
        """
        try:
            evaluation = await self.agents["advisor"].evaluate_progress({
                "plan": state["study_plan"],
                "progress": state["progress"]
            })
            return {
                **state,
                "progress": evaluation,
                "current_step": "evaluate_progress"
            }
        except Exception as e:
            logger.error(f"Progress evaluation failed: {str(e)}")
            return {**state, "status": "failed"}
    
    async def _provide_feedback(self, state: StudyState) -> StudyState:
        """Provide feedback and recommendations
        
        Args:
            state (StudyState): Current workflow state
            
        Returns:
            StudyState: Updated state with feedback
        """
        try:
            feedback = await self.agents["advisor"].provide_recommendations({
                "status": state["progress"],
                "profile": state["user_profile"]
            })
            return {
                **state,
                "feedback": state["feedback"] + [feedback],
                "current_step": "provide_feedback"
            }
        except Exception as e:
            logger.error(f"Feedback provision failed: {str(e)}")
            return {**state, "status": "failed"}
    def _update_progress_metrics(self, state: StudyState) -> StudyState:
        """Update progress metrics to help determine workflow completion"""
        progress = state["progress"]
        latest_session = progress.get("latest_session", {})
        
        # Calculate completion score
        tasks = state["study_plan"].get("tasks", [])
        completed_tasks = len([t for t in tasks if t.get("completed", False)])
        completion_score = completed_tasks / len(tasks) if tasks else 0
        
        # Calculate understanding score
        focus_scores = latest_session.get("focus_scores", [])
        understanding_score = sum(s.get("focus_score", 0) for s in focus_scores) / len(focus_scores) if focus_scores else 0
        
        state["completion_score"] = completion_score
        state["understanding_score"] = understanding_score
        
        return state
    def _should_complete_workflow(self, state: StudyState) -> bool:
        """Determine if workflow should complete based on multiple factors"""
        conditions = [
            state["attempts"] >= self.config["max_attempts"],
            state["iteration_count"] >= self.config["recursion_limit"],
            state.get("review_attempts", 0) >= self.config["max_review_attempts"],
            state.get("plan_adjustments", 0) >= self.config["max_plan_adjustments"],
            state.get("completion_score", 0) >= self.config["min_completion_rate"],
            state.get("understanding_score", 0) >= self.config["min_understanding_level"],
            state["status"] == "failed"
        ]
        
        if any(conditions):
            logger.info(f"Completing workflow due to conditions: {conditions}")
            return True
        return False

    def _route_based_on_progress(self, state: StudyState) -> str:
        """Enhanced routing with better completion logic"""
        try:
            # Update tracking metrics
            state["attempts"] = state.get("attempts", 0) + 1
            state["iteration_count"] = state.get("iteration_count", 0) + 1
            
            # Update progress metrics
            state = self._update_progress_metrics(state)
            
            # Log current state
            logger.debug(
                f"Progress routing - Attempts: {state['attempts']}, "
                f"Completion: {state['completion_score']:.2f}, "
                f"Understanding: {state['understanding_score']:.2f}"
            )
            
            # Check if workflow should complete
            if self._should_complete_workflow(state):
                return "complete"
            
            # Route based on scores
            if state["understanding_score"] < self.config["min_understanding_level"]:
                state["review_attempts"] = state.get("review_attempts", 0) + 1
                if state["review_attempts"] <= self.config["max_review_attempts"]:
                    return "review_material"
            
            if state["completion_score"] < self.config["min_completion_rate"]:
                state["plan_adjustments"] = state.get("plan_adjustments", 0) + 1
                if state["plan_adjustments"] <= self.config["max_plan_adjustments"]:
                    return "adjust_plan"
            
            return "complete"
                
        except Exception as e:
            logger.error(f"Error in progress routing: {str(e)}")
            return "complete"

    def _route_based_on_feedback(self, state: StudyState) -> str:
        """Simplified feedback routing with better completion checks"""
        try:
            if self._should_complete_workflow(state):
                return "complete"
            
            if not state["feedback"]:
                return "complete"
            
            latest_feedback = state["feedback"][-1]
            session_complete = latest_feedback.get("session_complete", False)
            
            logger.debug(f"Feedback routing - Session complete: {session_complete}")
            
            return "complete" if session_complete else "continue"
            
        except Exception as e:
            logger.error(f"Error in feedback routing: {str(e)}")
            return "complete"
    async def execute(self, initial_state: StudyState):
        """Execute the workflow with enhanced state tracking"""
        try:
            # Initialize state tracking
            initial_state.update({
                "attempts": 0,
                "iteration_count": 0,
                "understanding_score": 0.0,
                "completion_score": 0.0,
                "review_attempts": 0,
                "plan_adjustments": 0
            })
            
            logger.info("Starting workflow execution")
            
            result = await self.workflow.ainvoke(
                initial_state,
                config={"recursion_limit": self.config["recursion_limit"]}
            )
            
            logger.info(f"Workflow completed. Status: {result['status']}")
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
            return {**initial_state, "status": "failed", "error": str(e)}
        
    def visualize(self, filename: str = "workflow.png"):
        from graphviz import Digraph
        try:
            
            dot = Digraph(comment='Study Workflow')
            
            # Add nodes
            nodes = ["analyze_profile", "process_material", "create_plan", 
                    "execute_session", "evaluate_progress", "provide_feedback"]
            for node in nodes:
                dot.node(node, node)
            
            # Add edges
            dot.edge("analyze_profile", "process_material")
            dot.edge("process_material", "create_plan")
            dot.edge("create_plan", "execute_session")
            dot.edge("execute_session", "evaluate_progress")
            dot.edge("evaluate_progress", "provide_feedback")
            dot.edge("provide_feedback", "execute_session")
            
            dot.render(filename, view=True)
        except Exception as e:
            logger.error(f"Failed to visualize workflow: {str(e)}")