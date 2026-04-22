"""
ZCode Free Welcome Bot — entrypoint.
Detecta nuevos miembros en el canal Free y les da bienvenida.
Panel de admin accesible vía /menu en chat privado.
"""
import logging

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

import config
from handlers import (
    handle_chat_member,
    handle_vip,
    handle_start,
    handle_menu,
    handle_callback,
    handle_cancelar,
    handle_photo,
    handle_texto_admin,
)

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─── Arranque ─────────────────────────────────────────────────────────────────

def main() -> None:
    logger.info("Iniciando ZCode Free Welcome Bot...")
    if config.BANNER_FILE_ID:
        logger.info("Banner inicial: %s…", config.BANNER_FILE_ID[:30])
    else:
        logger.info("Sin banner — bienvenida solo con texto.")

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # ── Eventos del canal ─────────────────────────────────────────────────────
    app.add_handler(ChatMemberHandler(handle_chat_member, ChatMemberHandler.CHAT_MEMBER))

    # ── Comandos públicos ─────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("vip",   handle_vip))

    # ── Panel de admin ────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("menu",     handle_menu))
    app.add_handler(CommandHandler("cancelar", handle_cancelar))
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Foto y texto en privado (para responder a los modos de edición)
    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE, handle_photo
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_texto_admin
    ))

    logger.info("Bot corriendo. Canal: %s | Admin: %s",
                config.CHANNEL_ID, config.ADMIN_CHAT_ID or "no configurado")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["chat_member", "message", "callback_query"],
    )


if __name__ == "__main__":
    main()
