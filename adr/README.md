# Registros de decisiones arquitectónicas (ADR) · OHTLI

Este directorio documenta las decisiones arquitectónicas principales del diseño de OHTLI (entregable P3). Cada registro sigue el formato propuesto por Nygard [1] y la estructura que pide la Actividad 3: **contexto, decisión, alternativas, fundamento y consecuencias**. Se añaden el estado, la fecha y los requerimientos de P2 V4 a los que responde, para mantener la trazabilidad.

Un ADR aceptado no se edita: si la decisión cambia, se escribe un ADR nuevo que lo sustituye y se actualiza el campo «Estado» del anterior.

| ADR | Decisión | Requerimientos | Diagramas | Estado |
|---|---|---|---|---|
| [ADR-01](ADR-01-tecnologia-django-postgresql.md) | Django con PostgreSQL, aplicación web adaptable en servidor institucional | RNF-02, RNF-03, RNF-07, RNF-09, RES-04 | D06, D07 | Aceptada |
| [ADR-02](ADR-02-control-de-acceso-en-capas.md) | Control de acceso en capas: aplicación, roles de base de datos con RLS y vista para la coordinación | RF-01, RNF-02, RN-03, RN-05 | D05, D06, D08 | Aceptada |
| [ADR-03](ADR-03-transiciones-validadas-en-la-base.md) | Transiciones de la canalización validadas en la base contra la Tabla VI | RF-06, RF-07, RN-03, RN-04, RN-09 | D03, D05, D08 | Aceptada |
| [ADR-04](ADR-04-bitacora-solo-insercion.md) | Bitácora de solo inserción: triggers para cambios y registro de accesos desde la aplicación | RF-13, RNF-02 | D05, D06, D08 | Aceptada |
| [ADR-05](ADR-05-yolia-desacoplado.md) | Yolia como servicio aparte, desactivado, sin acceso a los datos de OHTLI | RF-15, RNF-08, RN-08, RES-02 | D01, D06, D07, D08 | Aceptada |
| [ADR-06](ADR-06-cambio-rnf-07.md) | Cambio de RNF-07: de Windows 11 con SQLite a Django con PostgreSQL en servidor institucional | RNF-07, RES-04 | D07 | Aceptada |

Plantilla para nuevos registros: [plantilla.md](plantilla.md).

**Alcance.** OHTLI se entrega en P3 como diseño y en P4 como prototipo navegable. Estas decisiones rigen la construcción futura; el prototipo modela las mismas responsabilidades, pero no las implementa con esta tecnología. Lo que solo una construcción real demuestra (hash con sal, HTTPS, RLS, rendimiento) se declara como limitación en P3 y P4.

## Referencia

[1] M. Nygard, «Documenting architecture decisions», *Cognitect Blog*, 15 nov. 2011. [En línea]. Disponible: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
