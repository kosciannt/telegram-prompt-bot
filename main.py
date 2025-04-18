from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOOLS = ["KlingAI", "GenfluenceAI", "LoRA", "ComfyUI"]
PARAMETERS = {
    "style": ["cinematic", "cyberpunk", "anime", "digital painting", "realism", "dreamcore", "baroque", "3D render"],
    "character": ["young woman", "astronaut", "elf warrior", "android", "medieval knight", "dragon", "urban landscape"],
    "emotion": ["happy", "melancholic", "mysterious", "angry", "dreamy", "epic"],
    "camera": ["close-up", "wide shot", "over-the-shoulder", "aerial view", "first-person", "isometric"],
    "quality": ["ultra HD", "4k", "soft lighting", "high detail", "photorealistic", "noise-free", "sharp focus"],
    "lighting": ["golden hour", "moonlight", "neon", "studio lighting", "backlit", "volumetric"],
    "background": ["futuristic city", "enchanted forest", "deep space", "foggy street", "beach at sunset"]
}

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(tool, callback_data=f"tool:{tool}")] for tool in TOOLS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Wybierz narzędzie do generowania promptu:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    data = query.data
    if data.startswith("tool:"):
        tool = data.split(":")[1]
        user_sessions[user_id]["tool"] = tool
        await query.edit_message_text(f"Wybrano narzędzie: {tool}\nWybierz styl:")
        await send_options(update, context, "style")
    elif any(data.startswith(f"{param}:") for param in PARAMETERS):
        param, value = data.split(":")
        user_sessions[user_id][param] = value
        next_param = get_next_param(user_sessions[user_id])
        if next_param:
            await send_options(update, context, next_param)
        else:
            await send_prompt(update, context, user_sessions[user_id])
            user_sessions.pop(user_id)

async def send_options(update: Update, context: ContextTypes.DEFAULT_TYPE, param: str):
    keyboard = [[InlineKeyboardButton(val, callback_data=f"{param}:{val}")] for val in PARAMETERS[param]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(f"Wybierz {param}:", reply_markup=reply_markup)

def get_next_param(session):
    for param in PARAMETERS:
        if param not in session:
            return param
    return None

async def send_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict):
    prompt = f"{session['character']}, {session['emotion']}, {session['style']}, {session['camera']}, {session['quality']}, {session['lighting']}, {session['background']}"
    tool = session["tool"]
    await update.callback_query.message.reply_text(f"Gotowy prompt dla {tool}:\n\n{prompt}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("7744294449:AAFBS2CzH6BEKZDOSvqmjCJbyPzTgdVjeZc")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("Bot is running...")
    app.run_polling()
