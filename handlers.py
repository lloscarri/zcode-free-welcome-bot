"""
Handlers del bot ZCode Free Welcome.
- Bienvenida automática a nuevos miembros del canal
- Comando /vip en privado
"""
import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import config

logger = logging.getLogger(__name__)

# ─── Mensaje de bienvenida ───────────────────────────────────────────────────

BIENVENIDA_TEXTO = (
    "🔥 ¡Bienvenido {firstname} a ZCode Español\\!\n\n"
    "Aquí recibirás picks gratis, análisis de partidos y contenido\n"
    "diario de nuestro equipo\\.\n\n"
    "📅 Los picks salen todos los días por la mañana\\.\n\n"
    "📡 Guarda nuestros canales de respaldo\n"
    "\\(por si Telegram falla o te banean el acceso\\):"
)

def bienvenida_botones() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Canal Backup Telegram", url=config.BACKUP_TELEGRAM_URL)],
        [InlineKeyboardButton("📢 ZCode en WhatsApp",    url=config.WHATSAPP_CHANNEL_URL)],
    ])

# ─── Mensaje /vip ────────────────────────────────────────────────────────────

VIP_TEXTO = (
    "🎯 ¿Listo para probar ZCode VIP GRATIS 7 días\\?\n"
    "Habla con nuestro asistente aquí 👇"
)

def vip_botones() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Probar ZCode VIP Gratis", url=config.VIP_BOT_URL)],
    ])


# ─── Handler: nuevo miembro en el canal ─────────────────────────────────────

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Se dispara cuando alguien entra al canal.
    Funciona con message.new_chat_members (el método más fiable para canales/grupos).
    """
    message = update.message
    if not message or not message.new_chat_members:
        return

    for user in message.new_chat_members:
        # Ignorar cuando el propio bot entra
        if user.is_bot:
            continue

        firstname = user.first_name or "amigo"
        texto = BIENVENIDA_TEXTO.format(firstname=firstname)

        try:
            await context.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=texto,
                parse_mode="MarkdownV2",
                reply_markup=bienvenida_botones(),
            )
            logger.info(
                "Bienvenida enviada | user_id=%s | first_name=%s | timestamp=%s",
                user.id,
                firstname,
                datetime.utcnow().isoformat(),
            )
        except Exception as e:
            logger.error("Error enviando bienvenida a user_id=%s: %s", user.id, e)


# ─── Handler: /vip en privado ────────────────────────────────────────────────

async def handle_vip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Responde al comando /vip con CTA al bot VIP.
    Solo funciona en chat privado.
    """
    if not update.message:
        return

    # Solo en privado
    if update.message.chat.type != "private":
        return

    try:
        await update.message.reply_text(
            text=VIP_TEXTO,
            parse_mode="MarkdownV2",
            reply_markup=vip_botones(),
        )
        logger.info(
            "/vip solicitado | user_id=%s | first_name=%s",
            update.message.from_user.id if update.message.from_user else "unknown",
            update.message.from_user.first_name if update.message.from_user else "unknown",
        )
    except Exception as e:
        logger.error("Error respondiendo /vip: %s", e)
