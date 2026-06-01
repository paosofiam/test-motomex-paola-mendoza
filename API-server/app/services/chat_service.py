"""Capa de orquestación del recurso chats (router → service → model) — SCAFFOLD (pendiente).

Mediará entre `routers/chats.py` y `ChatModel` (aún scaffold): recibirá los schemas validados,
aplicará la regla de un chat activo por lead (soft-delete del previo al crear) y construirá el
`ChatResponse` (incluido el `status` Tier 1 derivado). Sin implementar en esta sesión.
"""
