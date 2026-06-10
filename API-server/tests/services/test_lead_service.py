"""lead_service: orquestación de /leads (router → service → model).

Aquí vive el comportamiento que antes estaba en `LeadModel`: armado del DTO con campos derivados
(`chat_id`/`status` vía `resolvers.get_active_chat`, `estado` por `ciudad → estados`,
`intencion_de_compra` string, vehículos como objetos), `create` IDEMPOTENTE por `chat_whatsapp_id`
(si ya hay un lead activo con ese `chat_whatsapp_id`, devuelve el existente sin crear; los leads no se
borran vía API), consulta `get_by_chat_whatsapp_id` (un solo objeto), reconciliación de
`productos_interes` (find-or-skip aditivo, multimatch) y `vehiculo` (find-or-create), y resolución de
`ciudad` ({ciudad, estado}) con éxito parcial. Tanto `productos_interes` como `vehiculo` se vinculan
de forma aditiva en `update` (combinan con lo existente; vacío/omitido = sin cambios). `create`
devuelve `(respuesta, avisos, creado)` y `update` `(respuesta, avisos)`. Llamadas directas con
`Session`.
"""

from datetime import datetime

import pytest

from app.core.exceptions import NotFoundError
from app.models.lead_model import LeadModel
from app.schemas.lead import LeadCreate, LeadUpdate
from app.services import lead_service
from tests.factories import make_chat, make_producto

JALISCO = {"ciudad": "Guadalajara", "estado": "Jalisco"}


def _create(**over):
    base = dict(
        chat_whatsapp_id="wa-001",
        nombre_whatsapp="Juan",
        telefono="+5213311112222",
        intencion_de_compra_id=1,
    )
    base.update(over)
    return LeadCreate(**base)


def test_create_returns_response_with_derived_fields(db, seed_catalogs):
    """Campos derivados: `ciudad` Tier 2 normalizada, `estado` por join ciudad → estados, `lead_id`
    alias (= id), y `chat_id`/`status` None mientras el lead no tiene chat activo."""
    resp, _, creado = lead_service.create(db, _create(ciudad=JALISCO))
    assert creado is True
    assert resp.ciudad == "guadalajara"
    assert resp.estado == "Jalisco"
    assert isinstance(resp.intencion_de_compra, str) and resp.intencion_de_compra
    assert resp.lead_id == resp.id
    assert resp.chat_id is None
    assert resp.status is None


def test_create_vehiculo_travels_as_object(db, seed_catalogs):
    resp, _, _ = lead_service.create(db, _create(vehiculo=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}]))
    assert [v.model_dump() for v in resp.vehiculo] == [
        {"modelo": "versa", "marca": "nissan", "anio": 2015}
    ]


def test_create_unknown_estado_skips_city_with_warning(db, seed_catalogs):
    """`ciudad` viaja como {ciudad, estado} y se resuelve con éxito parcial: si el estado no se
    reconoce, el lead se guarda SIN ciudad y se acumula un aviso (no es find-or-fail)."""
    resp, avisos, _ = lead_service.create(db, _create(ciudad={"ciudad": "Tijuana", "estado": "Estado Inexistente"}))
    assert resp.ciudad is None
    assert resp.estado is None
    assert len(avisos) == 1


def test_productos_interes_multimatch_persists_all(db, seed_catalogs):
    """`productos_interes` es find-or-skip aditivo por modelo: un modelo que matchea varios productos
    persiste la relación con todos ellos (dos entradas en la respuesta)."""
    make_producto(db, marca="Bosch", modelo="Balata X", precio=100)
    make_producto(db, marca="ATE", modelo="Balata X", precio=200)
    resp, _, _ = lead_service.create(db, _create(productos_interes=["Balata X"]))
    assert resp.productos_interes == ["Balata X", "Balata X"]


def test_create_unknown_producto_skips_with_warning(db, seed_catalogs):
    """find-or-skip: un modelo que no existe en inventario NO falla ni bloquea el lead. El lead se
    crea igual sin ese producto y el modelo omitido se reporta como aviso (no es find-or-fail)."""
    resp, avisos, _ = lead_service.create(db, _create(productos_interes=["NoExiste"]))
    assert resp.productos_interes == []
    assert len(avisos) == 1
    assert "NoExiste" in avisos[0]


def test_update_productos_interes_is_additive(db, seed_catalogs):
    """En PATCH `productos_interes` es aditivo: combina lo enviado con lo ya vinculado (no reemplaza)."""
    make_producto(db, marca="Bosch", modelo="Filtro A", precio=100)
    make_producto(db, marca="ATE", modelo="Balata B", precio=200)
    lead, _, _ = lead_service.create(db, _create(productos_interes=["Filtro A"]))
    updated, _ = lead_service.update(db, lead.id, LeadUpdate(productos_interes=["Balata B"]))
    assert sorted(updated.productos_interes) == ["Balata B", "Filtro A"]


def test_update_empty_productos_interes_keeps_existing(db, seed_catalogs):
    """Body vacío u omitido = sin cambios: no hay remoción de relaciones vía API."""
    make_producto(db, marca="Bosch", modelo="Filtro A", precio=100)
    lead, _, _ = lead_service.create(db, _create(productos_interes=["Filtro A"]))
    vaciado, _ = lead_service.update(db, lead.id, LeadUpdate(productos_interes=[]))
    assert vaciado.productos_interes == ["Filtro A"]
    omitido, _ = lead_service.update(db, lead.id, LeadUpdate(nombre="Otro"))
    assert omitido.productos_interes == ["Filtro A"]


