from typing import Dict, Any, List, Optional
from googleapiclient.discovery import build
from backend.mcp.google_auth import get_user_google_credentials
from flask import request
from backend.database.connection import SessionLocal

def append_row(
    values: List[Any], 
    spreadsheet_id: Optional[str] = None, 
    sheet_name: str = "Sheet1"
) -> Dict[str, Any]:
    """Append a row of data to a Google Sheet."""
    creds = get_user_google_credentials()
    if not creds:
        raise ValueError("User Google credentials not found. Please log in with Google.")
        
    try:
        service = build('sheets', 'v4', credentials=creds)
        
        # Determine which spreadsheet_id to use
        current_user = getattr(request, 'current_user', None)
        
        if not spreadsheet_id:
            if not current_user:
                raise ValueError("Cannot auto-create spreadsheet: no current user found in request.")
                
            # If the user already has a default spreadsheet, use it
            if current_user.default_spreadsheet_id:
                spreadsheet_id = current_user.default_spreadsheet_id
            else:
                # Create a new spreadsheet
                spreadsheet = {
                    'properties': {
                        'title': 'Commercial AI - Exports'
                    }
                }
                spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
                spreadsheet_id = spreadsheet.get('spreadsheetId')
                
                # Save it to the database so it's reused
                db = SessionLocal()
                try:
                    # Refresh the user object in this session
                    from backend.models.user import User
                    db_user = db.query(User).filter(User.id == current_user.id).first()
                    if db_user:
                        db_user.default_spreadsheet_id = spreadsheet_id
                        db.commit()
                        # Update the current_user object so subsequent calls in the same request have it
                        current_user.default_spreadsheet_id = spreadsheet_id
                finally:
                    db.close()
        
        if not spreadsheet_id:
            raise ValueError("Failed to determine or create a spreadsheet_id.")
            
        # Fetch the actual name of the first sheet to avoid locale issues (e.g. 'Sheet1' vs 'Feuille 1')
        try:
            sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            if sheet_name == "Sheet1" and sheets:
                sheet_name = sheets[0].get("properties", {}).get("title", "Sheet1")
            else:
                # Check if the specific sheet_name exists
                sheet_exists = any(s.get("properties", {}).get("title") == sheet_name for s in sheets)
                if not sheet_exists:
                    # Create the sheet
                    add_sheet_request = {
                        "requests": [
                            {
                                "addSheet": {
                                    "properties": {
                                        "title": sheet_name
                                    }
                                }
                            }
                        ]
                    }
                    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=add_sheet_request).execute()
        except Exception as e:
            print(f"Warning checking/creating sheet {sheet_name}: {e}")
            pass # Fallback to whatever was provided
                
        # Quote the sheet name in case it has spaces
        range_name = f"'{sheet_name}'!A:A"
        body = {
            'values': [values]
        }
        
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, 
            range=range_name,
            valueInputOption="USER_ENTERED", 
            body=body
        ).execute()
        
        link = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        try:
            if current_user and current_user.email:
                link = f"{link}?authuser={current_user.email}"
        except Exception:
            pass

        return {
            "status": "success",
            "message": "Row appended successfully",
            "spreadsheet_id": spreadsheet_id,
            "link": link,
            "updatedRange": result.get('updates', {}).get('updatedRange')
        }
    except Exception as e:
        raise RuntimeError(f"Failed to append row to Google Sheet: {str(e)}")
