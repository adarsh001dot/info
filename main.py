import logging
import requests
import random
import string
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8432105036:AAE6BQDg9qcxdjeEkyr9G1QiQGuHhWVgMoI"
OWNER_ID = 7459756974
ADMIN_IDS = [7459756974, 2011028235]

# ✅ FIXED MongoDB Connection String
MONGO_URI = "mongodb+srv://nikilsaxena843_db_user:3gFwy2T4IjsFt0cY@vipbot.puv6gfk.mongodb.net/vip_bot?retryWrites=true&w=majority&authSource=admin"

# Price Configuration: 1 Point = ₹5
POINT_PRICE = 5
POINT_PACKAGES = {
    "100": {"points": 100, "price": 500, "emoji": "💎"},
    "250": {"points": 250, "price": 1250, "emoji": "💎💎"},
    "500": {"points": 500, "price": 2500, "emoji": "👑"},
    "1000": {"points": 1000, "price": 5000, "emoji": "👑👑"},
    "2500": {"points": 2500, "price": 12500, "emoji": "🔥"},
    "5000": {"points": 5000, "price": 25000, "emoji": "⚡"},
}

API_URL = "https://open-source-1.onrender.com/tg-user"
REACTIONS = ["❤️‍🔥", "💀", "😈", "☠️", "💘", "💝", "💕", "💞", "💓", "💗"]

# Languages
LANGUAGES = {
    "hi": {
        "welcome": "🎉 स्वागत है VIP बॉट में!\nआपके पॉइंट्स: {points}",
        "menu": "मुख्य मेनू",
        "check_user": "🔍 यूजर चेक करें",
        "buy_points": "💰 पॉइंट्स खरीदें",
        "gift_code": "🎁 गिफ्ट कोड",
        "contact_admin": "📞 एडमिन से संपर्क",
        "language": "🌐 भाषा बदलें",
        "points_balance": "आपके पॉइंट्स: {points}",
        "enter_user_id": "यूजर आईडी भेजें:",
        "processing": "⏳ प्रोसेस हो रहा है...",
        "result": "✅ रिजल्ट:\nदेश: {country}\nकोड: {code}\nनंबर: {number}",
        "insufficient_points": "❌ अपर्याप्त पॉइंट्स! आपके पास {points} पॉइंट्स हैं।",
        "points_deducted": "{points} पॉइंट्स कट गए। बचे पॉइंट्स: {remaining}",
        "error": "❌ एरर: {error}",
        "no_user": "❌ यूजर नहीं मिला",
        "choose_package": "पैकेज चुनें:",
        "payment_info": "💳 पेमेंट के लिए UPI: vip@paytm\nराशि: ₹{price}\n{points} पॉइंट्स के लिए",
        "payment_done": "✅ पेमेंट कर दिया है?",
        "confirm_payment": "✅ हां, पेमेंट किया",
        "cancel": "❌ रद्द करें",
        "payment_confirm_msg": "एडमिन को सूचना भेज दी गई है। जल्द ही पॉइंट्स ऐड कर दिए जाएंगे।",
        "gift_code_prompt": "गिफ्ट कोड भेजें:",
        "gift_code_success": "🎉 {points} पॉइंट्स मिल गए!",
        "gift_code_invalid": "❌ गलत या एक्सपायर कोड",
        "admin_contact_msg": "एडमिन से संपर्क करने के लिए यहां लिखें:",
        "msg_sent": "✅ मैसेज भेज दिया गया",
        "owner_panel": "👑 ओनर पैनल",
        "total_users": "कुल यूजर्स: {count}",
        "total_points": "कुल पॉइंट्स: {points}",
        "today_income": "आज की कमाई: ₹{income}",
        "month_income": "महीने की कमाई: ₹{income}",
    },
    "en": {
        "welcome": "🎉 Welcome to VIP Bot!\nYour Points: {points}",
        "menu": "Main Menu",
        "check_user": "🔍 Check User",
        "buy_points": "💰 Buy Points",
        "gift_code": "🎁 Gift Code",
        "contact_admin": "📞 Contact Admin",
        "language": "🌐 Change Language",
        "points_balance": "Your Points: {points}",
        "enter_user_id": "Send User ID:",
        "processing": "⏳ Processing...",
        "result": "✅ Result:\nCountry: {country}\nCode: {code}\nNumber: {number}",
        "insufficient_points": "❌ Insufficient Points! You have {points} points.",
        "points_deducted": "{points} points deducted. Remaining: {remaining}",
        "error": "❌ Error: {error}",
        "no_user": "❌ User not found",
        "choose_package": "Choose Package:",
        "payment_info": "💳 Pay to UPI: vip@paytm\nAmount: ₹{price}\nFor {points} Points",
        "payment_done": "✅ Done Payment?",
        "confirm_payment": "✅ Yes, Paid",
        "cancel": "❌ Cancel",
        "payment_confirm_msg": "Notification sent to admin. Points will be added soon.",
        "gift_code_prompt": "Send Gift Code:",
        "gift_code_success": "🎉 You got {points} Points!",
        "gift_code_invalid": "❌ Invalid or Expired Code",
        "admin_contact_msg": "Write your message to admin:",
        "msg_sent": "✅ Message Sent",
        "owner_panel": "👑 Owner Panel",
        "total_users": "Total Users: {count}",
        "total_points": "Total Points: {points}",
        "today_income": "Today's Income: ₹{income}",
        "month_income": "Month's Income: ₹{income}",
    }
}

