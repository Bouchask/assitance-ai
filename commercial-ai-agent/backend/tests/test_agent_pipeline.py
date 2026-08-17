import json
import logging
import sys
import os

# Add the project root to sys.path so we can import 'backend'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.agents.prompt_engineer import PromptEngineerAgent
from backend.agents.planner import PlannerAgent
from backend.llm.router import ModelRouter
from backend.mcp.registry import registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_pipeline")

def run_tests():
    router = ModelRouter()
    prompt_engineer = PromptEngineerAgent(router)
    planner = PlannerAgent(router)
    available_tools = registry.get_planner_tools()

    tests = [
        {
            "name": "Initial Quote Creation",
            "prompt": "Create a quote for Atlas Mao (mr.bouchakyahya@gmail.com) for e-commerce website, SEO, and 12 months maintenance. Add 15% discount and 10% tax. Send via email.",
            "context": "",
            "next_step_id": 1,
            "expected_actions": ["db.find_or_create_client", "utils.prepare_quote_items", "db.create_quote", "document.generate", "email.prepare", "email.send"]
        },
        {
            "name": "Amendment - Change Discount",
            "prompt": "change remise a 30%",
            "context": '''
Here is what was accomplished in previous steps of this conversation:
- Step 1: {"name": "Atlas Mao", "email": "mr.bouchakyahya@gmail.com"}
- Step 2: {"codes": ["WEB-ECOMM", "SEO-OPT", "MAINT-6"], "quantities": {"WEB-ECOMM": 1, "SEO-OPT": 1, "MAINT-6": 2}, "custom_descriptions": {"MAINT-6": "12 Months Maintenance"}, "discount_percent": 0.15, "tax_rate": 0.1}
- Step 3: {"client_id": 8, "items": [{"service_id": 2, "code": "MAINT-6", "description": "12 Months Maintenance", "quantity": 2, "price": 1200.0, "line_total": 2400.0, "tax_rate": 0.1}], "total_ht": 6970.0, "total_tax": 697.0, "total_ttc": 7667.0}
- Step 4: {"file_path": "/path/to/quote.pdf"}
            ''',
            "next_step_id": 5,
            "expected_actions": ["utils.prepare_quote_items", "db.create_quote", "document.generate", "email.prepare", "email.send"]
        },
        {
            "name": "Invoice Request (Should map to quote)",
            "prompt": "generer une facture pour Google avec SEO",
            "context": "",
            "next_step_id": 1,
            "expected_actions": ["db.find_or_create_client", "utils.prepare_quote_items", "db.create_quote", "document.generate"]
        }
    ]

    results = []

    for idx, test in enumerate(tests):
        logger.info(f"--- Running Test {idx+1}: {test['name']} ---")
        
        # 1. Test Prompt Engineer
        try:
            intent = prompt_engineer.analyze(test['prompt'], test['context'])
            valid_intent = True
            intent_errors = []
            
            if intent.get("document_type") != "quote":
                valid_intent = False
                intent_errors.append(f"document_type is '{intent.get('document_type')}' instead of 'quote'")
                
            actions = intent.get("actions", [])
            allowed_actions = {"db.find_or_create_client", "utils.prepare_quote_items", "db.create_quote", "document.generate", "email.prepare", "email.send"}
            for action in actions:
                if action not in allowed_actions:
                    valid_intent = False
                    intent_errors.append(f"Invalid action hallucinated: {action}")
                    
            if not valid_intent:
                logger.error(f"Intent Validation Failed: {intent_errors}")
                logger.debug(f"Intent Output: {json.dumps(intent, indent=2)}")
            else:
                logger.info("Intent Validation: PASS")
                
        except Exception as e:
            logger.error(f"Intent Generation Exception: {e}")
            valid_intent = False
            intent = {}

        # 2. Test Planner (only if intent is somehow formed, even if invalid, to see planner response)
        try:
            plan = planner.plan(intent, available_tools, test['context'], test['next_step_id'])
            valid_plan = True
            plan_errors = []
            
            steps = plan.get("steps", [])
            if not steps:
                valid_plan = False
                plan_errors.append("Plan returned 0 steps!")
            
            for step in steps:
                if not isinstance(step.get("id"), int):
                    valid_plan = False
                    plan_errors.append(f"Step ID {step.get('id')} is not an integer")
                if "depends_on" not in step:
                    valid_plan = False
                    plan_errors.append(f"Step {step.get('id')} missing depends_on")
                    
            if not valid_plan:
                logger.error(f"Plan Validation Failed: {plan_errors}")
                logger.debug(f"Plan Output: {json.dumps(plan, indent=2)}")
            else:
                logger.info("Plan Validation: PASS")
                
        except Exception as e:
            logger.error(f"Plan Generation Exception: {e}")
            valid_plan = False
            
        results.append({
            "test": test["name"],
            "intent_pass": valid_intent,
            "plan_pass": valid_plan
        })

    logger.info("=== SUMMARY ===")
    all_passed = True
    for res in results:
        status = "✅ PASS" if res["intent_pass"] and res["plan_pass"] else "❌ FAIL"
        logger.info(f"{status} | {res['test']} (Intent: {res['intent_pass']}, Plan: {res['plan_pass']})")
        if not (res["intent_pass"] and res["plan_pass"]):
            all_passed = False
            
    if all_passed:
        logger.info("All tests passed successfully!")
    else:
        logger.error("Some tests failed. Fix the agent logic.")

if __name__ == "__main__":
    run_tests()
