from typing import Optional
from flask import request
from google.oauth2.credentials import Credentials
from backend.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def get_user_google_credentials() -> Optional[Credentials]:
    """
    Retrieve Google OAuth2 Credentials for the currently authenticated user.
    Assumes this is called within a Flask request context where request.current_user is set.
    """
    user = getattr(request, 'current_user', None)
    if not user:
        logger.warning("get_user_google_credentials called outside an authenticated request context.")
        return None
        
    if not user.google_access_token:
        logger.warning(f"User {user.email} does not have a google_access_token.")
        return None
        
    return Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET
    )
