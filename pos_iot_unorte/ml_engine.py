import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from database import DB_NAME

def obtener_analitica_ia():
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT timestamp, monto FROM transacciones WHERE estado = 'APROBADO'"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty or len(df) < 10:
        return {
            "curva_horaria": {str(h): 0 for h in range(7, 21)},
            "predicciones_manana": {str(h): 0 for h in range(7, 21)},
            "alertas": ["Aún hay pocos datos para entrenar el modelo predictivo. Ejecuta seed_data.py o registra más compras."]
        }

    # 1. Limpieza y extracción de variables temporales con Pandas
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hora'] = df['timestamp'].dt.hour
    df['dia_semana'] = df['timestamp'].dt.dayofweek
    df['fecha'] = df['timestamp'].dt.date

    # Agrupar por fecha y hora para contar volumen de transacciones
    grouped = df.groupby(['fecha', 'dia_semana', 'hora']).size().reset_index(name='cantidad_compras')

    # 2. Curva de demanda horaria histórica (promedio por hora entre las 07:00 y 20:00)
    curva_promedio = grouped.groupby('hora')['cantidad_compras'].mean().round(1).to_dict()
    curva_horaria = {f"{h:02d}:00": curva_promedio.get(h, 0) for h in range(7, 21)}

    # 3. Entrenamiento del Modelo Predictivo (Scikit-Learn)
    X = grouped[['dia_semana', 'hora']]
    y = grouped['cantidad_compras']

    modelo = RandomForestRegressor(n_estimators=50, random_state=42)
    modelo.fit(X, y)

    # Predecir demanda para mañana de 07:00 a 20:00
    manana_dia_semana = (datetime.now() + timedelta(days=1)).weekday()
    horas_operativas = list(range(7, 21))
    X_pred = pd.DataFrame({'dia_semana': [manana_dia_semana]*len(horas_operativas), 'hora': horas_operativas})
    
    y_pred = modelo.predict(X_pred)
    predicciones_manana = {f"{h:02d}:00": round(float(val), 1) for h, val in zip(horas_operativas, y_pred)}

    # 4. Generación de Alertas Operativas Inteligentes
    promedio_general = np.mean(list(predicciones_manana.values()))
    hora_pico = max(predicciones_manana, key=predicciones_manana.get)
    valor_pico = predicciones_manana[hora_pico]

    alertas = []
    if promedio_general > 0:
        incremento_pct = int(((valor_pico - promedio_general) / promedio_general) * 100)
        alertas.append(
            f"🔥 Hora pico detectada a las {hora_pico} hs: Se espera un incremento del {incremento_pct}% "
            f"sobre el promedio ({valor_pico} consumos/hora); asegurar inventario y personal en caja."
        )
    
    # Detectar segunda franja alta
    horas_ordenadas = sorted(predicciones_manana.items(), key=lambda x: x[1], reverse=True)
    if len(horas_ordenadas) > 1:
        segunda_hora, segundo_val = horas_ordenadas[1]
        alertas.append(
            f"📊 Tendencia secundaria: Alta afluencia proyectada cerca de las {segunda_hora} hs ({segundo_val} compras estimadas)."
        )

    return {
        "curva_horaria": curva_horaria,
        "predicciones_manana": predicciones_manana,
        "alertas": alertas
    }