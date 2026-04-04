import logging

from fastapi import FastAPI,APIRouter,Depends, HTTPException, status
from dataBaseManagement.dbManagement import get_db, init_db
from dataBaseManagement.dbservices import TaskManager
from dataBaseManagement.schemas import TaskCreate, TaskUpdate, TaskResponse
from typing import List

router = APIRouter()
logger = logging.getLogger("api.endpoints")

init_db() # Aseguramos la creación de tablas en el arranque

def init_fastapi():
    description = """
    Actividad final del módulo 3 - Contenedores y Virtualización. 

    ## Objetivos de aprendizaje:
        1) Aplicar principios de programación orientada a objetos y desarrollar código que se englobe en este paradigma de programación.
        2) Desarrollar aplicaciones web backend con el framework FastAPI, basado en Python.
        3) Usar diferentes verbos HTTP y diferentes técnicas habituales en el mundo backend, en arquitecturas REST (enviar payload, responder con el código HTTP adecuado a cada caso...).
        4) Desplegar aplicaciones backend en entornos locales.
        5) Crear código en Python usando la librería requests para interactuar con APIs
        6) se agrega un manejador de excepciones personalizado para capturar los errores de validación de solicitudes (RequestValidationError) y registrar los detalles del error utilizando el logger configurado. Esto permitirá que los errores de validación se registren con un nivel de advertencia (warning) en lugar de error (error), lo que facilitará la identificación y solución de problemas relacionados con la validación de solicitudes en la API.
        7) se agrega un logger.info para registrar los mensajes de log en el módulo "api.endpoints". Esto permite que los mensajes de log se identifiquen claramente como provenientes de este módulo específico y generar la trazabilidad de los errores de validación en el módulo "api.endpoints" para facilitar la identificación y solución de problemas relacionados con la validación de solicitudes en la API.        
    ## Tecnologías utilizadas:
        - Python 3.8+
        - FastAPI
        - postgreSQL
        - psycopg2
        - Pydantic
    ## Modelo de DB:
        - TaskDB: id, titulo, contenido, status, deadline, created_at, updated_at
        - Pydantic: TaskCreate, TaskUpdate, TaskResponse (hereda orm_mode)
        - TaskManager con encapsulamiento + abstracción:  _clean_text() (normaliza / censura palabras malsonantes) 
    ## Notas:
        - El proyecto se desarrollará usando FastAPI, un framework moderno y rápido para construir APIs con Python.
        - Se implementarán endpoints para crear tareas, obtener detalles de tareas, marcar tareas como completadas y listar tareas caducadas.
        - La persistencia de datos se realizará utilizando PostgreSQL, lo que permitirá almacenar las tareas de manera eficiente.
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
def crear_tarea(task: TaskCreate, db=Depends(get_db)):
    logger.info("event=create_task_start title=%s", task.titulo)
    manager = TaskManager(db)
    created_task = manager.add_task(task)
    logger.info("event=create_task_success task_id=%s", created_task.get("id"))
    return created_task
    
# cambiar el estado de una tarea a completada
@router.put("/tasks/completar/{task_id}", response_model=TaskResponse)
def marcar_completada(task_id: int, db=Depends(get_db)):
    logger.info("event=complete_task_start task_id=%s", task_id)
    manager = TaskManager(db)
    try:
        updated_task = manager.set_task_completed(task_id)
        logger.info("event=complete_task_success task_id=%s", task_id)
        return updated_task
    except ValueError as e:
        logger.warning("event=complete_task_not_found task_id=%s detail=%s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# Actualización de tarea (no requerida en los tests pero implementada para completar la API)
@router.put("/tasks/{task_id}", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
def actualizar_tarea(task_id: int, task_update: TaskUpdate, db=Depends(get_db)):
    logger.info("event=update_task_start task_id=%s", task_id)
    manager = TaskManager(db)
    try:
        updated_task = manager.update_task(task_id, task_update)
        logger.info("event=update_task_success task_id=%s", task_id)
        return updated_task
    except ValueError as e:
        logger.warning("event=update_task_not_found task_id=%s detail=%s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )   

# Endpoint para listar todas las tareas    
@router.get("/tasks/", response_model=List[TaskResponse])
def listar_tareas(db=Depends(get_db)):
    logger.info("event=list_tasks")
    manager = TaskManager(db)
    return manager.get_all_tasks()

# Endpoint para listar tareas caducadas
@router.get("/tasks/caducadas", response_model=List[TaskResponse])
def obtener_tareas_caducadas(db=Depends(get_db)):
    logger.info("event=list_expired_tasks")
    manager = TaskManager(db)
    return manager.get_expired_tasks()

# Endpoint para contar tareas caducadas
@router.get("/tasks/caducadas/count")
def contar_caducadas(db=Depends(get_db)):
    logger.info("event=count_expired_tasks")
    manager = TaskManager(db)
    return {"overdue": manager.count_overdue()}

# Endpoint para obtener detalles de una tarea específica
@router.get("/tasks/{task_id}", response_model=TaskResponse)
def obtener_tarea(task_id: int, db=Depends(get_db)):
    logger.info("event=get_task_start task_id=%s", task_id)
    manager = TaskManager(db)
    try:
        task = manager.get_task(task_id)
        logger.info("event=get_task_success task_id=%s", task_id)
        return task
    except ValueError as e:
        logger.warning("event=get_task_not_found task_id=%s detail=%s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )

# Endpoint para eliminar una tarea
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_tarea(task_id: int, db=Depends(get_db)):
    logger.info("event=delete_task_start task_id=%s", task_id)
    manager = TaskManager(db)
    try:
        manager.delete_task(task_id)
        logger.info("event=delete_task_success task_id=%s", task_id)
    except ValueError as e:
        logger.warning("event=delete_task_not_found task_id=%s detail=%s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    return None

# Endpoint raíz para verificar que la API está funcionando
@router.get("/")
def root():
    return {"message": "Task Management API"}
