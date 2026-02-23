import os
import logging
import requests
import random
import string
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# ==================== LOAD ENVIRONMENT VARIABLES ====================
load_dotenv()

# Get MongoDB URI from .env file
MONGO_URI = os.getenv('MONGODB_URI')

if not MONGO_URI:
    print("❌ ERROR: MONGODB_URI not found in .env file!")
    print("Please create .env file with: MONGODB_URI=your_connection_string")
    exit(1)

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8432105036:AAE6BQDg9qcxdjeEkyr9G1QiQGuHhWVgMoI"
OWNER_ID = 7459756974
ADMIN_IDS = [7459756974, 2011028235]

# UPI ID for payments
UPI_ID = "nanhin.3@ptaxis"

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

# Reaction emojis - just for reference (will be sent as message reactions)
REACTIONS = ["❤️‍🔥", "💀", "😈", "☠️", "💘", "💝", "💕", "💞", "💓", "💗"]

# Languages
LANGUAGES = {
    "hi": {
        "welcome": "🎉 स्वागत है VIP बॉट में!\nआपके पॉइंट्स: {points}",
        "check_user": "🔍 यूजर चेक करें",
        "buy_points": "💰 पॉइंट्स खरीदें",
        "gift_code": "🎁 गिफ्ट कोड",
        "contact_admin": "📞 एडमिन से संपर्क",
        "language": "🌐 भाषा बदलें",
        "enter_user_id": "यूजर आईडी भेजें:",
        "processing": "⏳ प्रोसेस हो रहा है...",
        "result": "✅ रिजल्ट:\nदेश: {country}\nकोड: {code}\nनंबर: {number}",
        "insufficient_points": "❌ अपर्याप्त पॉइंट्स! आपके पास {points} पॉइंट्स हैं।",
        "points_deducted": "{points} पॉइंट्स कट गए। बचे पॉइंट्स: {remaining}",
        "error": "❌ एरर: {error}",
        "no_user": "❌ यूजर नहीं मिला",
        "choose_package": "पैकेज चुनें:",
        "payment_info": "💳 {points} पॉइंट्स के लिए UPI: {upi}\nराशि: ₹{price}\n\n✅ पेमेंट करने के बाद नीचे बटन दबाएं",
        "send_screenshot": "✅ पेमेंट का स्क्रीनशॉट भेजें",
        "screenshot_prompt": "📸 कृपया UPI पेमेंट का स्क्रीनशॉट भेजें।\n\nएडमिन चेक करके पॉइंट्स ऐड कर देंगे।",
        "payment_request_sent": "✅ आपका पेमेंट रिक्वेस्ट एडमिन को भेज दिया गया है!\nजल्द ही पॉइंट्स ऐड कर दिए जाएंगे।",
        "cancel": "❌ रद्द करें",
        "gift_code_prompt": "गिफ्ट कोड भेजें:",
        "gift_code_success": "🎉 {points} पॉइंट्स मिल गए!",
        "gift_code_invalid": "❌ गलत कोड",
        "admin_contact_msg": "एडमिन से संपर्क करने के लिए यहां लिखें:",
        "msg_sent": "✅ मैसेज भेज दिया गया",
        "owner_panel": "👑 ओनर पैनल",
        "total_users": "कुल यूजर्स: {count}",
        "total_points": "कुल पॉइंट्स: {points}",
        "today_income": "आज की कमाई: ₹{income}",
        "month_income": "महीने की कमाई: ₹{income}",
        "pending_payments": "⏳ लंबित पेमेंट्स: {count}",
        "approve": "✅ Approve",
        "reject": "❌ Reject",
        "payment_approved": "✅ पेमेंट स्वीकृत! {points} पॉइंट्स आपके अकाउंट में ऐड कर दिए गए हैं।",
        "payment_rejected": "❌ पेमेंट अस्वीकृत। कृपया एडमिन से संपर्क करें।",
        "no_pending": "कोई लंबित पेमेंट नहीं है।",
        "gift_created": "✅ गिफ्ट कोड बन गया!\nकोड: `{code}`\nपॉइंट्स: {points}\nएक्सपायरी: कभी नहीं"
    },
    "en": {
        "welcome": "🎉 Welcome to VIP Bot!\nYour Points: {points}",
        "check_user": "🔍 Check User",
        "buy_points": "💰 Buy Points",
        "gift_code": "🎁 Gift Code",
        "contact_admin": "📞 Contact Admin",
        "language": "🌐 Change Language",
        "enter_user_id": "Send User ID:",
        "processing": "⏳ Processing...",
        "result": "✅ Result:\nCountry: {country}\nCode: {code}\nNumber: {number}",
        "insufficient_points": "❌ Insufficient Points! You have {points} points.",
        "points_deducted": "{points} points deducted. Remaining: {remaining}",
        "error": "❌ Error: {error}",
        "no_user": "❌ User not found",
        "choose_package": "Choose Package:",
        "payment_info": "💳 Pay to UPI: {upi}\nAmount: ₹{price}\nFor {points} Points\n\n✅ Click button after payment",
        "send_screenshot": "✅ Send Payment Screenshot",
        "screenshot_prompt": "📸 Please send the UPI payment screenshot.\n\nAdmin will verify and add points.",
        "payment_request_sent": "✅ Your payment request has been sent to admin!\nPoints will be added soon.",
        "cancel": "❌ Cancel",
        "gift_code_prompt": "Send Gift Code:",
        "gift_code_success": "🎉 You got {points} Points!",
        "gift_code_invalid": "❌ Invalid Code",
        "admin_contact_msg": "Write your message to admin:",
        "msg_sent": "✅ Message Sent",
        "owner_panel": "👑 Owner Panel",
        "total_users": "Total Users: {count}",
        "total_points": "Total Points: {points}",
        "today_income": "Today's Income: ₹{income}",
        "month_income": "Month's Income: ₹{income}",
        "pending_payments": "⏳ Pending Payments: {count}",
        "approve": "✅ Approve",
        "reject": "❌ Reject",
        "payment_approved": "✅ Payment Approved! {points} points added to your account.",
        "payment_rejected": "❌ Payment Rejected. Please contact admin.",
        "no_pending": "No pending payments.",
        "gift_created": "✅ Gift Code Created!\nCode: `{code}`\nPoints: {points}\nExpiry: Never"
    }
}

