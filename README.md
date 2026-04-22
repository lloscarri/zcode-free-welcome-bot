# ZCode Free Welcome Bot

Bot de bienvenida para el canal gratuito de ZCode Español.
Reemplaza ChannelHelp con un bot propio sin publicidad de terceros.

## Setup paso a paso (Alberto hace esto)

### 1. Crear el bot en BotFather
1. Abre Telegram → busca `@BotFather`
2. `/newbot`
3. Nombre visible: `ZCode Free Welcome`
4. Username: `ZcodeFree_Welcome_bot`
5. Copia el token que te da → lo necesitas para `BOT_TOKEN`

### 2. Obtener el CHANNEL_ID del canal Free
**Opción A (recomendada):**
1. Reenvía cualquier mensaje del canal a `@userinfobot`
2. Te dará el ID del canal en formato `-100XXXXXXXXXX`

**Opción B:**
1. Agrega `@RawDataBot` al canal temporalmente
2. Publica cualquier mensaje → el bot te muestra el chat_id
3. Saca el bot

### 3. Agregar el bot al canal como admin
1. Ve al canal Free → Administradores → Agregar administrador
2. Busca `@ZcodeFree_Welcome_bot`
3. Permisos mínimos necesarios:
   - ✅ Publicar mensajes
   - ✅ Todo lo demás: OFF

### 4. Variables de entorno en Railway
En Railway → tu proyecto → nuevo servicio → Variables:

| Variable | Valor |
|----------|-------|
| `BOT_TOKEN` | Token de BotFather |
| `CHANNEL_ID` | `-100XXXXXXXXXX` (ID del canal) |
| `BACKUP_TELEGRAM_URL` | `https://t.me/+OcrWBke2k2ExZmMx` |
| `WHATSAPP_CHANNEL_URL` | `https://whatsapp.com/channel/0029VbC07l4EwEjsVtCH3a0D` |
| `VIP_BOT_URL` | `https://t.me/Bienvenido_Zcode_bot` |

### 5. Deploy en Railway
1. Railway → New Service → GitHub repo (o subir carpeta)
2. Root directory: `zcode-free-welcome-bot`
3. Railway detecta `Procfile` automáticamente → `worker: python main.py`
4. Deploy

### 6. Verificar que funciona
1. Entra al canal con una cuenta secundaria
2. Debes ver el mensaje de bienvenida con los botones
3. Escribe `/vip` en privado al bot → debe responder con el CTA

### 7. Transición (después de verificar)
1. Sacar ChannelHelp del canal Free (Admins → quitar permisos → remover)
2. Avisar a Cess que ChannelHelp sale y entra bot propio

## Logs
Cada bienvenida enviada genera un log:
```
2026-04-21 10:30:00 | INFO | handlers | Bienvenida enviada | user_id=123456 | first_name=Juan | timestamp=2026-04-21T10:30:00
```
Visibles en Railway → Deployments → Logs.