# ==================== ✅ FIXED DATABASE SETUP ====================
print("\n" + "="*60)
print("🔌 CONNECTING TO MONGODB...")
print("="*60)

try:
    # ✅ Simple connection without extra options
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.admin.command('ping')
    
    # Database and Collections
    db = client['vip_bot']
    users_col = db['users']
    gift_codes_col = db['gift_codes']
    payments_col = db['payments']
    admin_msgs_col = db['admin_messages']
    
    # Create indexes
    try:
        users_col.create_index('user_id', unique=True)
        gift_codes_col.create_index('code', unique=True)
        payments_col.create_index('timestamp')
        admin_msgs_col.create_index('timestamp')
    except Exception as e:
        print(f"⚠️ Index warning: {e}")
    
    print("✅✅✅ MongoDB Connected Successfully! ✅✅✅")
    print(f"📊 Database: vip_bot")
    print(f"📁 Collections: users, gift_codes, payments, admin_msgs")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")
    print("\n🔴🔴🔴 FIX THESE ISSUES: 🔴🔴🔴")
    print("1. Go to MongoDB Atlas -> Network Access -> Add IP: 0.0.0.0/0")
    print("2. Go to Database Access -> Reset password for nikilsaxena843_db_user")
    print("3. Use this EXACT connection string in MongoDB Compass to test:")
    print("   mongodb+srv://nikilsaxena843_db_user:3gFwy2T4IjsFt0cY@vipbot.puv6gfk.mongodb.net/")
    print("="*60)
    exit(1)

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== HELPER FUNCTIONS ====================
def get_user_lang(user_id):
    user = users_col.find_one({"user_id": user_id})
    return user.get("lang", "en") if user else "en"

def get_text(user_id, key, **kwargs):
    lang = get_user_lang(user_id)
    text = LANGUAGES[lang].get(key, LANGUAGES["en"][key])
    return text.format(**kwargs)

def generate_gift_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

