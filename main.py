from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Order
from database import SessionLocal, engine
from pydantic import BaseModel, Field, validator
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List

# Create database tables
Order.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request model with validation
class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=50, example="John Doe")
    product_name: str = Field(..., min_length=2, max_length=100, example="Laptop")
    price: float = Field(..., gt=0, example=999.99)

    @validator('price')
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError('Price must be greater than zero')
        return round(value, 2)

# Response model
class OrderResponse(BaseModel):
    id: int
    customer_name: str
    product_name: str
    price: float
    order_date: datetime

    class Config:
        orm_mode = True

# Global exception handler
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc):
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database error occurred"
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error"
    )

# Root endpoint
@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"message": "Welcome to Order Management System"}

# Create Order Endpoint
@app.post("/order", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
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
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Get All Orders
@app.get("/orders", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    try:
        orders = db.query(Order).all()
        return orders
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders"
        )

# Get Single Order
@app.get("/order/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
    return order

# Delete Order
@app.delete("/order/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
    try:
        db.delete(order)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete order"
        )
