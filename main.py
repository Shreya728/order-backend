from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Order
from database import SessionLocal, engine
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import datetime

# Create database tables
Order.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

# Request model
class OrderCreate(BaseModel):
    customer_name: str
    product_name: str
    price: float

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Order Management System"}

# Create Order Endpoint
@app.post("/order")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(
        customer_name=order.customer_name,
        product_name=order.product_name,
        price=order.price
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

# Get All Orders
@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

# Get Single Order
@app.get("/order/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Delete Order
@app.delete("/order/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"message": "Order deleted"}