def test_update_vehiculo_is_additive(db, seed_catalogs):
    """En PATCH `vehiculo` también es aditivo: combina con lo ya vinculado (no reemplaza)."""
    lead, _, _ = lead_service.create(
        db, _create(vehiculo=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}])
    )
    updated, _ = lead_service.update(
        db, lead.id, LeadUpdate(vehiculo=[{"modelo": "Aveo", "marca": "Chevrolet", "anio": 2020}])
    )
    assert sorted(v.modelo for v in updated.vehiculo) == ["aveo", "versa"]


def test_get_by_id_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        lead_service.get_by_id(db, 999999)


def test_chat_id_and_status_are_derived_after_chat_created(db, seed_catalogs):
    """`chat_id` y `status` del lead se derivan del chat activo (join), no son columnas."""
    lead, _, _ = lead_service.create(db, _create())
    chat = make_chat(db, lead_id=lead.id, chat_whatsapp_id="wa-001")
    resp = lead_service.get_by_id(db, lead.id)
    assert resp.chat_id == chat.id
    assert resp.status == chat.chat_status.status


def test_update_partial_changes_only_sent_fields(db, seed_catalogs):
    """Update parcial: solo cambian los campos enviados; los no enviados quedan intactos."""
    lead, _, _ = lead_service.create(db, _create(nombre="Original"))
    updated, _ = lead_service.update(db, lead.id, LeadUpdate(nombre="Real Name"))
    assert updated.nombre == "Real Name"
    assert updated.nombre_whatsapp == "Juan"


def test_update_refreshes_updated_at_only(db, seed_catalogs):
    """update refresca updated_at y deja created_at intacto. Se fuerzan los timestamps al pasado
    para esquivar la truncación a segundos de MySQL DATETIME, que igualaría ambos."""
    resp, _, _ = lead_service.create(db, _create())
    lead = LeadModel.get_by_id(db, resp.id)
    past = datetime(2020, 1, 1, 0, 0, 0)
    lead.created_at = past
    lead.updated_at = past
    db.flush()

    updated, _ = lead_service.update(db, lead.id, LeadUpdate(nombre="Real Name"))
    assert updated.nombre == "Real Name"
    raw = LeadModel.get_by_id(db, lead.id)
    assert raw.created_at == past
    assert raw.updated_at > past


def test_update_unknown_lead_raises_not_found(db, seed_catalogs):
    """Un id inexistente se traduce a NotFoundError (→ 404) en el service."""
    with pytest.raises(NotFoundError):
        lead_service.update(db, 999999, LeadUpdate(nombre="x"))


def test_get_by_chat_whatsapp_id_returns_single_object(db, seed_catalogs):
    a, _, _ = lead_service.create(db, _create(chat_whatsapp_id="wa-A"))
    lead_service.create(db, _create(chat_whatsapp_id="wa-B", telefono="+5213300000000"))
    resp = lead_service.get_by_chat_whatsapp_id(db, "wa-A")
    assert resp.id == a.id
    assert resp.chat_whatsapp_id == "wa-A"


def test_get_by_chat_whatsapp_id_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        lead_service.get_by_chat_whatsapp_id(db, "no-existe")


def test_create_is_idempotent_by_chat_whatsapp_id(db, seed_catalogs):
    """Idempotente: un segundo create con el mismo `chat_whatsapp_id` devuelve el lead existente
    (creado=False), sin crear uno nuevo ni borrar el anterior."""
    primero, _, creado1 = lead_service.create(db, _create(chat_whatsapp_id="wa-dup", nombre="Uno"))
    segundo, avisos2, creado2 = lead_service.create(
        db, _create(chat_whatsapp_id="wa-dup", nombre="Dos")
    )
    assert creado1 is True and creado2 is False
    assert segundo.id == primero.id
    assert segundo.nombre == "Uno"  # body ignorado: devuelve el existente tal cual
    assert avisos2 == []


def test_create_populates_relations_under_production_autoflush(db, seed_catalogs):
    """Candado de regresión del bug de 'valores vacíos'.

    Producción usa SessionLocal(autoflush=False); sin el db.flush() explícito de las filas de
    relación antes del refresh, la carga selectin de leads_productos/leads_vehiculos leería las
    tablas aún vacías y la respuesta saldría con listas vacías. El conftest usa autoflush=True
    (default), que enmascara el bug, así que aquí lo suspendemos con db.no_autoflush para reproducir
    producción. El producto se siembra FUERA del bloque para que find_productos_by_modelo lo
    encuentre; lo que se prueba es el create del lead.
    """
    make_producto(db, marca="Bosch", modelo="Filtro Z", precio=100)
    payload = _create(
        productos_interes=["Filtro Z"],
        vehiculo=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}],
    )
    with db.no_autoflush:
        resp, _, _ = lead_service.create(db, payload)

    assert resp.productos_interes == ["Filtro Z"]
    assert len(resp.vehiculo) == 1
    assert resp.vehiculo[0].modelo == "versa"
