"""Paquete de seeders de Motomex.

`catalog_defaults` siembra los valores OBLIGATORIOS y EXACTOS (ids fijos) de los catálogos
Tier 1 estáticos (monedas, intenciones_de_compra_de_leads, chat_statuses). `estados` siembra
las 32 entidades federativas de México (Tier 1, ids fijos). `sample_data` siembra datos de
ejemplo deterministas (mínimos) para el resto de tablas. `run_all` los orquesta en orden
FK-safe e imprime conteos.
"""
