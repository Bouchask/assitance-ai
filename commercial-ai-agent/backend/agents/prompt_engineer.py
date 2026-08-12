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
            "document_format": "string ('excel' or 'pdf', default to 'pdf')",
            "client": "string (name of the client) or null",
            "client_email": "string (extracted email address) or null",
            "requirements": [
                {
                    "service": "string (e.g., ecommerce, seo, maintenance)",
                    "quantity": "integer (number of items requested, MUST be at least 1, default to 1, NEVER 0)"
                }
            ],
            "maintenance_duration": "integer (months) or null",
            "attachments": ["list of absolute file paths to attach, if provided in context"],
            "actions": ["list of requested actions (e.g., db.find_or_create_client, utils.prepare_quote_items, db.create_quote, document.generate, email.send)"]
        }
        
        Rules:
        - Do not include explanations, ONLY valid JSON.
        - Normalize terms (e.g., "devis" -> "quote", "facture" -> "invoice").
        - Extract exact client names if present.
        - Extract exact email addresses if present (e.g., director@atlasecommerce.ma).
        - If the Previous Context shows a quote/document was already generated, and the user just asks to send it via email, DO NOT include quote creation actions (like db.create_quote, document.generate) UNLESS they explicitly request a different document format (e.g. they ask for PDF). If they just want to send the existing one, ONLY include email actions (email.prepare, email.send) and put the previously generated file_path in "attachments".
        """

    def analyze(self, user_input: str, previous_context: str = "") -> Dict[str, Any]:
        """
        Analyzes raw user input and returns a structured JSON intent.
        """
        prompt = f"Previous Context (use this to find file paths for attachments):\n{previous_context}\n\nUser request: {user_input}"
        # We use commercial_reasoning capability for accurate intent extraction
        return self.router.generate_json(
            capability="commercial_reasoning",
            prompt=prompt,
            system_prompt=self.system_prompt
        )
