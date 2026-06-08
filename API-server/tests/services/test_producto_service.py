"""producto_service: orquestación de /productos (router → service → model).

Aquí vive el comportamiento que antes estaba en `ProductoModel`: find-or-create de catálogos
(`marca`, `vehiculos` cascada marca, `categorias`), resolución de `ciudades` ({ciudad, estado}) con
éxito parcial, filtrado de `search`, conversión a MXN y armado del DTO, y soft delete. `create`
devuelve `(respuesta, avisos)`. Se invocan las funciones del módulo directamente con la `Session`.
"""

import pytest

from app.core.exceptions import NotFoundError
from app.models.producto_model import ProductoModel
from app.schemas.producto import ProductoCreate
from app.services import producto_service


def _payload(**over):
    base = dict(marca="Nissan", modelo="Versa", precio=12999, moneda_id=1)
    base.update(over)
    return ProductoCreate(**base)


def test_create_finds_or_creates_marca_and_defaults(db, seed_catalogs):
    """La marca se resuelve por find-or-create y se persiste normalizada; la moneda cae por defecto
    a MXN (id 1) y el precio se guarda como int en centavos. `created_at == updated_at`."""
    resp, _ = producto_service.create(db, _payload(modelo="Filtro", precio=9999))
    raw = db.get(ProductoModel, resp.id)
    assert raw.marca.marca == "nissan"
    assert raw.moneda_id == 1
    assert isinstance(raw.precio, int)
    assert raw.created_at == raw.updated_at


def test_create_returns_mxn_price_int_and_moneda_string(db, seed_catalogs):
    """Precio MXN (tipo_de_cambio 100) sin cambio, en centavos int (nunca float); `moneda` Tier 1
    como string y `marca` Tier 2 normalizada."""
    resp, _ = producto_service.create(db, _payload(precio=12999, moneda_id=1))
    assert resp.precio == 12999
    assert isinstance(resp.precio, int)
    assert resp.moneda == "MXN"
    assert resp.marca == "nissan"


def test_create_converts_usd_price_to_mxn(db, seed_catalogs):
    """Un precio en USD se convierte a centavos MXN; la etiqueta `moneda` también queda en MXN."""
    resp, _ = producto_service.create(db, _payload(marca="Bosch", modelo="Bateria", precio=12999, moneda_id=2))
    assert resp.precio == round(12999 * 1700 / 100) == 220983
    assert isinstance(resp.precio, int)
    assert resp.moneda == "MXN"


def test_create_cascades_vehiculo_and_categoria_relations(db, seed_catalogs):
    """Crear un producto cascada las relaciones con vehículos (find-or-create) y categorías; la
    respuesta las expone normalizadas."""
    resp, _ = producto_service.create(db, _payload(
        modelo="Filtro",
        vehiculos=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}],
        categorias=["Filtros"],
    ))
    assert [v.modelo for v in resp.vehiculos] == ["versa"]
    assert resp.categorias == ["filtros"]


def test_create_links_known_city_and_warns_unknown_estado(db, seed_catalogs):
    """`ciudades` ({ciudad, estado}) se resuelven con éxito parcial: la de estado conocido se vincula
    y la de estado no reconocido se omite con un aviso (el producto se crea igual)."""
    resp, avisos = producto_service.create(db, _payload(modelo="ConCiudad", ciudades=[
        {"ciudad": "Guadalajara", "estado": "Jalisco"},
        {"ciudad": "Tijuana", "estado": "Estado Inexistente"},
    ]))
    assert [c.ciudad for c in resp.ciudades] == ["guadalajara"]
    assert len(avisos) == 1


def test_get_by_id_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        producto_service.get_by_id(db, 999999)


def test_get_by_id_returns_active(db, seed_catalogs):
    created, _ = producto_service.create(db, _payload())
    assert producto_service.get_by_id(db, created.id).id == created.id


