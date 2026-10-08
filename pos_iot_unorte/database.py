import sqlite3
from datetime import datetime

DB_NAME = "robotica.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de Usuarios / Tarjetas RFID
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            uid TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            saldo INTEGER NOT NULL
        )
    ''')
    
    # Tabla de Transacciones (Telemetría de precisión)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            monto INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY (uid) REFERENCES usuarios (uid)
        )
    ''')
    
    # Insertar tarjetas de prueba (2 a 4 tarjetas según documento)
    tarjetas_iniciales = [
        ("A1B2C3D4", "Alexis Benitez", 150000),
        ("E5F6G7H8", "Carlos Alcaraz", 85000),
        ("I9J0K1L2", "Moisés Zárate", 45000),
        ("M3N4O5P6", "Cliente Prueba (Sin Saldo)", 5000)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO usuarios (uid, nombre, saldo) VALUES (?, ?, ?)
    ''', tarjetas_iniciales)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada correctamente.")