import os
import sys

# Ensure backend module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.app import create_app
from backend.config.settings import settings

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = settings.APP_ENV == "development"
    # Only enable the interactive debugger if explicitly allowed (avoid printing the PIN)
    use_debugger = bool(debug and getattr(settings, "ALLOW_DEBUGGER", False))
    app.run(host="0.0.0.0", port=port, debug=debug, use_debugger=use_debugger, use_reloader=False)
