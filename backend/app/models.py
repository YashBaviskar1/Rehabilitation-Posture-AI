from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(1000))
    username = Column(String(100), unique=True, index=True)
    password = Column(String(1000), nullable=False)
    role = Column(String(10), nullable=False)
    age = Column(Integer, nullable=True)

    assignments = relationship("User_Exercises", back_populates="user")
    exercise_scores = relationship("UserExerciseScore", back_populates="user")



class Exercises(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), unique=True)

    assignments = relationship("User_Exercises", back_populates="exercise")
    user_scores = relationship("UserExerciseScore", back_populates="exercise")



class User_Exercises(Base):
    __tablename__ = "user_exercises"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), primary_key=True)

    user = relationship("User", back_populates="assignments")
    exercise = relationship("Exercises", back_populates="assignments")



class UserExerciseScore(Base):
    __tablename__ = 'user_exercise_scores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)

    score = Column(Integer, nullable=False)
    timestamp = Column(BigInteger, nullable=False)  # store in milliseconds

    # Optional: add relationships if needed
    user = relationship("User", back_populates="exercise_scores")
    exercise = relationship("Exercises", back_populates="user_scores")

