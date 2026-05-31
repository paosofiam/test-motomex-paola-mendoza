"""Entidad Tier 3: productos — MODELO FUNCIONAL.

Métodos permitidos (matriz): get_all, get_by_id, search, create, delete. NO update.

Notas de contrato (la conversión a MXN y el shaping de respuesta viven en la futura capa
de controladores; aquí los métodos devuelven instancias ORM con `marca`/`moneda` cargadas):
- `precio` se almacena en centavos en la moneda original (`moneda_id`).
- `create` resuelve por find-or-create: `marca` (string), `vehiculos` [{modelo,marca,anio}]
  (cascada marca), `categorias` [string]. Para `ciudades` el comportamiento es find-or-fail
  efectivo: la BD exige estado_id NOT NULL que el payload de productos no transporta; falla
  con ResolutionError si la ciudad aún no existe en el catálogo.
- `delete` es soft delete; deja intactas las filas de relación.
"""

from sqlalchemy import ForeignKey, Integer, JSON, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core import resolvers
from app.core.mixins import TimestampMixin, _now
from app.core.normalization import normalize
from app.database import Base
from app.models.marca_model import MarcaModel
from app.models.producto_categoria_model import ProductoCategoriaModel
from app.models.producto_ciudad_model import ProductoCiudadModel
from app.models.producto_vehiculo_model import ProductoVehiculoModel


class ProductoModel(TimestampMixin, Base):
    __tablename__ = "productos"

    marca_id: Mapped[int] = mapped_column(ForeignKey("marcas.id"), nullable=False)
    modelo: Mapped[str] = mapped_column(String(255), nullable=False)
    precio: Mapped[int] = mapped_column(Integer, nullable=False)  # centavos (moneda original)
    moneda_id: Mapped[int] = mapped_column(ForeignKey("monedas.id"), nullable=False, default=1)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    especificaciones: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    marca: Mapped["MarcaModel"] = relationship(lazy="joined")
    moneda: Mapped["MonedaModel"] = relationship(lazy="joined")  # noqa: F821

    # ---- Métodos de la matriz -------------------------------------------------

    @classmethod
    def get_all(cls, db: Session) -> list["ProductoModel"]:
        """Todos los productos activos (deleted_at IS NULL)."""
        return list(db.scalars(select(cls).where(cls.deleted_at.is_(None))))

    @classmethod
    def get_by_id(cls, db: Session, producto_id: int) -> "ProductoModel | None":
        """Producto activo por id, o None."""
        return db.scalar(
            select(cls).where(cls.id == producto_id, cls.deleted_at.is_(None))
        )

    @classmethod
    def search(
        cls,
        db: Session,
        marca: str | None = None,
        precio_minimo: int | None = None,
    ) -> list["ProductoModel"]:
        """Búsqueda activa por `marca` (string normalizado, vía join) y/o `precio_minimo`.

        Nota: `precio_minimo` compara contra el `precio` almacenado en centavos (moneda
        original). El filtrado normalizado a MXN se incorporará con la capa de shaping.
        """
        stmt = select(cls).where(cls.deleted_at.is_(None))
        if marca is not None:
            stmt = stmt.join(MarcaModel, cls.marca_id == MarcaModel.id).where(
                MarcaModel.marca == normalize(marca),
                MarcaModel.deleted_at.is_(None),
            )
        if precio_minimo is not None:
            stmt = stmt.where(cls.precio >= precio_minimo)
        return list(db.scalars(stmt))

    @classmethod
    def create(
        cls,
        db: Session,
        *,
        marca: str,
        modelo: str,
        precio: int,
        moneda_id: int = 1,
        stock: int = 0,
        especificaciones: dict | None = None,
        vehiculos: list[dict] | None = None,
        categorias: list[str] | None = None,
        ciudades: list[str] | None = None,
    ) -> "ProductoModel":
        """Crea un producto resolviendo catálogos y sus relaciones.

        - `marca`, `vehiculos`, `categorias`: find-or-create (catálogos conversacionales).
        - `ciudades`: find-or-fail efectivo — la BD exige estado_id NOT NULL que este
          payload no transporta; lanza ResolutionError si la ciudad no existe en catálogo.
        `created_at == updated_at`. Hace commit y devuelve el producto recién creado.
        """
        marca_row = resolvers.find_or_create_marca(db, marca)
        ts = _now()
        producto = cls(
            marca_id=marca_row.id,
            modelo=modelo,
            precio=precio,
            moneda_id=moneda_id,
            stock=stock,
            especificaciones=especificaciones,
            created_at=ts,
            updated_at=ts,
        )
        db.add(producto)
        db.flush()

        for v in vehiculos or []:
            veh = resolvers.find_or_create_vehiculo(db, v["modelo"], v["marca"], v["anio"])
            db.add(ProductoVehiculoModel(
                producto_id=producto.id, vehiculo_id=veh.id, created_at=ts, updated_at=ts
            ))
        for c in categorias or []:
            cat = resolvers.find_or_create_categoria(db, c)
            db.add(ProductoCategoriaModel(
                producto_id=producto.id, categoria_id=cat.id, created_at=ts, updated_at=ts
            ))
        for ci in ciudades or []:
            ciu = resolvers.find_or_create_ciudad(db, ci)
            db.add(ProductoCiudadModel(
                producto_id=producto.id, ciudad_id=ciu.id, created_at=ts, updated_at=ts
            ))

        # TODO (services layer): el commit se moverá al servicio que conecte modelo y controlador;
        # el modelo pasará a hacer solo flush() para que múltiples operaciones puedan componerse
        # en una sola transacción atómica. Los métodos de solo lectura (get_all, get_by_id,
        # search) nunca comitean — solo los métodos de escritura (create, delete) lo hacen aquí.
        db.commit()
        db.refresh(producto)
        return producto

    @classmethod
    def delete(cls, db: Session, producto_id: int) -> bool:
        """Soft delete (set deleted_at). No toca filas de relación. Devuelve False si no existe."""
        producto = cls.get_by_id(db, producto_id)
        if producto is None:
            return False
        producto.deleted_at = _now()
        # TODO (services layer): ver nota en create().
        db.commit()
        return True
