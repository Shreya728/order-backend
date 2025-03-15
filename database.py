from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv  # Add this
import os

# Load environment variables first!
load_dotenv()

# Then get DATABASE_URL
# In database.py
DATABASE_URL = "postgresql://postgres@localhost:5432/orderdb1"  # No password


engine = create_engine(DATABASE_URL)
Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
