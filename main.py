import logging
import requests
import random
import string
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8432105036:AAE6BQDg9qcxdjeEkyr9G1QiQGuHhWVgMoI"
OWNER_ID = 7459756974  # Aapki ID
ADMIN_IDS = [7459756974, 2011028235]  # Admins

# MongoDB Connection String
MONGO_URI = "mongodb+srv://nikilsaxena843_db_user:3gFwy2T4IjsFt0cY@vipbot.puv6gfk.mongodb.net/?appName=vipbot"

# Price Configuration: 1 Point = ₹5
POINT_PRICE = 5  # ₹5 per point
POINT_PACKAGES = {
    "100": {"points": 100, "price": 500, "emoji": "💎"},    # 100 pts = ₹500
    "250": {"points": 250, "price": 1250, "emoji": "💎💎"},  # 250 pts = ₹1250
    "500": {"points": 500, "price": 2500, "emoji": "👑"},    # 500 pts = ₹2500
    "1000": {"points": 1000, "price": 5000, "emoji": "👑👑"}, # 1000 pts = ₹5000
    "2500": {"points": 2500, "price": 12500, "emoji": "🔥"}, # 2500 pts = ₹12500
    "5000": {"points": 5000, "price": 25000, "emoji": "⚡"},  # 5000 pts = ₹25000
}

# API Endpoint
API_URL = "https://open-source-1.onrender.com/tg-user"

# Reaction emojis list
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

# ==================== DATABASE SETUP ====================
print("🔄 Connecting to MongoDB...")

try:
    # MongoDB Connection with timeout
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
    users_col.create_index('user_id', unique=True)
    gift_codes_col.create_index('code', unique=True)
    
    print("✅ MongoDB Connected Successfully!")
    print(f"📊 Database: vip_bot")
    print(f"📁 Collections: users, gift_codes, payments, admin_messages")
    
except ServerSelectionTimeoutError as e:
    print("❌ MongoDB Connection Failed: Server timeout")
    print(f"Error: {e}")
    print("\n💡 Troubleshooting:")
    print("1. Check your internet connection")
    print("2. Verify MongoDB URI is correct")
    print("3. Make sure IP is whitelisted in MongoDB Atlas")
    print("4. Try: mongodb+srv://nikilsaxena843_db_user:3gFwy2T4IjsFt0cY@vipbot.puv6gfk.mongodb.net/")
    exit(1)
    
except ConnectionFailure as e:
    print("❌ MongoDB Connection Failed: Connection error")
    print(f"Error: {e}")
    exit(1)
    
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    exit(1)

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== HELPER FUNCTIONS ====================
def get_user_lang(user_id):
    """Get user's language preference"""
    user = users_col.find_one({"user_id": user_id})
    return user.get("lang", "en") if user else "en"

def get_text(user_id, key, **kwargs):
    """Get text in user's language"""
    lang = get_user_lang(user_id)
    text = LANGUAGES[lang].get(key, LANGUAGES["en"][key])
    return text.format(**kwargs)

def generate_gift_code():
    """Generate random gift code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

async def add_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add random reaction to bot's message"""
    try:
        message = update.effective_message
        reaction = random.choice(REACTIONS)
        # Note: Telegram Bot API doesn't support reactions directly yet
        # This is a placeholder for future implementation
        # You can use custom emoji in text instead
        logger.info(f"Would react with: {reaction}")
    except Exception as e:
        logger.error(f"Reaction error: {e}")

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    user_id = user.id
    
    # Check if user exists in database
    existing_user = users_col.find_one({"user_id": user_id})
    
    if not existing_user:
        # New user
        user_data = {
            "user_id": user_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "points": 10,  # Welcome bonus
            "lang": "en",
            "joined_date": datetime.now(),
            "total_used": 0,
            "total_spent": 0
        }
        users_col.insert_one(user_data)
        points = 10
    else:
        points = existing_user.get("points", 0)
    
    # Create keyboard
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "check_user"), callback_data="check_user")],
        [InlineKeyboardButton(get_text(user_id, "buy_points"), callback_data="buy_points"),
         InlineKeyboardButton(get_text(user_id, "gift_code"), callback_data="gift_code")],
        [InlineKeyboardButton(get_text(user_id, "contact_admin"), callback_data="contact_admin"),
         InlineKeyboardButton(get_text(user_id, "language"), callback_data="change_lang")]
    ]
    
    # Add owner panel button if owner
    if user_id == OWNER_ID or user_id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("👑 Owner Panel", callback_data="owner_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = get_text(user_id, "welcome", points=points)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
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
        await process_payment(query, user_id, package)
        
    elif data == "confirm_payment":
        await query.edit_message_text("✅ Payment request sent to admin. You will get points soon.")
        
    elif data == "owner_panel":
        await owner_panel(query, user_id)
        
    elif data.startswith("gen_gift_"):
        if user_id == OWNER_ID or user_id in ADMIN_IDS:
            points = int(data.replace("gen_gift_", ""))
            await generate_gift(query, user_id, points)
            
    elif data.startswith("lang_"):
        lang = data.replace("lang_", "")
        users_col.update_one({"user_id": user_id}, {"$set": {"lang": lang}})
        await start(update, context)

async def show_point_packages(query, user_id):
    """Show available point packages"""
    keyboard = []
    for key, package in POINT_PACKAGES.items():
        btn_text = f"{package['emoji']} {package['points']} Points - ₹{package['price']}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy_package_{key}")])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "cancel"), callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        get_text(user_id, "choose_package"),
        reply_markup=reply_markup
    )