async def add_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE, message=None):
    try:
        if not message:
            message = update.effective_message
        reaction = random.choice(REACTIONS)
        await message.reply_text(reaction)
    except Exception as e:
        logger.error(f"Reaction error: {e}")

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    existing_user = users_col.find_one({"user_id": user_id})
    
    if not existing_user:
        user_data = {
            "user_id": user_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "points": 10,
            "lang": "en",
            "joined_date": datetime.now(),
            "total_used": 0,
            "total_spent": 0
        }
        users_col.insert_one(user_data)
        points = 10
    else:
        points = existing_user.get("points", 0)
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "check_user"), callback_data="check_user")],
        [InlineKeyboardButton(get_text(user_id, "buy_points"), callback_data="buy_points"),
         InlineKeyboardButton(get_text(user_id, "gift_code"), callback_data="gift_code")],
        [InlineKeyboardButton(get_text(user_id, "contact_admin"), callback_data="contact_admin"),
         InlineKeyboardButton(get_text(user_id, "language"), callback_data="change_lang")]
    ]
    
    if user_id == OWNER_ID or user_id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("👑 Owner Panel", callback_data="owner_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = get_text(user_id, "welcome", points=points)
    
    sent_msg = await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    await add_reaction(update, context, sent_msg)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "check_user":
        context.user_data['action'] = 'check_user'
        await query.edit_message_text(get_text(user_id, "enter_user_id"))
        
    elif data == "buy_points":
        await show_point_packages(query, user_id)
        
    elif data == "gift_code":
        context.user_data['action'] = 'gift_code'
        await query.edit_message_text(get_text(user_id, "gift_code_prompt"))
        
    elif data == "contact_admin":
        context.user_data['action'] = 'contact_admin'
        await query.edit_message_text(get_text(user_id, "admin_contact_msg"))
        
    elif data == "change_lang":
        await change_language(query, user_id)
        
    elif data.startswith("buy_package_"):
        package = data.replace("buy_package_", "")
        await process_payment(query, user_id, package, context)
        
    elif data == "confirm_payment":
        payment_data = {
            "user_id": user_id,
            "package": context.user_data.get('pending_package'),
            "amount": context.user_data.get('pending_amount'),
            "timestamp": datetime.now(),
            "status": "pending"
        }
        payments_col.insert_one(payment_data)
        
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin_id,
                    f"💰 New Payment Request!\n"
                    f"User: {user_id}\n"
                    f"Package: {context.user_data.get('pending_package')} points\n"
                    f"Amount: ₹{context.user_data.get('pending_amount')}"
                )
            except:
                pass
        
        await query.edit_message_text(get_text(user_id, "payment_confirm_msg"))
        
    elif data == "owner_panel":
        await owner_panel(query, user_id, context)
        
    elif data.startswith("gen_gift_"):
        if user_id == OWNER_ID or user_id in ADMIN_IDS:
            points = int(data.replace("gen_gift_", ""))
            await generate_gift(query, user_id, points, context)
            
    elif data.startswith("lang_"):
        lang = data.replace("lang_", "")
        users_col.update_one({"user_id": user_id}, {"$set": {"lang": lang}})
        await query.edit_message_text("✅ Language Changed! Send /start again.")
        
    elif data == "back":
        await start(update, context)

async def show_point_packages(query, user_id):
    keyboard = []
    for key, package in POINT_PACKAGES.items():
        btn_text = f"{package['emoji']} {package['points']} Points - ₹{package['price']}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy_package_{key}")])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "cancel"), callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        get_text(user_id, "choose_package"),
        reply_markup=reply_markup
    )

