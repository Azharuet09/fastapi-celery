from celery_config import celery_app
from sqlalchemy.orm import Session
from models import User, Transaction, StockData
from database import SessionLocal
from fastapi import HTTPException
from datetime import datetime

@celery_app.task(bind = True, name="process_transaction")
def process_transaction(self,transaction_data):
    db: Session = SessionLocal()
    try:
        # existing list sy new list create jab wo condition sy satify ho filter
        stock = db.query(StockData).filter(StockData.ticker == transaction_data['ticker']).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock data not found")
        
        user = db.query(User).filter(User.user_id == transaction_data['user_id']).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        transaction_price = stock.close_price
        total_cost = transaction_price * transaction_data['transaction_volume']
        
        if transaction_data['transaction_type'] == "buy":
            if user.balance < total_cost:
                raise HTTPException(status_code=400, detail="Insufficient balance")
            user.balance -= total_cost
        elif transaction_data['transaction_type'] == "sell":
            user.balance += total_cost
        else:
            raise HTTPException(status_code=400, detail="Invalid transaction type")
        
        new_transaction = Transaction(
            user_id=transaction_data['user_id'],
            ticker=transaction_data['ticker'],
            transaction_type=transaction_data['transaction_type'],
            transaction_volume=transaction_data['transaction_volume'],
            transaction_price=transaction_price,
            timestamp=datetime.utcnow()
        )
        
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        db.refresh(user)

        # Return a JSON-serializable dictionary
        return {
            "transaction_id": new_transaction.transaction_id,
            "user_id": new_transaction.user_id,
            "ticker": new_transaction.ticker,
            "transaction_type": new_transaction.transaction_type,
            "transaction_volume": new_transaction.transaction_volume,
            "transaction_price": new_transaction.transaction_price,
            "timestamp": new_transaction.timestamp.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
