# ADR-04: Bitácora de solo inserción con triggers para cambios y registro de accesos desde la aplicación

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Decisores:** equipo OHTLI
- **Requerimientos relacionados:** RF-13, RNF-02, RN-05, RES-05
- **Diagramas relacionados:** D01 (caso «Registrar en bitácora»), D05 (secuencia), D06 (componentes), D08 (modelo físico)

## Contexto

RF-13 pide registrar en bitácora **todo acceso al expediente** y **todo cambio** en notas, sesiones y canalizaciones. Su criterio de aceptación es que el 100 % de las operaciones del escenario de prueba aparezcan con usuario, fecha, acción y registro afectado. La responsabilidad en el tratamiento de datos personales (EV-08) exige además que la bitácora no pueda alterarse: una bitácora que se puede editar no prueba nada.

Hay una limitación técnica: los triggers de PostgreSQL se disparan con `INSERT`, `UPDATE`, `DELETE` y `TRUNCATE`, pero **no con `SELECT`**. Ningún mecanismo dentro de la base registra por sí solo las lecturas del expediente, y RF-13 sí las pide.

## Decisión

Una sola tabla `bitacora` (D08), con dos vías de escritura y protección contra modificaciones:

1. **Cambios: triggers.** Un trigger `AFTER INSERT OR UPDATE OR DELETE` en `nota_seguimiento`, `sesion`, `sesion_asistente`, `canalizacion` y `cambio_estado` inserta en `bitacora` el usuario (`app.id_usuario`), el rol de base de datos, la acción, la entidad y el identificador del registro. La función del trigger es `SECURITY DEFINER`, así que los roles de la aplicación no necesitan privilegios de escritura directa.
2. **Accesos: aplicación.** Al abrir el expediente de un tutorado, el detalle de un folio o la bandeja, la vista de Django inserta un registro con la acción «consulta». La consulta y su registro van en la misma transacción. Los accesos denegados se registran con `resultado = 'denegado'` (D05).
3. **Inmutabilidad:**
   - `REVOKE UPDATE, DELETE, TRUNCATE ON bitacora` para todos los roles;
   - los roles de la aplicación solo tienen `INSERT`, y solo `r_admin` tiene `SELECT` (D01: el administrador consulta la bitácora);
   - un trigger `BEFORE UPDATE OR DELETE` rechaza cualquier intento, incluso del dueño de la tabla.
4. **Minimización.** La bitácora guarda **qué** se tocó (entidad e identificador), no el contenido. No copia descripciones, notas ni observaciones, para no duplicar datos sensibles.

## Alternativas consideradas

| Alternativa | Ventajas | Desventajas | Motivo del descarte |
|---|---|---|---|
| Solo en la aplicación (señales de Django o middleware) | Un solo lugar; registra lecturas y cambios | Las actualizaciones masivas, el SQL directo y los scripts no disparan señales; un error en una vista omite el registro | Deja cambios sin registrar; RF-13 pide el 100 % |
| Solo triggers | Imposible de omitir para los cambios | No registra lecturas | No cumple la mitad de RF-13 |
| Extensión pgAudit | Estándar para auditoría en PostgreSQL; registra también lecturas | Escribe en el log del servidor, no en una tabla que el administrador consulte desde OHTLI; mucho ruido; no conoce al usuario de la aplicación | Útil para el área de sistemas como complemento, no para RF-13 dentro del sistema |
| Archivos de registro | Simples | Se pueden editar o borrar en el servidor; difíciles de consultar por registro | No garantizan inmutabilidad |

## Fundamento

- Cada vía cubre lo que la otra no puede: los triggers garantizan los cambios sin importar su origen y la aplicación cubre las lecturas, que solo ella ve.
- La identidad del usuario llega a los triggers por la variable `app.id_usuario` que fija el middleware (ADR-02). Es el mismo mecanismo de RLS, sin infraestructura adicional.
- La inmutabilidad se apoya en privilegios y en un trigger, no en una convención.

## Consecuencias

- **Positivas:** bitácora consultable desde el sistema, a prueba de omisiones en los cambios y sin datos sensibles copiados.
- **Negativas o costos:** el registro de lecturas depende de que cada vista lo haga. Se mitiga con un decorador común para las vistas de expediente y de folio, y con CP-13, que cuenta los registros esperados del escenario.
- **Crecimiento:** la tabla solo crece. El plazo de conservación debe definirse en la evaluación de impacto que exige RES-05 antes de cualquier uso real. Mientras tanto no se borra nada.
- **Verificación:**
  - CP-13: el 100 % de las operaciones del escenario aparecen en la bitácora;
  - ESC-02: el historial completo;
  - prueba negativa: `UPDATE` y `DELETE` sobre la bitácora son rechazados para todos los roles.

  En P4 el prototipo navegable registra las operaciones en su bitácora simulada; la inmutabilidad en la base se declara como limitación hasta la construcción.

## Referencias

- Documentación de PostgreSQL, «Overview of Trigger Behavior» (eventos que disparan un trigger). https://www.postgresql.org/docs/current/trigger-definition.html
- Proyecto pgAudit. https://www.pgaudit.org/
