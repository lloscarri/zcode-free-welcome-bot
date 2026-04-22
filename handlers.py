"""
Handlers del bot ZCode Free Welcome.

Funciones públicas:
  - Bienvenida automática a nuevos miembros del canal (con banner opcional)
  - /vip en privado → CTA al bot VIP

Panel de admin (/menu):
  - Preview del mensaje de bienvenida
  - Cambiar banner (enviar foto)
  - Cambiar texto de bienvenida
  - Cambiar texto/URL de cualquier botón
"""
import logging
from datetime import datetime

from telegram import (
    ChatMember,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.helpers import escape_markdown
from telegram.ext import ContextTypes

import config

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO MUTABLE
# ═══════════════════════════════════════════════════════════════════════════════

_state = {
    "banner_file_id": config.BANNER_FILE_ID,
    "bienvenida_texto": (
        "🔥 ¡Bienvenido {firstname} a ZCode Español!\n\n"
        "Aquí recibirás picks gratis, análisis de partidos y contenido "
        "diario de nuestro equipo.\n\n"
        "📅 Los picks salen todos los días por la mañana.\n\n"
        "📡 Guarda nuestros canales de respaldo "
        "(por si Telegram falla o te banean el acceso):"
    ),
    "botones": [
        {"text": "📱 Canal Backup Telegram",      "url": config.BACKUP_TELEGRAM_URL},
        {"text": "📢 ZCode en WhatsApp",           "url": config.WHATSAPP_CHANNEL_URL},
        {"text": "🎯 Quiero acceso VIP completo",  "url": config.VIP_BOT_URL},
    ],
}

# Rastrea qué está editando cada admin: { chat_id: "banner" | "mensaje" | "boton_1" | ... }
_editing: dict[int, str] = {}


# ─── Accesores ────────────────────────────────────────────────────────────────

def _is_admin(chat_id: int) -> bool:
    if not config.ADMIN_CHAT_ID:
        return True
    return chat_id == config.ADMIN_CHAT_ID


def _markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(b["text"], url=b["url"])]
        for b in _state["botones"]
    ])


def _texto_escapado(firstname: str) -> str:
    raw = _state["bienvenida_texto"].format(firstname=firstname)
    return escape_markdown(raw, version=2)


