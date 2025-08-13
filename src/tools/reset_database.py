import argparse
import os
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = "inventario.db"


TABLES_IN_ORDER = [
    # Children first (to respect FK constraints)
    "venta_items",
    "ventas",
    "movimientos",
    "productos",
    "categorias",
]


def table_exists(con: sqlite3.Connection, table_name: str) -> bool:
    cur = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
    )
    return cur.fetchone() is not None


def reset_database(db_path: str = DEFAULT_DB_PATH, verbose: bool = True) -> None:
    """Delete all data while preserving schema. Resets AUTOINCREMENT counters.

    This is safe for the app schema and avoids dropping tables.
    """
    db_file = Path(db_path)
    if not db_file.exists():
        raise FileNotFoundError(f"No se encontró la base de datos en: {db_file.resolve()}")

    con = sqlite3.connect(str(db_file))
    try:
        if verbose:
            print(f"Conectado a: {db_file.resolve()}")
        con.execute("PRAGMA foreign_keys=OFF")
        cur = con.cursor()

        # Borrar datos de tablas existentes
        for t in TABLES_IN_ORDER:
            if table_exists(con, t):
                if verbose:
                    print(f"Limpiando tabla: {t}")
                cur.execute(f"DELETE FROM {t}")
            else:
                if verbose:
                    print(f"Aviso: la tabla '{t}' no existe. Se omite.")

        # Resetear secuencias autoincrement si existe sqlite_sequence
        if table_exists(con, "sqlite_sequence"):
            existing_tables = [t for t in TABLES_IN_ORDER if table_exists(con, t)]
            if existing_tables:
                q = (
                    "DELETE FROM sqlite_sequence WHERE name IN ("
                    + ",".join(["?"] * len(existing_tables))
                    + ")"
                )
                cur.execute(q, existing_tables)
                if verbose:
                    print("Secuencias autoincrement reiniciadas.")
        else:
            if verbose:
                print("Aviso: 'sqlite_sequence' no existe. No hay AUTOINCREMENT a reiniciar.")

        con.commit()
    finally:
        con.execute("PRAGMA foreign_keys=ON")
        con.close()
        if verbose:
            print("Limpieza completada.")


def main():
    parser = argparse.ArgumentParser(
        description="Restablece la base de datos dejándola vacía y conservando el esquema."
    )
    parser.add_argument(
        "--db",
        dest="db_path",
        default=DEFAULT_DB_PATH,
        help=f"Ruta al archivo SQLite (por defecto: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="No preguntar confirmación (modo no interactivo)",
    )
    args = parser.parse_args()

    if not args.yes:
        resp = input(
            f"Esto eliminará TODOS los datos de '{args.db_path}' y conservará el esquema. ¿Continuar? [escribe 'SI' para confirmar]: "
        ).strip()
        if resp.upper() != "SI":
            print("Operación cancelada.")
            return

    reset_database(args.db_path, verbose=True)


if __name__ == "__main__":
    main()
