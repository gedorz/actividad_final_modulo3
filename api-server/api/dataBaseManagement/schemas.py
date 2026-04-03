from datetime import datetime, date
from pydantic import BaseModel, Field   

# Is done: Modelos Pydantic
class TaskCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=100, description="Título de la tarea")
    contenido: str = Field(min_length=1, max_length=200, description="Contenido de la tarea")
    deadline: date = Field(description="Fecha de vencimiento")

class TaskUpdate(BaseModel):
    titulo: str = Field(min_length=1, max_length=100, description="Edit Título de la tarea") 
    contenido: str = Field(min_length=1, max_length=200, description="Edit Contenido de la tarea")
    deadline: date = Field(description="Edit fecha de vencimiento")
    completada: bool = Field(description="Edit estado de completado")

class TaskResponse(BaseModel):
    id: int
    titulo: str
    contenido: str
    deadline: date
    completada: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
