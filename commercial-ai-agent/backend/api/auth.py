import jwt
from functools import wraps
from flask import request, jsonify
from backend.config.settings import settings
from backend.database.connection import SessionLocal
from backend.models.user import User

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
        if not token:
            print("JWT ERROR: Authentication token is missing")
            return jsonify({"error": "Authentication token is missing"}), 401

        try:
            data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            db = SessionLocal()
            current_user = db.query(User).filter(User.id == data["sub"]).first()
            db.close()
            
            if not current_user or not current_user.is_active:
                print(f"JWT ERROR: User {data['sub']} no longer exists or is inactive")
                return jsonify({"error": "User no longer exists or is inactive"}), 401
                
        except jwt.ExpiredSignatureError:
            print("JWT ERROR: Authentication token has expired")
            return jsonify({"error": "Authentication token has expired"}), 401
        except jwt.InvalidTokenError as e:
            print(f"JWT ERROR: Invalid authentication token: {e}")
            return jsonify({"error": "Invalid authentication token"}), 401
            
        # Attach user to request
        request.current_user = current_user
        
        return f(*args, **kwargs)
        
    return decorated
