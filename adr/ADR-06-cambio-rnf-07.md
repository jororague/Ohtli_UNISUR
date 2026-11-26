# ADR-06: Cambio de RNF-07 (plataforma de ejecución)

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Decisores:** equipo OHTLI
- **Requerimientos relacionados:** RNF-07 (se modifica), RES-04, RNF-02, RNF-03, RNF-09; casos CP-22 y VR-04
- **Diagramas relacionados:** D07 (despliegue)
- **Documentos afectados:** P2 V4 (Tabla VIII y Anexo B), Anexos B y C del Excel. P2 V4 no se reabre: el cambio se registra en el control de cambios de P3.

## Contexto

RNF-07, en P2 V4, dice: «El prototipo debe ejecutarse en Windows 11 con Python 3 y SQLite, sin licencias de pago». Prioridad alta. Fuente: EV-09. Justificación: factibilidad técnica y económica declarada en P1. Criterio: instalación limpia siguiendo el manual en un equipo del equipo de trabajo (CP-22).

El requerimiento venía de una etapa en que OHTLI se concebía como herramienta de escritorio de un solo usuario, cercana a la forma en que se construyó Yolia. La especificación posterior de P2 V4 lo dejó en conflicto con otros requerimientos:

- RNF-02 y RN-05 exigen mínimo privilegio entre cinco roles que comparten datos; SQLite no tiene roles ni seguridad por filas.
- RNF-09 y el supuesto SUP-01 plantean que el área de apoyo use un teléfono; una aplicación de escritorio en Windows no lo permite.
- RNF-03 exige HTTPS en un despliegue institucional, lo que supone un servidor.
- RF-07 y RF-09 requieren que tutor y área de apoyo trabajen a la vez sobre la misma canalización; SQLite admite un solo escritor a la vez y no está pensado para uso concurrente en red.

La comparación de alternativas de P3 y el ADR-01 eligieron Django con PostgreSQL. RNF-07 debe actualizarse para que requerimientos y diseño no se contradigan.

## Decisión

RNF-07 se reformula así:

> **RNF-07 (P3).** El sistema debe construirse con Python 3, Django y PostgreSQL y desplegarse en un servidor institucional Linux, usando únicamente software libre, sin licencias de pago.
> **Criterio de aceptación:** instalación limpia en un servidor de prueba Linux siguiendo el manual de instalación; el inventario de componentes (VR-04) no contiene software con licencia de pago.

Se conservan la prioridad (alta), la fuente (EV-09) y la relación con RES-04. Cambian la plataforma y el criterio de aceptación (CP-22).

## Alternativas consideradas

| Alternativa | Ventajas | Desventajas | Motivo del descarte |
|---|---|---|---|
| Mantener RNF-07 sin cambios | P2 V4 queda intacto | El diseño de P3 contradiría un requerimiento de prioridad alta; RNF-02, RNF-03 y RNF-09 no podrían cumplirse | Inconsistencia entre requerimientos y diseño, que la Actividad 3 pide revisar (instrucción 9) |
| Mantener Python 3 y SQLite, pero en un servidor web | Cambio menor en la redacción | SQLite sigue sin roles ni RLS y con un solo escritor | Resuelve solo RNF-09 |
| Eliminar RNF-07 | Simplicidad | Se pierde la restricción de software libre y de factibilidad económica | RES-04 y la factibilidad de P1 siguen vigentes |

## Fundamento

- La intención original de RNF-07 (ejecutable con recursos del equipo y del instituto, sin costo de licencias) se conserva; solo cambia la plataforma concreta.
- Es una modificación de requerimiento que nace de la revisión cruzada del diseño frente a los requerimientos. Se documenta en lugar de esconderse, y queda con su origen y su efecto (P2 → P3).
- Inventario de componentes y sus licencias (VR-04):

| Componente | Licencia |
|---|---|
| Python 3 | PSF License |
| Django | BSD de 3 cláusulas |
| PostgreSQL | PostgreSQL License |
| Nginx | BSD de 2 cláusulas |
| Gunicorn | MIT |
| Distribución Linux del servidor (supuesto) | Software libre (GPL y otras) |

Las licencias deben confirmarse con la versión exacta que se instale y anotarse en el manual de instalación.

## Consecuencias

- **Positivas:** requerimientos y diseño quedan consistentes; la decisión tecnológica tiene respaldo en P2 y en P3.
- **Negativas o costos:** el criterio de aceptación pasa a exigir un servidor Linux de prueba. Para P4, que se valida con el prototipo navegable, CP-22 se verifica solo como revisión de diseño (VR-04 y el manual de instalación previsto). La instalación real se declara como limitación.
- **Trazabilidad:** la matriz de P3 sustituye el texto de RNF-07 y conserva su identificador, para no romper las referencias de P2 (CP-22 y Anexo C).
- **Verificación:** VR-04 (inventario sin licencias de pago) en P3; CP-22 (instalación limpia) en la construcción futura.
