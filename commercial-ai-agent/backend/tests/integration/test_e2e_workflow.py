import os
import sys
import json
import logging

# Ensure backend module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.agents.orchestrator import Orchestrator
from backend.mcp.database.server import register_database_tools
from backend.mcp.spreadsheet.server import register_spreadsheet_tools
from backend.mcp.document.server import register_document_tools
from backend.mcp.email.server import register_email_tools

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("E2E_Test")

def run_e2e_test():
    logger.info("1. Registering all MCP Tools...")
    register_database_tools()
    register_spreadsheet_tools()
    register_document_tools()
    register_email_tools()
    
    logger.info("2. Initializing Orchestrator (Loads LLM models...)")
    orchestrator = Orchestrator()
    
    # Example Prompt
    prompt = "I need a quote for Mr. Bouchak Yahya for an E-commerce Website at 5000 MAD. Please add it to the database, generate the PDF quote, and email it to mr.bouchakyahya@gmail.com with the products CSV attached."
    
    logger.info(f"3. Submitting Prompt: '{prompt}'")
    result = orchestrator.process_request(prompt)
    
    # Handle Human Approval Loop
    while result.get("status") == "waiting_approval":
        execution_id = result.get("execution_id")
        step_id = result.get("step")
        tool_name = result.get("tool")
        arguments = result.get("arguments")
        
        logger.warning(f"--- HUMAN APPROVAL REQUIRED ---")
        logger.warning(f"Tool '{tool_name}' wants to run with arguments: {json.dumps(arguments, indent=2)}")
        logger.warning(f"Automatically approving for test purposes...")
        
        result = orchestrator.process_approval(execution_id, step_id, approved=True)
        
    logger.info("4. Final Result from Orchestrator:")
    
    if result.get("status") == "completed":
        logger.info("\n=== AGENT RESPONSE ===")
        print(result.get("response"))
        logger.info("======================\n")
        logger.info("Execution was fully completed successfully!")
    else:
        logger.error(f"Workflow failed: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    run_e2e_test()
