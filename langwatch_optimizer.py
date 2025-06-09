"""
LangWatch Prompt Optimization Integration
Provides prompt optimization capabilities using LangWatch libraries
"""

import os
import json
import logging
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime

# Note: LangWatch integration is implemented with a mock for demonstration
# To use actual LangWatch, install: pip install langwatch-python
# and set LANGWATCH_API_KEY environment variable

try:
    # For now we'll use a mock implementation
    # import langwatch
    # from langwatch.types import PromptRole, ChatMessage
    LANGWATCH_AVAILABLE = False  # Set to False for mock implementation
    print("ℹ️  Using LangWatch mock implementation for demonstration")
except ImportError:
    LANGWATCH_AVAILABLE = False
    print("ℹ️  LangWatch library not installed, using mock implementation")

@dataclass
class OptimizationResult:
    """Result of prompt optimization"""
    optimized_prompt: str
    original_prompt: str
    optimization_score: float
    suggestions: List[str]
    reasoning: str
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

class LangWatchOptimizer:
    """LangWatch prompt optimization manager"""
    
    def __init__(self):
        self.langwatch_available = LANGWATCH_AVAILABLE
        self.api_key = os.getenv("LANGWATCH_API_KEY")
        self.project_id = os.getenv("LANGWATCH_PROJECT_ID", "ai-prompt-manager")
        self.initialized = False
        
        # For demonstration, we'll use a mock implementation
        # In a real scenario, uncomment the following:
        # if self.langwatch_available and self.api_key:
        #     try:
        #         langwatch.initialize(api_key=self.api_key, project_id=self.project_id)
        #         self.initialized = True
        #         logging.info("✅ LangWatch initialized successfully")
        #     except Exception as e:
        #         logging.error(f"❌ LangWatch initialization failed: {e}")
        #         self.initialized = False
        # else:
        #     logging.warning("⚠️  LangWatch not initialized - missing API key or library")
        
        # Mock initialization for demonstration
        self.initialized = True
        logging.info("ℹ️  Using mock LangWatch optimization (demonstration mode)")
    
    def is_available(self) -> bool:
        """Check if LangWatch optimization is available"""
        # For demonstration, always return True
        return self.initialized
    
    def get_status(self) -> Dict[str, any]:
        """Get optimization service status"""
        return {
            "available": self.is_available(),
            "library_installed": self.langwatch_available,
            "initialized": self.initialized,
            "api_key_set": bool(self.api_key),
            "project_id": self.project_id
        }
    
    def optimize_prompt(self, 
                       original_prompt: str, 
                       context: Optional[str] = None,
                       target_model: Optional[str] = "gpt-4",
                       optimization_goals: Optional[List[str]] = None) -> OptimizationResult:
        """
        Optimize a prompt using LangWatch
        
        Args:
            original_prompt: The prompt to optimize
            context: Additional context about the prompt's purpose
            target_model: Target AI model for optimization
            optimization_goals: List of optimization goals (clarity, specificity, etc.)
        
        Returns:
            OptimizationResult with the optimized prompt and metadata
        """
        
        if not self.is_available():
            return OptimizationResult(
                optimized_prompt=original_prompt,
                original_prompt=original_prompt,
                optimization_score=0.0,
                suggestions=["LangWatch optimization not available"],
                reasoning="LangWatch is not properly configured or available",
                timestamp=datetime.now(),
                success=False,
                error_message="LangWatch not available or not configured"
            )
        
        try:
            # Default optimization goals
            if optimization_goals is None:
                optimization_goals = [
                    "clarity",
                    "specificity", 
                    "effectiveness",
                    "conciseness"
                ]
            
            # Create optimization prompt for LangWatch
            optimization_context = self._create_optimization_context(
                original_prompt, context, target_model, optimization_goals
            )
            
            # Mock LangWatch optimization for demonstration
            # In a real implementation, uncomment the following:
            # with langwatch.trace(name="prompt_optimization") as trace:
            #     trace.add_input("original_prompt", original_prompt)
            #     trace.add_input("context", context or "")
            #     trace.add_input("target_model", target_model)
            #     trace.add_input("goals", optimization_goals)
            
            # Perform optimization using our rule-based approach
            optimized_result = self._perform_optimization(
                original_prompt, optimization_context
            )
            
            #     trace.add_output("optimized_prompt", optimized_result["optimized_prompt"])
            #     trace.add_output("score", optimized_result["score"])
            #     trace.add_output("suggestions", optimized_result["suggestions"])
            
            return OptimizationResult(
                optimized_prompt=optimized_result["optimized_prompt"],
                original_prompt=original_prompt,
                optimization_score=optimized_result["score"],
                suggestions=optimized_result["suggestions"],
                reasoning=optimized_result["reasoning"],
                timestamp=datetime.now(),
                success=True
            )
                
        except Exception as e:
            logging.error(f"❌ LangWatch optimization failed: {e}")
            return OptimizationResult(
                optimized_prompt=original_prompt,
                original_prompt=original_prompt,
                optimization_score=0.0,
                suggestions=[f"Optimization failed: {str(e)}"],
                reasoning=f"Error during optimization: {str(e)}",
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    def _create_optimization_context(self, 
                                   original_prompt: str, 
                                   context: Optional[str],
                                   target_model: str,
                                   goals: List[str]) -> str:
        """Create context for optimization"""
        
        context_parts = [
            f"Original prompt: {original_prompt}",
            f"Target AI model: {target_model}",
            f"Optimization goals: {', '.join(goals)}"
        ]
        
        if context:
            context_parts.append(f"Additional context: {context}")
        
        return "\n".join(context_parts)
    
    def _perform_optimization(self, original_prompt: str, context: str) -> Dict:
        """
        Perform the actual optimization using LangWatch capabilities
        This is a simplified implementation - actual LangWatch integration may vary
        """
        
        # For demo purposes, we'll use a rule-based approach
        # In a real implementation, this would use LangWatch's optimization APIs
        
        optimized_prompt = self._apply_optimization_rules(original_prompt)
        score = self._calculate_optimization_score(original_prompt, optimized_prompt)
        suggestions = self._generate_suggestions(original_prompt, optimized_prompt)
        reasoning = self._generate_reasoning(original_prompt, optimized_prompt)
        
        return {
            "optimized_prompt": optimized_prompt,
            "score": score,
            "suggestions": suggestions,
            "reasoning": reasoning
        }
    
    def _apply_optimization_rules(self, prompt: str) -> str:
        """Apply optimization rules to improve the prompt"""
        
        optimized = prompt
        
        # Rule 1: Add structure if missing
        if not any(word in prompt.lower() for word in ['step', 'first', 'then', 'finally']):
            if len(prompt) > 100:
                optimized = f"Please follow these steps:\n\n{optimized}\n\nProvide a structured response."
        
        # Rule 2: Add context if very short
        if len(prompt.strip()) < 20:
            optimized = f"You are an AI assistant. {optimized} Please provide a detailed and helpful response."
        
        # Rule 3: Add specificity
        if 'help me' in prompt.lower() and 'specific' not in prompt.lower():
            optimized = optimized.replace('help me', 'help me with specific guidance on')
        
        # Rule 4: Add output format if missing
        if len(prompt) > 50 and not any(word in prompt.lower() for word in ['format', 'structure', 'organize']):
            optimized += "\n\nPlease organize your response clearly with appropriate formatting."
        
        # Rule 5: Add role definition for complex tasks
        if len(prompt) > 100 and not prompt.lower().startswith('you are'):
            if any(word in prompt.lower() for word in ['analyze', 'write', 'create', 'develop']):
                optimized = f"You are an expert assistant. {optimized}"
        
        return optimized.strip()
    
    def _calculate_optimization_score(self, original: str, optimized: str) -> float:
        """Calculate optimization score (0-100)"""
        
        score = 50.0  # Base score
        
        # Length improvement
        if len(optimized) > len(original) and len(original) > 0:
            score += min(20, (len(optimized) - len(original)) / len(original) * 100)
        
        # Structure indicators
        structure_words = ['step', 'first', 'then', 'format', 'organize', 'structure']
        original_structure = sum(1 for word in structure_words if word in original.lower())
        optimized_structure = sum(1 for word in structure_words if word in optimized.lower())
        
        if optimized_structure > original_structure:
            score += (optimized_structure - original_structure) * 10
        
        # Specificity indicators
        specific_words = ['specific', 'detailed', 'comprehensive', 'thorough']
        original_specific = sum(1 for word in specific_words if word in original.lower())
        optimized_specific = sum(1 for word in specific_words if word in optimized.lower())
        
        if optimized_specific > original_specific:
            score += (optimized_specific - original_specific) * 5
        
        return min(100.0, max(0.0, score))
    
    def _generate_suggestions(self, original: str, optimized: str) -> List[str]:
        """Generate optimization suggestions"""
        
        suggestions = []
        
        if len(optimized) > len(original):
            suggestions.append("Added more detailed instructions for clarity")
        
        if 'you are' in optimized.lower() and 'you are' not in original.lower():
            suggestions.append("Added role definition to improve response quality")
        
        if 'step' in optimized.lower() and 'step' not in original.lower():
            suggestions.append("Added structured approach for better organization")
        
        if 'format' in optimized.lower() and 'format' not in original.lower():
            suggestions.append("Added output formatting instructions")
        
        if not suggestions:
            suggestions.append("Applied general prompt optimization best practices")
        
        return suggestions
    
    def _generate_reasoning(self, original: str, optimized: str) -> str:
        """Generate reasoning for the optimization"""
        
        improvements = []
        
        if len(optimized) > len(original):
            improvements.append("expanded the prompt with additional context")
        
        if 'you are' in optimized.lower() and 'you are' not in original.lower():
            improvements.append("defined the AI's role for better responses")
        
        if any(word in optimized.lower() for word in ['step', 'structure', 'organize']):
            improvements.append("added structural elements for clarity")
        
        if improvements:
            return f"The optimization {', '.join(improvements)} to enhance effectiveness and clarity."
        else:
            return "Applied standard prompt optimization techniques to improve clarity and effectiveness."

# Global optimizer instance
langwatch_optimizer = LangWatchOptimizer()