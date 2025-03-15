from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Fetch DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://orderuser:T82RTOC1gVMtxhbHyqcIYYqWskLKN7EO@dpg-cvar0sdsvqrc73c1ai10-a/orderdb1")

# Replace "postgres://" with "postgresql://" for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create the database engine
engine = create_engine(DATABASE_URL)

# Base class for models
Base = declarative_base()

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
