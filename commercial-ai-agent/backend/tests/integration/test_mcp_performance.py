import os
import sys
import time
import json
import logging

# Ensure backend module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.mcp.registry import registry
from backend.mcp.database.server import register_database_tools
from backend.mcp.spreadsheet.server import register_spreadsheet_tools
from backend.mcp.document.server import register_document_tools
from backend.mcp.email.server import register_email_tools
from backend.execution.executor import ExecutionEngine
from backend.execution.state_machine import StateMachine
from backend.mcp.client import MCPClient
from backend.database.connection import SessionLocal
from backend.models.client import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_Performance_Test")

def setup_dummy_client():
    db = SessionLocal()
    try:
        client = db.query(Client).filter_by(email="mr.bouchakyahya@gmail.com").first()
        if not client:
            client = Client(name="Mr. Bouchak Yahya", email="mr.bouchakyahya@gmail.com", address="Local")
            db.add(client)
            db.commit()
            db.refresh(client)
        return client.id
    finally:
        db.close()

def run_test():
    logger.info("Registering MCP tools...")
    register_database_tools()
    register_spreadsheet_tools()
    register_document_tools()
    register_email_tools()
    
    logger.info("Setting up dummy client in DB...")
    client_id = setup_dummy_client()
    
    # We create a fake plan that executes the requested flow
    plan = {
        "steps": [
            {
                "id": 1,
                "tool": "spreadsheet.search",
                "arguments": {
                    "filepath": os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "products.csv"),
                    "query_column": "product_code",
                    "query_value": "WEB-ECOMM"
                },
                "depends_on": []
            },
            {
                "id": 2,
                "tool": "db.create_quote",
                "arguments": {
                    "client_id": client_id,
                    "total_ht": 5000.00,
                    "total_tax": 1000.00,
                    "total_ttc": 6000.00
                },
                "depends_on": []
            },
            {
                "id": 3,
                "tool": "document.generate",
                "arguments": {
                    "document_type": "quote",
                    "client_name": "Mr. Bouchak Yahya",
                    "items": [
                        {
                            "description": "E-commerce Website",
                            "quantity": 1,
                            "price": 5000.00
                        }
                    ],
                    "total_ht": 5000.00,
                    "tax": 1000.00,
                    "total_ttc": 6000.00,
                    "template_name": "b2b"
                },
                "depends_on": []
            }
        ]
    }
    
    logger.info("Starting Execution Engine...")
    start_time = time.time()
    
    mcp_client = MCPClient()
    executor = ExecutionEngine(mcp_client)
    state_machine = StateMachine()
    
    result = executor.execute_plan("test-exec-1", plan, state_machine, approved_step_ids=[])
    
    end_time = time.time()
    
    logger.info(f"Execution finished in {end_time - start_time:.2f} seconds.")
    logger.info(f"Status: {result.get('status')}")
    
    if result.get("status") == "completed":
        results = result.get("results", {})
        doc_result = results.get(3, {}).get("data", {})
        pdf_path = doc_result.get("file_path")
        
        if pdf_path:
            logger.info(f"Generated PDF at: {pdf_path}")
            
            # Send Email manually for step 4 (Since it requires approval in a real flow, we execute it directly here)
            logger.info("Sending Email...")
            csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "products.csv")
            
            email_res = mcp_client.execute_tool(
                "email.send", 
                {
                    "to": "mr.bouchakyahya@gmail.com",
                    "subject": "Your Requested Quote and Data",
                    "body": "Hello,\n\nPlease find attached the quote you requested, along with the data export in CSV format.\n\nBest regards,\nCommercial AI Agent",
                    "attachments": [pdf_path, csv_path]
                },
                "test-exec-1"
            )
            
            logger.info(f"Email Tool Result: {json.dumps(email_res.dict(), indent=2)}")
        else:
            logger.error("Document generation failed or returned no path.")
    else:
        logger.error(f"Execution failed: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run_test()
