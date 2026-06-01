"""lead_service: orquestación de /leads (router → service → model).

Invariantes que vive el service: armado del DTO con campos derivados (`chat_id` vía
`resolvers.get_active_chat_id`, `estado` por `ciudad → estados`, `intencion_de_compra` string,
vehículos como objetos), `NotFoundError` (→ 404) en `get_by_id`/`update` y propagación del
`ResolutionError` (→ 422) de la ciudad find-or-fail. Llamadas directas con `Session`.

Nota: `intencion_de_compra_id` NO se valida en el service (zona gris documentada en los tests de
endpoints: un id inexistente provoca IntegrityError → 500, no un 404 limpio) → no se cubre aquí.
"""

import pytest

from app.core.exceptions import NotFoundError, ResolutionError
from app.schemas.lead import LeadCreate, LeadUpdate
from app.services import lead_service
from tests.factories import make_chat


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
    resp = lead_service.create(db, _create(ciudad="Guadalajara"))
    assert resp.ciudad == "guadalajara"               # Tier 2 normalizado
    assert resp.estado == "Jalisco"                   # derivado: ciudad → estados
    assert isinstance(resp.intencion_de_compra, str) and resp.intencion_de_compra
    assert resp.chat_id is None                        # sin chat activo aún


def test_create_vehiculo_travels_as_object(db, seed_catalogs):
    resp = lead_service.create(db, _create(vehiculo=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}]))
    assert [v.model_dump() for v in resp.vehiculo] == [
        {"modelo": "versa", "marca": "nissan", "anio": 2015}
    ]


def test_create_unknown_city_raises_resolution_error(db, seed_catalogs):
    with pytest.raises(ResolutionError) as exc:
        lead_service.create(db, _create(ciudad="Tijuana"))
    assert exc.value.field == "ciudad"
    assert exc.value.value_received == "Tijuana"


def test_get_by_id_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        lead_service.get_by_id(db, 999999)


def test_chat_id_is_derived_after_chat_created(db, seed_catalogs):
    lead = lead_service.create(db, _create())
    chat = make_chat(db, lead_id=lead.id, chat_whatsapp_id="wa-001")
    assert lead_service.get_by_id(db, lead.id).chat_id == chat.id


def test_update_partial_changes_only_sent_fields(db, seed_catalogs):
    lead = lead_service.create(db, _create(nombre="Original"))
    updated = lead_service.update(db, lead.id, LeadUpdate(nombre="Real Name"))
    assert updated.nombre == "Real Name"
    assert updated.nombre_whatsapp == "Juan"           # no enviado → intacto


def test_update_unknown_lead_raises_not_found(db, seed_catalogs):
    # El modelo devuelve None; el service lo traduce a NotFoundError (→ 404).
    with pytest.raises(NotFoundError):
        lead_service.update(db, 999999, LeadUpdate(nombre="x"))


def test_search_filters_by_chat_whatsapp_id(db, seed_catalogs):
    a = lead_service.create(db, _create(chat_whatsapp_id="wa-A"))
    lead_service.create(db, _create(chat_whatsapp_id="wa-B", telefono="+5213300000000"))
    res = lead_service.search(db, chat_whatsapp_id="wa-A")
    assert [l.id for l in res] == [a.id]


def test_create_populates_relations_under_production_autoflush(db, seed_catalogs):
    """Candado de regresión del bug de 'valores vacíos'.

    Producción usa SessionLocal(autoflush=False); sin el db.flush() explícito de LeadModel.create,
    la carga selectin de leads_productos/leads_vehiculos leería las tablas de relación aún vacías y la
    respuesta saldría con listas vacías. El conftest usa autoflush=True (default), que enmascara el
    bug, así que aquí lo suspendemos puntualmente con db.no_autoflush para reproducir producción.
    """
    from app.models.producto_model import ProductoModel

    # El producto se siembra FUERA del bloque no_autoflush para que find_productos_by_modelo_or_fail
    # lo encuentre; lo que se prueba es el create del lead, no el seeding.
    ProductoModel.create(db, marca="Bosch", modelo="Filtro Z", precio=100)
    payload = _create(
        productos_interes=["Filtro Z"],
        vehiculo=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}],
    )
    with db.no_autoflush:
        resp = lead_service.create(db, payload)

    assert resp.productos_interes == ["Filtro Z"]   # no vacío: el fix las persistió antes del refresh
    assert len(resp.vehiculo) == 1
    assert resp.vehiculo[0].modelo == "versa"
