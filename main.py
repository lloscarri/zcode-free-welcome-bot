"""
ZCode Free Welcome Bot — entrypoint.
Detecta nuevos miembros en el canal Free y les da bienvenida.
"""
import logging

from telegram.ext import ApplicationBuilder, ChatMemberHandler, CommandHandler

import config
from handlers import handle_chat_member, handle_vip

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─── Arranque ────────────────────────────────────────────────────────────────

def main() -> None:
    logger.info("Iniciando ZCode Free Welcome Bot...")

    app = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .build()
    )

    # Detectar cambios de membresía en el canal (join/leave)
    # ChatMemberHandler.CHAT_MEMBER = updates del canal donde el bot es admin
    app.add_handler(ChatMemberHandler(handle_chat_member, ChatMemberHandler.CHAT_MEMBER))

    # Comando /vip en privado
    app.add_handler(CommandHandler("vip", handle_vip))

    logger.info("Bot corriendo. Canal ID: %s", config.CHANNEL_ID)
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["chat_member", "message"],  # solo los eventos que necesitamos
    )


if __name__ == "__main__":
    main()
