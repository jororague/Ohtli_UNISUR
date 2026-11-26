# Control de cambios de P3 respecto a P2 V4

P2 versión 4 se entrega sin modificaciones. Los ajustes siguientes surgieron al contrastar el diseño (P3) con los requerimientos y rigen a partir de P3. Ninguno cambia el alcance ni la prioridad aprobados en P2. Corresponden a la Tabla I del documento de P3.

| ID | Elemento de P2 | Cambio en P3 y motivo |
|---|---|---|
| CC-01 | RNF-07 | Se cambia de Windows 11 con Python 3 y SQLite a Python 3, Django y PostgreSQL en servidor institucional Linux, solo software libre. SQLite no tiene roles ni RLS y no admite uso concurrente ni desde teléfono ([ADR-06](../adr/ADR-06-cambio-rnf-07.md)). |
| CC-02 | Tabla VIII, RNF-09 | La Tabla VIII indica prioridad «Alta»; el Anexo B, el Excel y la sección VIII-F indican «Media», segundo incremento. Rige «Media». |
| CC-03 | Tabla VIII, RNF-06 | La síntesis dice 5000 registros; se rige por el texto del Anexo B: 500 tutorados y 5000 registros. |
| CC-04 | Anexo D, folio | Texto(12) → `varchar(13)`: «CAN-AAAA-NNNN» tiene 13 caracteres. |
| CC-05 | Anexo D, Usuario | Se añade `id_instancia`, obligatorio si el rol es apoyo, para que cada área vea solo sus canalizaciones (RF-07, RNF-02). |
| CC-06 | Anexo D, Usuario | Se añade `clave_carrera`, obligatoria para la jefatura de carrera (RF-08, segundo incremento). |
| CC-07 | Anexo D, Grupo | Se añaden clave y carrera del grupo, que exigen RF-02 y los indicadores por grupo de RF-12. |
| CC-08 | Anexo D | Entidad nueva `Notificacion`, que exige RF-09. |
| CC-09 | Anexo D, Tutorado | La pertenencia a un grupo se registra por ciclo (tabla `tutorado_grupo`, llave número de control y ciclo), que implementa RN-02 sin perder la historia. |
| CC-10 | Anexo D, `Sesion` | La lista de asistentes pasa a la tabla intermedia `sesion_asistente`. |
| CC-11 | RN-04 y RF-07 | El motivo de cierre y el resultado general se guardan en la observación del cambio de estado, obligatoria en esas transiciones. |
| CC-12 | Anexo D | Tablas de soporte: `carrera`, `ciclo`, `motivo_deteccion` (RF-14), `parametro`, `dia_inhabil` (RN-07), `folio_contador` (RF-05) y `transicion_permitida` (RF-06). |
| CC-13 | Anexo E | El usuario genérico denominado `APOYO` del historial sintético se asigna a la cuenta de Psicología o de Desarrollo Académico según la instancia del folio. |
| CC-14 | RN-07 | Definición operativa de día hábil: lunes a viernes posteriores al último cambio, hasta la fecha de corte inclusive, sin días inhábiles registrados. Reproduce el oráculo del Anexo E. |
