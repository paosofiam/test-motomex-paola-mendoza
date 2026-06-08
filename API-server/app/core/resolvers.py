"""Resolución de catálogos (find-or-create / find-or-fail) para la capa de datos.

Estos helpers encapsulan la lógica de ENTRADA del contrato (`POST /productos`,
`POST/PATCH /leads`): convierten los strings/objetos que envía el cliente a las FKs
internas, creando registros de catálogo cuando la política lo permite.

Importante: son funciones sueltas que operan con `db: Session`, NO métodos de los
modelos de catálogo. Así se respeta la matriz "solo 2 modelos funcionales": los
catálogos siguen sin métodos propios y crecen solo por find-or-create.

Política (de contracts.md / endpoints.md):
- `marca`, `vehiculos`, `categorias` en productos → find-or-create (cascada marca en vehiculos).
- `ciudades` en productos y `ciudad` en leads → cada una viaja como `{ciudad, estado}`. El estado
  se resuelve por nombre o abreviación (`find_estado`) y, si existe, la ciudad es find-or-create
  bajo ese estado. `resolver_ciudades` aplica éxito parcial: si el estado no se reconoce, omite esa
  ciudad y acumula un aviso (el recurso se crea/edita igual). La orquestación vive en los services.
- `productos_interes` en leads → find-or-skip aditivo por `productos.modelo` (puede devolver varios);
  los modelos sin match en inventario se omiten y se reportan como avisos (`resolver_productos_interes`).
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
    from datetime import datetime

    from app.models.categoria_model import CategoriaModel
    from app.models.chat_model import ChatModel
    from app.models.ciudad_model import CiudadModel
    from app.models.estado_model import EstadoModel
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


def find_estado(db: Session, estado: str) -> "EstadoModel | None":
    """Resuelve un estado por nombre o por abreviación (ambos normalizados); None si no existe.

    Compara en Python porque los estados se guardan con su nombre de display (sin normalizar): el
    catálogo es pequeño e inmutable (32 entidades), así que cargarlo entero es barato y determinista.
    """
    from app.models.estado_model import EstadoModel

    objetivo = normalize(estado)
    for row in db.scalars(select(EstadoModel).where(EstadoModel.deleted_at.is_(None))):
        if normalize(row.estado) == objetivo:
            return row
        if row.abreviacion and normalize(row.abreviacion) == objetivo:
            return row
    return None


def resolver_ciudades(db: Session, items: list[dict]) -> "tuple[list[CiudadModel], list[str]]":
    """Resuelve una lista de `{ciudad, estado}` a CiudadModel con éxito parcial.

    Por cada ciudad: si el estado no se reconoce, se omite y se acumula un aviso (el recurso se
    crea/edita igual); si resuelve, se hace find-or-create de la ciudad bajo ese estado. Devuelve
    `(ciudades_resueltas, avisos)`. Lo usan productos (lista) y leads (lista de un elemento).
    """
    resueltas = []
    avisos = []
    for item in items:
        estado_row = find_estado(db, item["estado"])
        if estado_row is None:
            avisos.append(
                f"No se guardó la ciudad '{item['ciudad']}': estado '{item['estado']}' no reconocido"
            )
            continue
        resueltas.append(find_or_create_ciudad(db, item["ciudad"], estado_row.id))
    return resueltas, avisos


def sync_link_rows(
    db: Session,
    model: type,
    owner_fk: str,
    owner_id: int,
    fk_name: str,
    desired_ids: list[int],
    ts: datetime,
    replace: bool = False,
) -> None:
    """Reconcilia filas de una tabla de relación N:M respetando soft-delete + UNIQUE(owner_fk, fk).

    `model` es la clase ORM de la tabla de relación (`LeadProductoModel`, `LeadVehiculoModel`, …);
    `owner_fk` es el nombre de la columna FK del dueño (p. ej. `"lead_id"`) y `fk_name` el de la otra
    FK (p. ej. `"producto_id"`). `desired_ids` se deduplica preservando orden. Reactiva filas
    soft-deleted que vuelven al conjunto deseado (evita violar el UNIQUE al re-insertar el mismo par),
    soft-elimina las que sobran (solo si `replace=True`) e inserta las nuevas. Nunca hard delete.

    Es una función suelta que opera con `db: Session`; las clases de relación se pasan como `model`
    para no importarlas aquí (evita ciclos de import).
    """
    existing = {
        getattr(r, fk_name): r
        for r in db.scalars(select(model).where(getattr(model, owner_fk) == owner_id))
    }
    desired = list(dict.fromkeys(desired_ids))
    for fk_id in desired:
        row = existing.get(fk_id)
        if row is None:
            db.add(model(**{owner_fk: owner_id, fk_name: fk_id}, created_at=ts, updated_at=ts))
        elif row.deleted_at is not None:
            row.deleted_at = None
            row.updated_at = ts
    if replace:
        desired_set = set(desired)
        for fk_id, row in existing.items():
            if fk_id not in desired_set and row.deleted_at is None:
                row.deleted_at = ts


def find_productos_by_modelo(db: Session, modelo: str) -> list[ProductoModel]:
    """Find por `productos.modelo`. Puede devolver VARIOS productos (ambigüedad de catálogo);
    la relación se persiste con todos los matches. Devuelve lista vacía si no hay ninguno: el
    llamador decide la política (los leads aplican éxito parcial, no fallan). `productos` es
    inventario real: nunca se crea por interés del cliente.
    """
    from app.models.producto_model import ProductoModel

    return list(
        db.scalars(
            select(ProductoModel).where(
                ProductoModel.modelo == modelo, ProductoModel.deleted_at.is_(None)
            )
        )
    )


def resolver_productos_interes(db: Session, modelos: list[str]) -> "tuple[list[int], list[str]]":
    """Resuelve una lista de modelos a `producto_id`s con éxito parcial (espejo de
    `resolver_ciudades`).

    Por cada modelo: si no existe en el inventario, se omite y se acumula un aviso (el lead se
    crea/edita igual); si matchea uno o varios productos, se incluyen TODOS sus ids. Devuelve
    `(producto_ids, avisos)`. `productos` es inventario: un interés del cliente no autoriza crear
    producto, por eso es find-or-skip y no find-or-create.
    """
    producto_ids = []
    avisos = []
    for modelo in modelos:
        rows = find_productos_by_modelo(db, modelo)
        if not rows:
            avisos.append(
                f"No se vinculó el producto de interés '{modelo}': no existe en el inventario"
            )
            continue
        producto_ids.extend(prod.id for prod in rows)
    return producto_ids, avisos


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
