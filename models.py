from sqlalchemy import Column, Integer, String, DateTime, Numeric
from database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100))
    product_name = Column(String(100))
    price = Column(Numeric(10,2))
    order_date = Column(DateTime, server_default='now()')
