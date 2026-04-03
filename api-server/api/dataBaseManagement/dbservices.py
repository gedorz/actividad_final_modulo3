from datetime import date, datetime
from typing import List
from sqlalchemy.orm import Session
from .dbManagement import TaskDB
from .schemas import TaskCreate, TaskUpdate

# Is done: Implementar clase TaskManager con lógica de negocio
class TaskManager:
    def __init__(self, db: Session):
        self.db = db

    def _is_future_deadline(self, deadline: date) -> bool:
        return deadline >= date.today()

    def _clean_text(self, text: str) -> str:
        # Función para normalizar o censurar palabras malsonantes en títulos y contenidos
        # Implementa la lógica de limpieza de palabras malsonantes
        censored_words = ["maldición", "tonto", "idiota","malo", "tonto", "feo"]
        for word in censored_words:
            text = text.replace(word, "****")
        return text.strip()

    def add_task(self, task_create: TaskCreate) -> TaskDB:
        # Crear una nueva tarea en la base de datos de tareas
        newTask = TaskDB(
            titulo=self._clean_text(task_create.titulo),
            contenido=self._clean_text(task_create.contenido),
            deadline=task_create.deadline,
            completada=False,
            fecha_creacion=datetime.utcnow()
        )
        self.db.add(newTask)
        self.db.commit()
        self.db.refresh(newTask)
        return newTask

    def get_task(self, task_id: int) -> TaskDB:
        # Obtener una tarea por su ID
        itemtask = self.db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if not itemtask:
            raise ValueError(f"Tarea con ID {task_id} no encontrada")
        return itemtask

    def get_all_tasks(self) -> List[TaskDB]:
        # Obtener todas las tareas de la base de datos
        return self.db.query(TaskDB).all()

    def set_task_completed(self, task_id: int) -> TaskDB:
        # Marcar una tarea como completada
        itemtask = self.get_task(task_id)
        if itemtask:
            itemtask.completada = True
            self.db.commit()
            self.db.refresh(itemtask)
        return itemtask

    def update_task(self, task_id: int, task_update: TaskUpdate) -> TaskDB:
        # Actualizar una tarea existente
        itemtask = self.get_task(task_id)
        if itemtask:
            itemtask.titulo = self._clean_text(task_update.titulo)
            itemtask.contenido = self._clean_text(task_update.contenido)
            itemtask.deadline = task_update.deadline
            itemtask.completada = task_update.completada
            self.db.commit()
            self.db.refresh(itemtask)
        return itemtask

    def delete_task(self, task_id: int) -> bool:
        # Eliminar una tarea por su ID
        itemtask = self.get_task(task_id)
        if itemtask:
            self.db.delete(itemtask)
            self.db.commit()
            return True
        return False

    def get_expired_tasks(self) -> List[TaskDB]:
        # Obtener tareas caducadas (deadline < fecha actual)
        today = date.today()
        return self.db.query(TaskDB).filter(TaskDB.deadline < today).all()

    def get_tasks_by_completion(self, completed: bool) -> List[TaskDB]:
        # Obtener tareas por estado de completado
        return self.db.query(TaskDB).filter(TaskDB.completada == completed).all()

    def get_tasks_by_deadline(self, deadline: date) -> List[TaskDB]:
        # Obtener tareas por fecha de vencimiento específica
        return self.db.query(TaskDB).filter(TaskDB.deadline == deadline).all()

    def count_tasks(self) -> int:
        # Contar el número total de tareas en la base de datos
        return self.db.query(TaskDB).count()

    def count_overdue(self) -> int:
        # Contar el número de tareas vencidas
        today = date.today()
        return self.db.query(TaskDB).filter(TaskDB.deadline < today, TaskDB.completada == False).count()

    def count_completed_tasks(self) -> int:
        # Contar el número de tareas completadas
        return self.db.query(TaskDB).filter(TaskDB.completada == True).count()