#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>
#include <LittleFS.h>
#include "time.h"

// ================= CONFIGURACIÓN WI-FI Y SERVIDOR =================
// En simuladores como Wokwi, usar SSID "Wokwi-GUEST" sin contraseña.
const char* ssid = "Wokwi-GUEST"; 
const char* password = "";

// ATENCIÓN: Un simulador online no puede ver tu "localhost" ni tu IP local (192.168.x.x).
// Para probar el envío al backend de Python desde un simulador web, debes exponer tu API
// usando herramientas como Ngrok o usar una IP pública.
String serverUrl = "https://dqnf350k-8000.brs.devtunnels.ms/api/transaccion"; 

// ================= PINES DEL ESP32-S3 (Validados) =================
#define RST_PIN 4   
#define SS_PIN  10  

MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2);

const int buzzerPin = 15;
const int ledPin = 14;

// Configuración NTP (Paraguay GMT-3)
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = -3 * 3600;
const int   daylightOffset_sec = 0;

void sonarBuzzerYLed(String tipo) {
  digitalWrite(ledPin, HIGH);
  if (tipo == "OK") {
    tone(buzzerPin, 2000, 150);
    delay(150);
  } else {
    tone(buzzerPin, 1000, 300);
    delay(300);
    tone(buzzerPin, 1000, 300);
    delay(300);
  }
  digitalWrite(ledPin, LOW);
  noTone(buzzerPin);
}

String obtenerFechaNTP() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "";
  }
  char buffer[25];
  strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &timeinfo);
  return String(buffer);
}

void guardarEnBufferOffline(String uid, int monto, String timestamp) {
  File file = LittleFS.open("/datos.txt", FILE_APPEND);
  if (file) {
    file.println(uid + "," + String(monto) + "," + timestamp);
    file.close();
    Serial.println(">>> GUARDADO OFFLINE EXITOSO EN datos.txt: " + uid);
  } else {
    Serial.println(">>> ERROR: No se pudo abrir datos.txt para escribir.");
  }
}

void sincronizarBufferOffline() {
  if (!LittleFS.exists("/datos.txt") || WiFi.status() != WL_CONNECTED) return;

  File file = LittleFS.open("/datos.txt", FILE_READ);
  if (!file) return;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Sincronizando...");
  Serial.println("\n--- INICIANDO SINCRONIZACION OFFLINE ---");

  DynamicJsonDocument doc(4096); 
  JsonArray lote = doc.to<JsonArray>();

  while (file.available()) {
    String linea = file.readStringUntil('\n');
    linea.trim();
    if (linea.length() == 0) continue;
    
    Serial.println("Linea leida de datos.txt: " + linea);

    int c1 = linea.indexOf(',');
    int c2 = linea.lastIndexOf(',');
    if (c1 == -1 || c2 == -1) {
      Serial.println("Linea ignorada por formato incorrecto.");
      continue; 
    }

    String uid = linea.substring(0, c1);
    int monto = linea.substring(c1 + 1, c2).toInt();
    String ts = linea.substring(c2 + 1);
    ts.trim();

    JsonObject tx = lote.createNestedObject();
    tx["uid"] = uid;
    tx["monto"] = monto;
    tx["categoria"] = "Comedor (Offline)";
    tx["timestamp"] = ts;
  }
  file.close();

  if (lote.size() == 0) {
    LittleFS.remove("/datos.txt");
    Serial.println("Archivo vacio o ilegible. Borrado.");
    return;
  }

  String requestBody;
  serializeJson(doc, requestBody);
  Serial.println("Payload a enviar: " + requestBody);

  HTTPClient http;
  String urlLote = serverUrl;
  urlLote.replace("transaccion", "sincronizar_buffer");

  http.begin(urlLote);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(requestBody);
  http.end();

  Serial.print("Servidor respondio con HTTP CODE: ");
  Serial.println(httpCode);

  if (httpCode == 200) {
    LittleFS.remove("/datos.txt");
    lcd.setCursor(0, 1);
    lcd.print("Buffer al dia!  ");
    Serial.println(">>> SINCRONIZACION EXITOSA. datos.txt BORRADO.");
    delay(1500);
  } else {
    lcd.setCursor(0, 1);
    lcd.print("Error: " + String(httpCode));
    Serial.println(">>> FALLO AL SINCRONIZAR. MANTENIENDO datos.txt");
    delay(2000);
  }
}

void mostrarPantallaEspera() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(" POS IoT UNINORTE");
  lcd.setCursor(0, 1);
  lcd.print("Acerque tarjeta ");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Inicializar bus SPI con los pines validados (SCK:12, MISO:13, MOSI:11, SS:10)
  SPI.begin(12, 13, 11, 10);
  rfid.PCD_Init();

  // Inicializar I2C con los pines validados (SDA:8, SCL:9)
  Wire.begin(8, 9);
  lcd.init();                      
  lcd.backlight();
  
  pinMode(buzzerPin, OUTPUT);
  pinMode(ledPin, OUTPUT);

  lcd.setCursor(0, 0);
  lcd.print("Iniciando POS...");

  // Inicializar Memoria Flash
  LittleFS.begin(true);

  // Conectar a Wi-Fi
  WiFi.begin(ssid, password);
  lcd.setCursor(0, 1);
  lcd.print("Conectando WiFi ");
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 20) {
    delay(500);
    Serial.print(".");
    intentos++;
  }
  Serial.println("");

  // Configurar Hora NTP
  if (WiFi.status() == WL_CONNECTED) {
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    sincronizarBufferOffline();
  }

  mostrarPantallaEspera();
  Serial.println("Terminal POS IoT (ESP32-S3) iniciada correctamente.");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  String uidString = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    uidString += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
    uidString += String(rfid.uid.uidByte[i], HEX);
  }
  uidString.toUpperCase();

  Serial.print("Tarjeta detectada. UID: ");
  Serial.println(uidString);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Procesando...   ");

  String fechaActual = obtenerFechaNTP();
  int montoConsumo = 15000;

  if (WiFi.status() == WL_CONNECTED) {
    sincronizarBufferOffline();

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<200> doc;
    doc["uid"] = uidString;
    doc["monto"] = montoConsumo;
    doc["categoria"] = "Comedor Universitario";
    if (fechaActual.length() > 0) doc["timestamp"] = fechaActual;

    String requestBody;
    serializeJson(doc, requestBody);

    int httpResponseCode = http.POST(requestBody);

    if (httpResponseCode == 200) {
      String response = http.getString();
      StaticJsonDocument<512> resDoc;
      deserializeJson(resDoc, response);

      String linea1 = resDoc["lcd_linea1"].as<String>();
      String linea2 = resDoc["lcd_linea2"].as<String>();
      String buzzer = resDoc["buzzer"].as<String>();

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print(linea1);
      lcd.setCursor(0, 1);
      lcd.print(linea2);
      sonarBuzzerYLed(buzzer);
    } else {
      guardarEnBufferOffline(uidString, montoConsumo, fechaActual);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Guardado Offline");
      lcd.setCursor(0, 1);
      lcd.print("-Gs.15000 (Mem) ");
      sonarBuzzerYLed("OK");
    }
    http.end();
  } else {
    guardarEnBufferOffline(uidString, montoConsumo, fechaActual);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Modo Offline    ");
    lcd.setCursor(0, 1);
    lcd.print("Guardado en Mem ");
    sonarBuzzerYLed("OK");
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  delay(2500);
  mostrarPantallaEspera();
}