# ADR-05: Yolia como servicio aparte, desactivado y sin acceso a los datos de OHTLI

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Decisores:** equipo OHTLI
- **Requerimientos relacionados:** RF-15, RNF-08, RN-08, RES-02
- **Diagramas relacionados:** D01 (caso «Operar módulo experimental Yolia»), D02 (interfaz MotorYolia), D06 (componentes), D07 (despliegue), D08 (esquema yolia)

## Contexto

Yolia es un sistema experto del mismo equipo, escrito en Python 3 con un motor de reglas propio sin dependencias: encadenamiento hacia adelante, factores de certeza y explicación de resultados. Su interfaz está hecha con Tkinter. Infiere un nivel de atención para el acompañamiento emocional e incluye su propio protocolo de canalización ante señales de riesgo.

En P2 V4, por la observación del asesor, Yolia dejó de ser una función central y quedó como **módulo experimental**:

- solo el administrador lo activa, en modo prueba (RF-15);
- sus resultados **nunca generan canalizaciones ni se muestran a la coordinación** (RN-08);
- debe integrarse como módulo intercambiable, con una sola interfaz de entrada y salida, sin modificar su base de conocimiento, y pasar una regresión de 6 perfiles (RNF-08);
- solo trabaja con datos sintéticos (RES-02).

Sus reglas no están validadas por especialistas. Si se integrara dentro de la aplicación, con acceso a los expedientes, RN-08 dependería de que nadie escribiera código que conecte ambos mundos.

## Decisión

Yolia se integra como un **servicio aparte**:

1. **Proceso propio.** El motor de Yolia, sin su interfaz Tkinter, se envuelve en un servicio HTTP mínimo que escucha solo en `127.0.0.1:8100`. Corre como servicio `systemd`, desactivado por omisión (D07). La elección del microframework se difiere al segundo incremento.
2. **Interfaz única `MotorYolia`** (D02): `evaluar(perfil) → resultado`, con nivel, factor de certeza (CF), reglas disparadas y explicación. El componente `cliente_yolia` de Django es el único que la usa (D06).
3. **Datos separados.** El esquema `yolia` tiene una tabla `registro` sin llaves hacia el esquema `ohtli` y con una restricción que solo admite números de control con prefijo `SIN` (D08). El servicio se conecta con el rol `yolia_app`, sin privilegios en el esquema `ohtli`. A su vez, `r_coord` y `r_jefatura` no tienen privilegios en `yolia`.
4. **Activación por parámetro.** `parametro.YOLIA_ACTIVO = falso`. Si es falso, el menú no aparece y `cliente_yolia` no hace llamadas. Solo `r_admin` puede cambiar el valor.
5. **El protocolo de canalización de Yolia** se presenta solo como parte de la explicación del resultado. Dentro de OHTLI no dispara ninguna acción.

## Alternativas consideradas

| Alternativa | Ventajas | Desventajas | Motivo del descarte |
|---|---|---|---|
| Aplicación de Django dentro del mismo proyecto | Menos procesos; despliegue más simple | Comparte la conexión y los privilegios de la aplicación; RN-08 quedaría protegido solo por convención | El riesgo que el asesor señaló exige una separación verificable |
| Importar Yolia como biblioteca en el proceso de Django | Llamada directa, sin red | El código experimental corre con los privilegios de OHTLI; un fallo del motor afecta a toda la aplicación | Mismo problema de aislamiento |
| Excluir Yolia del sistema | Máxima simplicidad | Contradice RF-15 y el objetivo OE3 de P2 | No responde a la especificación |

## Fundamento

- **RN-08 se cumple por permisos, no por disciplina.** El servicio no puede leer expedientes ni crear canalizaciones aunque se programe mal, porque su rol no tiene privilegios para hacerlo.
- **RNF-08 se verifica de forma aislada.** Los 6 perfiles de regresión se ejecutan contra el servicio sin levantar OHTLI. Desactivar el módulo no cambia ninguna otra prueba (CP-24).
- **Bajo costo.** El motor es Python puro y sin dependencias, así que se ejecuta en el servidor Linux sin cambios en su base de conocimiento. Solo se omite la interfaz Tkinter.

## Consecuencias

- **Positivas:** el módulo experimental se puede retirar, sustituir o validar sin tocar el núcleo de OHTLI; la separación es demostrable ante el área de psicología y el asesor.
- **Negativas o costos:** un proceso más que instalar y vigilar; una llamada HTTP local por evaluación (irrelevante en modo prueba).
- **Pendiente de validación:** el uso real de Yolia sigue condicionado a la validación de sus reglas por especialistas del área de psicología. Este ADR no la sustituye.
- **Alcance:** RF-15 y RNF-08 son del segundo incremento; en P4 no se implementan ni se prueban.
- **Verificación:**
  - CP-15: desactivado no aparece en ningún menú; activado, los 6 perfiles reproducen el nivel y el CF documentados;
  - CP-24: regresión aislada;
  - CP-32: con el módulo activo no se crea ninguna canalización y la coordinación no ve resultados;
  - VR-02: todos los números de control del esquema `yolia` tienen el prefijo `SIN`.
