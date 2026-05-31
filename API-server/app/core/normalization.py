"""Normalización determinista para catálogos Tier 2 (marcas, categorias, ciudades, vehiculos).

Esta función es la fuente ÚNICA de normalización: debe usarse de forma IDÉNTICA al
sembrar (los seeders almacenan el valor ya normalizado) y al resolver find-or-create /
find-or-fail. Garantiza que el UNIQUE natural a nivel BD tenga sentido y que el lookup
sea determinista (`lowercase + trim + sin acentos`, colapsando espacios internos).
"""

from unidecode import unidecode


def normalize(value: str) -> str:
    """lowercase + trim + sin acentos + espacios internos colapsados."""
    if value is None:
        return value
    sin_acentos = unidecode(value)
    return " ".join(sin_acentos.split()).lower()
