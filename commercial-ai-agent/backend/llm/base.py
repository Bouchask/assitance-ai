from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class LLMProvider(ABC):
    
    @abstractmethod
    def generate(self, prompt: str, model: str, system_prompt: Optional[str] = None) -> str:
        """Generate text response from the LLM."""
        pass

    @abstractmethod
    def generate_json(self, prompt: str, model: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate a JSON structured response from the LLM."""
        pass

    @abstractmethod
    def generate_with_tools(self, prompt: str, model: str, tools: List[Dict[str, Any]], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate response with tool calling capability."""
        pass

    @abstractmethod
    def analyze_image(self, prompt: str, image_path: str, model: str, system_prompt: Optional[str] = None) -> str:
        """Analyze an image using a vision model."""
        pass
