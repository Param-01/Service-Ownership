import os

# Set a placeholder so app/database.py can be imported during tests.
# Integration tests override get_db with SQLite; this value is never used.
os.environ.setdefault("DATABASE_URL", "sqlite://")
