from datetime import date, datetime, timezone
from typing import Any

from .dbManagement import (
    count_overdue_tasks,
    delete_record,
    get_all_records,
    get_expired_tasks,
    get_record_by_id,
    insert_record,
    update_record,
)
from .schemas import TaskCreate, TaskUpdate


class TaskManager:
    def __init__(self, _db: Any = None):
        # Se mantiene el parametro por compatibilidad con Depends(get_db).
        self.table_name = "tasks"

    def _clean_text(self, text: str | None) -> str:
        if text is None:
            return ""

        censored_words = ["maldicion", "tonto", "idiota", "malo", "feo"]
        cleaned_text = text.strip()
        for word in censored_words:
            cleaned_text = cleaned_text.replace(word, "****")
        return cleaned_text

    def _serialize_task(self, row: dict[str, Any]) -> dict[str, Any]:
        result = dict(row)

        deadline = result.get("deadline")
        if isinstance(deadline, datetime):
            result["deadline"] = deadline.date()

        return result

    def add_task(self, task_create: TaskCreate) -> dict[str, Any]:
        payload = {
            "titulo": self._clean_text(task_create.titulo),
            "contenido": self._clean_text(task_create.contenido),
            "deadline": datetime.combine(task_create.deadline, datetime.min.time(), tzinfo=timezone.utc),
            "completada": False,
        }
        created = insert_record(self.table_name, payload)
        return self._serialize_task(created)

    def get_task(self, task_id: int) -> dict[str, Any]:
        row = get_record_by_id(self.table_name, task_id)
        if not row:
            raise ValueError(f"Tarea con ID {task_id} no encontrada")
        return self._serialize_task(row)

    def get_all_tasks(self) -> list[dict[str, Any]]:
        rows = get_all_records(self.table_name)
        return [self._serialize_task(row) for row in rows]

    def set_task_completed(self, task_id: int) -> dict[str, Any]:
        updated = update_record(
            self.table_name,
            task_id,
            {
                "completada": True,
                "updated_at": datetime.now(timezone.utc),
            },
        )
        if not updated:
            raise ValueError(f"Tarea con ID {task_id} no encontrada")
        return self._serialize_task(updated)

    def update_task(self, task_id: int, task_update: TaskUpdate) -> dict[str, Any]:
        payload = {
            "titulo": self._clean_text(task_update.titulo),
            "contenido": self._clean_text(task_update.contenido),
            "deadline": datetime.combine(task_update.deadline, datetime.min.time(), tzinfo=timezone.utc),
            "completada": task_update.completada,
            "updated_at": datetime.now(timezone.utc),
        }

        updated = update_record(self.table_name, task_id, payload)
        if not updated:
            raise ValueError(f"Tarea con ID {task_id} no encontrada")
        return self._serialize_task(updated)

    def delete_task(self, task_id: int) -> bool:
        deleted = delete_record(self.table_name, task_id)
        if not deleted:
            raise ValueError(f"Tarea con ID {task_id} no encontrada")
        return True

    def get_expired_tasks(self) -> list[dict[str, Any]]:
        rows = get_expired_tasks()
        return [self._serialize_task(row) for row in rows]

    def count_overdue(self) -> int:
        return count_overdue_tasks()
