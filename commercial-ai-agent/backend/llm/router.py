from typing import Dict, Any, Optional
from backend.config.settings import settings
from backend.llm.base import LLMProvider
from backend.llm.ollama import OllamaProvider
from backend.llm.openrouter import OpenRouterProvider

class ModelRouter:
    def __init__(self, primary_provider: LLMProvider = None):
        # Automatically use OpenRouter if an API key is provided
        if primary_provider:
            self.provider = primary_provider
        elif settings.OPENROUTER_API_KEY:
            self.provider = OpenRouterProvider()
        else:
            self.provider = OllamaProvider()
        
        # Capability mapping based on settings
        self.capability_map = {
            "simple_extraction": settings.FAST_MODEL,
            "general_multimodal": settings.GENERAL_MODEL,
            "commercial_reasoning": settings.HEAVY_MODEL,
            "coding": settings.CODING_MODEL,
            "deep_reasoning": settings.REASONING_MODEL,
            "vision_specialist": settings.VISION_MODEL
        }

    def get_model(self, capability: str) -> str:
        """Get the specific model string for a given capability."""
        if capability in self.capability_map:
            return self.capability_map[capability]
        # Fallback to general model if capability not explicitly mapped
        return settings.GENERAL_MODEL

    def generate(self, capability: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        model = self.get_model(capability)
        return self.provider.generate(prompt=prompt, model=model, system_prompt=system_prompt)

    def generate_json(self, capability: str, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        model = self.get_model(capability)
        return self.provider.generate_json(prompt=prompt, model=model, system_prompt=system_prompt)

    def generate_with_tools(self, capability: str, prompt: str, tools: list, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        model = self.get_model(capability)
        return self.provider.generate_with_tools(prompt=prompt, model=model, tools=tools, system_prompt=system_prompt)
        
    def analyze_image(self, capability: str, prompt: str, image_path: str, system_prompt: Optional[str] = None) -> str:
        model = self.get_model(capability)
        return self.provider.analyze_image(prompt=prompt, image_path=image_path, model=model, system_prompt=system_prompt)
