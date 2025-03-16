from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables with fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://orderuser:T82RTOC1gVMtxhbHyqcIYYqWskLKN7EO@dpg-cvar0sdsvqrc73c1ai10-a/orderdb1"
)

# Fix connection string format for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Base class for declarative class definitions
Base = declarative_base()

# Configure session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
