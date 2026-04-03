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
    fecha_creacion: datetime

    class Config:
        # Permitir la conversión de objetos ORM a modelos Pydantic v2
        from_attributes = True
        # Permitir la conversión de objetos ORM a modelos Pydantic v1
        # orm_mode = True