async def process_payment(query, user_id, package_key):
    """Process payment for package"""
    package = POINT_PACKAGES[package_key]
    
    text = get_text(user_id, "payment_info", 
                    price=package['price'], 
                    points=package['points'])
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "confirm_payment"), callback_data="confirm_payment")],
        [InlineKeyboardButton(get_text(user_id, "cancel"), callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def change_language(query, user_id):
    """Change language menu"""
    keyboard = [
        [InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Choose Language / भाषा चुनें:", reply_markup=reply_markup)

async def owner_panel(query, user_id):
    """Owner panel with stats"""
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Unauthorized")
        return
    
    # Get stats
    total_users = users_col.count_documents({})
    total_points = sum(user.get("points", 0) for user in users_col.find())
    
    # Today's income
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_income = payments_col.count_documents({"timestamp": {"$gte": today_start}}) * 500  # Assuming min package
    
    # Month income
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_income = payments_col.count_documents({"timestamp": {"$gte": month_start}}) * 500
    
    text = f"👑 **Owner Panel**\n\n"
    text += f"📊 **Stats:**\n"
    text += f"👥 Total Users: {total_users}\n"
    text += f"💎 Total Points: {total_points}\n"
    text += f"💰 Today Income: ₹{today_income}\n"
    text += f"📅 Month Income: ₹{month_income}\n\n"
    text += f"🔧 **Admin Tools:**\n"
    
    keyboard = [
        [InlineKeyboardButton("🎁 Generate 100 Points Gift", callback_data="gen_gift_100")],
        [InlineKeyboardButton("🎁 Generate 250 Points Gift", callback_data="gen_gift_250")],
        [InlineKeyboardButton("🎁 Generate 500 Points Gift", callback_data="gen_gift_500")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("📊 Export Users", callback_data="export_users")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def generate_gift(query, user_id, points):
    """Generate gift code"""
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
    """Handle text messages"""
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
    """Check user via API"""
    user_id = update.effective_user.id
    
    # Check points
    user = users_col.find_one({"user_id": user_id})
    if not user or user.get("points", 0) < 10:
        await update.message.reply_text(
            get_text(user_id, "insufficient_points", points=user.get("points", 0))
        )
        return
    
    # Call API
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
                
                # Deduct points
                new_points = user["points"] - 10
                users_col.update_one(
                    {"user_id": user_id},
                    {"$set": {"points": new_points}, "$inc": {"total_used": 1}}
                )
                
                # Send result
                result_text = get_text(
                    user_id,
                    "result",
                    country=user_data.get("country", "N/A"),
                    code=user_data.get("country_code", "N/A"),
                    number=user_data.get("number", "N/A")
                )
                sent_msg = await update.message.reply_text(result_text)
                
                # Add reaction emoji (as text for now)
                reaction = random.choice(REACTIONS)
                await sent_msg.reply_text(f"{reaction}")
                
                # Send points info
                await update.message.reply_text(
                    get_text(user_id, "points_deducted", points=10, remaining=new_points)
                )
            else:
                await update.message.reply_text(get_text(user_id, "no_user"))
        else:
            await update.message.reply_text(get_text(user_id, "error", error="API Error"))
            
    except Exception as e:
        await update.message.reply_text(get_text(user_id, "error", error=str(e)))

async def redeem_gift(update: Update, context: ContextTypes.DEFAULT_TYPE, code):
    """Redeem gift code"""
    user_id = update.effective_user.id
    
    gift = gift_codes_col.find_one({
        "code": code.strip().upper(),
        "used_by": None,
        "expires": {"$gt": datetime.now()}
    })
    
    if not gift:
        await update.message.reply_text(get_text(user_id, "gift_code_invalid"))
        return
    
    # Add points
    users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"points": gift["points"]}}
    )
    
    # Mark as used
    gift_codes_col.update_one(
        {"_id": gift["_id"]},
        {"$set": {"used_by": user_id, "used_at": datetime.now()}}
    )
    
    await update.message.reply_text(
        get_text(user_id, "gift_code_success", points=gift["points"])
    )

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, message):
    """Contact admin"""
    user_id = update.effective_user.id
    user = users_col.find_one({"user_id": user_id})
    
    # Save message
    msg_data = {
        "user_id": user_id,
        "username": update.effective_user.username,
        "message": message,
        "timestamp": datetime.now(),
        "replied": False
    }
    admin_msgs_col.insert_one(msg_data)
    
    # Forward to owner
    try:
        forward_text = f"📨 New message from {user_id}\n"
        forward_text += f"User: @{update.effective_user.username}\n"
        forward_text += f"Message: {message}"
        
        await context.bot.send_message(OWNER_ID, forward_text)
    except:
        pass
    
    await update.message.reply_text(get_text(user_id, "msg_sent"))
    context.user_data['action'] = None

# ==================== MAIN ====================
def main():
    """Start the bot"""
    print("\n" + "="*50)
    print("🚀 Starting VIP Bot...")
    print("="*50)
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("redeem", redeem_gift))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    print("✅ Bot is ready! Press Ctrl+C to stop.")
    print("="*50 + "\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()