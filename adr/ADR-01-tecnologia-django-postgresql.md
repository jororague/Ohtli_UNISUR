# ADR-01: Django con PostgreSQL como tecnología de construcción

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Decisores:** equipo OHTLI (José Roberto Ramírez Guerrero, Patricia Gamboa Rodríguez, Luis Alberto Robles Anastasio)
- **Requerimientos relacionados:** RF-01, RF-11, RF-14, RNF-01, RNF-02, RNF-03, RNF-07, RNF-09, RES-04
- **Diagramas relacionados:** D06 (componentes), D07 (despliegue)

## Contexto

P1 y P2 V4 plantearon OHTLI como un prototipo de escritorio: RNF-07 pide «Windows 11, Python 3 y SQLite, sin licencias de pago». La especificación de P2 V4 añadió requerimientos que esa plataforma no puede cumplir:

- Cinco roles que trabajan a la vez sobre los mismos datos (RF-01) y control de acceso de mínimo privilegio, en el que la coordinación ve el estado de cada folio, pero no su descripción (RNF-02, RN-05).
- Un área de apoyo que, según el supuesto SUP-01, consultaría su bandeja desde un teléfono (RNF-09).
- Comunicación cifrada con HTTPS en un despliegue institucional (RNF-03).
- Datos personales sensibles bajo la LGPDPPSO, que deben permanecer bajo control del instituto (RES-05).

Una aplicación de escritorio con SQLite es monousuario, no se usa desde un teléfono y no ofrece roles ni seguridad por filas. Se necesitaba elegir una plataforma web antes de diseñar componentes, despliegue y modelo físico. El equipo domina Python, JavaScript y PHP en igual medida, así que el lenguaje no inclinó la decisión.

## Decisión

OHTLI se construirá como **aplicación web adaptable con Django (Python 3) y PostgreSQL**, desplegada en un **servidor institucional Linux** con Nginx y Gunicorn (D07). Componentes principales:

- Django para la lógica, las vistas y la autenticación. El modelo de usuario es propio (`cuentas.Usuario`, tabla `usuario`) y las contraseñas se guardan con el hasher PBKDF2-SHA256 con sal de Django (RNF-01).
- El administrador de Django sirve para los catálogos y la asignación tutor-grupo (RF-14).
- PostgreSQL aporta roles, seguridad por filas (RLS), vistas, funciones y triggers (ADR-02, ADR-03 y ADR-04).
- Plantillas HTML con diseño adaptable, sin aplicación móvil nativa (RNF-09).
- Generación de PDF para el informe del tutor (RF-11) con una biblioteca libre, por ejemplo WeasyPrint.

## Alternativas consideradas

Se evaluaron seis alternativas con siete criterios ponderados aprobados por el equipo. Los pesos son: C1 datos bajo control institucional 20, C2 mínimo privilegio en el servidor 15, C3 escritorio y teléfono 15, C4 software libre 15, C5 viabilidad y mantenimiento 20, C6 integración 10, C7 adopción 5. El detalle está en el documento «Comparación de alternativas tecnológicas» y en la sección 3 de P3.

| Alternativa | Puntaje | Motivo principal del descarte |
|---|---|---|
| **Django con PostgreSQL** | **93 %** | Elegida |
| Next.js con Supabase en servidor propio | 83 % | La mejor en C2 (RLS es su mecanismo central), pero en servidor propio la configuración oficial levanta catorce servicios y el instituto queda a cargo de respaldos, seguridad y actualizaciones (C5: 2) |
| Laravel con PostgreSQL | 81 % | El acceso por rol suele aplicarse solo en la aplicación (C2: 3) y Yolia en Python obliga a integrar dos lenguajes (C6: 3) |
| Tkinter con SQLite (plataforma original de RNF-07) | 53 % | No sirve en el teléfono ni para varios usuarios a la vez; SQLite no tiene control de acceso por usuario |
| Power Apps | 53 % | Requiere licencia de pago (Power Apps Premium, por usuario al mes) y los datos residen en la nube de Microsoft |
| Flutter con Firebase | 52 % | Firebase no ofrece despliegue en servidor propio: los datos de estudiantes quedarían en la nube de Google (C1: 1) |

## Fundamento

- **Control de los datos (C1) y mínimo privilegio (C2).** PostgreSQL se instala en un servidor del instituto y ofrece roles, privilegios por columna, vistas y seguridad por filas. Con eso RN-05 y RNF-02 se cumplen también en la base, no solo en la interfaz (ADR-02).
- **Escritorio y teléfono (C3).** Una sola aplicación web adaptable atiende ambos casos. No hace falta publicar en tiendas de aplicaciones ni mantener dos clientes.
- **Software libre (C4, RES-04).** Django (BSD), PostgreSQL (licencia PostgreSQL), Nginx (BSD) y Gunicorn (MIT) no requieren licencias de pago.
- **Viabilidad y mantenimiento (C5).** Django incluye autenticación, sesiones, migraciones, protección CSRF y administrador. Son funciones que el incremento mínimo necesita y que no hay que construir desde cero.
- **Integración (C6).** Python permite reutilizar el motor de Yolia, también en Python, como servicio aparte (ADR-05) y escribir el adaptador de SIGEA en el mismo lenguaje (RES-01).

Frente al conjunto, la diferencia la deciden C1, C4 y C5: dónde viven los datos, si hay licencias y cuánto cuesta operar la solución. Frente a Next.js con Supabase, la ventaja de 10 puntos (465 frente a 415 de 500) viene sobre todo de C5. El resultado es estable: Next.js solo ganaría si el peso de C5 bajara a 3 o menos de 100, cosa que no se sostiene con un incremento mínimo de 44 horas. Si la decisión se revisa, esa es la alternativa natural.

La comparación calificó a Django con 4 en C2 porque suponía que la regla de acceso principal viviría en la aplicación. El ADR-02 añade la capa de base de datos (roles, RLS y vista), así que el diseño final cubre C2 mejor de lo que se calificó. La calificación no se modifica para no alterar la comparación aprobada.

## Consecuencias

- **Positivas:** una sola base de código para todos los roles; cumplimiento de RNF-02 y RN-05 en dos capas; plataforma libre y conocida en el ámbito académico.
- **Negativas o costos:** requiere un servidor institucional y a alguien que lo administre (sistema operativo, respaldos, certificados TLS). Ese recurso no está confirmado: el servidor es un **supuesto de diseño** de D07.
- **Riesgos y mitigación:** el equipo no ha construido antes con Django. Se mitiga con un incremento mínimo acotado (44 h, Tabla X de P2) y con el uso de funciones incluidas en el framework en lugar de código propio.
- **Efecto sobre los requerimientos:** RNF-07 debe modificarse (ADR-06).
- **Alcance:** el prototipo navegable de P4 modela las pantallas y las reglas, pero no está construido con Django. Las pruebas de P4 validan el comportamiento especificado, no esta tecnología.
- **Verificación:** revisión de diseño en P3 (inventario de licencias, VR-04) y, en la construcción futura, CP-16 (hash con sal), CP-17 (matriz rol × recurso), CP-18 (HTTPS) y CP-23 (360 px).

## Referencias

- Equipo OHTLI, «OHTLI · P3 · Comparación de alternativas tecnológicas», 24 nov. 2026 (matriz de calificación y fuentes de cada criterio).
- Documentación de Django, «Password management in Django». https://docs.djangoproject.com/en/stable/topics/auth/passwords/
- Documentación de PostgreSQL, «Row Security Policies». https://www.postgresql.org/docs/current/ddl-rowsecurity.html
