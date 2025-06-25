import os
import time
import requests
from datetime import datetime
from itertools import product
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Cargar variables de entorno
load_dotenv()

# Configuración general
ORIGENES = ["EZE", "SCL"]
DESTINOS = [
    "FRA", "MUC", "TXL", "BER",  # Alemania
    "CDG", "ORY",               # Francia
    "ATH",                      # Grecia
    "MAD", "BCN",               # España
    "FCO", "MXP", "VCE",        # Italia
    "LIS", "OPO",               # Portugal
    "OSL"                       # Noruega
]

# Clasificación de precios
EXTREMADAMENTE_BARATO = 200
MUY_BARATO = 300
UMBRAL = 400

# Fecha actual
MES_ACTUAL = datetime.today().strftime("%Y-%m")

# Env vars
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_selenium_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    if "AWS_EXECUTION_ENV" in os.environ:
        # AWS Lambda environment
        options.binary_location = "/opt/headless-chromium"
        service = Service("/opt/chromedriver")
    else:
        # Local environment
        chromedriver_path = (".lib\chromedriver.exe")
        service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=options)
    return driver


def clasificar_precio(precio):
    if precio < EXTREMADAMENTE_BARATO:
        return "🚨 *Extremadamente barato*"
    elif precio < MUY_BARATO:
        return "🔥 *Muy barato*"
    else:
        return "💰 *Barato*"


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    try:
        r = requests.post(url, data=payload)
        r.raise_for_status()
        print("✅ Mensaje enviado por Telegram")
    except Exception as e:
        print(f"❌ Error al enviar Telegram: {e}")

def buscar_vuelo(origen, destino):
    url = f"https://www.flylevel.com/Flight/Select?culture=es-ES&triptype=OW&o1={origen}&d1={destino}&dd1={MES_ACTUAL}&ADT=1&CHD=0&INL=0&r=false&mm=true&forcedCurrency=EUR&forcedCulture=es-ES&newecom=true&currency=USD"
    print(f"🔍 Revisando {origen} -> {destino}")
    
    driver = None
    try:
        driver = get_selenium_driver()
        driver.get(url)
        time.sleep(5)
        print(driver)
        # Buscar todas las fechas con precios
        dias = driver.find_elements(By.CLASS_NAME, "cal-day")

        for dia in dias:
            try:
                num_dia = dia.find_element(By.CLASS_NAME, "cal-day-num").text
                precio_str = dia.find_element(By.CLASS_NAME, "cal-day-price").text

                # Limpieza del texto
                precio = int(precio_str.replace(".", "").replace(",", "").replace("€", "").strip())
                fecha_completa = f"{MES_ACTUAL}-{int(num_dia):02d}"

                if precio < UMBRAL:
                    tipo = clasificar_precio(precio)
                    mensaje = (
                        f"{tipo}\n\n"
                        f"🛫 Ruta: {origen} → {destino}\n"
                        f"📅 Fecha: {fecha_completa}\n"
                        f"💶 Precio: {precio}€\n"
                        f"🔗 Link: {url}"
                    )
                    enviar_telegram(mensaje)
            except Exception as e:
                print(f"❌ Error al parsear día: {e}")

    except Exception as e:
        print(f"❌ Error con Selenium: {e}")
    finally:
        if driver:
            driver.quit()


def main(event, context):
    print("🚀 Monitor de vuelos iniciado...")
    for origen, destino in product(ORIGENES, DESTINOS):
        buscar_vuelo(origen, destino)


if __name__ == "__main__":
    main(None, None)
