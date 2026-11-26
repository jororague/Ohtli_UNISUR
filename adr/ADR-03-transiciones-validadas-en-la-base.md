# ADR-03: Transiciones de la canalización validadas en la base contra la Tabla VI

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Decisores:** equipo OHTLI
- **Requerimientos relacionados:** RF-05, RF-06, RF-07, RF-08, RN-03, RN-04, RN-09
- **Diagramas relacionados:** D03 (máquina de estados), D04 (actividad), D05 (secuencia), D08 (modelo físico)

## Contexto

El ciclo de estados de la canalización es el núcleo de OHTLI: convierte la obligación normativa de dar seguimiento en transiciones registrables (P2 V4, VII-A). RF-06 pide tres cosas: que solo se permitan las transiciones de la Tabla VI, que cada cambio guarde usuario, fecha y observación, y que una transición no permitida se rechace. Además:

- cada transición tiene un actor autorizado: el área de apoyo de destino, el tutor o la jefatura (Tabla VI, RN-03);
- cerrar desde «Registrada» o «No asistió» exige motivo (RN-04);
- «No asistió» no cierra el caso por sí sola (RN-09);
- las 3 transiciones de «Escalada» pertenecen al segundo incremento, y en P4 no se implementan ni se prueban.

Validar solo en la aplicación deja abierta la posibilidad de un cambio de estado por otra vía, como una consulta directa, un script de carga o un error en una vista. El historial dejaría entonces de ser fiable como evidencia de seguimiento.

## Decisión

La Tabla VI se guarda como datos y la base valida cada transición:

1. **Tabla `transicion_permitida`** (estado de origen, estado de destino, rol requerido, si requiere observación, incremento, si está activa). Tiene las 11 filas de la Tabla VI: las 8 del incremento mínimo están activas y las 3 de «Escalada», inactivas. `requiere_observacion` es verdadero en Registrada → Cerrada y No asistió → Cerrada (motivo de cierre, RN-04), y en En atención → Atendida (resultado general, RF-07).
2. **Función `fn_cambiar_estado(folio, destino, observacion)`**, definida con `SECURITY DEFINER` y `search_path` fijo. En una sola transacción:
   - bloquea la canalización (`SELECT … FOR UPDATE`);
   - comprueba que el trío (estado actual, destino, rol en sesión) exista y esté activo;
   - comprueba el ámbito: el área de apoyo solo actúa sobre folios de su instancia y el tutor solo sobre los suyos;
   - exige la observación cuando corresponde;
   - actualiza el estado e inserta el registro en `cambio_estado`. La bitácora la escribe el trigger de ADR-04.

   Si algo no se cumple, lanza una excepción con el estado actual y nada se guarda.
3. **Función `fn_registrar_canalizacion(...)`.** Exige que el tutorado pertenezca a un grupo del tutor en el ciclo vigente (RN-03) y que se haya registrado si el estudiante fue informado (RN-09). Asigna el folio `CAN-AAAA-NNNN` con `folio_contador` e inserta el primer cambio (sin origen → Registrada).
4. **Ningún rol de la aplicación tiene `INSERT` ni `UPDATE` directo** sobre `canalizacion` ni sobre `cambio_estado`; solo `EXECUTE` sobre las dos funciones.
5. **Trigger `BEFORE UPDATE` de defensa** sobre `canalizacion`. Rechaza cualquier cambio de estado que no venga de `fn_cambiar_estado`. La función marca la transacción con una variable local que el trigger verifica.

## Alternativas consideradas

| Alternativa | Ventajas | Desventajas | Motivo del descarte |
|---|---|---|---|
| Validar solo en la aplicación (máquina de estados en Python) | Fácil de probar con pruebas unitarias; mensajes de error claros | Cualquier vía que no pase por la aplicación puede romper el ciclo | El historial es la evidencia del seguimiento (RF-06, RF-13); necesita una garantía más fuerte |
| Restricción `CHECK` | Declarativa | No puede comparar el valor nuevo con el anterior | Técnicamente insuficiente |
| Solo un trigger, sin función | Intercepta cualquier `UPDATE` | El trigger no recibe la observación ni puede escribir el historial completo de forma natural | Se conserva como defensa, no como mecanismo principal |
| Transiciones escritas en el código del trigger | Menos tablas | Cambiar la Tabla VI exigiría cambiar código | Contradice los supuestos SUP-02 y SUP-03, que pueden cambiar la tabla |

## Fundamento

- **Una sola fuente de verdad.** La Tabla VI de P2, D03 y la tabla `transicion_permitida` contienen exactamente las mismas filas, así que la trazabilidad es directa.
- **La operación es atómica,** como exige D05: el estado, el historial y la bitácora se guardan todos o ninguno.
- **Preparada para cambiar.** Si SUP-03 no se confirma y el cierre pasa al área de apoyo, basta cambiar el rol de dos filas. Si SUP-02 reduce el ciclo, se desactivan filas. Activar el escalamiento en el segundo incremento (RF-08) es cambiar `activa` de tres filas, sin código nuevo.
- La aplicación conserva una validación previa para mostrar las acciones posibles en la pantalla, pero la decisión final la toma la base.

## Consecuencias

- **Positivas:** el historial de cada folio es fiable por construcción; las pruebas de transiciones se pueden ejecutar directamente en SQL; el escalamiento queda especificado sin activarse.
- **Negativas o costos:** parte de la lógica vive en PL/pgSQL, lo que exige probar en dos lugares; las funciones `SECURITY DEFINER` requieren `search_path` fijo para no ser vulnerables.
- **Carga de datos sintéticos:** el historial del Anexo E (incluidos dos folios ya en «Escalada») lo carga `ohtli_owner` sin pasar por la función, porque reproduce hechos ya ocurridos. Se documenta en el script de carga.
- **Verificación:**
  - ESC-03 y CP-06: Registrada → Atendida es rechazada y no se registra cambio;
  - ESC-04 y CP-28: no se puede cerrar desde Recibida sin motivo;
  - ESC-05 y CP-33: «No asistió» deja el caso abierto;
  - ESC-02: los 42 cambios sin huecos.

  En P4 se comprueban en el prototipo navegable; la validación en la base se declara como limitación hasta la construcción.

## Referencias

- Documentación de PostgreSQL, «CREATE FUNCTION» (sección «Writing SECURITY DEFINER Functions Safely»). https://www.postgresql.org/docs/current/sql-createfunction.html
- Documentación de PostgreSQL, «Triggers». https://www.postgresql.org/docs/current/triggers.html
