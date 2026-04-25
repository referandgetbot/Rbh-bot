from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os
import re
import json

TOKEN = os.environ.get("BOT_TOKEN", "8786143482:AAE3aRUD7JJmswz4mr9D72r5dF3jHe5-igo")

# ========== FORCE JOIN CHANNELS ==========
FORCE_CHANNELS = ["ZyroXEra", "PrimeXStoree"]

CHANNEL_LINKS = [
    "https://t.me/ZyroXEra",
    "https://t.me/PrimeXStoree",
    "https://t.me/+FP4snJy6j7U3MWM9",
    "https://t.me/+vznpmYI8UX8wZGU9",
    "https://t.me/+2PJYCDSXRnExZTVl"
]

# ========== POINTS SYSTEM ==========
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

users = load_users()

def get_points(user_id):
    return users.get(str(user_id), {}).get("points", 2)

def add_points(user_id, points):
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"points": 2}
    users[uid]["points"] = users[uid].get("points", 2) + points
    save_users(users)

def deduct_points(user_id, points):
    uid = str(user_id)
    current = get_points(user_id)
    if current >= points:
        users[uid]["points"] = current - points
        save_users(users)
        return True
    return False

# ========== FORCE JOIN CHECK ==========
async def check_force_join(user_id, context):
    not_joined = []
    for channel in FORCE_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=f"@{channel}", user_id=user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(channel)
        except:
            not_joined.append(channel)
    return not_joined

