import os
from dotenv import load_dotenv
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import List
from .schemas import TaskCreate, TaskUpdate, TaskResponse

load_dotenv()  # Cargar variables de entorno desde el archivo .env

# Is done: Variables de entorno para configuración de la base de datos
database_url = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

# Is done: Base de datos en persistencia SQLite con SQLAlchemy
engine = create_engine(database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()   

class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    contenido = Column(String(200), nullable=False)
    deadline = Column(Date, nullable=False)
    completada = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    