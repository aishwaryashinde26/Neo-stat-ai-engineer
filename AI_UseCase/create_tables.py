"""
Script to create/update database tables.
Run this after adding new models to ensure all tables exist.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from db.database import Base, engine
from db.models import Customer, Booking, ConversationHistory

print("Creating/updating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")

# Verify tables
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"\nExisting tables: {tables}")

if 'conversation_history' in tables:
    print("✅ conversation_history table exists")
else:
    print("❌ conversation_history table missing")
