import json
import requests
from typing import Dict, Any, List, Optional
from backend.llm.base import LLMProvider
from backend.config.settings import settings

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.api_url = f"{self.base_url}/api/generate"
        self.chat_url = f"{self.base_url}/api/chat"

    def generate(self, prompt: str, model: str, system_prompt: Optional[str] = None, timeout: Optional[float] = None, **kwargs) -> str:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        response = requests.post(self.api_url, json=payload, timeout=(timeout if timeout is not None else None))
        response.raise_for_status()
        return response.json().get("response", "")

    def generate_json(self, prompt: str, model: str, system_prompt: Optional[str] = None, timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        response = requests.post(self.api_url, json=payload, timeout=(timeout if timeout is not None else None))
        response.raise_for_status()
        raw_response = response.json().get("response", "{}")
        
        # Manually extract JSON to support Reasoning models (like deepseek-r1)
        # which must output <think> tags before the JSON. Ollama's strict 'format: json'
        # causes an infinite hang because it blocks the <think> tags.
        import re
        
        # 1. Strip out <think>...</think> blocks entirely
        raw_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL)
        
        # 2. Extract content from inside ```json ... ``` blocks if they exist
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_response)
        if json_match:
            raw_response = json_match.group(1)
            
        try:
            return json.loads(raw_response.strip())
        except json.JSONDecodeError:
            import logging
            try:
                import json_repair
                repaired = json_repair.repair_json(raw_response, return_objects=True)
                if isinstance(repaired, dict):
                    return repaired
                if isinstance(repaired, list) and len(repaired) > 0 and isinstance(repaired[0], dict):
                    return repaired[0]
                logging.warning(f"json_repair did not return a dict: {repaired}")
            except Exception as e:
                logging.error(f"Failed to repair JSON: {e}")
                
            logging.error(f"Failed to parse JSON from Ollama. Raw string: {raw_response}")
            raise Exception("Failed to parse valid JSON from Ollama. Response was empty or malformed.")

    def generate_with_tools(self, prompt: str, model: str, tools: List[Dict[str, Any]], system_prompt: Optional[str] = None, timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "tools": tools,
            "stream": False
        }
        
        response = requests.post(self.chat_url, json=payload, timeout=(timeout if timeout is not None else None))
        response.raise_for_status()
        
        return response.json().get("message", {})

    def analyze_image(self, prompt: str, image_path: str, model: str, system_prompt: Optional[str] = None, timeout: Optional[float] = None, **kwargs) -> str:
        import base64
        
        with open(image_path, "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode("utf-8")
            
        payload = {
            "model": model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        response = requests.post(self.api_url, json=payload, timeout=(timeout if timeout is not None else None))
        response.raise_for_status()
        return response.json().get("response", "")