def test_search_filters_by_marca_and_excludes_soft_deleted(db, seed_catalogs):
    """search normaliza la marca Tier 2 al filtrar y excluye filas soft-deleted (también en get_by_id)."""
    a, _ = producto_service.create(db, _payload(marca="Nissan", modelo="Versa"))
    producto_service.create(db, _payload(marca="Toyota", modelo="Corolla"))
    solo_nissan = producto_service.search(db, marca="  NISSAN ")
    assert [p.id for p in solo_nissan] == [a.id]
    producto_service.delete(db, a.id)
    assert a.id not in [p.id for p in producto_service.search(db)]
    with pytest.raises(NotFoundError):
        producto_service.get_by_id(db, a.id)


def test_search_precio_minimo_converts_to_mxn(db, seed_catalogs):
    """El filtro precio_minimo compara contra el precio convertido a MXN (centavos), no contra el
    precio en la moneda original del producto."""
    producto_service.create(db, _payload(marca="Bosch", modelo="Bateria", precio=12999, moneda_id=2))
    assert len(producto_service.search(db, precio_minimo=220983)) == 1
    assert len(producto_service.search(db, precio_minimo=220984)) == 0


def test_delete_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        producto_service.delete(db, 999999)


def test_delete_is_soft_keeps_row(db, seed_catalogs):
    """Soft delete: delete devuelve None (204 sin body) y la fila sigue en BD con deleted_at puesto."""
    created, _ = producto_service.create(db, _payload())
    assert producto_service.delete(db, created.id) is None
    raw = db.get(ProductoModel, created.id)
    assert raw is not None and raw.deleted_at is not None


def test_search_modelo_is_partial_match(db, seed_catalogs):
    """`modelo` filtra por coincidencia parcial 'contiene' (no exacta) sobre el término normalizado."""
    a, _ = producto_service.create(db, _payload(modelo="Bateria LTH 12V"))
    producto_service.create(db, _payload(modelo="Filtro de aceite"))
    assert [p.id for p in producto_service.search(db, modelo="bateria")] == [a.id]


def test_search_precio_maximo_in_mxn(db, seed_catalogs):
    """`precio_maximo` acota por arriba contra el precio ya convertido a MXN (centavos)."""
    barato, _ = producto_service.create(db, _payload(modelo="Barato", precio=10000, moneda_id=1))
    producto_service.create(db, _payload(marca="Bosch", modelo="Caro", precio=12999, moneda_id=2))
    assert [p.id for p in producto_service.search(db, precio_maximo=10000)] == [barato.id]


def test_search_by_moneda_id_original_currency(db, seed_catalogs):
    """`moneda_id` filtra por la moneda ORIGINAL del producto (la respuesta sigue siempre en MXN)."""
    producto_service.create(db, _payload(modelo="EnPesos", moneda_id=1))
    usd, _ = producto_service.create(db, _payload(marca="Bosch", modelo="EnDolares", precio=10000, moneda_id=2))
    assert [p.id for p in producto_service.search(db, moneda_id=2)] == [usd.id]


def test_search_by_stock_range(db, seed_catalogs):
    """`stock_minimo`/`stock_maximo` acotan el inventario disponible."""
    agotado, _ = producto_service.create(db, _payload(modelo="Agotado", stock=0))
    disponible, _ = producto_service.create(db, _payload(modelo="Disponible", stock=7))
    assert [p.id for p in producto_service.search(db, stock_minimo=1)] == [disponible.id]
    assert [p.id for p in producto_service.search(db, stock_maximo=0)] == [agotado.id]


def test_search_by_especificaciones_json(db, seed_catalogs):
    """`espec_clave`+`espec_valor` filtran por un campo del JSON `especificaciones` (solo MySQL)."""
    if db.get_bind().dialect.name != "mysql":
        pytest.skip("el filtro de especificaciones usa json_unquote/json_extract (MySQL)")
    v12, _ = producto_service.create(db, _payload(modelo="Bat12", especificaciones={"voltaje": "12V"}))
    producto_service.create(db, _payload(modelo="Bat24", especificaciones={"voltaje": "24V"}))
    res = producto_service.search(db, espec_clave="voltaje", espec_valor="12V")
    assert [p.id for p in res] == [v12.id]