async def process_payment(query, user_id, package_key, context):
    package = POINT_PACKAGES[package_key]
    
    context.user_data['pending_package'] = package_key
    context.user_data['pending_amount'] = package['price']
    
    text = get_text(user_id, "payment_info", 
                    price=package['price'], 
                    points=package['points'])
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "confirm_payment"), callback_data="confirm_payment")],
        [InlineKeyboardButton(get_text(user_id, "cancel"), callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def change_language(query, user_id):
    keyboard = [
        [InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Choose Language / भाषा चुनें:", reply_markup=reply_markup)

async def owner_panel(query, user_id, context):
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Unauthorized")
        return
    
    total_users = users_col.count_documents({})
    total_points = 0
    for user in users_col.find():
        total_points += user.get("points", 0)
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_payments = payments_col.count_documents({"timestamp": {"$gte": today_start}})
    today_income = today_payments * 500
    
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_payments = payments_col.count_documents({"timestamp": {"$gte": month_start}})
    month_income = month_payments * 500
    
    pending = payments_col.count_documents({"status": "pending"})
    
    text = f"👑 **Owner Panel**\n\n"
    text += f"📊 **Stats:**\n"
    text += f"👥 Total Users: {total_users}\n"
    text += f"💎 Total Points: {total_points}\n"
    text += f"💰 Today Income: ₹{today_income}\n"
    text += f"📅 Month Income: ₹{month_income}\n"
    text += f"⏳ Pending Payments: {pending}\n\n"
    text += f"🔧 **Admin Tools:**\n"
    
    keyboard = [
        [InlineKeyboardButton("🎁 Generate 100 Points Gift", callback_data="gen_gift_100")],
        [InlineKeyboardButton("🎁 Generate 250 Points Gift", callback_data="gen_gift_250")],
        [InlineKeyboardButton("🎁 Generate 500 Points Gift", callback_data="gen_gift_500")],
        [InlineKeyboardButton("🎁 Generate 1000 Points Gift", callback_data="gen_gift_1000")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def generate_gift(query, user_id, points, context):
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        return
    
    code = generate_gift_code()
    gift_data = {
        "code": code,
        "points": points,
        "created_by": user_id,
        "created_at": datetime.now(),
        "expires": datetime.now() + timedelta(days=7),
        "used_by": None,
        "used_at": None
    }
    gift_codes_col.insert_one(gift_data)
    
    await query.edit_message_text(
        f"✅ Gift Code Generated!\n\n"
        f"Code: `{code}`\n"
        f"Points: {points}\n"
        f"Valid for: 7 days\n\n"
        f"Copy: `/redeem {code}`",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    action = context.user_data.get('action')
    
    if action == 'check_user':
        await check_user(update, context, text)
    elif action == 'gift_code':
        await redeem_gift(update, context, text)
    elif action == 'contact_admin':
        await contact_admin(update, context, text)
    else:
        await start(update, context)

async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id_to_check):
    user_id = update.effective_user.id
    
    user = users_col.find_one({"user_id": user_id})
    if not user or user.get("points", 0) < 10:
        await update.message.reply_text(
            get_text(user_id, "insufficient_points", points=user.get("points", 0) if user else 0)
        )
        return
    
    try:
        await update.message.reply_text(get_text(user_id, "processing"))
        
        response = requests.post(
            API_URL,
            json={"userId": user_id_to_check},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data", {}).get("success"):
                user_data = data["data"]
                
                new_points = user["points"] - 10
                users_col.update_one(
                    {"user_id": user_id},
                    {"$set": {"points": new_points}, "$inc": {"total_used": 1}}
                )
                
                result_text = get_text(
                    user_id,
                    "result",
                    country=user_data.get("country", "N/A"),
                    code=user_data.get("country_code", "N/A"),
                    number=user_data.get("number", "N/A")
                )
                sent_msg = await update.message.reply_text(result_text)
                await add_reaction(update, context, sent_msg)
                
                await update.message.reply_text(
                    get_text(user_id, "points_deducted", points=10, remaining=new_points)
                )
            else:
                await update.message.reply_text(get_text(user_id, "no_user"))
        else:
            await update.message.reply_text(get_text(user_id, "error", error="API Error"))
            
    except Exception as e:
        await update.message.reply_text(get_text(user_id, "error", error=str(e)))
    
    context.user_data['action'] = None

async def redeem_gift(update: Update, context: ContextTypes.DEFAULT_TYPE, code):
    user_id = update.effective_user.id
    
    gift = gift_codes_col.find_one({
        "code": code.strip().upper(),
        "used_by": None,
        "expires": {"$gt": datetime.now()}
    })
    
    if not gift:
        await update.message.reply_text(get_text(user_id, "gift_code_invalid"))
        context.user_data['action'] = None
        return
    
    users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"points": gift["points"]}}
    )
    
    gift_codes_col.update_one(
        {"_id": gift["_id"]},
        {"$set": {"used_by": user_id, "used_at": datetime.now()}}
    )
    
    sent_msg = await update.message.reply_text(
        get_text(user_id, "gift_code_success", points=gift["points"])
    )
    await add_reaction(update, context, sent_msg)
    context.user_data['action'] = None

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, message):
    user_id = update.effective_user.id
    
    msg_data = {
        "user_id": user_id,
        "username": update.effective_user.username,
        "first_name": update.effective_user.first_name,
        "message": message,
        "timestamp": datetime.now(),
        "replied": False
    }
    admin_msgs_col.insert_one(msg_data)
    
    forward_text = f"📨 **New Message from User**\n\n"
    forward_text += f"👤 **User:** {user_id}\n"
    forward_text += f"📝 **Name:** {update.effective_user.first_name}\n"
    forward_text += f"🆔 **Username:** @{update.effective_user.username or 'None'}\n"
    forward_text += f"💬 **Message:** {message}\n"
    forward_text += f"🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(admin_id, forward_text, parse_mode='Markdown')
        except:
            pass
    
    sent_msg = await update.message.reply_text(get_text(user_id, "msg_sent"))
    await add_reaction(update, context, sent_msg)
    context.user_data['action'] = None

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /redeem <gift_code>")
        return
    
    code = context.args[0]
    await redeem_gift(update, context, code)

# ==================== MAIN ====================
def main():
    print("\n" + "="*60)
    print("🚀 STARTING VIP BOT...")
    print("="*60)
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"👥 Admins: {ADMIN_IDS}")
    print(f"💎 Points: 1 = ₹{POINT_PRICE}")
    print("="*60)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("redeem", redeem_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot is ready! Press Ctrl+C to stop.")
    print("="*60 + "\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
