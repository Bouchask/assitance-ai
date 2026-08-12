import json
from typing import Dict, Any, List
from backend.llm.router import ModelRouter

class PlannerAgent:
    def __init__(self, router: ModelRouter):
        self.router = router
        self.system_prompt = """
        You are the Planner for a Commercial AI Agent.
        Your task is to take a structured user intent and a list of available tools, and generate a dependency-aware execution plan.
        
        Available tools are provided in the prompt. You must ONLY use the provided tools. DO NOT invent tools.
        
        Expected JSON format:
        {
            "steps": [
                {
                    "id": "integer (sequential step ID, starting from the NEXT available ID requested by the user)",
                    "tool": "string (name of the tool to use)",                "arguments": {
                        "arg_name": "arg_value"
                    },
                    "depends_on": [] 
                }
            ]
        }
        
        CRITICAL Rules:
        - Step "id" MUST be an integer (1, 2, 3, ...), NOT a string.
        - "depends_on" is a list of integer step IDs that must complete before this step.
        - For clients: ALWAYS use "db.find_or_create_client" (NOT "db.search_client"). It guarantees a client with an "id" is returned.
        - For emails: ONLY use email tools if the user explicitly requested to send an email or if an email address is provided. If used, ALWAYS use "email.prepare" first, then "email.send" (NEVER "email.generate").
        - To prepare quote lines and handle discounts, use "utils.prepare_quote_items" instead of multiple calculate steps.
        - For every quote creation, the required order is: db.find_or_create_client, utils.prepare_quote_items, db.create_quote, AND THEN generate the document.
        - IMPORTANT: If the Intent specifies "document_format": "excel", use "document.generate_excel". If it specifies "pdf" or is omitted, use "document.generate". Pass {{stepN.items}}, {{stepN.total_ht}}, {{stepN.tax}} (for the total_tax argument), and {{stepN.total_ttc}} into db.create_quote. Pass the client id and quote id to the document tool as client_id and reference_id.
        - The 'requirements' field from the Intent contains objects like {"service": "SEO", "quantity": 2}. You MUST map these to valid catalogue codes (e.g. "SEO-OPT") for the 'codes' argument of 'utils.prepare_quote_items'.
        - You MUST also pass a 'quantities' dictionary (e.g. {"SEO-OPT": 2}) to 'utils.prepare_quote_items' to properly reflect the requested quantities!
        - Use only actual catalogue codes returned by the tool descriptions: WEB-ECOMM, MAINT-6, SEO-OPT. Never invent a price or a service.
        - To reference output from a previous step, use placeholders like "{{step1.id}}" or "{{step4.file_path}}".
          - The placeholder suffix MUST match the actual key from the tool's output_schema.
          - E.g. use "{{stepN.id}}" or "{{stepN.name}}" for db.find_or_create_client.
          - E.g. use "{{stepN.items}}", "{{stepN.tax}}", or "{{stepN.total_ttc}}" for utils.prepare_quote_items.
          - E.g. use "{{stepN.file_path}}" for document.generate.
          - E.g. use "{{stepN.result}}" ONLY for utils.calculate.
          - Make sure to map "{{stepN.original_subtotal}}", "{{stepN.discount_amount}}", and "{{stepN.discount_percent_val}}" to document.generate if available.
          - The placeholder must be the ENTIRE value, not embedded in other text, when used for numeric/array fields.
        - For document.generate, ALWAYS omit the "template_name" argument so it uses the system default, or pass exactly "b2b" if required.
        - If 'client_email' is present in the Intent, use that exact email string for the 'email.prepare' "to" argument instead of generating a placeholder.
        - Ensure arguments match the expected schema for the tools.
        - Do not include explanations, reasoning, or conversational text. Output the valid JSON object ONLY.

        IMPORTANT:
        - If attachments are present in the intent, use them as literal file paths in your tool arguments.
        - Start numbering your steps from {next_step_id}. Do not start from 1 unless {next_step_id} is 1.
        """

    def plan(self, intent: Dict[str, Any], available_tools: List[Dict[str, Any]], previous_context: str = "", next_step_id: int = 1) -> Dict[str, Any]:
        """
        Generates an execution plan based on the intent and available tools.
        """
        tools_str = json.dumps(available_tools, indent=2)
        intent_str = json.dumps(intent, indent=2)
        
        prompt = f"Previous Context:\n{previous_context}\n\nStructured Intent:\n{intent_str}\n\nAvailable Tools:\n{tools_str}\n\nStart your step numbering from ID: {next_step_id}"
        
        # We use commercial_reasoning capability for accurate planning
        return self.router.generate_json(
            capability="commercial_reasoning",
            prompt=prompt,
            system_prompt=self.system_prompt
        )
