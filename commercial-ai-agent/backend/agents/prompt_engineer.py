from typing import Dict, Any
from backend.llm.router import ModelRouter

class PromptEngineerAgent:
    def __init__(self, router: ModelRouter):
        self.router = router
        self.system_prompt = """
        You are the Prompt Engineer for a Commercial AI Agent.
        Your task is to analyze the user's natural language request and output a structured JSON representing their intent.
        
        Expected JSON format:
        {
            "intent": "string (e.g., create_quote, create_invoice, find_client)",
            "document_type": "string (e.g., quote, invoice, proposal) or null",
            "client": "string (name of the client) or null",
            "client_email": "string (extracted email address) or null",
            "requirements": [
                {
                    "service": "string (e.g., ecommerce, seo, maintenance)",
                    "quantity": "integer (number of items requested, default to 1)"
                }
            ],
            "maintenance_duration": "integer (months) or null",
            "actions": ["list of requested actions (e.g., db.find_or_create_client, utils.prepare_quote_items, db.create_quote, document.generate, email.send)"]
        }
        
        Rules:
        - Do not include explanations, ONLY valid JSON.
        - Normalize terms (e.g., "devis" -> "quote", "facture" -> "invoice").
        - Extract exact client names if present.
        - Extract exact email addresses if present (e.g., director@atlasecommerce.ma).
        """

    def analyze(self, user_input: str) -> Dict[str, Any]:
        """
        Analyzes raw user input and returns a structured JSON intent.
        """
        # We use commercial_reasoning capability for accurate intent extraction
        return self.router.generate_json(
            capability="commercial_reasoning",
            prompt=f"User request: {user_input}",
            system_prompt=self.system_prompt
        )
