"""Capa de orquestación del recurso pre_ordenes (router → service → model) — SCAFFOLD (pendiente).

Mediará entre `routers/pre_ordenes.py` y `PreOrdenModel` (aún scaffold): recibirá los schemas
validados, verificará cada `producto_id` exacto (Tier 3, sin resolución por string) y construirá
el `PreOrdenResponse` (`total` ya en MXN centavos). Sin implementar en esta sesión.
"""