def test_search_by_categoria_relation(db, seed_catalogs):
    """`categoria` filtra por la relación N:M productos_categorias (Tier 2 normalizado)."""
    con_cat, _ = producto_service.create(db, _payload(modelo="ConCat", categorias=["Baterias"]))
    producto_service.create(db, _payload(modelo="SinCat"))
    assert [p.id for p in producto_service.search(db, categoria="baterias")] == [con_cat.id]


def test_search_by_ciudad_and_estado_relation(db, seed_catalogs):
    """`ciudad` y `estado` filtran por disponibilidad (productos_ciudades → ciudades → estados)."""
    en_gdl, _ = producto_service.create(db, _payload(
        modelo="EnGDL", ciudades=[{"ciudad": "Guadalajara", "estado": "Jalisco"}]
    ))
    producto_service.create(db, _payload(modelo="SinCiudad"))
    assert [p.id for p in producto_service.search(db, ciudad="guadalajara")] == [en_gdl.id]
    assert [p.id for p in producto_service.search(db, estado="Jalisco")] == [en_gdl.id]


def test_search_by_vehiculo_compatibility(db, seed_catalogs):
    """Los tres `vehiculo_*` estrechan el MISMO vehículo compatible ('qué sirve para mi Versa 2015')."""
    versa, _ = producto_service.create(db, _payload(
        modelo="BateriaVersa", vehiculos=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}]
    ))
    producto_service.create(db, _payload(modelo="Generico"))
    assert [p.id for p in producto_service.search(db, vehiculo_modelo="versa", vehiculo_anio=2015)] == [versa.id]
    assert producto_service.search(db, vehiculo_anio=2020) == []
    assert [p.id for p in producto_service.search(db, vehiculo_marca="Nissan")] == [versa.id]


def test_search_combina_filtros_con_and(db, seed_catalogs):
    """Múltiples filtros se combinan con AND; uno contradictorio reduce a lista vacía."""
    a, _ = producto_service.create(db, _payload(marca="Nissan", modelo="Combo", stock=5, categorias=["Baterias"]))
    assert [p.id for p in producto_service.search(db, marca="nissan", stock_minimo=1, categoria="baterias")] == [a.id]
    assert producto_service.search(db, marca="nissan", categoria="inexistente") == []


def test_search_unknown_tier2_returns_empty_not_error(db, seed_catalogs):
    """Un valor de catálogo Tier 2 que no resuelve devuelve [] (semántica de búsqueda, no error)."""
    producto_service.create(db, _payload())
    assert producto_service.search(db, marca="marca_inexistente") == []
    assert producto_service.search(db, categoria="cat_inexistente") == []
    assert producto_service.search(db, estado="Estado Inexistente") == []


def test_search_order_by_precio_and_direction(db, seed_catalogs):
    """`order_by`/`orden` ordenan el resultado; `precio` ordena por el valor ya convertido a MXN."""
    barato, _ = producto_service.create(db, _payload(modelo="Barato", precio=10000, moneda_id=1))
    caro, _ = producto_service.create(db, _payload(marca="Bosch", modelo="Caro", precio=12999, moneda_id=2))
    assert [p.id for p in producto_service.search(db, order_by="precio", orden="asc")] == [barato.id, caro.id]
    assert [p.id for p in producto_service.search(db, order_by="precio", orden="desc")] == [caro.id, barato.id]


def test_search_limit_and_offset(db, seed_catalogs):
    """`limit`/`offset` paginan el resultado (orden por defecto: id asc)."""
    a, _ = producto_service.create(db, _payload(modelo="A"))
    b, _ = producto_service.create(db, _payload(modelo="B"))
    producto_service.create(db, _payload(modelo="C"))
    assert [p.id for p in producto_service.search(db, limit=2)] == [a.id, b.id]
    assert [p.id for p in producto_service.search(db, offset=1, limit=1)] == [b.id]
