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
                    "id": 1,
                    "tool": "tool_name",
                    "arguments": {
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
        - For every quote creation, the required order is: db.find_or_create_client, utils.prepare_quote_items, db.create_quote, document.generate. Pass {{stepN.items}}, {{stepN.total_ht}}, {{stepN.tax}}, and {{stepN.total_ttc}} into db.create_quote. Pass the client id and quote id to document.generate as client_id and reference_id.
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
        - Do not include explanations, reasoning, or conversational text. ONLY output the raw, valid JSON object. Do not invent your own keys.
        """

    def plan(self, intent: Dict[str, Any], available_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates an execution plan based on the intent and available tools.
        """
        tools_str = json.dumps(available_tools, indent=2)
        intent_str = json.dumps(intent, indent=2)
        
        prompt = f"""
        Structured Intent:
        {intent_str}
        
        Available Tools:
        {tools_str}
        
        Generate the JSON execution plan.
        """
        
        # We use commercial_reasoning capability for accurate planning
        return self.router.generate_json(
            capability="commercial_reasoning",
            prompt=prompt,
            system_prompt=self.system_prompt
        )
