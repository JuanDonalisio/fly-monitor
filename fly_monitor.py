import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from itertools import product


# Cargar variables de entorno
load_dotenv()

# Configuración general
ORIGENES = ["EZE", "SCL"]
DESTINOS = [
    "FRA", "MUC", "TXL", "BER",     # Alemania
    "CDG", "ORY",                   # Francia
    "ATH",                         # Grecia
    "MAD", "BCN",                  # España
    "FCO", "MXP", "VCE",           # Italia
    "LIS", "OPO",                  # Portugal
    "OSL"                          # Noruega
]

FECHA = "2025-12-01"
UMBRAL = 400

# Clasificación de precios
EXTREMADAMENTE_BARATO = 200
MUY_BARATO = 300

# Credenciales Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Credenciales Email
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Guardar alertas ya enviadas
enviadas = set()

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    try:
        r = requests.post(url, data=payload)
        r.raise_for_status()
        print("✅ Mensaje enviado por Telegram")
    except Exception as e:
        print(f"❌ Error al enviar Telegram: {e}")


def enviar_email(mensaje):
    msg = MIMEText(mensaje)
    msg["Subject"] = "✈️ Alerta de vuelo barato"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📧 Email enviado correctamente")
    except Exception as e:
        print(f"❌ Error al enviar Email: {e}")


def clasificar_precio(precio):
    if precio < EXTREMADAMENTE_BARATO:
        return "🚨 *Extremadamente barato*"
    elif precio < MUY_BARATO:
        return "🔥 *Muy barato*"
    else:
        return "💰 *Barato*"


def buscar_vuelo(origen, destino):
    url = f"https://www.flylevel.com/es/vuelos?origin={origen}&destination={destino}&departureDate={FECHA}"
    headers = {"User-Agent": "Mozilla/5.0"}

    print(f"🔍 Revisando {origen} -> {destino} para {FECHA}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error al consultar {origen}->{destino}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    precios = soup.find_all(string=lambda text: text and "€" in text)

    for precio_str in precios:
        try:
            precio = int(precio_str.replace("€", "").replace(".", "").strip())

            # Para evitar repetir alertas
            key = f"{origen}-{destino}-{precio}"
            if key in enviadas:
                continue
            if precio < UMBRAL:
                tipo = clasificar_precio(precio)
                mensaje = (
                    f"{tipo}\n\n"
                    f"🛫 Ruta: {origen} → {destino}\n"
                    f"📅 Fecha: {FECHA}\n"
                    f"💶 Precio: {precio}€\n"
                    f"🔗 Link: {url}"
                )
                enviar_telegram(mensaje)
                enviar_email(mensaje)
                enviadas.add(key)
        except ValueError:
            continue


def main(event, context):
    print("🚀 Monitor de vuelos iniciado...")
    for origen, destino in product(ORIGENES, DESTINOS):
        buscar_vuelo(origen, destino)
