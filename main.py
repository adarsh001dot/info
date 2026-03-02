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
from bson.objectid import ObjectId

# ==================== LOAD ENVIRONMENT VARIABLES ====================
load_dotenv()

# Get MongoDB URI from .env file
MONGO_URI = os.getenv('MONGODB_URI')

if not MONGO_URI:
    print("❌ ERROR: MONGODB_URI not found in .env file!")
    print("Please create .env file with: MONGODB_URI=your_connection_string")
    exit(1)

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8432105036:AAF_hiRAwU7N2nCVWakv9pjb1zOT4yfc-zk"
OWNER_ID = 7459756974
ADMIN_IDS = [7459756974, 2011028235]
ADMIN_USERNAME = "@VIP_X_OFFICIAL"  # Admin username with underscore

# NEW API CONFIGURATION
API_URL = "http://api.subhxcosmo.in/api"
API_KEY = "suryanshHacker"  # API key from the URL

# UPI ID for payments
UPI_ID = "nanhin.3@ptaxis"

# Price Configuration: 1 Point = ₹5
POINT_PRICE = 5
WELCOME_BONUS = 2
CHECK_PRICE = 1  # 1 point per search

# Point Packages
POINT_PACKAGES = {
    "5": {"points": 5, "price": 25, "emoji": "⚡"},
    "10": {"points": 10, "price": 50, "emoji": "💫"},
    "15": {"points": 15, "price": 75, "emoji": "✨"},
    "20": {"points": 20, "price": 100, "emoji": "⭐"},
    "30": {"points": 30, "price": 150, "emoji": "🌟"},
    "50": {"points": 50, "price": 250, "emoji": "💎"},
    "100": {"points": 100, "price": 500, "emoji": "👑"},
}

# Gift Packages
GIFT_PACKAGES = {
    "5": {"points": 5, "emoji": "⚡"},
    "10": {"points": 10, "emoji": "💫"},
    "15": {"points": 15, "emoji": "✨"},
    "20": {"points": 20, "emoji": "⭐"},
    "30": {"points": 30, "emoji": "🌟"},
    "50": {"points": 50, "emoji": "💎"},
    "100": {"points": 100, "emoji": "👑"},
}

REACTIONS = ["❤️‍🔥", "💀", "😈", "☠️", "💘", "💝", "💕", "💞", "💓", "💗"]

# Conversation states
WAITING_SCREENSHOT = 1
WAITING_ADMIN_REPLY = 2

# ==================== PROFESSIONAL UI DESIGNS ====================
BORDER = "━" * 30

def format_points_display(points):
    """Format points display"""
    return f"💎 **Points:** `{points}`"

def format_price(amount):
    """Format price display"""
    return f"💰 **₹{amount}**"

