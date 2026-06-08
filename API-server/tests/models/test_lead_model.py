"""LeadModel (Tier 3): tabla ORM pura. Solo `get_by_id`; el comportamiento (search, create con
ciudad/productos_interes/vehiculo, update parcial, derivados estado/chat_id) vive en
`tests/services/test_lead_service.py`.
"""

from app.models.lead_model import LeadModel
from tests.factories import make_lead


def test_get_by_id_returns_active_or_none(db, seed_catalogs):
    lead = make_lead(db)
    assert LeadModel.get_by_id(db, lead.id).id == lead.id
    assert LeadModel.get_by_id(db, 999999) is None
