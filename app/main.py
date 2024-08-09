from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session # SQLAlchemy used for better data manipulation, such as filtering, ordering and grouping.
from redis import asyncio as aioredis
import json
from database import get_db, engine
from models import Base, User, StockData, Transaction
from schemas import UserCreate, UserResponse, StockDataCreate, StockDataResponse, TransactionCreate, TransactionResponse
from typing import List
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from celery import Celery

# Use environment variable for Redis URL
redis_url = os.getenv('REDIS_URL')

celery = Celery(__name__, broker=redis_url, backend=redis_url)

# Initialize FastAPI app
app = FastAPI()

# Initialize Redis client with connection details
redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
# Utility function to convert datetime to string
def convert_datetime_to_str(data):
    # Check if the input data is a list
    if isinstance(data, list):
        # Recursively call the function for each item in the list
        return [convert_datetime_to_str(item) for item in data]
    
    # Check if the input data is a dictionary
    elif isinstance(data, dict):
        # Recursively call the function for each key-value pair in the dictionary
        return {key: convert_datetime_to_str(value) for key, value in data.items()}
    
    # Check if the input data is a datetime object
    elif isinstance(data, datetime):
        # Convert the datetime object to an ISO 8601 formatted string
        return data.isoformat()
    
    # If the data is neither a list, dictionary, nor datetime, return it as is
    else:
        return data

# It gets a database session from the get_db function
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(username=user.username, balance=user.balance)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{username}/", response_model=UserResponse)
async def get_user(username: str, db: Session = Depends(get_db)):
    try:
        cached_user = await redis.get(username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")

    if cached_user:
        return json.loads(cached_user)

    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert the database user object to a UserResponse object using ORM conversion
    user_response = UserResponse.from_orm(db_user)

    try:
        # Attempt to set the username and its corresponding user response in Redis cache
        # The data is serialized to JSON and set with an expiration time of 60 seconds
        await redis.set(username, user_response.json(), ex=60)
    except Exception as e:
        # If an exception occurs, raise an HTTP 500 error with a detailed message
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")

    # Return the user response object
    return user_response


@app.post("/stocks/")
async def create_stock_data(stock_data: StockDataCreate, db: Session = Depends(get_db)):
    new_stock_data = StockData(
        ticker=stock_data.ticker,
        open_price=stock_data.open_price,
        close_price=stock_data.close_price,
        high=stock_data.high,
        low=stock_data.low,
        volume=stock_data.volume,
        timestamp=stock_data.timestamp
    )
    db.add(new_stock_data)
    db.commit()
    db.refresh(new_stock_data)
    return new_stock_data

@app.get("/stocks/", response_model=List[StockDataResponse])
async def get_stocks(db: Session = Depends(get_db)):
    try:
        cached_stocks = await redis.get("stocks")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")

    if cached_stocks:
        return json.loads(cached_stocks)

    db_stocks = db.query(StockData).all()
    if not db_stocks:
        raise HTTPException(status_code=404, detail="No stock data found")
    
    stock_responses = [StockDataResponse.from_orm(stock) for stock in db_stocks]
    stock_data_to_cache = convert_datetime_to_str([stock.dict() for stock in stock_responses])
    
    try:
        await redis.set("stocks", json.dumps(stock_data_to_cache), ex=60)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")
    
    return stock_responses

@app.get("/stocks/{ticker}/", response_model=StockDataResponse)
async def get_stock_by_ticker(ticker: str, db: Session = Depends(get_db)):
    try:
        cached_stock = await redis.get(f"stock_{ticker}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")

    if cached_stock:
        return json.loads(cached_stock)

    db_stock = db.query(StockData).filter(StockData.ticker == ticker).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock data not found")
    
    stock_response = StockDataResponse.from_orm(db_stock)
    stock_data_to_cache = convert_datetime_to_str(stock_response.dict())
    
    try:
        await redis.set(f"stock_{ticker}", json.dumps(stock_data_to_cache), ex=60)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")
    
    return stock_response


from tasks import process_transaction
@app.post("/transactions/")
async def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    transaction_data = {
        "user_id": transaction.user_id,
        "ticker": transaction.ticker,
        "transaction_type": transaction.transaction_type,
        "transaction_volume": transaction.transaction_volume
    }
    task = process_transaction.delay(transaction_data)
    task_id = task.id
    print("Task Id::::::::::::", task_id)
    return {"task_id": task.id, "status": "Processing"}

@app.get("/transaction/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Convert the transaction ORM object to a response model
    transaction_response = TransactionResponse.from_orm(transaction)
    return transaction_response

@app.get("/transactions/{user_id}/", response_model=List[TransactionResponse])
async def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    try:
        cached_transactions = await redis.get(f"user_transactions_{user_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")

    if cached_transactions:
        return json.loads(cached_transactions)

    db_transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    if not db_transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this user")
    
    transaction_responses = [TransactionResponse.from_orm(transaction) for transaction in db_transactions]
    transaction_data_to_cache = convert_datetime_to_str([transaction.dict() for transaction in transaction_responses])
    
    try:
        await redis.set(f"user_transactions_{user_id}", json.dumps(transaction_data_to_cache), ex=60)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")
    
    return transaction_responses


@app.get("/transactions/{user_id}/{start_timestamp}/{end_timestamp}/", response_model=List[TransactionResponse])
async def get_user_transactions_in_range(user_id: int, start_timestamp: str, end_timestamp: str, db: Session = Depends(get_db)):
    try:
        # Convert timestamps from string to datetime
        start_datetime = datetime.fromisoformat(start_timestamp)
        end_datetime = datetime.fromisoformat(end_timestamp)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format. Use ISO format.")

    # Validate timestamps
    if start_datetime > end_datetime:
        raise HTTPException(status_code=400, detail="Start timestamp must be before end timestamp.")
    
    try:
        # Try to fetch the cached transactions
        cache_key = f"user_transactions_{user_id}_{start_timestamp}_{end_timestamp}"
        cached_transactions = await redis.get(cache_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")

    if cached_transactions:
        # If cached, return the cached data
        return json.loads(cached_transactions)

    # Query the database for the user's transactions within the time range
    db_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.timestamp >= start_datetime,
        Transaction.timestamp <= end_datetime
    ).all()

    if not db_transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this user in the specified range.")
    
    # Convert database transactions to response models
    transaction_responses = [TransactionResponse.from_orm(transaction) for transaction in db_transactions]
    transaction_data_to_cache = convert_datetime_to_str([transaction.dict() for transaction in transaction_responses])
    
    try:
        # Cache the transaction data
        await redis.set(cache_key, json.dumps(transaction_data_to_cache), ex=60)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")
    
    return transaction_responses


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
