from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from backend.config.settings import settings
import os

from sqlalchemy.pool import QueuePool

# Allow overriding DATABASE_URL for local testing
database_url = os.environ.get('DATABASE_URL', settings.DATABASE_URL)

engine_kwargs = {
    "pool_pre_ping": True,
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30
}

if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = QueuePool

engine = create_engine(database_url, **engine_kwargs)

# For sqlite, register a simple SQL function 'now' so migrations that use
# server_default=sa.text('now()') continue to work when running against
# a sqlite file during local development/testing.
if engine.url.drivername.startswith('sqlite'):
    try:
        from datetime import datetime

        @event.listens_for(engine, 'connect')
        def _sqlite_register_now(dbapi_connection, connection_record):
            # sqlite requires registering UDFs on the raw connection
            try:
                dbapi_connection.create_function('now', 0, lambda: datetime.utcnow().isoformat())
            except Exception:
                # ignore if connection type does not support create_function
                pass
    except Exception:
        pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
