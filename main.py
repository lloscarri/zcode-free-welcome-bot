"""
ZCode Free Welcome Bot — entrypoint.
Detecta nuevos miembros en el canal Free y les da bienvenida.
"""
import logging

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

import config
from handlers import handle_new_member, handle_vip

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─── Arranque ────────────────────────────────────────────────────────────────

def main() -> None:
    logger.info("Iniciando ZCode Free Welcome Bot...")

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Nuevos miembros en el canal/grupo
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member)
    )

    # Comando /vip en privado
    app.add_handler(CommandHandler("vip", handle_vip))

    logger.info("Bot corriendo. Esperando actualizaciones (polling)...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
