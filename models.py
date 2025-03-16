from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(50), nullable=False)
    product_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
