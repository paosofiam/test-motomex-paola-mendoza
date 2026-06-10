"""Tipos de query param opcionales que tratan la cadena vacía como ausencia de filtro.

El consumidor de la API es un agente LLM (el chatbot de n8n) que cablea los filtros opcionales con
`$fromAI(...)`. n8n **envía el parámetro aunque el modelo lo deje vacío** (`GET /productos?vehiculo_anio=`),
y no ofrece omitir un query param vacío. Sin esto, un `int | None = Query(None)` recibe `""` *presente*
y Pydantic intenta parsearlo como entero → `422 int_parsing`, en vez de tratar el filtro como omitido
(que es la intención: marca+modelo sin año es una consulta válida).

`BeforeValidator` colapsa `""`/espacios a `None` ANTES de la validación de tipo, de modo que un filtro
vacío equivale a no enviarlo. Un valor no vacío realmente inválido (`vehiculo_anio=abc`) sigue dando
`422`: no se enmascara input malo, solo la cadena vacía. Reutilizable por cualquier router cuyo
consumidor sea el agente.
"""

from datetime import datetime
from typing import Annotated

from pydantic import BeforeValidator


def _vacio_a_none(valor: object) -> object:
    """Colapsa la cadena vacía o de solo espacios a `None` (filtro ausente); deja pasar lo demás."""
    if isinstance(valor, str) and valor.strip() == "":
        return None
    return valor


OptInt = Annotated[int | None, BeforeValidator(_vacio_a_none)]
OptStr = Annotated[str | None, BeforeValidator(_vacio_a_none)]
OptDatetime = Annotated[datetime | None, BeforeValidator(_vacio_a_none)]
