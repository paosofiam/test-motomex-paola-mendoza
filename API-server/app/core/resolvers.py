"""Resolución de catálogos (find-or-create / find-or-fail) para la capa de datos.

Estos helpers encapsulan la lógica de ENTRADA del contrato (`POST /productos`,
`POST/PATCH /leads`): convierten los strings/objetos que envía el cliente a las FKs
internas, creando registros de catálogo cuando la política lo permite.

Importante: son funciones sueltas que operan con `db: Session`, NO métodos de los
modelos de catálogo. Así se respeta la matriz "solo 2 modelos funcionales": los
catálogos siguen sin métodos propios y crecen solo por find-or-create.

Política (de contracts.md / endpoints.md):
- `marca`, `vehiculos`, `categorias` en productos → find-or-create (cascada marca en vehiculos).
- `ciudades` en productos → find-or-fail efectivo: la BD exige estado_id NOT NULL que el
  payload de productos no transporta; se resuelve solo si la ciudad ya existe en catálogo.
- `ciudad` en leads → find-or-fail explícito (find_ciudad_or_fail).
- `productos_interes` en leads → find-or-fail por `productos.modelo` (puede devolver varios).
- Toda query filtra `deleted_at IS NULL`.

Los valores Tier 2 se almacenan y consultan SIEMPRE normalizados (ver `normalize`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ResolutionError
from app.core.mixins import _now
from app.core.normalization import normalize

if TYPE_CHECKING:
    from app.models.categoria_model import CategoriaModel
    from app.models.chat_model import ChatModel
    from app.models.ciudad_model import CiudadModel
    from app.models.marca_model import MarcaModel
    from app.models.producto_model import ProductoModel
    from app.models.vehiculo_model import VehiculoModel


def find_or_create_marca(db: Session, marca: str) -> MarcaModel:
    """Devuelve la MarcaModel cuyo nombre normalizado coincide; la crea si no existe."""
    from app.models.marca_model import MarcaModel

    nombre = normalize(marca)
    row = db.scalar(
        select(MarcaModel).where(MarcaModel.marca == nombre, MarcaModel.deleted_at.is_(None))
    )
    if row is None:
        ts = _now()
        row = MarcaModel(marca=nombre, created_at=ts, updated_at=ts)
        db.add(row)
        db.flush()
    return row


def find_or_create_categoria(db: Session, categoria: str) -> CategoriaModel:
    """Devuelve la CategoriaModel normalizada; la crea si no existe."""
    from app.models.categoria_model import CategoriaModel

    nombre = normalize(categoria)
    row = db.scalar(
        select(CategoriaModel).where(
            CategoriaModel.categoria == nombre, CategoriaModel.deleted_at.is_(None)
        )
    )
    if row is None:
        ts = _now()
        row = CategoriaModel(categoria=nombre, created_at=ts, updated_at=ts)
        db.add(row)
        db.flush()
    return row


def find_or_create_vehiculo(db: Session, modelo: str, marca: str, anio: int) -> VehiculoModel:
    """Find-or-create determinista por la tripleta (modelo, marca_id, anio).

    Si la marca del vehículo no existe, se crea en cascada (find_or_create_marca).
    """
    from app.models.vehiculo_model import VehiculoModel

    marca_row = find_or_create_marca(db, marca)
    modelo_norm = normalize(modelo)
    row = db.scalar(
        select(VehiculoModel).where(
            VehiculoModel.modelo == modelo_norm,
            VehiculoModel.marca_id == marca_row.id,
            VehiculoModel.anio == anio,
            VehiculoModel.deleted_at.is_(None),
        )
    )
    if row is None:
        ts = _now()
        row = VehiculoModel(
            modelo=modelo_norm, marca_id=marca_row.id, anio=anio, created_at=ts, updated_at=ts
        )
        db.add(row)
        db.flush()
    return row


def find_or_create_ciudad(db: Session, ciudad: str, estado_id: int | None = None) -> CiudadModel:
    """Devuelve la CiudadModel normalizada.

    Crear una ciudad nueva exige `estado_id` (la columna es NOT NULL y el campo derivado
    `leads.estado` depende de que toda ciudad tenga estado). Por eso, en flujos sin estado
    (p. ej. `productos.ciudades`, que solo envían el nombre) este helper se comporta como
    find-or-fail para ciudades aún no existentes.
    """
    from app.models.ciudad_model import CiudadModel

    nombre = normalize(ciudad)
    row = db.scalar(
        select(CiudadModel).where(CiudadModel.ciudad == nombre, CiudadModel.deleted_at.is_(None))
    )
    if row is None:
        if estado_id is None:
            raise ResolutionError(
                field="ciudades",
                value_received=ciudad,
                detail=f"La ciudad '{ciudad}' no existe y no puede crearse sin estado",
            )
        ts = _now()
        row = CiudadModel(ciudad=nombre, estado_id=estado_id, created_at=ts, updated_at=ts)
        db.add(row)
        db.flush()
    return row


def find_ciudad_or_fail(db: Session, ciudad: str) -> CiudadModel:
    """Find-or-fail de ciudad (usado por leads). Lanza ResolutionError si no existe."""
    from app.models.ciudad_model import CiudadModel

    nombre = normalize(ciudad)
    row = db.scalar(
        select(CiudadModel).where(CiudadModel.ciudad == nombre, CiudadModel.deleted_at.is_(None))
    )
    if row is None:
        raise ResolutionError(field="ciudad", value_received=ciudad)
    return row


def find_productos_by_modelo_or_fail(db: Session, modelo: str) -> list[ProductoModel]:
    """Find-or-fail por `productos.modelo`. Puede devolver VARIOS productos (ambigüedad
    de catálogo); la relación se persiste con todos los matches. Lanza ResolutionError si
    no hay ninguno. `productos` es inventario real: no se crea por interés del cliente.
    """
    from app.models.producto_model import ProductoModel

    rows = list(
        db.scalars(
            select(ProductoModel).where(
                ProductoModel.modelo == modelo, ProductoModel.deleted_at.is_(None)
            )
        )
    )
    if not rows:
        raise ResolutionError(field="productos_interes", value_received=modelo)
    return rows


def get_active_chat_id(db: Session, lead_id: int) -> int | None:
    """Id del chat activo más reciente del lead (campo derivado `Lead.chat_id`).

    `chats WHERE lead_id=? AND deleted_at IS NULL ORDER BY created_at DESC LIMIT 1`.
    Consulta suelta (no método de ChatModel) para preservar la matriz de métodos.
    """
    from app.models.chat_model import ChatModel

    return db.scalar(
        select(ChatModel.id)
        .where(ChatModel.lead_id == lead_id, ChatModel.deleted_at.is_(None))
        .order_by(ChatModel.created_at.desc())
        .limit(1)
    )