# ========== START COMMAND ==========
async def start(update, context):
    user = update.effective_user
    user_id = user.id
    
    # Handle referral
    args = context.args
    if args and args[0].startswith("ref_"):
        referrer_id = int(args[0].replace("ref_", ""))
        if referrer_id != user_id:
            add_points(referrer_id, 2)
    
    # Init user
    if str(user_id) not in users:
        users[str(user_id)] = {"points": 2}
        save_users(users)
    
    # Check force join
    not_joined = await check_force_join(user_id, context)
    
    if not_joined:
        keyboard = []
        for ch in not_joined:
            # Find link for channel
            link = f"https://t.me/{ch}"
            keyboard.append([InlineKeyboardButton("𝐌ᴀɪɴ 𝐂ʜᴀɴɴᴇʟ ♻️", url=link)])
        keyboard.append([InlineKeyboardButton("🔄 Check Again", callback_data="check_join")])
        
        await update.message.reply_text(
            "⚠️ **Access Restricted!**\n\nPlease join required channels first.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return
    
    points = get_points(user_id)
    bot_username = (await context.bot.get_me()).username
    refer_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    await update.message.reply_text(
        f"✨ **Welcome {user.first_name}!** ✨\n\n"
        f"💰 **Points:** {points} ⭐\n"
        f"👥 **Referrals:** {users.get(str(user_id), {}).get('total_refers', 0)}\n\n"
        f"📌 **Send me:**\n"
        f"   📸 Instagram Reel\n"
        f"   🎵 TikTok Video\n"
        f"   📺 YouTube Short\n\n"
        f"⚠️ Each repurpose costs 2 points\n"
        f"👥 Invite friends: /refer\n\n"
        f"🔗 Your refer link:\n`{refer_link}`",
        parse_mode="Markdown"
    )

# ========== REFER COMMAND ==========
async def refer(update, context):
    user_id = update.effective_user.id
    bot_username = (await context.bot.get_me()).username
    refer_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    points = get_points(user_id)
    refers = users.get(str(user_id), {}).get('total_refers', 0)
    
    await update.message.reply_text(
        f"👥 **Refer & Earn Points**\n\n"
        f"🔗 Your link:\n`{refer_link}`\n\n"
        f"📊 Stats:\n"
        f"   • Points: {points} ⭐\n"
        f"   • Referrals: {refers}\n\n"
        f"✅ Each referral = +2 points",
        parse_mode="Markdown"
    )

# ========== POINTS COMMAND ==========
async def points(update, context):
    user_id = update.effective_user.id
    points = get_points(user_id)
    refers = users.get(str(user_id), {}).get('total_refers', 0)
    
    await update.message.reply_text(
        f"💰 **Your Balance**\n\n"
        f"⭐ Points: {points}\n"
        f"👥 Referrals: {refers}\n\n"
        f"📝 Each search = -2 points\n"
        f"👥 Each referral = +2 points",
        parse_mode="Markdown"
    )

# ========== VIRAL CAPTION ==========
async def handle_message(update, context):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Check force join first
    not_joined = await check_force_join(user_id, context)
    if not_joined:
        await update.message.reply_text("⚠️ Please join required channels first. Send /start")
        return
    
    # Check if it's a link
    if not (text.startswith("http") and ("instagram" in text or "tiktok" in text or "youtube" in text or "youtu.be" in text)):
        await update.message.reply_text(
            "❌ **Invalid!**\n\n"
            "Send me:\n"
            "📸 Instagram Reel: `https://instagram.com/reel/...`\n"
            "🎵 TikTok Video: `https://tiktok.com/@.../video/...`\n"
            "📺 YouTube Short: `https://youtube.com/shorts/...`",
            parse_mode="Markdown"
        )
        return
    
    # Check points
    if get_points(user_id) < 2:
        await update.message.reply_text(
            "❌ **Insufficient Points!**\n\n"
            f"⭐ Your points: {get_points(user_id)}\n"
            f"👥 Need 2 points for search\n\n"
            f"📢 Invite friends: /refer",
            parse_mode="Markdown"
        )
        return
    
    # Deduct points and process
    if deduct_points(user_id, 2):
        await update.message.reply_text("🔄 **Analyzing your video...**")
        
        # Detect platform
        platform = "Instagram"
        if "tiktok" in text:
            platform = "TikTok"
        elif "youtube" in text or "youtu.be" in text:
            platform = "YouTube"
        
        # Generate caption
        captions = {
            "Instagram": "🔥 **This reel is pure GOLD!** 🔥\n\nTag someone who needs to see this! 👇\n\n#viral #trending #reels #explore",
            "TikTok": "😱 **CAN'T STOP WATCHING THIS!** 😱\n\nFollow for more! 🚀\n\n#fyp #viral #tiktok #foryou",
            "YouTube": "⚡ **WAIT FOR THE END!** ⚡\n\nSubscribe for more! 🔔\n\n#shorts #viral #youtube"
        }
        
        hashtags = {
            "Instagram": "#viral #trending #reels #explore",
            "TikTok": "#fyp #viral #tiktok #foryou",
            "YouTube": "#shorts #viral #youtube"
        }
        
        new_points = get_points(user_id)
        
        await update.message.reply_text(
            f"📱 **Platform:** {platform}\n\n"
            f"📝 **Viral Caption:**\n{captions.get(platform)}\n\n"
            f"🔥 **Hashtags:**\n{hashtags.get(platform)}\n\n"
            f"⏰ **Best Time:** 7-9 PM IST\n\n"
            f"✅ **-2 points used**\n"
            f"💰 **Remaining points:** {new_points}",
            parse_mode="Markdown"
        )

# ========== BUTTON HANDLER ==========
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_join":
        user_id = update.effective_user.id
        not_joined = await check_force_join(user_id, context)
        
        if not_joined:
            keyboard = []
            for ch in not_joined:
                keyboard.append([InlineKeyboardButton("𝐌ᴀɪɴ 𝐂ʜᴀɴɴᴇʟ ♻️", url=f"https://t.me/{ch}")])
            keyboard.append([InlineKeyboardButton("🔄 Check Again", callback_data="check_join")])
            await query.edit_message_text(
                "⚠️ Still not joined!\n\nJoin all channels and try again.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text("✅ Thanks for joining! Send /start to continue.")

# ========== MAIN ==========
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("refer", refer))
    app.add_handler(CommandHandler("points", points))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Bot Started!")
    print(f"📢 Force Join: {len(FORCE_CHANNELS)} channels")
    print("💰 Points System: Active")
    app.run_polling()

if __name__ == "__main__":
    main()
