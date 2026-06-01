"""LeadModel (Tier 3): create (ciudad find-or-fail, productos_interes multi, vehiculo cascade),
update parcial, derivados estado/chat_id."""

from datetime import datetime

import pytest
from sqlalchemy import func, select

from app.core import resolvers
from app.core.exceptions import ResolutionError
from app.models.lead_model import LeadModel
from app.models.lead_producto_model import LeadProductoModel
from app.models.producto_model import ProductoModel
from tests.factories import make_chat, make_lead


def test_create_with_known_city_ok(db, seed_catalogs):
    lead = make_lead(db, ciudad="Guadalajara")
    assert lead.ciudad.ciudad == "guadalajara"


def test_create_with_unknown_city_raises(db, seed_catalogs):
    with pytest.raises(ResolutionError) as exc:
        make_lead(db, ciudad="Tijuana")
    assert exc.value.field == "ciudad"
    assert exc.value.value_received == "Tijuana"


def test_create_vehiculo_find_or_create_cascades(db, seed_catalogs):
    lead = make_lead(db, vehiculo=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}])
    assert len(lead.leads_vehiculos) == 1


def test_productos_interes_multimatch_persists_all(db, seed_catalogs):
    # Un mismo `modelo` que matchea dos productos → dos filas en leads_productos.
    ProductoModel.create(db, marca="Bosch", modelo="Balata X", precio=100)
    ProductoModel.create(db, marca="ATE", modelo="Balata X", precio=200)
    lead = make_lead(db, productos_interes=["Balata X"])
    n = db.scalar(
        select(func.count()).select_from(LeadProductoModel).where(
            LeadProductoModel.lead_id == lead.id
        )
    )
    assert n == 2


def test_update_refreshes_updated_at_only(db, seed_catalogs):
    lead = make_lead(db)
    # Forzamos timestamps al pasado para evitar la truncación a segundos de MySQL DATETIME.
    past = datetime(2020, 1, 1, 0, 0, 0)
    lead.created_at = past
    lead.updated_at = past
    db.flush()

    updated = LeadModel.update(db, lead.id, nombre="Real Name")
    assert updated.nombre == "Real Name"
    assert updated.created_at == past          # no cambia
    assert updated.updated_at > past           # se refresca


def test_update_unknown_lead_returns_none(db, seed_catalogs):
    # El modelo devuelve None; la traducción a NotFoundError (404) vive en el service.
    assert LeadModel.update(db, 999999, nombre="x") is None


def test_search_filters_by_whatsapp_and_intencion(db, seed_catalogs):
    a = make_lead(db, chat_whatsapp_id="wa-A", intencion_de_compra_id=3)  # "alta"
    make_lead(db, chat_whatsapp_id="wa-B", intencion_de_compra_id=1)      # "baja"
    by_wa = LeadModel.search(db, chat_whatsapp_id="wa-A")
    assert [l.id for l in by_wa] == [a.id]
    by_intencion = LeadModel.search(db, intencion_de_compra="alta")
    assert [l.id for l in by_intencion] == [a.id]


def test_estado_is_derived_from_city(db, seed_catalogs):
    lead = make_lead(db, ciudad="Guadalajara")
    assert lead.ciudad.estado.estado == "Jalisco"  # leads.ciudad → ciudades.estado → estados


def test_active_chat_id_resolver(db, seed_catalogs):
    lead = make_lead(db)
    assert resolvers.get_active_chat_id(db, lead.id) is None
    chat = make_chat(db, lead_id=lead.id, chat_whatsapp_id=lead.chat_whatsapp_id)
    assert resolvers.get_active_chat_id(db, lead.id) == chat.id


def test_has_no_delete_method():
    assert not hasattr(LeadModel, "delete")
