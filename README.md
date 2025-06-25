# ✈️ Fly Monitor

Fly Monitor es un sistema automatizado para la detección y notificación de vuelos baratos desde Sudamérica hacia Europa. Utiliza AWS Lambda y Serverless Framework para ejecutar búsquedas periódicas y enviar alertas por Telegram y correo electrónico cuando se detectan precios por debajo de un umbral configurable.

## Características principales

- **Búsqueda automática de vuelos**: Consulta rutas predefinidas entre orígenes y destinos europeos cada 30 minutos.
- **Alertas inteligentes**: Clasifica los precios encontrados y envía notificaciones solo si el precio es menor al umbral configurado.
- **Notificaciones por Telegram y Email**: Envía alertas a un chat de Telegram y a una casilla de correo.
- **Configuración por variables de entorno**: Las credenciales y parámetros sensibles se gestionan mediante variables de entorno y archivos `.env`.
- **Despliegue serverless**: Utiliza AWS Lambda y Serverless Framework para un despliegue sencillo y escalable.
- **Pruning automático de versiones**: Mantiene el entorno limpio eliminando versiones antiguas de la función Lambda.

## Estructura del proyecto

```
fly-monitor/
├── fly_monitor.py         # Lógica principal de scraping y notificación
├── handler.py            # (No usado, puede eliminarse si no es necesario)
├── serverless.yml        # Configuración de Serverless Framework
├── .env                  # Variables de entorno (no versionado)
├── README.md             # Este archivo
└── .github/workflows/
    └── deploy.yml        # CI/CD para despliegue automático
```

## ¿Cómo funciona?

1. **Búsqueda de vuelos**: Cada 30 minutos, la función Lambda ejecuta combinaciones de rutas entre los orígenes y destinos definidos en el código (`fly_monitor.py`).
2. **Scraping**: Utiliza `requests` y `BeautifulSoup` para extraer precios desde la web de LEVEL.
3. **Clasificación y alerta**: Si el precio es menor al umbral, clasifica el nivel de oferta y envía una alerta por Telegram y correo electrónico.
4. **Evita duplicados**: No repite alertas para el mismo vuelo y precio.

## Configuración

### Variables de entorno
Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_chat_id
EMAIL_SENDER=tu_email@gmail.com
EMAIL_PASSWORD=tu_password
EMAIL_RECEIVER=destinatario@gmail.com
```

### Dependencias

- Python 3.13
- requests
- beautifulsoup4
- python-dotenv

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

> **Nota:** El despliegue en AWS Lambda utiliza `serverless-python-requirements` para empaquetar las dependencias.

## Despliegue

1. Instala Serverless Framework:
   ```bash
   npm install -g serverless@^3.38.0
   ```
2. Configura tus credenciales de AWS.
3. Despliega con:
   ```bash
   serverless deploy --stage main
   ```

El workflow de GitHub Actions (`.github/workflows/deploy.yml`) permite despliegue automático al hacer push en la rama `main`.

## Personalización

- Modifica los orígenes, destinos, fecha y umbrales en `fly_monitor.py` según tus necesidades.
- Puedes agregar más métodos de notificación o ajustar la lógica de scraping según la web objetivo.

## Seguridad
- No subas tu archivo `.env` ni credenciales al repositorio.
- Usa variables de entorno y secrets en GitHub Actions para el despliegue.

## Licencia

MIT

---

> Desarrollado para monitorear oportunidades de vuelos baratos de manera automática y eficiente.
