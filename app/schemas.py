from pydantic import BaseModel # pydantic to use validate environment variables
from datetime import datetime

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str

class UserCreate(BaseModel):
    username: str
    balance: float

class UserResponse(BaseModel):
    user_id: int
    username: str
    balance: float

    class Config:
        orm_mode = True
        from_attributes = True


class StockDataCreate(BaseModel):
    ticker: str
    open_price: float
    close_price: float
    high: float
    low: float
    volume: int
    timestamp: datetime

class StockDataResponse(BaseModel):
    id: int  # Ensure the id field is included
    ticker: str
    open_price: float
    close_price: float
    high: float
    low: float
    volume: int
    timestamp: datetime
# is used in Pydantic models to enable specific functionalities
    class Config:
        orm_mode = True
        from_attributes = True

class TransactionCreate(BaseModel):
    user_id: int
    ticker: str
    transaction_type: str  # "buy" or "sell"
    transaction_volume: int

class TransactionResponse(BaseModel):
    transaction_id: int
    user_id: int
    ticker: str
    transaction_type: str
    transaction_volume: int
    transaction_price: float
    timestamp: datetime

    class Config:
        orm_mode = True
        from_attributes = True

