from fastapi import FastAPI,APIRouter,Depends, HTTPException, status
from DataBaseManagement.dbManagement import get_db, init_db
from DataBaseManagement.dbservices import TaskManager
from DataBaseManagement.schemas import TaskCreate, TaskUpdate, TaskResponse
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

init_db() # Aseguramos la creación de tablas en el arranque
get_db()  # Inicializar la base de datos

def init_fastapi():
    description = """
    Actividad final del módulo 2 - Programación Avanzada. 

    ## Objetivos de aprendizaje:
        1) Aplicar principios de programación orientada a objetos y desarrollar código que se englobe en este paradigma de programación.
        2) Desarrollar aplicaciones web backend con el framework FastAPI, basado en Python.
        3) Usar diferentes verbos HTTP y diferentes técnicas habituales en el mundo backend, en arquitecturas REST (enviar payload, responder con el código HTTP adecuado a cada caso...).
        4) Desplegar aplicaciones backend en entornos locales.
        5) Crear código en Python usando la librería requests para interactuar con APIs
    ## Tecnologías utilizadas:
        - Python 3.8+
        - FastAPI
        - Persistencia SQLite + SQLAlchemy (sqlite:///./tasks.db)
    ## Modelo de DB:
        - TaskDB: id, titulo, contenido, deadline, completada, fecha_creacion
        - Pydantic: TaskCreate, TaskUpdate, TaskResponse (hereda orm_mode)
        - TaskManager con encapsulamiento + abstracción:  _clean_text() (normaliza / censura palabras malsonantes) 
    ## Notas:
        - El proyecto se desarrollará usando FastAPI, un framework moderno y rápido para construir APIs con Python.
        - Se implementarán endpoints para crear tareas, obtener detalles de tareas, marcar tareas como completadas y listar tareas caducadas.
        - La persistencia de datos se realizará utilizando SQLite a través de SQLAlchemy, lo que permitirá almacenar las tareas de manera eficiente.
        - Se aplicarán principios de programación orientada a objetos para estructurar el código de manera modular y mantenible.
        - Se utilizarán modelos Pydantic para validar y serializar los datos de entrada y salida de la API.
        - Se implementa una clase TaskManager para encapsular la lógica de negocio relacionada con las tareas, incluyendo una función _clean_text() para normalizar o censurar palabras malsonantes en los títulos y contenidos de las tareas.   
    """
    app = FastAPI(title="Task Management API",
                description=description,
                version="1.0.5",
                contact={
                    "url": "https://www.linkedin.com/in/german-dario-realpe-zambrano/",
                    "name": "Creador: German Dario realpe zambrano",
                    "email": "gedorz@gmail.com",
                })
    return app

# Endpoints de la API para crear una tarea
@router.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(task: TaskCreate, db: Session = Depends(get_db)):
    manager = TaskManager(db)
    return manager.add_task(task)
    
# cambiar el estado de una tarea a completada
@router.put("/tasks/completar/{task_id}", response_model=TaskResponse)
def marcar_completada(task_id: int, db: Session = Depends(get_db)):
    manager = TaskManager(db)
    try:
        return manager.set_task_completed(task_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# Actualización de tarea (no requerida en los tests pero implementada para completar la API)
@router.put("/tasks/{task_id}", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
def actualizar_tarea(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    manager = TaskManager(db)
    try:
        return manager.update_task(task_id, task_update)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )   

# Endpoint para listar todas las tareas    
@router.get("/tasks/", response_model=List[TaskResponse])
def listar_tareas(db: Session = Depends(get_db)):
    manager = TaskManager(db)
    return manager.get_all_tasks()

# Endpoint para listar tareas caducadas
@router.get("/tasks/caducadas", response_model=List[TaskResponse])
def obtener_tareas_caducadas(db: Session = Depends(get_db)):
    manager = TaskManager(db)
    return manager.get_expired_tasks()

# Endpoint para contar tareas caducadas
@router.get("/tasks/caducadas/count")
def contar_caducadas(db: Session = Depends(get_db)):
    manager = TaskManager(db)
    return {"overdue": manager.count_overdue()}

# Endpoint para obtener detalles de una tarea específica
@router.get("/tasks/{task_id}", response_model=TaskResponse)
def obtener_tarea(task_id: int, db: Session = Depends(get_db)):
    manager = TaskManager(db)
    try:
        return manager.get_task(task_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )

# Endpoint para eliminar una tarea
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_tarea(task_id: int, db: Session = Depends(get_db)):
    manager = TaskManager(db)
    try:
        manager.delete_task(task_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    return None

# Endpoint raíz para verificar que la API está funcionando
@router.get("/")
def root():
    return {"message": "Task Management API"}
