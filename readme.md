# 💳 Terminal IoT Inteligente de Punto de Consumo (POS) + IA Predictiva

![ESP32-S3](https://img.shields.io/badge/Hardware-ESP32--S3-E7352C?style=for-the-badge&logo=espressif&logoColor=white)
![Python](https://img.shields.io/badge/Backend-FastAPI_%7C_Flask-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/IA-Scikit--Learn_%7C_Pandas-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Database](https://img.shields.io/badge/DB-PostgreSQL_%7C_SQLite-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Frontend](https://img.shields.io/badge/Web-Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)

> **Proyecto de Robótica / IoT** — Ingeniería Informática  
> **Universidad del Norte (UniNorte)**  
> **Autores:** Alexis Benítez · Carlos Alcaraz · Moisés Zárate

---

## Descripción del Proyecto

Prototipo de **terminal IoT inteligente** para puntos de cobro o consumo rápido, diseñado para comedores universitarios, autoservicios y tiendas de conveniencia en estaciones de servicio. 

El sistema permite registrar transacciones al instante acercando una tarjeta o llavero **RFID/NFC**. El microcontrolador **ESP32-S3** valida al usuario, sincroniza la operación con marca de tiempo exacta (**NTP**) y transmite los datos a un servidor central, donde un motor de **Inteligencia Artificial** analiza los patrones de consumo para predecir picos de demanda, horas de mayor afluencia y optimizar suministros o turnos de personal.

---

## Metodología Design Thinking (IDEO)

Para asegurar que la solución técnica responda a necesidades operativas y humanas reales, el proyecto fue diseñado aplicando las **5 fases del Design Thinking**:

### 1. Empatizar 
Analizamos los dos perfiles principales que interactúan con el sistema en el día a día:
* **El Consumidor (Estudiante / Cliente):** Sufre filas lentas en horarios pico, incertidumbre sobre su saldo disponible y demoras en el cobro tradicional. Necesita una transacción sin fricción y confirmación inmediata.
* **El Administrador del Local:** Planifica el inventario y los turnos de atención basándose en la intuición, lo que genera quiebres de stock en horas clave o personal ocioso en horas bajas.
* **El Entorno Técnico:** Los puntos de cobro suelen sufrir microcortes de Wi-Fi. Un sistema que dependa 100% de conexión continua detiene la fila ante cualquier caída de red.

### 2. Definir 
Sintetizamos los hallazgos en dos declaraciones de punto de vista (*Point of View*):
* **POV Usuario:** *"Un cliente con pocos minutos disponibles necesita registrar su consumo en menos de 2 segundos con confirmación visual y auditiva clara, sin depender de procesos manuales lentos."*
* **POV Negocio:** *"El gestor operativo necesita transformar registros aislados de ventas en predicciones accionables de demanda horaria para anticipar compras de insumos y asignar personal eficientemente."*
* **Retos clave (*How Might We?*):**
  * ¿Cómo agilizar el cobro físico y dar *feedback* instantáneo al usuario?
  * ¿Cómo garantizar **cero pérdida de ventas** si se cae la conexión Wi-Fi del local?
  * ¿Cómo convertir marcas de tiempo (*timestamps*) en recomendaciones operativas automáticas?

### 3. Idear 
A partir de los retos definidos, diseñamos la propuesta tecnológica:
* **Cobro sin contacto y multisensorial:** Uso de lector **RFID RC522** acompañado de un **Buzzer/LED** y una **pantalla LCD 16x2 I2C** para confirmar al instante (`"Consumo Aprobado - Gs. 15.000"` / `"Saldo Restante: OK"`).
* **Resiliencia con Buffer Offline:** Elección del **ESP32-S3** (dual-core y mayor memoria flash) para almacenar cobros localmente si cae el Wi-Fi y sincronizarlos automáticamente vía `HTTP POST/JSON` al recuperar la red, sin bloquear la lectura en vivo.
* **Telemetría de precisión (NTP):** Sincronización de fecha, hora, minutos y segundos por red para alimentar series temporales exactas.
* **Analítica Predictiva:** Plataforma web con modelos de **Machine Learning (Scikit-Learn)** para proyectar curvas de demanda y emitir alertas (ej. *"Se espera un incremento del 40% de compras entre las 12:00 y 13:30; asegurar inventario"*).

### 4. Prototipar 
El desarrollo se estructuró en tres capas de validación rápida:
1. **Esquemático Virtual:** Diseño y validación de pines en **Wokwi / Fritzing**.
2. **Prototipo Físico (Hardware):** Montaje en protoboard integrando el **ESP32-S3**, lector **RC522**, pantalla **LCD 16x2 I2C**, buzzer pasivo y tarjetas RFID de prueba.
3. **Prototipo de Software e IA:** API REST en **Python (Flask/FastAPI)** con base de datos **SQLite/PostgreSQL**, panel web interactivo con **Chart.js** y entrenamiento inicial del modelo con series temporales de prueba.

### 5. Testear
* **Pruebas de Usabilidad (POS):** Evaluación de velocidad de lectura RFID, legibilidad de saldos en pantalla LCD y claridad de la alerta sonora en entornos ruidosos.
* **Pruebas de Contingencia (Modo Offline):** Simulación de corte de red Wi-Fi durante ráfagas de cobro para verificar el encolamiento en memoria flash y la posterior sincronización íntegra hacia el backend.
* **Validación del Modelo Predictivo:** Simulación de jornadas de consumo para contrastar la precisión de los mapas de calor y las proyecciones de demanda frente a los datos reales.

---

## Resumen de Fases y Entregables

| Fase | Objetivo en el Proyecto | Entregable / Evidencia |
| :--- | :--- | :--- |
| **Etapa 1. Empatizar** | Identificar cuellos de botella en cobros rápidos y gestión de stock. | Arquetipos de usuario (Cliente y Administrador) y relevamiento de contexto. |
| **Etapa 2. Definir** | Establecer requerimientos de velocidad, resiliencia offline y analítica. | Definición del problema (POV), alcance y requerimientos funcionales. |
| **Etapa 3. Idear** | Diseñar la arquitectura IoT + Backend + Machine Learning. | Arquitectura con ESP32-S3, NTP, Buffer Flash, API REST y Scikit-Learn. |
| **Etapa 4. Prototipar** | Construir el circuito físico, la API y el dashboard predictivo. | Diseño en Wokwi/Fritzing, montaje en protoboard y plataforma web funcional. |
| **Etapa 5. Testear** | Validar cobros en vivo, tolerancia a fallos de red y predicciones IA. | Pruebas de estrés offline, simulación de demanda y demostración en vivo. |

---


## Flujo de Funcionamiento

1. **Espera activa:** La terminal aguarda la aproximación de una credencial RFID.
2. **Lectura y Sello Temporal:** El usuario acerca su tarjeta; el `ESP32-S3` captura el UID y le asigna el *timestamp* exacto vía **NTP**.
3. **Despacho / Contingencia:** Se envía la transacción por Wi-Fi (`HTTP POST/JSON`). Si no hay red, se guarda en el buffer local hasta reconectar.
4. **Respuesta Instantánea:** El backend procesa el descuento y el LCD muestra `"Consumo Aprobado - Gs. 15.000"` junto con una señal auditiva del buzzer.
5. **Visualización y Predicción:** El panel web actualiza las métricas en tiempo real y el motor de IA recalcula las proyecciones de afluencia e inventario.
