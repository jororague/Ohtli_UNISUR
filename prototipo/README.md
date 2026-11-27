# Prototipo navegable OHTLI (v0.2)

`index.html` es un archivo autocontenido: se abre directamente en el navegador, sin instalar nada. Solo carga las tipografías desde Google Fonts; sin conexión se muestran las tipografías del sistema.

## Qué es y qué no es

- **Es** un modelo navegable que materializa los diagramas D01 a D05 de P3: casos de uso, clases, máquina de estados (Tabla VI de P2), actividad y secuencia del cambio de estado.
- **No es** el sistema construido. No usa Django ni PostgreSQL; valida el **comportamiento** especificado (estados, permisos, conteos y alertas), no la tecnología. Lo que solo una construcción real demuestra (hash de contraseñas, HTTPS, seguridad por filas, rendimiento y exportación a PDF) se declara como limitación en P3 y P4.

## Datos

Datos sintéticos del Anexo E de P2 V4 (semilla 20261118): 3 tutores, 120 tutorados con prefijo `SIN`, 27 sesiones, 15 canalizaciones y 42 cambios de estado. Fecha simulada: 18 de noviembre de 2026. El botón **Restablecer datos sintéticos** devuelve el prototipo a ese estado antes de cada corrida de pruebas.

## Cuentas de prueba

| Cuenta | Rol |
|---|---|
| T01, T02, T03 | Tutor (grupos ISC 1A, IIND 1B, IGE 1C) |
| APOYO-PSI | Área de apoyo: Psicología |
| APOYO-DA | Área de apoyo: Desarrollo Académico |
| JEF_CARRERA | Jefatura de carrera |
| COORD | Coordinación de tutoría |
| ADMIN | Administrador |

## Versiones

| Versión | Archivo | Cambios |
|---|---|---|
| v0.1 | `versiones/OHTLI_prototipo_v0.1.html` (etiqueta `v0.1-pruebas`) | Versión entregada con P3 y probada en P4 |
| v0.2 | `index.html` | INC-01: la observación es obligatoria en cada cambio de estado (RF-06, CP-06). INC-02: el informe del tutor lista cada sesión con su número de asistentes (RF-11, CP-04) |

## Pruebas

Los escenarios ESC-01 a ESC-09 del Anexo E aparecen en la pantalla de inicio. El protocolo, el registro de ejecución, el script de pruebas automatizadas y las evidencias de P4 están en [`../pruebas`](../pruebas/README.md). Cada pantalla muestra el requerimiento y el incremento al que pertenece (pantallas PT-01 a PT-17 en P3).
