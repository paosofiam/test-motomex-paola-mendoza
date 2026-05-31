"""Entrypoint único de seeders.

Uso (venv activo, desde API-server/):  python -m seeders.run_all

Orquesta catalog_defaults → sample_data en orden FK-safe (una sola sesión), e imprime
el conteo de filas activas por tabla como prueba de que las 18 quedaron pobladas.
Idempotente: re-ejecutar no duplica filas.
"""

import app.models  # noqa: F401  -- registra todas las tablas/relaciones
from app.database import Base, SessionLocal
from seeders import catalog_defaults, sample_data

# Orden de reporte (FK-safe / legible)
TABLA_ORDEN = [
    "monedas", "estados", "intenciones_de_compra_de_leads", "chat_statuses",
    "marcas", "categorias", "ciudades", "vehiculos",
    "productos", "leads", "chats", "pre_ordenes",
    "productos_vehiculos", "productos_ciudades", "productos_categorias",
    "leads_productos", "leads_vehiculos", "pre_ordenes_productos",
]


def _counts(db) -> dict[str, int]:
    from sqlalchemy import func, select

    out = {}
    for nombre in TABLA_ORDEN:
        tabla = Base.metadata.tables[nombre]
        out[nombre] = db.scalar(select(func.count()).select_from(tabla))
    return out


def main() -> None:
    db = SessionLocal()
    try:
        print(">> Sembrando catálogos Tier 1 (valores exactos)...")
        catalog_defaults.seed(db)
        print(">> Sembrando datos de ejemplo (productos/leads vía modelos funcionales)...")
        sample_data.seed(db)

        print("\n== Conteo de filas por tabla ==")
        counts = _counts(db)
        ancho = max(len(n) for n in counts)
        vacias = []
        for nombre, n in counts.items():
            marca = "OK " if n > 0 else "!! "
            print(f"  {marca}{nombre.ljust(ancho)} : {n}")
            if n == 0:
                vacias.append(nombre)

        if vacias:
            print(f"\n!! ADVERTENCIA: tablas sin filas -> {vacias}")
        else:
            print(f"\nTodas las {len(counts)} tablas pobladas correctamente.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
