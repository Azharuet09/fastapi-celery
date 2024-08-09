from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Define the URL for the database connection using the environment variable
DATABASE_URL = os.getenv('DATABASE_URL')
# Create an engine that will connect to the PostgreSQL database
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for our classes definitions
Base = declarative_base()

# Dependency to get a new database session for each request
def get_db():
    db = SessionLocal()  # Create a new session
    try:
        yield db  # Yield the session to the caller
    finally:
        db.close()  # Close the session after the request is finished
