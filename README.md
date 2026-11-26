# OHTLI · Sistema Integral de Tutoría y Acompañamiento Estudiantil

*Acompañamos tu trayectoria universitaria.*

OHTLI es un sistema de información para el **seguimiento tutorial y la canalización** de estudiantes del Instituto Tecnológico Superior de Coatzacoalcos (ITESCO). Complementa, sin sustituirlo, al Sistema de Gestión Escolar Administrativa (SIGEA): el módulo de tutoría de SIGEA tiene nueve opciones, de las cuales solo dos están desarrolladas, y no contempla el seguimiento de las canalizaciones de los tutorados hacia el área de psicología y otras áreas de apoyo.

Proyecto integrador del **Seminario de Análisis y Diseño de Sistemas**, Doctorado en Sistemas Computacionales, Universidad del Sur (UNISUR).

| | |
|---|---|
| **Equipo** | Patricia Guadalupe Gamboa Rodríguez · José Roberto Ramírez Guerrero · Luis Alberto Robles Anastasio |
| **Asesor académico** | Dr. José Alejandro Concha Uicab |
| **Estado** | P1 y P2 entregados · P3 (diseño) en versión 3 · P4 (prototipo y pruebas) en preparación |

> **Alcance.** OHTLI se entrega como **diseño** (P3) y como **prototipo navegable** (P4). No es un sistema construido ni en operación. Todos los datos del repositorio son **sintéticos** (números de control con prefijo `SIN`) y no corresponden a personas reales.

## Entregables

| Etapa | Contenido | Ubicación |
|---|---|---|
| P1 | Fundamentación y delimitación del problema | `docs/P1/` (pendiente de subir) |
| P2 | Especificación de requerimientos, versión 4: 15 RF, 9 RNF, 5 restricciones y 9 reglas de negocio | [`docs/P2/`](docs/P2/) |
| P3 | Diseño integral de la solución, en formato IEEE | [`docs/P3/`](docs/P3/) |
| P4 | Prototipo navegable y pruebas | [`prototipo/`](prototipo/), `pruebas/` (pendiente) |

## Estructura del repositorio

```
.
├── README.md
├── docs/
│   ├── P2/                    Requerimientos V4 y anexos B a E (Excel con datos sintéticos, oráculo y escenarios)
│   ├── P3/                    Documento de diseño (Word, formato IEEE)
│   └── control-de-cambios.md  Ajustes de P3 respecto a P2 V4 (CC-01 a CC-14)
├── diagramas/
│   ├── src/                   Código PlantUML (.puml) de D01 a D08b
│   └── export/                Diagramas en SVG (pendiente de subir)
├── adr/                       Registros de decisiones arquitectónicas (ADR-01 a ADR-06)
└── prototipo/                 Prototipo navegable (HTML autocontenido)
```

## Diagramas de diseño (P3)

| ID | Diagrama | Vista (modelo 4+1) |
|---|---|---|
| D01 | [Casos de uso](diagramas/src/D01_casos_de_uso.puml) | Escenarios |
| D02 | [Clases del dominio](diagramas/src/D02_clases_dominio.puml) | Lógica |
| D03 | [Máquina de estados de la canalización](diagramas/src/D03_estados_canalizacion.puml) | Lógica |
| D04 | [Actividad con carriles](diagramas/src/D04_actividad_canalizacion.puml) | Procesos |
| D05 | [Secuencia: cambio de estado](diagramas/src/D05_secuencia_cambio_estado.puml) | Procesos |
| D06 | [Componentes](diagramas/src/D06_componentes.puml) | Desarrollo |
| D07 | [Despliegue](diagramas/src/D07_despliegue.puml) | Física |
| D08 | [Modelo físico completo](diagramas/src/D08_modelo_fisico.puml) (referencia) | Física |
| D08a | [Modelo físico, parte 1: usuarios, grupos y seguimiento](diagramas/src/D08a_modelo_fisico_usuarios_seguimiento.puml) | Física |
| D08b | [Modelo físico, parte 2: canalización y auditoría](diagramas/src/D08b_modelo_fisico_canalizacion_auditoria.puml) | Física |

Los diagramas se compilan con [PlantUML](https://plantuml.com), en el servidor web o con la extensión PlantUML de VS Code (exportar a SVG).

## Decisiones arquitectónicas

Resumen en [`adr/README.md`](adr/README.md). La decisión principal (ADR-01) es construir OHTLI como **aplicación web adaptable con Django y PostgreSQL en un servidor institucional**, elegida entre seis alternativas con siete criterios ponderados (93 % del puntaje). Las reglas críticas se diseñaron para cumplirse en la base de datos además de en la aplicación: control de acceso por roles con seguridad por filas, transiciones validadas contra la tabla de estados y bitácora de solo inserción.

## Prototipo navegable

[`prototipo/index.html`](prototipo/index.html) es un modelo navegable construido a partir de D01 a D05, con los datos sintéticos del Anexo E de P2. Se abre en cualquier navegador; incluye ocho cuentas de prueba (tres tutores, dos áreas de apoyo, jefatura, coordinación y administrador) y un botón para restablecer los datos. Ver [`prototipo/README.md`](prototipo/README.md).
