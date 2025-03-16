from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
from models import Base, Order

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (update this in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for input validation and response formatting
class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=50)
    product_name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)

    @validator('price')
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError('Price must be greater than zero')
        return round(value, 2)

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    product_name: str
    price: float
    order_date: datetime

    class Config:
        orm_mode = True

# Exception handlers for better error responses
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc):
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database operation failed"
    )

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc)
    )

# Root endpoint for testing the API
@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"message": "Welcome to Order Management System"}

# Create a new order
@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        new_order = Order(
            customer_name=order.customer_name,
            product_name=order.product_name,
            price=order.price,
            order_date=datetime.utcnow()
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )

# Get all orders
@app.get("/orders", response_model=List[OrderResponse])
async def get_orders(db: Session = Depends(get_db)):
    try:
        orders = db.query(Order).all()
        return orders
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders"
        )

# Delete an order by ID
@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
    
    try:
        db.delete(order)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete order"
        )