# Conversation states
WAITING_SCREENSHOT = 1

# ==================== DATABASE SETUP ====================
print("\n" + "="*60)
print("🔌 CONNECTING TO MONGODB...")
print("="*60)

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    
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
        payments_col.create_index('status')
        admin_msgs_col.create_index('timestamp')
        print("✅ Indexes created/verified")
    except Exception as e:
        print(f"⚠️ Index warning: {e}")
    
    print("✅✅✅ MONGODB CONNECTED SUCCESSFULLY! ✅✅✅")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")
    print("\n🔴 FIX: Check MongoDB URI in .env file")
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
    """Add reaction to message - FIXED: Only for result messages, not every message"""
    try:
        # Only react to check_user results, not every message
        if context.user_data.get('reaction_for_message'):
            message_id = context.user_data.get('reaction_for_message')
            if message and message.message_id == message_id:
                # In future when Telegram supports reactions, we'll use:
                # await message.react(random.choice(REACTIONS))
                # For now, we don't send extra messages
                context.user_data['reaction_for_message'] = None
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
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    # No reaction on start

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
        
    elif data == "send_screenshot":
        # Ask user to send screenshot
        package_key = context.user_data.get('pending_package')
        if package_key:
            await query.edit_message_text(
                get_text(user_id, "screenshot_prompt")
            )
            return WAITING_SCREENSHOT
        
    elif data == "owner_panel":
        await owner_panel(query, user_id, context)
        
    elif data.startswith("approve_payment_"):
        if user_id == OWNER_ID or user_id in ADMIN_IDS:
            payment_id = data.replace("approve_payment_", "")
            await approve_payment(query, user_id, payment_id, context)
            
    elif data.startswith("reject_payment_"):
        if user_id == OWNER_ID or user_id in ADMIN_IDS:
            payment_id = data.replace("reject_payment_", "")
            await reject_payment(query, user_id, payment_id, context)
        
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
    
    return ConversationHandler.END

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
                    upi=UPI_ID,
                    price=package['price'], 
                    points=package['points'])
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "send_screenshot"), callback_data="send_screenshot")],
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
    total_points = sum(user.get("points", 0) for user in users_col.find())
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_payments = payments_col.count_documents({"timestamp": {"$gte": today_start}, "status": "approved"})
    today_income = today_payments * 500
    
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_payments = payments_col.count_documents({"timestamp": {"$gte": month_start}, "status": "approved"})
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
    
    # Add Pending Payments button if there are pending payments
    keyboard = []
    if pending > 0:
        keyboard.append([InlineKeyboardButton(f"📋 View Pending Payments ({pending})", callback_data="view_pending")])
    
    keyboard.extend([
        [InlineKeyboardButton("🎁 Generate 100 Points Gift", callback_data="gen_gift_100")],
        [InlineKeyboardButton("🎁 Generate 250 Points Gift", callback_data="gen_gift_250")],
        [InlineKeyboardButton("🎁 Generate 500 Points Gift", callback_data="gen_gift_500")],
        [InlineKeyboardButton("🎁 Generate 1000 Points Gift", callback_data="gen_gift_1000")],
        [InlineKeyboardButton("🎁 Generate 5000 Points Gift", callback_data="gen_gift_5000")],
        [InlineKeyboardButton("📋 View All Pending", callback_data="view_pending")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def view_pending_payments(query, user_id, context):
    """Show all pending payments with approve/reject buttons"""
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Unauthorized")
        return
    
    pending_payments = list(payments_col.find({"status": "pending"}).sort("timestamp", -1))
    
    if not pending_payments:
        await query.edit_message_text(get_text(user_id, "no_pending"))
        return
    
    for payment in pending_payments[:5]:  # Show first 5
        user = users_col.find_one({"user_id": payment['user_id']})
        username = user.get('username', 'Unknown') if user else 'Unknown'
        
        text = f"📋 **Payment Request**\n\n"
        text += f"🆔 ID: `{payment['_id']}`\n"
        text += f"👤 User: {payment['user_id']} (@{username})\n"
        text += f"💰 Package: {payment['package']} points\n"
        text += f"💵 Amount: ₹{payment['amount']}\n"
        text += f"📅 Date: {payment['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_payment_{payment['_id']}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_payment_{payment['_id']}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Don't edit the original message, just send new ones

async def approve_payment(query, user_id, payment_id, context):
    """Approve payment and add points to user"""
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Unauthorized")
        return
    
    from bson.objectid import ObjectId
    payment = payments_col.find_one({"_id": ObjectId(payment_id)})
    
    if not payment:
        await query.edit_message_text("❌ Payment not found")
        return
    
    # Update payment status
    payments_col.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": {"status": "approved", "approved_by": user_id, "approved_at": datetime.now()}}
    )
    
    # Add points to user
    points = POINT_PACKAGES[payment['package']]['points']
    users_col.update_one(
        {"user_id": payment['user_id']},
        {"$inc": {"points": points}}
    )
    
    # Notify user
    try:
        await context.bot.send_message(
            chat_id=payment['user_id'],
            text=get_text(payment['user_id'], "payment_approved", points=points)
        )
    except:
        pass
    
    await query.edit_message_text(f"✅ Payment approved! {points} points added to user {payment['user_id']}")

async def reject_payment(query, user_id, payment_id, context):
    """Reject payment"""
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Unauthorized")
        return
    
    from bson.objectid import ObjectId
    payment = payments_col.find_one({"_id": ObjectId(payment_id)})
    
    if not payment:
        await query.edit_message_text("❌ Payment not found")
        return
    
    # Update payment status
    payments_col.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": {"status": "rejected", "rejected_by": user_id, "rejected_at": datetime.now()}}
    )
    
    # Notify user
    try:
        await context.bot.send_message(
            chat_id=payment['user_id'],
            text=get_text(payment['user_id'], "payment_rejected")
        )
    except:
        pass
    
    await query.edit_message_text(f"❌ Payment rejected for user {payment['user_id']}")

async def generate_gift(query, user_id, points, context):
    """Generate gift code - /gift command and button both work"""
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Unauthorized")
        return
    
    code = generate_gift_code()
    gift_data = {
        "code": code,
        "points": points,
        "created_by": user_id,
        "created_at": datetime.now(),
        "used_by": None,
        "used_at": None
        # No expiry - never expires
    }
    gift_codes_col.insert_one(gift_data)
    
    text = get_text(user_id, "gift_created", code=code, points=points)
    await query.edit_message_text(text, parse_mode='Markdown')

async def gift_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gift command - Create gift code"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Unauthorized")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /gift <points>\nExample: /gift 14")
        return
    
    try:
        points = int(context.args[0])
        if points <= 0:
            await update.message.reply_text("❌ Points must be positive")
            return
        
        code = generate_gift_code()
        gift_data = {
            "code": code,
            "points": points,
            "created_by": user_id,
            "created_at": datetime.now(),
            "used_by": None,
            "used_at": None
            # No expiry
        }
        gift_codes_col.insert_one(gift_data)
        
        text = get_text(user_id, "gift_created", code=code, points=points)
        await update.message.reply_text(text, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ Invalid points value")

# ==================== MESSAGE HANDLERS ====================
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

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo/screenshot messages"""
    user_id = update.effective_user.id
    
    # Check if user was expecting to send screenshot
    package_key = context.user_data.get('pending_package')
    if not package_key:
        await update.message.reply_text("Please use /start first")
        return
    
    package = POINT_PACKAGES[package_key]
    
    # Save payment request with screenshot
    payment_data = {
        "user_id": user_id,
        "username": update.effective_user.username,
        "package": package_key,
        "amount": package['price'],
        "timestamp": datetime.now(),
        "status": "pending",
        "has_screenshot": True
    }
    result = payments_col.insert_one(payment_data)
    payment_id = str(result.inserted_id)
    
    # Forward screenshot to all admins with payment info
    caption = f"💰 **New Payment Request**\n\n"
    caption += f"👤 **User:** {user_id}\n"
    caption += f"📝 **Name:** {update.effective_user.first_name}\n"
    caption += f"🆔 **Username:** @{update.effective_user.username or 'None'}\n"
    caption += f"💎 **Package:** {package_key} points\n"
    caption += f"💵 **Amount:** ₹{package['price']}\n"
    caption += f"🆔 **Payment ID:** `{payment_id}`\n"
    caption += f"📅 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Create approve/reject buttons
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_payment_{payment_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_payment_{payment_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    for admin_id in ADMIN_IDS:
        try:
            # Send photo with caption and buttons
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=update.message.photo[-1].file_id,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to forward to admin {admin_id}: {e}")
    
    # Clear pending package
    context.user_data['pending_package'] = None
    
    # Confirm to user
    await update.message.reply_text(get_text(user_id, "payment_request_sent"))

async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id_to_check):
    user_id = update.effective_user.id
    
    user = users_col.find_one({"user_id": user_id})
    if not user or user.get("points", 0) < 10:
        await update.message.reply_text(
            get_text(user_id, "insufficient_points", points=user.get("points", 0) if user else 0)
        )
        context.user_data['action'] = None
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
                
                # Send result message
                sent_msg = await update.message.reply_text(result_text)
                
                # Store message ID for reaction (but don't send extra message)
                context.user_data['reaction_for_message'] = sent_msg.message_id
                
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
    
    context.user_data['action'] = None

async def redeem_gift(update: Update, context: ContextTypes.DEFAULT_TYPE, code):
    user_id = update.effective_user.id
    
    gift = gift_codes_col.find_one({
        "code": code.strip().upper(),
        "used_by": None
        # No expiry check - never expires
    })
    
    if not gift:
        await update.message.reply_text(get_text(user_id, "gift_code_invalid"))
        context.user_data['action'] = None
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
    # No reaction for gift redemption
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
    
    await update.message.reply_text(get_text(user_id, "msg_sent"))
    context.user_data['action'] = None

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /redeem <gift_code>")
        return
    
    code = context.args[0]
    await redeem_gift(update, context, code)

# ==================== CONVERSATION HANDLER FOR SCREENSHOT ====================
async def screenshot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle screenshot in conversation"""
    if update.message.photo:
        return await handle_photo(update, context)
    else:
        await update.message.reply_text("❌ Please send a photo/screenshot")
        return WAITING_SCREENSHOT

# ==================== MAIN ====================
def main():
    print("\n" + "="*60)
    print("🚀 STARTING VIP BOT...")
    print("="*60)
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"👥 Admins: {ADMIN_IDS}")
    print(f"💳 UPI ID: {UPI_ID}")
    print(f"💎 Points: 1 = ₹{POINT_PRICE}")
    print("="*60)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for screenshot
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^send_screenshot$")],
        states={
            WAITING_SCREENSHOT: [MessageHandler(filters.PHOTO, screenshot_handler)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("redeem", redeem_command))
    app.add_handler(CommandHandler("gift", gift_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("✅ Bot is ready! Press Ctrl+C to stop.")
    print("="*60 + "\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
