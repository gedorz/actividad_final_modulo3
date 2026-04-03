import os
from typing import Any

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


def _get_env(*keys: str, default: str) -> str:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return default


def get_postgres_connection():
    return psycopg2.connect(
        host=_get_env("POSTGRES_HOST", "DB_POSTGRESDB_HOST", default="postgres"),
        port=int(_get_env("POSTGRES_PORT", "DB_POSTGRESDB_PORT", default="5432")),
        dbname=_get_env("POSTGRES_DB_NAME", "DB_POSTGRESDB_DATABASE", default="dbtaskmanager"),
        user=_get_env("POSTGRES_USER_NAME", "DB_POSTGRESDB_USER", default="taskmanageruser"),
        password=_get_env("POSTGRES_PASSWORD_VALUE", "DB_POSTGRESDB_PASSWORD", default="Qazwsx12"),
    )


def insert_record(table: str, data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        raise ValueError("El cuerpo 'data' no puede estar vacio.")

    columns = list(data.keys())
    values = [data[column] for column in columns]

    query = sql.SQL(
        "INSERT INTO {table} ({fields}) VALUES ({placeholders}) RETURNING *"
    ).format(
        table=sql.Identifier(table),
        fields=sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        placeholders=sql.SQL(", ").join(sql.Placeholder() for _ in columns),
    )

    with get_postgres_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, values)
            created_row = cursor.fetchone()
        connection.commit()

    return dict(created_row) if created_row else {}


def update_record(table: str, record_id: Any, data: dict[str, Any], id_column: str = "id") -> dict[str, Any] | None:
    if record_id is None:
        raise ValueError("El campo 'id' es obligatorio.")

    if not data:
        raise ValueError("El cuerpo 'data' no puede estar vacio.")

    assignments = [
        sql.SQL("{field} = {placeholder}").format(
            field=sql.Identifier(column),
            placeholder=sql.Placeholder(),
        )
        for column in data.keys()
    ]

    query = sql.SQL(
        "UPDATE {table} SET {assignments} WHERE {id_column} = {id_placeholder} RETURNING *"
    ).format(
        table=sql.Identifier(table),
        assignments=sql.SQL(", ").join(assignments),
        id_column=sql.Identifier(id_column),
        id_placeholder=sql.Placeholder(),
    )

    with get_postgres_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, [*data.values(), record_id])
            updated_row = cursor.fetchone()
        connection.commit()

    return dict(updated_row) if updated_row else None