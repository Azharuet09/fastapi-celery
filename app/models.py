from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base  # Corrected import to match the actual location of Base

# Define the User class which maps to the 'users' table in the database
class User(Base):
    __tablename__ = 'users'
    
    # Define the columns of the 'users' table
    user_id = Column(Integer, primary_key=True, index=True)  # Primary key column
    username = Column(String, unique=True, index=True)  # Unique username column with an index for fast lookup
    balance = Column(Float)  # Column to store the user's balance

# Define the StockData class which maps to the 'stockdata' table in the database
class StockData(Base):
    __tablename__ = "stockdata"
    
    # Define the columns of the 'stockdata' table
    id = Column(Integer, primary_key=True, index=True)  # Primary key column
    ticker = Column(String, index=True)  # Ticker symbol column with an index for fast lookup
    open_price = Column(Float)  # Column to store the opening price of the stock
    close_price = Column(Float)  # Column to store the closing price of the stock
    high = Column(Float)  # Column to store the highest price of the stock
    low = Column(Float)  # Column to store the lowest price of the stock
    volume = Column(Integer)  # Column to store the volume of the stock traded
    timestamp = Column(DateTime)  # Column to store the timestamp of the stock data

# Define the Transaction class which maps to the 'transactions' table in the database
class Transaction(Base):
    __tablename__ = 'transactions'
    
    # Define the columns of the 'transactions' table
    transaction_id = Column(Integer, primary_key=True, index=True)  # Primary key column
    user_id = Column(Integer, ForeignKey('users.user_id'))  # Foreign key column linking to the 'users' table
    ticker = Column(String)  # Column to store the stock ticker symbol
    transaction_type = Column(String)  # Column to store the type of transaction (buy/sell)
    transaction_volume = Column(Integer)  # Column to store the volume of the transaction
    transaction_price = Column(Float)  # Column to store the price at which the transaction occurred
    timestamp = Column(DateTime, default=datetime.utcnow)  # Column to store the timestamp of the transaction with default value as current time

    # Define a relationship with the User class
    user = relationship("User")
