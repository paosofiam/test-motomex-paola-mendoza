# test-motomex-paola-mendoza
Repositorio con desarrollo para prueba téncica para el puesto de Especialista en Automatización e IA de Motomex. El objetivo es  implementar un **chatbot con IA** que pueda atender clientes por WhatsApp, vender refacciones directamente, recomendar productos compatibles y cerrar ventas sin intervención humana.
## Caso de estudio
Una empresa dedicada a la venta de **refacciones automotrices** ha incrementado sus ventas durante el último año. La mayoría de sus ventas y conversaciones con clientes ocurren por **WhatsApp**. Debido al aumento en volumen, los clientes hacen cada vez más preguntas sobre productos, disponibilidad, precios y compatibilidad. Actualmente, la empresa no cuenta con toda esta información estructurada en una base de datos, sino en textos descriptivos de productos.

La dirección de la empresa quiere implementar un **chatbot con IA** que pueda atender clientes por WhatsApp, vender refacciones directamente, recomendar productos compatibles y cerrar ventas sin intervención humana.
### Objetivo
Construir una solución de automatización e IA que permita:
1. Extraer información de productos desde texto en prosa.
2. Convertir esa información en datos estructurados.
3. Almacenar el catálogo en una base de datos.
4. Exponer la información mediante una API.
5. Crear un chatbot en n8n que consulte esa API.
6. Capturar información de nuevos clientes.
7. Registrar leads para seguimiento comercial.
### Entregables
1. Workflow de n8n exportado.
2. Código o configuración de la API.
3. Base de datos o evidencia de almacenamiento.
4. Ejemplo del catálogo estructurado.
5. Evidencia de conversaciones de prueba.
6. Registro de leads generado por el chatbot.
7. Documento breve explicando la arquitectura y la elección del modelo LLM.
8. Preguntas de cierre.

## Documentación técnica

Las especificaciones del proyecto están divididas en tres documentos complementarios:

- [`contracts.md`](./contracts.md) — stack, convenciones de nomenclatura, fases de desarrollo, modelos y las **decisiones de lógica de negocio** detrás de la base de datos y los endpoints.
- [`er_diagram.md`](./er_diagram.md) — diagrama entidad-relación en Mermaid, tablas, columnas, FKs, columnas estándar, valores por defecto y seeders.
- [`endpoints.md`](./endpoints.md) — tabla de endpoints REST, tipos de recursos, formato de respuestas y errores (RFC 7807), política Tier 1/2/3 de catálogos y política find-or-create/find-or-fail.

Stack: MySQL + FastAPI + SQLAlchemy/Pydantic, consumido por un chatbot de n8n sobre WhatsApp.