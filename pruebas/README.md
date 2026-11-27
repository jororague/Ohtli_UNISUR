# Pruebas del prototipo (P4)

Validación del prototipo navegable de OHTLI frente a los criterios de aceptación de P2 versión 4 (Anexo C) y los criterios de evaluación independiente de P2 (sección III-E). Los resultados esperados vienen del Anexo E de P2 (Tablas E1 a E3), calculados antes de construir el prototipo.

## Contenido

| Archivo | Qué es |
|---|---|
| `OHTLI_P4_Protocolo_pruebas_v1.docx` | Protocolo: 32 pruebas en 5 bloques, con pasos y resultado esperado |
| `OHTLI_P4_Registro_pruebas_v2.xlsx` | Registro de ejecución: resultado observado en v0.1 y en la regresión sobre v0.2, incidencias y matriz de acceso |
| `e2e_ohtli.py` | Script de pruebas automatizadas de interfaz (Python con Playwright) |
| `evidencias/automatizadas/corrida_v0.1/` | Capturas y `resultados.json` de la corrida sobre v0.1 |
| `evidencias/automatizadas/regresion_v0.2/` | Capturas y `resultados.json` de la regresión sobre v0.2 |
| `evidencias/manuales/` | Pruebas manuales independientes de Luis Robles (teléfono) y Patricia Gamboa (laptop) |
| `evidencias/revision_previa/` | Revisión de la lógica del dominio hecha el 26/11/2026 con apoyo de ChatGPT, sin usar la interfaz |

## Cómo se ejecutó

Por la suspensión de clases del 26/11/2026, el protocolo no pudo ejecutarse completo de forma manual. Se ejecutó en tres niveles, cada uno con su responsable real:

1. **Automatizada de interfaz.** `e2e_ohtli.py` abre el prototipo en Chrome sin pantalla, ejecuta los pasos del protocolo como lo haría una persona y guarda capturas. Lo escribió el equipo de desarrollo con apoyo de IA generativa (Claude, de Anthropic); no es independiente de quien implementó.
2. **Manual independiente.** Luis Alberto Robles Anastasio (teléfono Xiaomi Redmi Note 15 Pro 5G, Chrome Mobile 158) y Patricia Guadalupe Gamboa Rodríguez (laptop Lenovo, Chrome), que no implementaron el prototipo.
3. **Revisión documental** de P3 V3 y los diagramas (bloque E).

## Resultados

| | v0.1 | v0.2 (regresión) |
|---|---|---|
| Pruebas automatizadas que pasan | 26 de 28 | 28 de 28 |
| Incidencias | INC-01 (TR-10), INC-02 (B-04) | Corregidas |

D-01 (tiempos de RNF-05) requiere cronometrar a personas y queda pendiente.

## Reproducir

```bash
pip install playwright && python -m playwright install chromium
python e2e_ohtli.py ../prototipo/index.html salida v0.2
```

El script usa `/usr/bin/google-chrome`; para usar el Chromium de Playwright, quite el argumento `executable_path` en la última sección. Cada bloque abre un contexto nuevo del navegador, lo que equivale a «Restablecer datos sintéticos».
