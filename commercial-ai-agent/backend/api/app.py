import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.agents.langgraph_orchestrator import LangGraphOrchestrator
from backend.config.settings import cors_origins, settings
from backend.api.auth import jwt_required
import jwt
import datetime
from werkzeug.security import check_password_hash
from backend.database.connection import SessionLocal
from backend.models.user import User

# Configure basic logging if not already configured
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": cors_origins()}})
    
    # Register tools
    from backend.mcp.database.server import register_database_tools
    from backend.mcp.spreadsheet.server import register_spreadsheet_tools
    from backend.mcp.document.server import register_document_tools
    from backend.mcp.email.server import register_email_tools
    from backend.mcp.utils.server import register_utils_tools
    from backend.mcp.google_calendar.server import register_google_calendar_tools
    from backend.mcp.google_sheets.server import register_google_sheets_tools
    
    register_database_tools()
    register_spreadsheet_tools()
    register_document_tools()
    register_email_tools()
    register_utils_tools()
    register_google_calendar_tools()
    register_google_sheets_tools()

    # Dashboard API blueprint (clients, services, quotes, invoices)
    try:
        from backend.api.dashboard import bp as dashboard_bp
        app.register_blueprint(dashboard_bp)
    except Exception:
        # If dashboard blueprint is not present yet, continue without failing startup
        pass

    app.orchestrator = LangGraphOrchestrator()

    from flask import send_from_directory
    import os

    @app.route("/api/documents/<path:filename>", methods=["GET"])
    def serve_document(filename):
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
        return send_from_directory(data_dir, filename)

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok", "service": "commercial-ai-agent"})

    @app.route("/api/user/spreadsheet", methods=["GET"])
    @jwt_required
    def get_user_spreadsheet():
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
            
        db = SessionLocal()
        try:
            db_user = db.query(User).filter(User.id == user.id).first()
            if db_user and db_user.default_spreadsheet_id:
                return jsonify({"spreadsheet_id": db_user.default_spreadsheet_id})
            return jsonify({"spreadsheet_id": None})
        finally:
            db.close()

    @app.route("/api/auth/google", methods=["POST"])
    def google_auth():
        data = request.json
        code = data.get("code")
        if not code:
            return jsonify({"error": "Missing authorization code"}), 400
            
        import requests
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": "postmessage",
            "grant_type": "authorization_code"
        }
        
        resp = requests.post(token_url, data=payload)
        if not resp.ok:
            return jsonify({"error": "Failed to exchange token", "details": resp.json()}), 400
            
        token_data = resp.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        id_token_jwt = token_data.get("id_token")
        granted_scopes = token_data.get("scope", "")
        
        # Verify that the user checked the boxes for Calendar and Sheets
        if "calendar" not in granted_scopes.lower() or "spreadsheets" not in granted_scopes.lower():
            return jsonify({
                "error": "Autorisations manquantes. Vous DEVEZ cocher les cases pour Google Agenda et Google Sheets lors de la connexion."
            }), 403
        
        
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
        try:
            id_info = google_id_token.verify_oauth2_token(id_token_jwt, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
        except ValueError:
            return jsonify({"error": "Invalid ID token"}), 400
            
        email = id_info.get("email")
        google_id = id_info.get("sub")
        
        db = SessionLocal()
        try:
            user = db.query(User).filter((User.email == email) | (User.google_id == google_id)).first()
            if not user:
                user = User(
                    email=email,
                    google_id=google_id,
                    role="SALES",
                    is_active=True
                )
                db.add(user)
            else:
                user.google_id = google_id
                
            user.google_access_token = access_token
            if refresh_token:
                user.google_refresh_token = refresh_token
                
            db.commit()
            db.refresh(user)
            
            jwt_token = jwt.encode({
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }, settings.JWT_SECRET, algorithm="HS256")
            
            return jsonify({
                "token": jwt_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role
                }
            })
        finally:
            db.close()

    @app.route("/api/login", methods=["POST"])
    def login():
        data = request.json
        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Missing email or password"}), 400
            
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == data["email"]).first()
            if not user or not check_password_hash(user.hashed_password, data["password"]):
                return jsonify({"error": "Invalid credentials"}), 401
                
            token = jwt.encode({
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, settings.JWT_SECRET, algorithm="HS256")
            
            return jsonify({
                "token": token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role
                }
            })
        finally:
            db.close()

    @app.route("/api/chat", methods=["POST"])
    @jwt_required
    def chat():
        data = request.json
        if not data or "prompt" not in data:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
        
        prompt = data["prompt"]
        thread_id = data.get("thread_id")
        
        try:
            result = app.orchestrator.process_request(prompt, thread_id=thread_id)
            return jsonify(result)
        except Exception as e:
            logging.exception("Error during orchestrator execution")
            return jsonify({
                "status": "error",
                "error": str(e)
            }), 500

    @app.route("/api/approve", methods=["POST"])
    @jwt_required
    def approve():
        data = request.json
        if not data or "execution_id" not in data or "step_id" not in data or "approved" not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        try:
            result = app.orchestrator.process_approval(
                data["execution_id"], 
                data["step_id"], 
                data["approved"]
            )
            return jsonify(result)
        except Exception as e:
            logging.exception("Error during orchestrator approval")
            return jsonify({
                "status": "error",
                "error": str(e)
            }), 500

    return app
