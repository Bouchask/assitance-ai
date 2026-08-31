from typing import Dict, Any, List, Optional
from googleapiclient.discovery import build
from backend.mcp.google_auth import get_user_google_credentials
import datetime
import dateutil.parser

def create_meeting(
    title: str, 
    start_time: str, 
    end_time: Optional[str] = None, 
    attendees: Optional[List[str]] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Create a Google Calendar meeting."""
    creds = get_user_google_credentials()
    if not creds:
        raise ValueError("User Google credentials not found. Please log in with Google.")
        
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Parse start time
        start_dt = dateutil.parser.parse(start_time)
        
        # Default duration to 30 minutes if not provided
        if not end_time:
            end_dt = start_dt + datetime.timedelta(minutes=30)
        else:
            end_dt = dateutil.parser.parse(end_time)
            
        event = {
            'summary': title,
            'description': description or '',
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [{'email': email} for email in attendees] if attendees else [],
            'reminders': {
                'useDefault': True,
            },
        }

        event_result = service.events().insert(calendarId='primary', body=event).execute()
        
        html_link = event_result.get('htmlLink')
        
        # Multi-account fix: Append authuser to the link so the browser opens it with the correct account
        try:
            from flask import request
            user = getattr(request, 'current_user', None)
            if user and user.email and html_link:
                join_char = '&' if '?' in html_link else '?'
                html_link = f"{html_link}{join_char}authuser={user.email}"
        except Exception:
            pass
            
        return {
            "status": "success",
            "message": "Meeting created successfully",
            "event_id": event_result.get('id'),
            "link": html_link
        }
    except Exception as e:
        raise RuntimeError(f"Failed to create Google Calendar meeting: {str(e)}")

def check_availability(date_start: str, date_end: str) -> Dict[str, Any]:
    """
    Check Google Calendar availability by fetching events within a given time range.
    Returns a list of busy periods.
    """
    creds = get_user_google_credentials()
    if not creds:
        raise ValueError("User Google credentials not found. Please log in with Google.")
        
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Parse inputs
        start_dt = dateutil.parser.parse(date_start)
        end_dt = dateutil.parser.parse(date_end)
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        busy_slots = []
        for event in events:
            # Skip all-day events which only have 'date' not 'dateTime'
            if 'dateTime' in event['start']:
                busy_slots.append({
                    "summary": event.get("summary", "Busy"),
                    "start": event['start']['dateTime'],
                    "end": event['end']['dateTime']
                })
                
        return {
            "status": "success",
            "timeMin": start_dt.isoformat(),
            "timeMax": end_dt.isoformat(),
            "busy_slots": busy_slots
        }
    except Exception as e:
        raise RuntimeError(f"Failed to check availability: {str(e)}")