async def _send_bienvenida(bot, chat_id: int, firstname: str) -> None:
    texto  = _texto_escapado(firstname)
    banner = _state["banner_file_id"]
    markup = _markup()
    if banner:
        await bot.send_photo(
            chat_id=chat_id, photo=banner,
            caption=texto, parse_mode="MarkdownV2", reply_markup=markup,
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=texto, parse_mode="MarkdownV2", reply_markup=markup,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MENÚ PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def _menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👁 Preview del mensaje",    callback_data="preview")],
        [InlineKeyboardButton("🖼 Cambiar banner",         callback_data="set_banner")],
        [InlineKeyboardButton("✍️ Cambiar mensaje",        callback_data="set_mensaje")],
        [InlineKeyboardButton("🔘 Botón 1",  callback_data="set_boton_0"),
         InlineKeyboardButton("🔘 Botón 2",  callback_data="set_boton_1"),
         InlineKeyboardButton("🔘 Botón 3",  callback_data="set_boton_2")],
        [InlineKeyboardButton("❌ Cerrar",                callback_data="cerrar")],
    ])


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start — muestra el panel de admin si es el admin, CTA VIP si es usuario normal."""
    if not update.message or update.message.chat.type != "private":
        return
    chat_id = update.message.chat.id
    if _is_admin(chat_id):
        _editing.pop(chat_id, None)
        await update.message.reply_text(
            "⚙️ *Panel de administración — ZCode Free Welcome Bot*\n\nElige qué quieres hacer:",
            parse_mode="MarkdownV2",
            reply_markup=_menu_keyboard(),
        )
    else:
        await update.message.reply_text(
            "🎯 ¿Quieres acceso completo a ZCode VIP\\?\nChatea conmigo inmediatamente 👇",
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🚀 Quiero acceso VIP completo", url=config.VIP_BOT_URL)
            ]]),
        )


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/menu — abre el panel de administración."""
    if not update.message or update.message.chat.type != "private":
        return
    if not _is_admin(update.message.chat.id):
        return

    _editing.pop(update.message.chat.id, None)
    await update.message.reply_text(
        "⚙️ *Panel de administración*\n\nElige qué quieres hacer:",
        parse_mode="MarkdownV2",
        reply_markup=_menu_keyboard(),
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestiona todos los callbacks del menú inline."""
    query = update.callback_query
    if not query:
        return
    await query.answer()

    chat_id = query.message.chat.id
    if not _is_admin(chat_id):
        return

    data = query.data

    # ── Preview ───────────────────────────────────────────────────────────────
    if data == "preview":
        _editing.pop(chat_id, None)
        await query.message.reply_text("👇 Así se verá el mensaje de bienvenida:")
        await _send_bienvenida(context.bot, chat_id, "Nombre")
        banner = _state["banner_file_id"]
        info = f"🖼 Banner: `activo`" if banner else "🖼 Banner: _ninguno_"
        await query.message.reply_text(info, parse_mode="MarkdownV2", reply_markup=_menu_keyboard())

    # ── Cambiar banner ────────────────────────────────────────────────────────
    elif data == "set_banner":
        _editing[chat_id] = "banner"
        await query.message.reply_text(
            "📸 Envíame la imagen *como foto* \\(no como archivo\\)\\.\n\n"
            "Escribe /cancelar para volver al menú\\.",
            parse_mode="MarkdownV2",
        )

    # ── Cambiar mensaje ───────────────────────────────────────────────────────
    elif data == "set_mensaje":
        _editing[chat_id] = "mensaje"
        current = escape_markdown(_state["bienvenida_texto"][:300], version=2)
        await query.message.reply_text(
            f"✍️ *Escribe el nuevo texto de bienvenida*\n\n"
            f"Usa `{{firstname}}` donde quieras el nombre del usuario\\.\n\n"
            f"Texto actual:\n```\n{current}\n```\n\n"
            f"Escribe /cancelar para volver al menú\\.",
            parse_mode="MarkdownV2",
        )

    # ── Cambiar botón N ───────────────────────────────────────────────────────
    elif data.startswith("set_boton_"):
        idx = int(data.split("_")[-1])
        _editing[chat_id] = f"boton_{idx}"
        boton = _state["botones"][idx]
        t = escape_markdown(boton["text"], version=2)
        u = escape_markdown(boton["url"], version=2)
        await query.message.reply_text(
            f"🔘 *Editando Botón {idx + 1}*\n\n"
            f"Texto: {t}\nURL: `{u}`\n\n"
            f"Envíame el nuevo contenido en uno de estos formatos:\n"
            f"• Solo texto: `Nuevo texto del botón`\n"
            f"• Solo URL: `| https://nueva-url.com`\n"
            f"• Texto y URL: `Nuevo texto | https://nueva-url.com`\n\n"
            f"Escribe /cancelar para volver al menú\\.",
            parse_mode="MarkdownV2",
        )

    # ── Cerrar ────────────────────────────────────────────────────────────────
    elif data == "cerrar":
        _editing.pop(chat_id, None)
        await query.message.delete()


# ═══════════════════════════════════════════════════════════════════════════════
# RECEPCIÓN DE RESPUESTAS DEL ADMIN (texto y foto)
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or update.message.chat.type != "private":
        return
    if not _is_admin(update.message.chat.id):
        return
    _editing.pop(update.message.chat.id, None)
    await update.message.reply_text("✅ Cancelado\\.", parse_mode="MarkdownV2", reply_markup=_menu_keyboard())


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foto enviada en privado → nuevo banner (si el admin está en modo edición de banner)."""
    if not update.message or not update.message.photo:
        return
    if update.message.chat.type != "private":
        return
    chat_id = update.message.chat.id
    if not _is_admin(chat_id):
        return
    if _editing.get(chat_id) != "banner":
        return

    file_id = update.message.photo[-1].file_id
    _state["banner_file_id"] = file_id
    _editing.pop(chat_id, None)
    logger.info("Banner actualizado | file_id=%s", file_id)

    fid = escape_markdown(file_id, version=2)
    await update.message.reply_text(
        f"✅ *Banner actualizado*\n\n"
        f"⚠️ Para que persista tras un reinicio, copia este `BANNER_FILE_ID` "
        f"en Railway:\n`{fid}`",
        parse_mode="MarkdownV2",
        reply_markup=_menu_keyboard(),
    )


async def handle_texto_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Texto enviado en privado → aplica según el modo de edición activo."""
    if not update.message or not update.message.text:
        return
    if update.message.chat.type != "private":
        return
    chat_id = update.message.chat.id
    if not _is_admin(chat_id):
        return

    modo = _editing.get(chat_id)
    if not modo:
        return

    texto = update.message.text.strip()

    # ── Actualizar mensaje ────────────────────────────────────────────────────
    if modo == "mensaje":
        _state["bienvenida_texto"] = texto
        _editing.pop(chat_id, None)
        preview = escape_markdown(texto[:200], version=2)
        await update.message.reply_text(
            f"✅ *Mensaje actualizado*\n\n```\n{preview}\n```",
            parse_mode="MarkdownV2",
            reply_markup=_menu_keyboard(),
        )

    # ── Actualizar botón N ────────────────────────────────────────────────────
    elif modo.startswith("boton_"):
        idx = int(modo.split("_")[-1])
        if "|" in texto:
            parts = texto.split("|", 1)
            new_text = parts[0].strip() or None
            new_url  = parts[1].strip() or None
        else:
            new_text = texto or None
            new_url  = None

        if new_text:
            _state["botones"][idx]["text"] = new_text
        if new_url:
            _state["botones"][idx]["url"] = new_url

        _editing.pop(chat_id, None)
        boton = _state["botones"][idx]
        t = escape_markdown(boton["text"], version=2)
        u = escape_markdown(boton["url"][:60], version=2)
        logger.info("Botón %d actualizado | text=%s | url=%s", idx + 1, boton["text"], boton["url"])
        await update.message.reply_text(
            f"✅ *Botón {idx + 1} actualizado*\n\n{t}\n`{u}`",
            parse_mode="MarkdownV2",
            reply_markup=_menu_keyboard(),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# HANDLER PRINCIPAL: nuevo miembro en el canal
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = update.chat_member
    if not result or result.chat.id != config.CHANNEL_ID:
        return

    old_status = result.old_chat_member.status
    new_status  = result.new_chat_member.status
    user        = result.new_chat_member.user

    if user.is_bot:
        return

    entradas = {ChatMember.MEMBER, ChatMember.ADMINISTRATOR}
    salidas  = {ChatMember.LEFT, ChatMember.KICKED, ChatMember.BANNED, ChatMember.RESTRICTED}

    if old_status in salidas and new_status in entradas:
        firstname = user.first_name or "amigo"
        try:
            await _send_bienvenida(context.bot, config.CHANNEL_ID, firstname)
            logger.info(
                "Bienvenida enviada | user_id=%s | first_name=%s | banner=%s | ts=%s",
                user.id, firstname,
                "sí" if _state["banner_file_id"] else "no",
                datetime.utcnow().isoformat(),
            )
        except Exception as e:
            logger.error("Error enviando bienvenida a user_id=%s: %s", user.id, e)


# ═══════════════════════════════════════════════════════════════════════════════
# /vip (público)
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_vip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or update.message.chat.type != "private":
        return
    try:
        await update.message.reply_text(
            "🎯 ¿Quieres acceso completo a ZCode VIP\\?\nChatea conmigo inmediatamente 👇",
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🚀 Quiero acceso VIP completo", url=config.VIP_BOT_URL)
            ]]),
        )
    except Exception as e:
        logger.error("Error respondiendo /vip: %s", e)
