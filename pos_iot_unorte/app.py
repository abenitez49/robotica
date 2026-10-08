from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from datetime import datetime

from database import init_db, DB_NAME
from ml_engine import obtener_analitica_ia

app = FastAPI(title="Terminal IoT RFID - UNorte")
templates = Jinja2Templates(directory="templates")

# Inicializar BD al arrancar
init_db()

# Contrato de datos JSON que envía el ESP32-S3
class TransaccionInput(BaseModel):
    uid: str
    monto: int = 15000  # Por defecto Gs. 15.000 como en el documento
    categoria: str = "Comedor Universitario"
    timestamp: Optional[str] = None  # Fecha NTP enviada por el ESP32-S3 (YYYY-MM-DD HH:MM:SS)

@app.post("/api/transaccion")
def registrar_consumo(tx: TransaccionInput):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Si el ESP32 envía hora NTP la usamos; si no, usamos la del servidor
    fecha_tx = tx.timestamp if tx.timestamp else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uid_clean = tx.uid.strip().upper()

    cursor.execute("SELECT nombre, saldo FROM usuarios WHERE uid = ?", (uid_clean,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.execute(
            "INSERT INTO transacciones (uid, monto, categoria, timestamp, estado) VALUES (?, ?, ?, ?, ?)",
            (uid_clean, tx.monto, tx.categoria, fecha_tx, "TARJETA_NO_REGISTRADA")
        )
        conn.commit()
        conn.close()
        return {
            "aprobado": False,
            "lcd_linea1": "Tarjeta Invalida",
            "lcd_linea2": "No registrada",
            "buzzer": "ERROR"
        }

    nombre, saldo_actual = usuario

    if saldo_actual < tx.monto:
        cursor.execute(
            "INSERT INTO transacciones (uid, monto, categoria, timestamp, estado) VALUES (?, ?, ?, ?, ?)",
            (uid_clean, tx.monto, tx.categoria, fecha_tx, "SALDO_INSUFICIENTE")
        )
        conn.commit()
        conn.close()
        return {
            "aprobado": False,
            "lcd_linea1": "Saldo Insufic.",
            "lcd_linea2": f"Disp: Gs.{saldo_actual}",
            "buzzer": "ERROR"
        }

    # Descontar consumo y guardar transacción
    nuevo_saldo = saldo_actual - tx.monto
    cursor.execute("UPDATE usuarios SET saldo = ? WHERE uid = ?", (nuevo_saldo, uid_clean))
    cursor.execute(
        "INSERT INTO transacciones (uid, monto, categoria, timestamp, estado) VALUES (?, ?, ?, ?, ?)",
        (uid_clean, tx.monto, tx.categoria, fecha_tx, "APROBADO")
    )
    conn.commit()
    conn.close()

    # Respuesta diseñada exactamente para los 16 caracteres del LCD 16x2
    return {
        "aprobado": True,
        "usuario": nombre,
        "monto_cobrado": tx.monto,
        "saldo_restante": nuevo_saldo,
        "lcd_linea1": "Consumo Aprobado",
        "lcd_linea2": f"-Gs.{tx.monto} OK",
        "buzzer": "OK"
    }

# Endpoint para sincronizar el Buffer Offline del ESP32-S3 en lote
@app.post("/api/sincronizar_buffer")
def sincronizar_buffer(lote: List[TransaccionInput]):
    resultados = [registrar_consumo(tx) for tx in lote]
    return {"sincronizados": len(resultados), "detalles": resultados}

# Endpoint de datos para actualizar el Dashboard Web en vivo
@app.get("/api/dashboard_data")
def dashboard_data():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Última transacción (Para la Vista de Terminal)
    cursor.execute('''
        SELECT t.*, u.nombre, u.saldo 
        FROM transacciones t 
        LEFT JOIN usuarios u ON t.uid = u.uid 
        ORDER BY t.id DESC LIMIT 1
    ''')
    ultima = cursor.fetchone()

    # Historial reciente (Para la Vista Administrativa)
    cursor.execute('''
        SELECT t.*, u.nombre 
        FROM transacciones t 
        LEFT JOIN usuarios u ON t.uid = u.uid 
        ORDER BY t.timestamp DESC LIMIT 30
    ''')
    historial = [dict(row) for row in cursor.fetchall()]

    # Lista de tarjetas y saldos
    cursor.execute("SELECT * FROM usuarios")
    usuarios = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Analítica con IA
    ia_data = obtener_analitica_ia()

    return {
        "ultima_transaccion": dict(ultima) if ultima else None,
        "historial": historial,
        "usuarios": usuarios,
        "ia": ia_data
    }

from pathlib import Path

@app.get("/", response_class=HTMLResponse)
def home():
    ruta_html = Path("templates/index.html")
    if not ruta_html.exists():
        return """
        <h3>⚠️ No se encontró el archivo <code>templates/index.html</code></h3>
        <p>Verifica que la carpeta se llame exactamente <b>templates</b> y que el archivo no se haya guardado como <i>index.html.txt</i>.</p>
        """
    return HTMLResponse(content=ruta_html.read_text(encoding="utf-8"))