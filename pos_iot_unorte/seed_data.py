import sqlite3
import random
from datetime import datetime, timedelta
from database import init_db, DB_NAME

def poblar_datos_historicos():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    uids = ["A1B2C3D4", "E5F6G7H8", "I9J0K1L2"]
    ahora = datetime.now()

    registros = []
    # Simular los últimos 7 días de consumo
    for dias_atras in range(7, 0, -1):
        fecha_base = ahora - timedelta(days=dias_atras)
        for hora in range(7, 21):
            # Simular pico fuerte entre las 12:00 y 13:00 (almuerzo) y a las 18:00 (recreo noche)
            if hora in [12, 13]:
                cantidad = random.randint(12, 20)
            elif hora in [18, 19]:
                cantidad = random.randint(8, 14)
            else:
                cantidad = random.randint(1, 5)

            for _ in range(cantidad):
                minuto = random.randint(0, 59)
                segundo = random.randint(0, 59)
                ts = fecha_base.replace(hour=hora, minute=minuto, second=segundo).strftime("%Y-%m-%d %H:%M:%S")
                uid = random.choice(uids)
                registros.append((uid, 15000, "Comedor Universitario", ts, "APROBADO"))

    cursor.executemany(
        "INSERT INTO transacciones (uid, monto, categoria, timestamp, estado) VALUES (?, ?, ?, ?, ?)",
        registros
    )
    conn.commit()
    conn.close()
    print(f"¡Se insertaron {len(registros)} transacciones históricas para entrenar la IA!")

if __name__ == "__main__":
    poblar_datos_historicos()