import os
import # Versión 2 - Webhook para Render
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- CONFIGURACIÓN ---
# El token se leerá desde las variables de entorno de Render
TOKEN = os.environ.get("TOKEN")

alertas_activas = False

def obtener_todas_las_ofertas():
    return [
        "🎺 Trompetista profesional para banda de Jazz - Remoto",
        "🎸 Guitarrista para banda de rock - Bogotá",
        "🎵 Profesor de Guitarra - Escuela de Música (Remoto)",
        "🎻 Violinista para Orquesta Sinfónica - Bogotá",
        "🎹 Productor Musical - Estudio de Grabación (Híbrido)",
        "🥁 Baterista de sesión - Remoto",
        "🎤 Cantante para eventos - Medellín",
        "🎶 Se busca músicos para banda sinfónica - Medellín",
        "📯 Director de banda municipal - Cali",
        "🎼 Compositor para jingles publicitarios - Remoto"
    ]

def filtrar_ofertas(ofertas):
    palabras_clave = ["trumpet", "trompetista", "banda", "músicos", "band"]
    ofertas_filtradas = []
    for oferta in ofertas:
        oferta_lower = oferta.lower()
        if any(palabra.lower() in oferta_lower for palabra in palabras_clave):
            ofertas_filtradas.append(oferta)
    return ofertas_filtradas

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "¡Hola! Soy tu bot de ofertas de trabajo musicales. 🎶\n\n"
        "Usa /buscar para ver ofertas filtradas por: trumpet, trompetista, banda, músicos, band.\n"
        "Usa /alerta para activar/desactivar alertas automáticas.\n"
        "Usa /ayuda para ver los comandos."
    )
    await update.message.reply_text(mensaje)

async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Buscando ofertas de música con tu filtro...")
    todas_las_ofertas = obtener_todas_las_ofertas()
    ofertas_filtradas = filtrar_ofertas(todas_las_ofertas)
    
    if not ofertas_filtradas:
        await update.message.reply_text("No se encontraron ofertas que coincidan con tus palabras clave.")
        return
        
    respuesta = "🎼 *Últimas ofertas encontradas (ya filtradas):*\n\n"
    for oferta in ofertas_filtradas:
        respuesta += f"• {oferta}\n"
    
    await update.message.reply_text(respuesta, parse_mode="Markdown")

async def alerta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global alertas_activas
    alertas_activas = not alertas_activas
    
    if alertas_activas:
        await update.message.reply_text("✅ Alertas ACTIVADAS. Te enviaré ofertas nuevas de tu filtro cada 2 horas.")
        context.job_queue.run_repeating(enviar_alerta_automatica, interval=7200, first=5, chat_id=update.effective_chat.id)
    else:
        await update.message.reply_text("❌ Alertas DESACTIVADAS.")
        for job in context.job_queue.jobs():
            job.schedule_removal()

async def enviar_alerta_automatica(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    todas_las_ofertas = obtener_todas_las_ofertas()
    ofertas_filtradas = filtrar_ofertas(todas_las_ofertas)
    
    if ofertas_filtradas:
        nueva_oferta = ofertas_filtradas[0] 
        await context.bot.send_message(job.chat_id, text=f"🚨 *¡Nueva alerta de empleo musical (Filtrada)!*\n\n{nueva_oferta}", parse_mode="Markdown")
    else:
        await context.bot.send_message(job.chat_id, text="🚨 Alerta activa, pero no hay nuevas ofertas que coincidan con tu filtro.")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "/start - Iniciar el bot\n"
        "/buscar - Buscar ofertas con el filtro\n"
        "/alerta - Activar alertas automáticas\n"
        "/ayuda - Mostrar esta ayuda"
    )

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('buscar', buscar))
    application.add_handler(CommandHandler('alerta', alerta))
    application.add_handler(CommandHandler('ayuda', ayuda))
    
    print("🤖 Bot iniciado en modo Webhook.")
    
    # Configuración para Render
    PORT = int(os.environ.get("PORT", 8443))
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    webhook_url = f"https://{RENDER_URL}/{TOKEN}"
    
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=webhook_url
    )

