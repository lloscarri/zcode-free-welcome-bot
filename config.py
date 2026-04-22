"""
Carga y validación de variables de entorno.
"""
import os
import sys


def get_required(var: str) -> str:
    value = os.environ.get(var)
    if not value:
        print(f"[ERROR] Variable de entorno requerida no encontrada: {var}", file=sys.stderr)
        sys.exit(1)
    return value


# Token del bot (obligatorio)
BOT_TOKEN = get_required("BOT_TOKEN")

# ID numérico del canal Free (obligatorio, formato: -100XXXXXXXXXX)
CHANNEL_ID = int(get_required("CHANNEL_ID"))

# URLs de destino (con defaults para no bloquear el arranque)
BACKUP_TELEGRAM_URL = os.environ.get(
    "BACKUP_TELEGRAM_URL", "https://t.me/+OcrWBke2k2ExZmMx"
)
WHATSAPP_CHANNEL_URL = os.environ.get(
    "WHATSAPP_CHANNEL_URL",
    "https://whatsapp.com/channel/0029VbC07l4EwEjsVtCH3a0D",
)
VIP_BOT_URL = os.environ.get("VIP_BOT_URL", "https://t.me/zcode_asistente_bot")

# Admin: ID numérico del admin (para /preview y /setbanner)
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))

# Banner: file_id de Telegram del banner de bienvenida (opcional)
# Si está vacío, el mensaje de bienvenida se envía sin imagen
BANNER_FILE_ID = os.environ.get("BANNER_FILE_ID", "")
