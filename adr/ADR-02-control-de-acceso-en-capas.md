# ADR-02: Control de acceso en capas (aplicación, roles con RLS y vista para la coordinación)

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Decisores:** equipo OHTLI
- **Requerimientos relacionados:** RF-01, RF-02, RF-07, RF-12, RNF-02, RN-03, RN-05, RN-08
- **Diagramas relacionados:** D05 (secuencia), D06 (componentes), D08 (modelo físico)

## Contexto

OHTLI guarda notas de seguimiento, motivos de detección y descripciones de canalización que el Anexo D clasifica como **datos sensibles**. P2 V4 fija quién puede ver qué:

- El tutor solo ve a sus tutorados (RF-02, RN-03).
- El área de apoyo solo ve las canalizaciones dirigidas a su instancia (RF-07).
- La coordinación ve el estado y los tiempos de cada folio, pero **no** su descripción ni el número de control (RN-05).
- El criterio de RNF-02 es que el 100 % de los accesos no autorizados se denieguen (CP-17).

Hay dos dificultades. La primera es que RN-05 pide ocultar **columnas**, no solo filas, y la seguridad por filas (RLS) de PostgreSQL filtra filas. La segunda es que Django se conecta con un solo usuario de base de datos, así que la base no sabe por sí misma qué persona está actuando.

## Decisión

El acceso se controla en tres capas que se verifican por separado:

1. **Aplicación (Django).** Cada vista exige sesión iniciada y un rol permitido. Las consultas se filtran por el usuario en sesión. Un acceso denegado se registra en la bitácora (ADR-04) y devuelve «acceso denegado» (D05).
2. **Roles de base de datos con RLS.** Existen cinco roles de grupo sin inicio de sesión: `r_tutor`, `r_apoyo`, `r_jefatura`, `r_coord` y `r_admin`. Django se conecta como `ohtli_app`, que es miembro de los cinco, no es superusuario y no tiene `BYPASSRLS`. Al iniciar cada transacción, un middleware ejecuta:
   ```sql
   SET LOCAL ROLE r_tutor;                         -- según el rol del usuario en sesión
   SELECT set_config('app.id_usuario', '17', true); -- true = solo en esta transacción
   ```
   Las políticas RLS usan `current_setting('app.id_usuario')`:
   - `r_tutor` ve los tutorados, notas, sesiones y canalizaciones de sus grupos del ciclo vigente;
   - `r_apoyo` ve las canalizaciones cuya `id_instancia` coincide con la de su usuario, y su historial.
3. **Vista para la coordinación.** `r_coord` y `r_jefatura` **no tienen ningún privilegio** sobre `canalizacion`, `cambio_estado`, `nota_seguimiento` ni `sesion`. Solo pueden consultar:
   - `v_canalizacion_coordinacion`: folio, carrera, grupo, instancia, prioridad, estado, fechas y días hábiles sin cambio; sin número de control, descripción, motivo ni observaciones;
   - `v_indicadores_grupo`: los tres indicadores de RF-12.

   Las vistas pertenecen a `ohtli_owner` y se ejecutan con los privilegios de su dueño. La coordinación lee lo que la vista expone y nada más.

`r_admin` administra catálogos, usuarios y bitácora, pero no tiene acceso a notas, sesiones ni canalizaciones. El servicio de Yolia usa un rol aparte, `yolia_app`, sin privilegios en el esquema `ohtli` (ADR-05).

## Alternativas consideradas

| Alternativa | Ventajas | Desventajas | Motivo del descarte |
|---|---|---|---|
| Control solo en la aplicación | Simple; habitual en Django | Un error en una vista, una consulta nueva o un acceso directo a la base expone datos sensibles | Una sola barrera para datos sensibles no cumple el criterio del 100 % de RNF-02 con margen |
| Un usuario de base de datos por persona | La base conoce a cada usuario sin variables de sesión | Gestión de cuentas en dos lugares; incompatible con un grupo de conexiones compartido | Costo de operación desproporcionado para el instituto |
| Cifrar las columnas sensibles | Protege incluso ante una copia de la base | Gestión de llaves; impide buscar y agregar; no resuelve quién ve qué | Resuelve otro riesgo; queda como mejora posible para los respaldos |
| Esquemas separados por rol | Aislamiento fuerte | Duplica estructuras y complica las relaciones | Complejidad sin beneficio adicional frente a la vista |

## Fundamento

- **Defensa en profundidad.** Si una capa falla, la otra sigue protegiendo. Si la aplicación olvidara filtrar una consulta, RLS devolvería solo las filas permitidas. Si una pantalla de la coordinación intentara mostrar la descripción, la base respondería con un error de permisos.
- **RN-05 se cumple en la base.** Como `r_coord` no puede leer la tabla, ocultar columnas no depende de que cada pantalla las omita.
- **Sin efectos entre usuarios.** `SET LOCAL ROLE` y `set_config(..., true)` solo duran lo que dura la transacción. Con `ATOMIC_REQUESTS` activado, cada petición web es una transacción, así que el rol de un usuario no pasa a la siguiente petición aunque la conexión se reutilice.
- PostgreSQL documenta que los superusuarios, los roles con `BYPASSRLS` y el dueño de la tabla omiten RLS. Por eso `ohtli_app` no es dueño de nada ni tiene esos atributos.

## Consecuencias

- **Positivas:** las reglas de acceso de P2 quedan en el lugar donde están los datos y se pueden auditar con consultas SQL; la coordinación obtiene sus indicadores sin tocar datos sensibles.
- **Negativas o costos:** más objetos que mantener (roles, políticas y vistas); las migraciones las ejecuta `ohtli_owner`, no `ohtli_app`; los modelos de Django de la coordinación se apoyan en vistas (modelos no administrados).
- **Riesgos y mitigación:** si una petición se ejecuta fuera de transacción, el rol no se fija. Se mitiga con `ATOMIC_REQUESTS` y con políticas que niegan todo cuando `app.id_usuario` está vacío.
- **Supuesto:** SUP-04 (al área de apoyo le basta el número de control, el motivo y la descripción breve) determina qué columnas ve `r_apoyo`; si cambia, se ajustan las políticas sin cambiar la arquitectura.
- **Verificación:**
  - CP-17: matriz rol × recurso, probada dos veces, por la interfaz y con consultas SQL directas bajo cada rol;
  - CP-29 y ESC-06: la coordinación no ve descripción ni número de control;
  - CP-27 y ESC-07: un tutor no canaliza a un estudiante ajeno.

  En P4 el prototipo navegable comprueba la capa de aplicación; la capa de base de datos se declara como limitación hasta la construcción.

## Referencias

- Documentación de PostgreSQL, «Row Security Policies». https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- Documentación de PostgreSQL, «SET ROLE». https://www.postgresql.org/docs/current/sql-set-role.html
- Documentación de Django, «Database transactions» (ATOMIC_REQUESTS). https://docs.djangoproject.com/en/stable/topics/db/transactions/