# Professional UI Templates with admin name
UI = {
    "welcome": """
╔════════════════════════════════════╗
║     🎯 VIP USER LOOKUP BOT 🎯      ║
║         PROFESSIONAL EDITION       ║
╚════════════════════════════════════╝

👋 **Welcome, {name}!**

{points_display}

📊 **YOUR STATS:**
├─ 🆔 ID: `{user_id}`
├─ 💎 Points Balance: `{points}`
├─ 🔍 Total Searches: `{searches}`
└─ 📅 Joined: `{joined}`

📞 **ADMIN CONTACT:** {admin}

⚡ **QUICK ACTIONS:**
Simply click a button below to get started!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "check_user": """
╔════════════════════════════════════╗
║        🔍 USER LOOKUP SYSTEM       ║
╚════════════════════════════════════╝

📤 **Please send the Telegram User ID**
you want to lookup.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **Example:** `2011028235`
💎 **Cost:** `1 Point` per lookup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "result": """
╔════════════════════════════════════╗
║        ✅ USER DETAILS FOUND       ║
╚════════════════════════════════════╝

📱 **CONTACT INFORMATION:**
├─ 🌍 Country: `{country}`
├─ 📞 Country Code: `{code}`
└─ 📱 Phone Number: `{number}`

💎 **POINTS UPDATED:**
├─ Deducted: `1 Point`
└─ Remaining: `{remaining}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Use /start for main menu
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "insufficient_points": """
╔════════════════════════════════════╗
║        ❌ INSUFFICIENT POINTS      ║
╚════════════════════════════════════╝

📊 **CURRENT BALANCE:**
├─ 💎 Points: `{points}`
└─ 🔍 Required: `1 Point`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **SOLUTIONS:**
├─ 1️⃣ Buy points from store
├─ 2️⃣ Use gift code if you have
└─ 3️⃣ Contact {admin} for help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "buy_points": """
╔════════════════════════════════════╗
║        💰 POINTS PURCHASE          ║
╚════════════════════════════════════╝

📊 **PRICE CHART:** `1 Point = ₹{price}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "package_display": """
{emoji} **{points} Points** ─ {price_display}
└─ 💎 Cost per search: `{per_search}`
""",
    
    "payment_info": """
╔════════════════════════════════════╗
║        💳 PAYMENT DETAILS          ║
╚════════════════════════════════════╝

📦 **PACKAGE:** {emoji} {points} Points
💵 **AMOUNT:** ₹{price}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏦 **UPI DETAILS:**
└─ `{upi}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📸 **INSTRUCTIONS:**
1️⃣ Make payment to above UPI ID
2️⃣ Click "Send Screenshot" button
3️⃣ Upload payment screenshot
4️⃣ Wait for admin approval

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "screenshot_prompt": """
╔════════════════════════════════════╗
║        📸 SCREENSHOT UPLOAD        ║
╚════════════════════════════════════╝

✅ **Please send the payment screenshot.**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 **REQUIREMENTS:**
├─ Clear screenshot of UPI payment
├─ UPI ID should be visible
├─ Amount should match
└─ Transaction ID visible

⏳ Admin will verify and add points shortly.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "payment_sent": """
╔════════════════════════════════════╗
║     ✅ PAYMENT REQUEST SENT        ║
╚════════════════════════════════════╝

📤 Your payment request has been 
   forwarded to admin.

⏳ **Expected Time:** 5-10 minutes
📞 **Contact:** {admin} if urgent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "gift_code_prompt": """
╔════════════════════════════════════╗
║        🎁 GIFT CODE REDEEM         ║
╚════════════════════════════════════╝

📤 **Please send your gift code.**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **Example:** `ABC123XYZ789`
✨ Codes are case-insensitive
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "gift_success": """
╔════════════════════════════════════╗
║     ✅ GIFT CODE REDEEMED          ║
╚════════════════════════════════════╝

🎉 **Congratulations!**
├─ 💎 Points Added: `{points}`
└─ 💰 Value: ₹{value}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "gift_invalid": """
╔════════════════════════════════════╗
║        ❌ INVALID GIFT CODE        ║
╚════════════════════════════════════╝

❌ The code you entered is invalid
   or has already been used.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **Need help?** Contact {admin}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "contact_admin": """
╔════════════════════════════════════╗
║        📞 CONTACT ADMIN            ║
╚════════════════════════════════════╝

📤 **Please type your message below.**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Admin will reply as soon as possible
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "msg_sent": """
╔════════════════════════════════════╗
║        ✅ MESSAGE SENT             ║
╚════════════════════════════════════╝

📤 Your message has been forwarded
   to the admin team.

⏳ **Response time:** 5-30 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "owner_panel": """
╔════════════════════════════════════╗
║        👑 OWNER PANEL              ║
╚════════════════════════════════════╝

📊 **SYSTEM STATISTICS:**
├─ 👥 Total Users: `{users}`
├─ 💎 Total Points: `{points}`
├─ 💰 Today Income: `₹{today_income}`
├─ 📅 Month Income: `₹{month_income}`
└─ ⏳ Pending: `{pending}` payments

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ **ADMIN TOOLS:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "payment_request_admin": """
╔════════════════════════════════════╗
║     💰 NEW PAYMENT REQUEST         ║
╚════════════════════════════════════╝

👤 **USER DETAILS:**
├─ 🆔 ID: `{user_id}`
├─ 📝 Name: {name}
└─ 🆔 Username: @{username}

📦 **PACKAGE INFO:**
├─ 💎 Points: {points}
└─ 💵 Amount: ₹{amount}

📅 **TIME:** {time}
🆔 **Payment ID:** `{payment_id}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ **ACTIONS:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "payment_approved_user": """
╔════════════════════════════════════╗
║     ✅ PAYMENT APPROVED            ║
╚════════════════════════════════════╝

🎉 **Your payment has been approved!**

📦 **PACKAGE:** {points} Points
💰 **AMOUNT:** ₹{amount}
💎 **NEW BALANCE:** `{balance}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ You can now use /start
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "payment_rejected_user": """
╔════════════════════════════════════╗
║     ❌ PAYMENT REJECTED            ║
╚════════════════════════════════════╝

❌ Your payment has been rejected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **POSSIBLE REASONS:**
├─ Invalid screenshot
├─ Amount mismatch
├─ UPI ID not visible
└─ Transaction failed

📞 **Contact:** {admin} for help
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "gift_created_admin": """
╔════════════════════════════════════╗
║     ✅ GIFT CODE GENERATED         ║
╚════════════════════════════════════╝

🎁 **GIFT CODE DETAILS:**
├─ 📦 Points: `{points}`
├─ 💰 Value: ₹{value}
└─ 🆔 Code: `{code}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 **Share this code with user:**
`{code}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "no_pending": """
╔════════════════════════════════════╗
║        📭 NO PENDING PAYMENTS      ║
╚════════════════════════════════════╝

✅ All payments have been processed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    
    "admin_reply_prompt": """
✏️ **Reply to user {user_id}**

Type your message below. It will be sent directly to the user.
""",
    
    "admin_reply_sent": """
✅ **Reply sent to user {user_id}**
""",
    
    "admin_reply_received": """
📨 **Message from Admin {admin}:**

{message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
To reply, use /contact command
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
}

# Languages
LANGUAGES = {
    "hi": {
        "check_user": "🔍 यूजर चेक करें",
        "buy_points": "💰 पॉइंट्स खरीदें",
        "gift_code": "🎁 गिफ्ट कोड",
        "contact_admin": "📞 एडमिन से संपर्क",
        "language": "🌐 भाषा बदलें",
        "cancel": "❌ रद्द करें",
        "approve": "✅ Approve",
        "reject": "❌ Reject",
        "send_screenshot": "📸 Send Screenshot",
        "view_pending": "📋 View Pending",
        "back": "🔙 Back",
        "generate": "🎁 Generate",
        "reply": "✏️ Reply",
    },
    "en": {
        "check_user": "🔍 Check User",
        "buy_points": "💰 Buy Points",
        "gift_code": "🎁 Gift Code",
        "contact_admin": "📞 Contact Admin",
        "language": "🌐 Change Language",
        "cancel": "❌ Cancel",
        "approve": "✅ Approve",
        "reject": "❌ Reject",
        "send_screenshot": "📸 Send Screenshot",
        "view_pending": "📋 View Pending",
        "back": "🔙 Back",
        "generate": "🎁 Generate",
        "reply": "✏️ Reply",
    }
}

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
        admin_msgs_col.create_index('replied')
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

def disable_buttons(reply_markup):
    """Disable all buttons in a keyboard"""
    if not reply_markup or not reply_markup.inline_keyboard:
        return None
    
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            # Create disabled version of button
            new_row.append(InlineKeyboardButton(
                text=f"✓ {button.text}",  # Add checkmark to show processed
                callback_data="disabled"
            ))
        new_keyboard.append(new_row)
    
    return InlineKeyboardMarkup(new_keyboard)

def escape_markdown(text):
    """Escape markdown special characters but PRESERVE underscores"""
    if not text:
        return ""
    
    # List of characters that need escaping in Markdown
    # IMPORTANT: Underscore (_) is NOT included here to preserve it
    escape_chars = ['*', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    existing_user = users_col.find_one({"user_id": user_id})
    
    if not existing_user:
        user_data = {
            "user_id": user_id,
            "username": user.username,  # Store original username with underscores
            "first_name": user.first_name,
            "last_name": user.last_name,
            "points": WELCOME_BONUS,
            "lang": "en",
            "joined_date": datetime.now(),
            "total_used": 0,
            "total_spent": 0
        }
        users_col.insert_one(user_data)
        points = WELCOME_BONUS
        searches = 0
        joined = datetime.now().strftime("%Y-%m-%d")
    else:
        points = existing_user.get("points", 0)
        searches = existing_user.get("total_used", 0)
        joined = existing_user.get("joined_date", datetime.now()).strftime("%Y-%m-%d")
    
    # Don't escape the name - preserve all characters
    name = user.first_name
    
    welcome_text = UI["welcome"].format(
        name=name,
        points_display=format_points_display(points),
        user_id=user_id,
        points=points,
        searches=searches,
        joined=joined,
        admin=ADMIN_USERNAME  # This will show @VIP_X_OFFICIAL with underscore
    )
    
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
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # Handle disabled buttons
    if data == "disabled":
        await query.answer("This action has already been processed!", show_alert=True)
        return
    
    if data == "check_user":
        context.user_data['action'] = 'check_user'
        await query.edit_message_text(UI["check_user"], parse_mode='Markdown')
        
    elif data == "buy_points":
        await show_point_packages(query, user_id)
        
    elif data == "gift_code":
        context.user_data['action'] = 'gift_code'
        await query.edit_message_text(UI["gift_code_prompt"], parse_mode='Markdown')
        
    elif data == "contact_admin":
        context.user_data['action'] = 'contact_admin'
        await query.edit_message_text(UI["contact_admin"], parse_mode='Markdown')
        
    elif data == "change_lang":
        await change_language(query, user_id)
        
    elif data.startswith("buy_package_"):
        package = data.replace("buy_package_", "")
        await process_payment(query, user_id, package, context)
        
    elif data == "send_screenshot":
        package_key = context.user_data.get('pending_package')
        if package_key:
            await query.edit_message_text(UI["screenshot_prompt"], parse_mode='Markdown')
            return WAITING_SCREENSHOT
        
    elif data == "owner_panel":
        await owner_panel(query, user_id, context)
        
    elif data == "view_pending":
        await view_pending_payments(query, user_id, context)
        
    elif data.startswith("approve_payment_"):
        if user_id == OWNER_ID or user_id in ADMIN_IDS:
            payment_id = data.replace("approve_payment_", "")
            await approve_payment(query, user_id, payment_id, context)
            
    elif data.startswith("reject_payment_"):
        if user_id == OWNER_ID or user_id in ADMIN_IDS:
            payment_id = data.replace("reject_payment_", "")
            await reject_payment(query, user_id, payment_id, context)
            
    elif data.startswith("reply_to_"):
        if user_id == OWNER_ID or user_id in ADMIN_IDS:
            target_user_id = int(data.replace("reply_to_", ""))
            context.user_data['reply_to_user'] = target_user_id
            await query.edit_message_text(
                UI["admin_reply_prompt"].format(user_id=target_user_id),
                parse_mode='Markdown'
            )
            return WAITING_ADMIN_REPLY
        
    elif data.startswith("gen_gift_"):
        if user_id == OWNER_ID or user_id in ADMIN_IDS:
            points = int(data.replace("gen_gift_", ""))
            await generate_gift(query, user_id, points, context)
            
    elif data.startswith("lang_"):
        lang = data.replace("lang_", "")
        users_col.update_one({"user_id": user_id}, {"$set": {"lang": lang}})
        await query.edit_message_text("✅ Language Changed! Send /start again.")
        
    elif data == "back":
        context.user_data.clear()
        # Need to recreate the update for start function
        new_update = Update(update.update_id, message=query.message)
        new_update.effective_user = update.effective_user
        new_update.effective_chat = update.effective_chat
        await start(new_update, context)
    
    return ConversationHandler.END

async def show_point_packages(query, user_id):
    """Show available point packages"""
    text = UI["buy_points"].format(price=POINT_PRICE)
    
    for key, package in POINT_PACKAGES.items():
        per_search = f"₹{POINT_PRICE} per search"
        price_display = format_price(package['price'])
        text += UI["package_display"].format(
            emoji=package['emoji'],
            points=package['points'],
            price_display=price_display,
            per_search=per_search
        )
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    keyboard = []
    row = []
    for i, (key, package) in enumerate(POINT_PACKAGES.items()):
        btn_text = f"{package['emoji']} {package['points']}"
        row.append(InlineKeyboardButton(btn_text, callback_data=f"buy_package_{key}"))
        
        if len(row) == 3 or i == len(POINT_PACKAGES) - 1:
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "cancel"), callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def process_payment(query, user_id, package_key, context):
    """Process payment for package"""
    package = POINT_PACKAGES[package_key]
    
    context.user_data['pending_package'] = package_key
    context.user_data['pending_amount'] = package['price']
    
    text = UI["payment_info"].format(
        emoji=package['emoji'],
        points=package['points'],
        price=package['price'],
        upi=UPI_ID
    )
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "send_screenshot"), callback_data="send_screenshot")],
        [InlineKeyboardButton(get_text(user_id, "cancel"), callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def change_language(query, user_id):
    keyboard = [
        [InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Choose Language / भाषा चुनें:", reply_markup=reply_markup)

async def owner_panel(query, user_id, context):
    """Owner panel"""
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Unauthorized")
        return
    
    total_users = users_col.count_documents({})
    total_points = sum(user.get("points", 0) for user in users_col.find())
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_payments = list(payments_col.find({"timestamp": {"$gte": today_start}, "status": "approved"}))
    today_income = sum(p.get('amount', 500) for p in today_payments)
    
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_payments = list(payments_col.find({"timestamp": {"$gte": month_start}, "status": "approved"}))
    month_income = sum(p.get('amount', 500) for p in month_payments)
    
    pending = payments_col.count_documents({"status": "pending"})
    
    text = UI["owner_panel"].format(
        users=total_users,
        points=total_points,
        today_income=today_income,
        month_income=month_income,
        pending=pending
    )
    
    keyboard = []
    
    if pending > 0:
        keyboard.append([InlineKeyboardButton(f"📋 View Pending Payments ({pending})", callback_data="view_pending")])
    
    gift_row = []
    for i, (key, package) in enumerate(GIFT_PACKAGES.items()):
        btn_text = f"{package['emoji']} {package['points']}"
        gift_row.append(InlineKeyboardButton(btn_text, callback_data=f"gen_gift_{package['points']}"))
        
        if len(gift_row) == 4 or i == len(GIFT_PACKAGES) - 1:
            keyboard.append(gift_row)
            gift_row = []
    
    if pending == 0:
        keyboard.append([InlineKeyboardButton("📋 View Pending", callback_data="view_pending")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def view_pending_payments(query, user_id, context):
    """View all pending payments"""
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Unauthorized")
        return
    
    pending_payments = list(payments_col.find({"status": "pending"}).sort("timestamp", -1))
    
    if not pending_payments:
        await query.edit_message_text(UI["no_pending"], parse_mode='Markdown')
        return
    
    await query.edit_message_text("📋 **Fetching pending payments...**")
    
    for payment in pending_payments:
        user = users_col.find_one({"user_id": payment['user_id']})
        name = user.get('first_name', 'Unknown') if user else 'Unknown'
        username = user.get('username', 'None') if user else 'None'
        
        points = POINT_PACKAGES[payment['package']]['points'] if payment['package'] in POINT_PACKAGES else 0
        
        text = UI["payment_request_admin"].format(
            user_id=payment['user_id'],
            name=name,
            username=username,
            points=points,
            amount=payment['amount'],
            time=payment['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            payment_id=str(payment['_id'])
        )
        
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
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="owner_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=user_id,
        text="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔍 End of pending payments list",
        reply_markup=reply_markup
    )

async def approve_payment(query, user_id, payment_id, context):
    """Approve payment - FIXED: Only works once with button disable"""
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Unauthorized")
        return
    
    try:
        # Disable the buttons immediately
        if query.message.reply_markup:
            disabled_markup = disable_buttons(query.message.reply_markup)
            await query.edit_message_reply_markup(reply_markup=disabled_markup)
        
        # Check if payment already processed
        payment = payments_col.find_one({"_id": ObjectId(payment_id)})
        
        if not payment:
            await query.edit_message_text("❌ Payment not found")
            return
        
        if payment.get('status') != 'pending':
            await query.edit_message_text(f"❌ Payment already {payment.get('status')}")
            return
        
        # Update payment status - ATOMIC operation
        result = payments_col.update_one(
            {"_id": ObjectId(payment_id), "status": "pending"},
            {"$set": {"status": "approved", "approved_by": user_id, "approved_at": datetime.now()}}
        )
        
        if result.modified_count == 0:
            await query.edit_message_text("❌ Payment already processed by someone else")
            return
        
        # Add points to user
        points = POINT_PACKAGES[payment['package']]['points']
        
        user = users_col.find_one({"user_id": payment['user_id']})
        current_points = user.get('points', 0) if user else 0
        
        users_col.update_one(
            {"user_id": payment['user_id']},
            {"$inc": {"points": points}}
        )
        
        new_balance = current_points + points
        
        # Notify user
        try:
            user_text = UI["payment_approved_user"].format(
                points=points,
                amount=payment['amount'],
                balance=new_balance
            )
            await context.bot.send_message(
                chat_id=payment['user_id'],
                text=user_text,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")
        
        # Update the button message
        await query.edit_message_text(
            f"✅ Payment approved!\n\n"
            f"User: {payment['user_id']}\n"
            f"Points: {points}\n"
            f"Amount: ₹{payment['amount']}\n"
            f"New Balance: {new_balance}"
        )
        
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {str(e)}")

async def reject_payment(query, user_id, payment_id, context):
    """Reject payment - FIXED: Only works once with button disable"""
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Unauthorized")
        return
    
    try:
        # Disable the buttons immediately
        if query.message.reply_markup:
            disabled_markup = disable_buttons(query.message.reply_markup)
            await query.edit_message_reply_markup(reply_markup=disabled_markup)
        
        # Check if payment already processed
        payment = payments_col.find_one({"_id": ObjectId(payment_id)})
        
        if not payment:
            await query.edit_message_text("❌ Payment not found")
            return
        
        if payment.get('status') != 'pending':
            await query.edit_message_text(f"❌ Payment already {payment.get('status')}")
            return
        
        # Update payment status - ATOMIC operation
        result = payments_col.update_one(
            {"_id": ObjectId(payment_id), "status": "pending"},
            {"$set": {"status": "rejected", "rejected_by": user_id, "rejected_at": datetime.now()}}
        )
        
        if result.modified_count == 0:
            await query.edit_message_text("❌ Payment already processed by someone else")
            return
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=payment['user_id'],
                text=UI["payment_rejected_user"].format(admin=ADMIN_USERNAME),
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")
        
        await query.edit_message_text(f"❌ Payment rejected for user {payment['user_id']}")
        
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {str(e)}")

async def generate_gift(query, user_id, points, context):
    """Generate gift code"""
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Unauthorized")
        return
    
    code = generate_gift_code()
    gift_data = {
        "code": code,
        "points": points,
        "value": points * POINT_PRICE,
        "created_by": user_id,
        "created_at": datetime.now(),
        "used_by": None,
        "used_at": None
    }
    gift_codes_col.insert_one(gift_data)
    
    text = UI["gift_created_admin"].format(
        points=points,
        value=points * POINT_PRICE,
        code=code
    )
    
    await query.edit_message_text(text, parse_mode='Markdown')

async def gift_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gift command"""
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
            "value": points * POINT_PRICE,
            "created_by": user_id,
            "created_at": datetime.now(),
            "used_by": None,
            "used_at": None
        }
        gift_codes_col.insert_one(gift_data)
        
        text = UI["gift_created_admin"].format(
            points=points,
            value=points * POINT_PRICE,
            code=code
        )
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
    
    # Clear pending package
    context.user_data['pending_package'] = None
    
    # Forward to admins
    for admin_id in ADMIN_IDS:
        try:
            points = package['points']
            
            caption = UI["payment_request_admin"].format(
                user_id=user_id,
                name=update.effective_user.first_name,
                username=update.effective_user.username or 'None',
                points=points,
                amount=package['price'],
                time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                payment_id=payment_id
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_payment_{payment_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_payment_{payment_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=update.message.photo[-1].file_id,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to forward to admin {admin_id}: {e}")
    
    # Confirm to user
    await update.message.reply_text(UI["payment_sent"].format(admin=ADMIN_USERNAME), parse_mode='Markdown')

async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id_to_check):
    """Check user via NEW API"""
    user_id = update.effective_user.id
    
    user = users_col.find_one({"user_id": user_id})
    if not user or user.get("points", 0) < CHECK_PRICE:
        await update.message.reply_text(
            UI["insufficient_points"].format(
                points=user.get("points", 0) if user else 0,
                admin=ADMIN_USERNAME
            ),
            parse_mode='Markdown'
        )
        context.user_data['action'] = None
        return
    
    try:
        await update.message.reply_text("⏳ **Processing your request...**", parse_mode='Markdown')
        
        # NEW API CALL
        params = {
            "key": API_KEY,
            "type": "sms",
            "term": user_id_to_check
        }
        
        response = requests.get(
            API_URL,
            params=params,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # Check the nested result structure
            if data.get("success") and data.get("result", {}).get("success"):
                result_data = data["result"]
                
                new_points = user["points"] - CHECK_PRICE
                users_col.update_one(
                    {"user_id": user_id},
                    {"$set": {"points": new_points}, "$inc": {"total_used": 1}}
                )
                
                result_text = UI["result"].format(
                    country=result_data.get("country", "N/A"),
                    code=result_data.get("country_code", "N/A"),
                    number=result_data.get("number", "N/A"),
                    remaining=new_points
                )
                
                await update.message.reply_text(result_text, parse_mode='Markdown')
                
            else:
                error_msg = data.get("result", {}).get("msg", "User not found")
                await update.message.reply_text(
                    f"❌ **{error_msg}**\n\nPlease check the ID and try again.",
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text(
                "❌ **API Error**\n\nPlease try again later or contact admin.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Error:** {str(e)}",
            parse_mode='Markdown'
        )
    
    context.user_data['action'] = None

async def redeem_gift(update: Update, context: ContextTypes.DEFAULT_TYPE, code):
    """Redeem gift code"""
    user_id = update.effective_user.id
    
    gift = gift_codes_col.find_one({
        "code": code.strip().upper(),
        "used_by": None
    })
    
    if not gift:
        await update.message.reply_text(
            UI["gift_invalid"].format(admin=ADMIN_USERNAME),
            parse_mode='Markdown'
        )
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
        UI["gift_success"].format(
            points=gift["points"],
            value=gift["points"] * POINT_PRICE
        ),
        parse_mode='Markdown'
    )
    context.user_data['action'] = None

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, message):
    """Contact admin - User to Admin"""
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
    forward_text += f"👤 **User:** `{user_id}`\n"
    forward_text += f"📝 **Name:** {update.effective_user.first_name}\n"
    forward_text += f"🆔 **Username:** @{update.effective_user.username or 'None'}\n"
    forward_text += f"💬 **Message:** {message}\n"
    forward_text += f"🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Add reply button for admin
    keyboard = [[InlineKeyboardButton("✏️ Reply to User", callback_data=f"reply_to_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                admin_id,
                forward_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to forward to admin {admin_id}: {e}")
    
    await update.message.reply_text(UI["msg_sent"], parse_mode='Markdown')
    context.user_data['action'] = None

async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin reply to user - FIXED: Now working properly"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Unauthorized")
        return ConversationHandler.END
    
    # Get the target user ID from context
    target_user_id = context.user_data.get('reply_to_user')
    if not target_user_id:
        await update.message.reply_text("❌ No user selected to reply to")
        return ConversationHandler.END
    
    message = update.message.text
    
    # Send reply to user
    try:
        reply_text = UI["admin_reply_received"].format(
            admin=ADMIN_USERNAME,
            message=message
        )
        await context.bot.send_message(
            chat_id=target_user_id,
            text=reply_text,
            parse_mode='Markdown'
        )
        
        # Mark original message as replied
        admin_msgs_col.update_many(
            {"user_id": target_user_id, "replied": False},
            {"$set": {"replied": True, "replied_at": datetime.now(), "reply_by": user_id, "reply_text": message}}
        )
        
        await update.message.reply_text(
            UI["admin_reply_sent"].format(user_id=target_user_id),
            parse_mode='Markdown'
        )
        
        # Clear the reply target
        context.user_data['reply_to_user'] = None
        
        # End the conversation
        return ConversationHandler.END
        
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send reply: {str(e)}")
        return ConversationHandler.END

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /redeem <gift_code>")
        return
    
    code = context.args[0]
    await redeem_gift(update, context, code)

# ==================== CONVERSATION HANDLERS ====================
async def screenshot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle screenshot in conversation"""
    if update.message.photo:
        return await handle_photo(update, context)
    else:
        await update.message.reply_text("❌ Please send a photo/screenshot")
        return WAITING_SCREENSHOT

async def admin_reply_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin reply conversation - FIXED"""
    if update.message and update.message.text:
        return await admin_reply_handler(update, context)
    else:
        await update.message.reply_text("❌ Please send a text message")
        return WAITING_ADMIN_REPLY

# ==================== MAIN ====================
def main():
    print("\n" + "="*60)
    print("🚀 STARTING VIP BOT...")
    print("="*60)
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"👥 Admins: {ADMIN_IDS}")
    print(f"📞 Admin Username: {ADMIN_USERNAME}")
    print(f"💳 UPI ID: {UPI_ID}")
    print(f"💎 Points: 1 = ₹{POINT_PRICE}")
    print(f"🎁 Welcome Bonus: {WELCOME_BONUS} Points")
    print(f"🔍 Search Cost: {CHECK_PRICE} Point")
    print(f"📦 Packages: {len(POINT_PACKAGES)}")
    print(f"🌐 New API: {API_URL}")
    print("="*60)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for screenshot
    screenshot_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^send_screenshot$")],
        states={
            WAITING_SCREENSHOT: [MessageHandler(filters.PHOTO, screenshot_handler)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    # Conversation handler for admin reply - FIXED entry point
    admin_reply_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^reply_to_")],
        states={
            WAITING_ADMIN_REPLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply_conversation)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("redeem", redeem_command))
    app.add_handler(CommandHandler("gift", gift_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(screenshot_conv)
    app.add_handler(admin_reply_conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("✅ Bot is ready! Press Ctrl+C to stop.")
    print("="*60 + "\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
