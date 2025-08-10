from sqlalchemy import Column, Integer, String
from app.db import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    password = Column(String(1000), nullable=False)
    role = Column(String(10), nullable=False)
