"""
===========================================
🤖 COMPLETE TELEGRAM BOT - ALL FEATURES
===========================================
Developer:@VIP_X_OFFICIAL
Version: 4.0 (ULTIMATE)
Features: 100+ Features
Database: MongoDB (IST Timezone)
===========================================
"""

import logging
import asyncio
import random
import string
import requests
import csv
import os
import json
from datetime import datetime, timedelta
from pytz import timezone
from pymongo import MongoClient
from bson import ObjectId
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8432105036:AAF_hiRAwU7N2nCVWakv9pjb1zOT4yfc-zk"
MONGODB_URI = "mongodb+srv://nikilsaxena843_db_user:3gF2wyT4IjsFt0cY@vipbot.puv6gfk.mongodb.net/?appName=vipbot"
API_URL = "http://api.subhxcosmo.in/api"
API_KEY = "suryanshHacker"
OWNER_ID = 7459756974
OWNER_USERNAME = "@VIP_X_OFFICIAL"

# India Timezone
IST = timezone('Asia/Kolkata')

# Point Packages
POINT_PACKAGES = {
    "5": {"points": 5, "price": 25, "emoji": "⚡", "popular": False},
    "10": {"points": 10, "price": 50, "emoji": "💫", "popular": False},
    "15": {"points": 15, "price": 75, "emoji": "✨", "popular": False},
    "20": {"points": 20, "price": 100, "emoji": "⭐", "popular": True},
    "30": {"points": 30, "price": 150, "emoji": "🌟", "popular": False},
    "50": {"points": 50, "price": 250, "emoji": "💎", "popular": False},
    "100": {"points": 100, "price": 500, "emoji": "👑", "popular": True},
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

# Reactions
REACTIONS = ["❤️‍🔥", "💀", "😈", "☠️", "💘", "💝", "💕", "💞", "💓", "💗"]

# Conversation States
(
    CONTACT_ADMIN,
    GENERATE_CODE,
    ADD_POINTS,
    BROADCAST_MSG,
    BROADCAST_PHOTO,
    BROADCAST_VIDEO,
    ADD_REFERRAL,
    SEARCH_NUMBER,
    REDEEM_CODE,
    BUY_POINTS,
    USER_SETTINGS,
    FEEDBACK,
    REPORT_ISSUE,
    BAN_USER,
    WARN_USER,
    EXPORT_DATA,
    BACKUP_DB,
    MAINTENANCE_MODE,
    FORCE_JOIN,
    RATE_LIMIT,
    API_SETTINGS,
    PACKAGE_SETTINGS,
    REACTION_SETTINGS,
) = range(23)

# ==================== DATABASE CONNECTION ====================
try:
    client = MongoClient(MONGODB_URI)
    db = client['vip_bot']
    
    # Collections
    users_col = db['users']
    transactions_col = db['transactions']
    gift_codes_col = db['gift_codes']
    orders_col = db['orders']
    settings_col = db['settings']
    backup_col = db['backup']
    referral_col = db['referrals']
    search_history_col = db['search_history']
    feedback_col = db['feedback']
    reports_col = db['reports']
    blacklist_col = db['blacklist']
    broadcast_col = db['broadcast']
    
    # Create indexes
    users_col.create_index('user_id', unique=True)
    gift_codes_col.create_index('code', unique=True)
    orders_col.create_index('order_id', unique=True)
    referral_col.create_index('referral_code', unique=True)
    blacklist_col.create_index('user_id', unique=True)
    
    # Default settings
    if not settings_col.find_one({'key': 'bot_settings'}):
        settings_col.insert_one({
            'key': 'bot_settings',
            'maintenance_mode': False,
            'force_join_channel': None,
            'rate_limit': 5,
            'reactions_enabled': True,
            'api_url': API_URL,
            'api_key': API_KEY,
            'point_rate': 5,
            'min_withdraw': 100,
            'referral_bonus': 10,
            'daily_bonus': 5,
            'welcome_bonus': 10,
            'created_at': datetime.now(IST)
        })
    
    # Stats
    current_time = datetime.now(IST).strftime("%d-%m-%Y %I:%M:%S %p")
    print("="*50)
    print("✅ DATABASE CONNECTED SUCCESSFULLY!")
    print("="*50)
    print(f"🕐 IST Time: {current_time}")
    print(f"📊 Database: vip_bot")
    print(f"📁 Collections:")
    print(f"   ├─ users: {users_col.count_documents({})} documents")
    print(f"   ├─ transactions: {transactions_col.count_documents({})}")
    print(f"   ├─ gift_codes: {gift_codes_col.count_documents({})}")
    print(f"   ├─ orders: {orders_col.count_documents({})}")
    print(f"   ├─ referrals: {referral_col.count_documents({})}")
    print(f"   └─ search_history: {search_history_col.count_documents({})}")
    print("="*50)
    
except Exception as e:
    print(f"❌ DATABASE ERROR: {e}")
    exit(1)

# ==================== LANGUAGE STRINGS ====================
LANG = {
    'hi': {
        # Basic
        'welcome': "👋 स्वागत है! कृपया भाषा चुनें:",
        'main_menu': "🏠 मुख्य मेनू\n\n👤 उपयोगकर्ता: {}\n💰 पॉइंट्स: {}\n📊 कुल सर्च: {}",
        'loading': "⏳ कृपया प्रतीक्षा करें...",
        'success': "✅ सफल!",
        'error': "❌ त्रुटि!",
        'back': "🔙 वापस",
        'cancel': "❌ रद्द करें",
        
        # Points
        'check_points': "💰 आपके पॉइंट्स: {}\n\n1 पॉइंट = ₹5\n1 सर्च = 1 पॉइंट",
        'buy_points': "🛒 पॉइंट्स खरीदें\n\nपैकेज चुनें:",
        'insufficient_points': "❌ अपर्याप्त पॉइंट्स! आपके पास {} पॉइंट्स हैं।",
        
        # Search
        'enter_number': "📱 10 अंकों का मोबाइल नंबर दर्ज करें:",
        'invalid_number': "❌ अमान्य नंबर! केवल 10 अंक भारतीय नंबर दर्ज करें।",
        'processing': "⏳ प्रोसेसिंग... कृपया प्रतीक्षा करें।",
        'api_error': "❌ API त्रुटि! बाद में प्रयास करें।",
        'search_result': "✅ सफल!\n\n📱 नंबर: {}\n🌍 देश: {}\n📞 कोड: {}\n\n💎 बचे पॉइंट्स: {}\n🕐 समय: {}",
        
        # Gift Codes
        'gift_packages': "🎁 गिफ्ट कोड पैकेज:\nकितने पॉइंट्स का कोड चाहिए?",
        'enter_gift_code': "🎁 {}+ पॉइंट्स वाला गिफ्ट कोड दर्ज करें:",
        'invalid_code': "❌ अमान्य या इस्तेमाल किया गया कोड!",
        'code_success': "✅ {} पॉइंट्स जोड़े गए!\nनया बैलेंस: {}",
        
        # Profile
        'profile': "👤 प्रोफाइल\n\n🆔 आईडी: {}\n👤 नाम: {}\n📅 ज्वाइन: {}\n💰 पॉइंट्स: {}\n🔍 कुल सर्च: {}\n🎁 रिडीम: {}\n🤝 रेफरल: {}",
        'settings': "⚙️ सेटिंग्स\n\nभाषा, नोटिफिकेशन और प्राइवेसी सेटिंग्स",
        
        # Referral
        'referral': "🤝 रेफरल सिस्टम\n\nआपका रेफरल कोड: `{}`\nरेफरल लिंक: https://t.me/{}?start={}\n\nकमीशन: {} पॉइंट्स प्रति रेफरल\nकुल रेफरल: {}\nकुल कमीशन: {} पॉइंट्स",
        
        # Daily Bonus
        'daily_bonus': "🎁 डेली बोनस\n\nआपको {} पॉइंट्स मिले!\nअगला बोनस कल {} बजे",
        'already_claimed': "❌ आज का बोनस पहले ही ले चुके हो!\nअगला बोनस कल {} बजे",
        
        # Admin
        'admin_panel': "👑 एडमिन पैनल\n\n🕐 {} IST",
        
        # Contact
        'contact_admin': "📝 अपना संदेश लिखें (एडमिन जल्दी जवाब देगा):",
        'msg_sent': "✅ संदेश भेज दिया गया!",
        
        # History
        'search_history': "📋 हाल की सर्च (पिछले 10):\n\n{}",
        'transaction_history': "📊 हाल के ट्रांजैक्शन:\n\n{}",
        
        # Help
        'help_text': "❓ मदद\n\n/start - शुरू करें\n/profile - प्रोफाइल\n/points - पॉइंट्स\n/buy - खरीदें\n/redeem - कोड रिडीम\n/referral - रेफरल\n/history - हिस्ट्री\n/settings - सेटिंग्स\n/help - मदद",
    },
    'en': {
        # Basic
        'welcome': "👋 Welcome! Please select language:",
        'main_menu': "🏠 Main Menu\n\n👤 User: {}\n💰 Points: {}\n📊 Total Searches: {}",
        'loading': "⏳ Please wait...",
        'success': "✅ Success!",
        'error': "❌ Error!",
        'back': "🔙 Back",
        'cancel': "❌ Cancel",
        
        # Points
        'check_points': "💰 Your Points: {}\n\n1 Point = ₹5\n1 Search = 1 Point",
        'buy_points': "🛒 Buy Points\n\nChoose package:",
        'insufficient_points': "❌ Insufficient points! You have {} points.",
        
        # Search
        'enter_number': "📱 Enter 10-digit mobile number:",
        'invalid_number': "❌ Invalid number! Enter 10-digit Indian number only.",
        'processing': "⏳ Processing... Please wait.",
        'api_error': "❌ API Error! Try again later.",
        'search_result': "✅ Success!\n\n📱 Number: {}\n🌍 Country: {}\n📞 Code: {}\n\n💎 Remaining: {}\n🕐 Time: {}",
        
        # Gift Codes
        'gift_packages': "🎁 Gift Code Packages:\nHow many points code?",
        'enter_gift_code': "🎁 Enter {}+ points gift code:",
        'invalid_code': "❌ Invalid or used code!",
        'code_success': "✅ {} points added!\nNew balance: {}",
        
        # Profile
        'profile': "👤 Profile\n\n🆔 ID: {}\n👤 Name: {}\n📅 Joined: {}\n💰 Points: {}\n🔍 Total Searches: {}\n🎁 Redeemed: {}\n🤝 Referrals: {}",
        'settings': "⚙️ Settings\n\nLanguage, Notifications & Privacy settings",
        
        # Referral
        'referral': "🤝 Referral System\n\nYour Referral Code: `{}`\nReferral Link: https://t.me/{}?start={}\n\nCommission: {} points per referral\nTotal Referrals: {}\nTotal Commission: {} points",
        
        # Daily Bonus
        'daily_bonus': "🎁 Daily Bonus\n\nYou got {} points!\nNext bonus tomorrow at {}",
        'already_claimed': "❌ Already claimed today!\nNext bonus tomorrow at {}",
        
        # Admin
        'admin_panel': "👑 Admin Panel\n\n🕐 {} IST",
        
        # Contact
        'contact_admin': "📝 Write your message (Admin will reply soon):",
        'msg_sent': "✅ Message sent to admin!",
        
        # History
        'search_history': "📋 Recent Searches (Last 10):\n\n{}",
        'transaction_history': "📊 Recent Transactions:\n\n{}",
        
        # Help
        'help_text': "❓ Help\n\n/start - Start bot\n/profile - View profile\n/points - Check points\n/buy - Buy points\n/redeem - Redeem code\n/referral - Referral system\n/history - Search history\n/settings - Settings\n/help - This help",
    }
}

# ==================== HELPER FUNCTIONS ====================
def get_ist():
    """Get current IST time"""
    return datetime.now(IST)

def format_ist(dt):
    """Format IST datetime"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone('UTC')).astimezone(IST)
    return dt.strftime("%d-%m-%Y %I:%M:%S %p")

def get_user_lang(user_id):
    """Get user language"""
    user = users_col.find_one({'user_id': user_id})
    return user.get('language', 'en') if user else 'en'

def get_text(user_id, key):
    """Get text in user's language"""
    lang = get_user_lang(user_id)
    return LANG[lang].get(key, LANG['en'][key])

def format_number(num):
    """Format number with commas"""
    return f"{num:,}"

def generate_code(prefix=""):
    """Generate random code"""
    return prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def generate_order_id():
    """Generate unique order ID"""
    return f"ORD{datetime.now(IST).strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

def generate_referral_code():
    """Generate unique referral code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ==================== USER FUNCTIONS ====================
async def get_or_create_user(user_id, username=None, first_name=None):
    """Get or create user"""
    user = users_col.find_one({'user_id': user_id})
    
    if not user:
        # Create referral code
        ref_code = generate_referral_code()
        while referral_col.find_one({'code': ref_code}):
            ref_code = generate_referral_code()
        
        # Create user
        user_data = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'points': 0,
            'language': 'en',
            'joined_date': get_ist(),
            'last_active': get_ist(),
            'total_searches': 0,
            'total_redeemed': 0,
            'total_referrals': 0,
            'referral_code': ref_code,
            'referred_by': None,
            'daily_bonus_last': None,
            'is_banned': False,
            'is_admin': user_id == OWNER_ID,
            'warnings': 0,
            'settings': {
                'notifications': True,
                'private_mode': False
            }
        }
        users_col.insert_one(user_data)
        
        # Add referral code to referral collection
        referral_col.insert_one({
            'code': ref_code,
            'user_id': user_id,
            'created_at': get_ist(),
            'used_by': []
        })
        
        # Welcome bonus
        settings = settings_col.find_one({'key': 'bot_settings'})
        welcome_bonus = settings.get('welcome_bonus', 10) if settings else 10
        await add_points(user_id, welcome_bonus, "Welcome bonus")
        
        return user_data
    
    # Update last active
    users_col.update_one(
        {'user_id': user_id},
        {'$set': {'last_active': get_ist(), 'username': username, 'first_name': first_name}}
    )
    return user

async def add_points(user_id, points, reason, admin_id=None):
    """Add points to user"""
    user = users_col.find_one({'user_id': user_id})
    if not user:
        return False
    
    new_balance = user['points'] + points
    users_col.update_one(
        {'user_id': user_id},
        {'$set': {'points': new_balance}}
    )
    
    # Log transaction
    transactions_col.insert_one({
        'user_id': user_id,
        'type': 'credit',
        'amount': points,
        'reason': reason,
        'admin_id': admin_id,
        'balance': new_balance,
        'timestamp': get_ist()
    })
    
    return new_balance

async def deduct_points(user_id, points, reason):
    """Deduct points from user"""
    user = users_col.find_one({'user_id': user_id})
    if not user or user['points'] < points:
        return False
    
    new_balance = user['points'] - points
    users_col.update_one(
        {'user_id': user_id},
        {'$set': {'points': new_balance}}
    )
    
    # Log transaction
    transactions_col.insert_one({
        'user_id': user_id,
        'type': 'debit',
        'amount': points,
        'reason': reason,
        'balance': new_balance,
        'timestamp': get_ist()
    })
    
    return new_balance

async def add_reaction(message):
    """Add random reaction to message"""
    try:
        reaction = random.choice(REACTIONS)
        await message.set_reaction(reaction)
    except:
        pass

def clean_api_response(data):
    """Remove owner info from API response"""
    if isinstance(data, dict):
        data.pop('owner', None)
        if 'result' in data and isinstance(data['result'], dict):
            data['result'].pop('owner', None)
    return data

# ==================== COMMAND HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user_id = update.effective_user.id
    args = context.args
    
    # Check if user is banned
    banned = blacklist_col.find_one({'user_id': user_id})
    if banned:
        await update.message.reply_text("❌ आप ब्लैकलिस्ट कर दिए गए हैं!\nYou have been blacklisted!")
        return
    
    # Check referral
    if args and args[0].startswith('ref_'):
        ref_code = args[0][4:]
        referrer = referral_col.find_one({'code': ref_code})
        if referrer and referrer['user_id'] != user_id:
            context.user_data['referred_by'] = referrer['user_id']
    
    # Get or create user
    user = await get_or_create_user(
        user_id,
        update.effective_user.username,
        update.effective_user.first_name
    )
    
    # Handle referral
    if context.user_data.get('referred_by') and not user.get('referred_by'):
        referrer_id = context.user_data['referred_by']
        settings = settings_col.find_one({'key': 'bot_settings'})
        bonus = settings.get('referral_bonus', 10) if settings else 10
        
        # Update referrer
        await add_points(referrer_id, bonus, f"Referral bonus for user {user_id}")
        users_col.update_one(
            {'user_id': referrer_id},
            {'$inc': {'total_referrals': 1}}
        )
        
        # Update referral collection
        referral_col.update_one(
            {'user_id': referrer_id},
            {'$push': {'used_by': user_id}}
        )
        
        # Update user
        users_col.update_one(
            {'user_id': user_id},
            {'$set': {'referred_by': referrer_id}}
        )
        
        # Notify referrer
        try:
            await context.bot.send_message(
                referrer_id,
                f"🎉 नया रेफरल! {user['first_name']} ने आपके लिंक से जॉइन किया!\n+{bonus} पॉइंट्स मिले!"
            )
        except:
            pass
    
    # Language selection
    keyboard = [
        [InlineKeyboardButton("🇮🇳 हिंदी", callback_data="lang_hi"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        LANG['en']['welcome'],
        reply_markup=reply_markup
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main menu handler"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = users_col.find_one({'user_id': user_id})
    
    if not user:
        await query.edit_message_text("❌ User not found! Send /start")
        return
    
    points = user.get('points', 0)
    searches = user.get('total_searches', 0)
    name = user.get('first_name', 'User')
    lang = get_user_lang(user_id)
    
    # Main menu buttons
    keyboard = [
        [
            InlineKeyboardButton("💰 Points", callback_data="check_points"),
            InlineKeyboardButton("🛒 Buy", callback_data="buy_points")
        ],
        [
            InlineKeyboardButton("📱 Search", callback_data="use_service"),
            InlineKeyboardButton("🎁 Redeem", callback_data="redeem_code")
        ],
        [
            InlineKeyboardButton("👤 Profile", callback_data="view_profile"),
            InlineKeyboardButton("🤝 Referral", callback_data="view_referral")
        ],
        [
            InlineKeyboardButton("📋 History", callback_data="view_history"),
            InlineKeyboardButton("⚙️ Settings", callback_data="user_settings")
        ],
        [
            InlineKeyboardButton("📞 Contact", callback_data="contact_admin"),
            InlineKeyboardButton("❓ Help", callback_data="show_help")
        ]
    ]
    
    # Admin button
    if user_id == OWNER_ID:
        keyboard.append([InlineKeyboardButton("👑 ADMIN PANEL", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        LANG[lang]['main_menu'].format(name, format_number(points), searches),
        reply_markup=reply_markup
    )

# ==================== PROFILE & SETTINGS ====================
async def view_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View user profile"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = users_col.find_one({'user_id': user_id})
    lang = get_user_lang(user_id)
    
    if not user:
        await query.edit_message_text("❌ Error!")
        return
    
    join_date = format_ist(user.get('joined_date', get_ist()))
    
    # Get stats
    transactions = transactions_col.count_documents({'user_id': user_id})
    referrals = user.get('total_referrals', 0)
    
    profile_text = LANG[lang]['profile'].format(
        user_id,
        user.get('first_name', 'Unknown'),
        join_date,
        format_number(user.get('points', 0)),
        user.get('total_searches', 0),
        user.get('total_redeemed', 0),
        referrals
    )
    
    keyboard = [[InlineKeyboardButton(LANG[lang]['back'], callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(profile_text, reply_markup=reply_markup)

async def user_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User settings menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    user = users_col.find_one({'user_id': user_id})
    
    settings = user.get('settings', {})
    notif_status = "✅ ON" if settings.get('notifications', True) else "❌ OFF"
    private_status = "✅ ON" if settings.get('private_mode', False) else "❌ OFF"
    
    keyboard = [
        [InlineKeyboardButton(f"🔔 Notifications {notif_status}", callback_data="toggle_notif")],
        [InlineKeyboardButton(f"🕵️ Private Mode {private_status}", callback_data="toggle_private")],
        [InlineKeyboardButton("🌐 Change Language", callback_data="change_lang")],
        [InlineKeyboardButton(LANG[lang]['back'], callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        LANG[lang]['settings'],
        reply_markup=reply_markup
    )

async def toggle_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle notifications"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = users_col.find_one({'user_id': user_id})
    
    current = user.get('settings', {}).get('notifications', True)
    users_col.update_one(
        {'user_id': user_id},
        {'$set': {'settings.notifications': not current}}
    )
    
    await user_settings(update, context)

async def toggle_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle private mode"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = users_col.find_one({'user_id': user_id})
    
    current = user.get('settings', {}).get('private_mode', False)
    users_col.update_one(
        {'user_id': user_id},
        {'$set': {'settings.private_mode': not current}}
    )
    
    await user_settings(update, context)

# ==================== POINTS SYSTEM ====================
async def check_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check points balance"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = users_col.find_one({'user_id': user_id})
    lang = get_user_lang(user_id)
    
    if not user:
        await query.edit_message_text("❌ Error!")
        return
    
    points = user.get('points', 0)
    
    keyboard = [
        [InlineKeyboardButton("🛒 Buy Points", callback_data="buy_points")],
        [InlineKeyboardButton(LANG[lang]['back'], callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        LANG[lang]['check_points'].format(format_number(points)),
        reply_markup=reply_markup
    )

async def buy_points_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show buy points menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    
    keyboard = []
    for key, package in POINT_PACKAGES.items():
        popular = "🔥 " if package['popular'] else ""
        keyboard.append([InlineKeyboardButton(
            f"{package['emoji']} {popular}{package['points']} Points - ₹{package['price']}",
            callback_data=f"buy_pkg_{package['points']}"
        )])
    
    keyboard.append([InlineKeyboardButton(LANG[lang]['back'], callback_data="back_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        LANG[lang]['buy_points'],
        reply_markup=reply_markup
    )

async def process_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process point purchase"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    points = int(query.data.split('_')[2])
    
    # Create order
    order_id = generate_order_id()
    orders_col.insert_one({
        'order_id': order_id,
        'user_id': user_id,
        'points': points,
        'amount': points * 5,
        'status': 'pending',
        'payment_method': None,
        'created_at': get_ist()
    })
    
    # Payment options
    keyboard = [
        [InlineKeyboardButton("💳 Razorpay", callback_data=f"pay_razor_{order_id}")],
        [InlineKeyboardButton("📲 PhonePe", callback_data=f"pay_phonepe_{order_id}")],
        [InlineKeyboardButton("🧾 Google Pay", callback_data=f"pay_gpay_{order_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="buy_points")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🛒 Order #{order_id}\n\n"
        f"📦 Package: {points} Points\n"
        f"💰 Amount: ₹{points * 5}\n\n"
        f"Select payment method:",
        reply_markup=reply_markup
    )

async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process payment"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data.split('_')
    method = data[1]
    order_id = data[2]
    
    order = orders_col.find_one({'order_id': order_id, 'user_id': user_id})
    if not order:
        await query.edit_message_text("❌ Order not found!")
        return
    
    # Update order
    orders_col.update_one(
        {'order_id': order_id},
        {'$set': {
            'payment_method': method,
            'status': 'processing'
        }}
    )
    
    # Payment instructions
    upi_id = "nikilsaxena843@okhdfcbank"
    
    if method == "razor":
        instructions = f"🔴 RAZORPAY PAYMENT\n\n"
    elif method == "phonepe":
        instructions = f"🔵 PHONEPE PAYMENT\n\n"
    else:
        instructions = f"🟢 GPAY PAYMENT\n\n"
    
    instructions += (
        f"Order: #{order_id}\n"
        f"Amount: ₹{order['amount']}\n"
        f"UPI ID: `{upi_id}`\n\n"
        f"Steps:\n"
        f"1️⃣ Open {method.upper()} app\n"
        f"2️⃣ Pay to: {upi_id}\n"
        f"3️⃣ Send payment screenshot\n"
        f"4️⃣ Click 'I Paid' button\n\n"
        f"⚠️ Payment verify होने पर पॉइंट्स自动 मिल जाएंगे!"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ I PAID", callback_data=f"verify_pay_{order_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="buy_points")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        instructions,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify payment"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    order_id = query.data.split('_')[2]
    
    order = orders_col.find_one({'order_id': order_id, 'user_id': user_id})
    if not order:
        await query.edit_message_text("❌ Order not found!")
        return
    
    # Notify admin
    admin_msg = (
        f"💰 PAYMENT VERIFICATION REQUIRED\n\n"
        f"Order: #{order_id}\n"
        f"User: {user_id}\n"
        f"Points: {order['points']}\n"
        f"Amount: ₹{order['amount']}\n"
        f"Method: {order['payment_method']}\n\n"
        f"Verify and add points!"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{order_id}")],
        [InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{order_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(OWNER_ID, admin_msg, reply_markup=reply_markup)
    
    await query.edit_message_text(
        "✅ Payment notification sent to admin!\n"
        "Points will be added after verification."
    )

# ==================== SMS SERVICE ====================
async def use_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Use SMS service"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    user = users_col.find_one({'user_id': user_id})
    
    if user.get('points', 0) < 1:
        keyboard = [
            [InlineKeyboardButton("🛒 Buy Points", callback_data="buy_points")],
            [InlineKeyboardButton(LANG[lang]['back'], callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            LANG[lang]['insufficient_points'].format(user.get('points', 0)),
            reply_markup=reply_markup
        )
        return
    
    await query.edit_message_text(
        LANG[lang]['enter_number'],
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(LANG[lang]['back'], callback_data="back_to_menu")
        ]])
    )
    return SEARCH_NUMBER

async def handle_search_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle number input for search"""
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    number = update.message.text.strip()
    
    # Validate number
    if not (number.isdigit() and len(number) == 10):
        await update.message.reply_text(LANG[lang]['invalid_number'])
        return SEARCH_NUMBER
    
    # Check points
    user = users_col.find_one({'user_id': user_id})
    if user.get('points', 0) < 1:
        await update.message.reply_text(LANG[lang]['insufficient_points'].format(user.get('points', 0)))
        return ConversationHandler.END
    
    # Processing
    processing = await update.message.reply_text(LANG[lang]['processing'])
    
    try:
        # Call API
        response = requests.get(
            API_URL,
            params={'key': API_KEY, 'type': 'sms', 'term': number},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            data = clean_api_response(data)
            
            # Deduct points
            new_balance = await deduct_points(user_id, 1, f"SMS API: {number}")
            
            if new_balance:
                # Save to history
                search_history_col.insert_one({
                    'user_id': user_id,
                    'number': number,
                    'result': data,
                    'timestamp': get_ist()
                })
                
                # Update user stats
                users_col.update_one(
                    {'user_id': user_id},
                    {'$inc': {'total_searches': 1}}
                )
                
                # Format result
                if data.get('success') and data.get('result'):
                    result = data['result']
                    msg = LANG[lang]['search_result'].format(
                        result.get('number', number),
                        result.get('country', 'India'),
                        result.get('country_code', '+91'),
                        format_number(new_balance),
                        format_ist(get_ist())
                    )
                else:
                    msg = f"✅ Success!\n📱 Number: {number}\n💎 Remaining: {format_number(new_balance)}"
                
                # Send result
                result_msg = await update.message.reply_text(msg)
                
                # Add reaction
                settings = settings_col.find_one({'key': 'bot_settings'})
                if settings and settings.get('reactions_enabled', True):
                    await add_reaction(result_msg)
                
                await processing.delete()
            else:
                await processing.edit_text("❌ Error!")
        else:
            await processing.edit_text(LANG[lang]['api_error'])
    
    except Exception as e:
        await processing.edit_text(f"❌ Error: {str(e)}")
    
    return ConversationHandler.END

# ==================== GIFT CODE SYSTEM ====================
async def redeem_code_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show gift code packages"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    
    keyboard = []
    for key, package in GIFT_PACKAGES.items():
        keyboard.append([InlineKeyboardButton(
            f"{package['emoji']} {package['points']} Points Code",
            callback_data=f"redeem_pkg_{package['points']}"
        )])
    
    keyboard.append([InlineKeyboardButton(LANG[lang]['back'], callback_data="back_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        LANG[lang]['gift_packages'],
        reply_markup=reply_markup
    )

async def enter_gift_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enter gift code"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    points = int(query.data.split('_')[2])
    
    context.user_data['redeem_points'] = points
    
    await query.edit_message_text(
        LANG[lang]['enter_gift_code'].format(points),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(LANG[lang]['back'], callback_data="redeem_code")
        ]])
    )
    return REDEEM_CODE

async def handle_gift_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gift code redemption"""
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    code = update.message.text.strip().upper()
    expected_points = context.user_data.get('redeem_points')
    
    # Find code
    gift_code = gift_codes_col.find_one({
        'code': code,
        'used': False,
        'points': expected_points
    })
    
    if not gift_code:
        await update.message.reply_text(LANG[lang]['invalid_code'])
        return REDEEM_CODE
    
    # Mark as used
    gift_codes_col.update_one(
        {'code': code},
        {'$set': {
            'used': True,
            'used_by': user_id,
            'used_date': get_ist()
        }}
    )
    
    # Add points
    points = gift_code['points']
    new_balance = await add_points(user_id, points, f"Redeemed gift code: {code}")
    
    # Update user stats
    users_col.update_one(
        {'user_id': user_id},
        {'$inc': {'total_redeemed': 1}}
    )
    
    await update.message.reply_text(
        LANG[lang]['code_success'].format(points, format_number(new_balance)),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")
        ]])
    )
    
    return ConversationHandler.END

# ==================== REFERRAL SYSTEM ====================
async def view_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View referral info"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = users_col.find_one({'user_id': user_id})
    lang = get_user_lang(user_id)
    
    if not user:
        return
    
    ref_code = user.get('referral_code', '')
    bot_username = (await context.bot.get_me()).username
    settings = settings_col.find_one({'key': 'bot_settings'})
    bonus = settings.get('referral_bonus', 10) if settings else 10
    
    # Get referral stats
    ref_data = referral_col.find_one({'user_id': user_id})
    used_by = ref_data.get('used_by', []) if ref_data else []
    total_ref = len(used_by)
    total_commission = total_ref * bonus
    
    keyboard = [
        [InlineKeyboardButton("📤 Share Referral Link", callback_data="share_referral")],
        [InlineKeyboardButton(LANG[lang]['back'], callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        LANG[lang]['referral'].format(
            ref_code,
            bot_username,
            f"ref_{ref_code}",
            bonus,
            total_ref,
            format_number(total_commission)
        ),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def share_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Share referral link"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = users_col.find_one({'user_id': user_id})
    bot_username = (await context.bot.get_me()).username
    
    ref_link = f"https://t.me/{bot_username}?start=ref_{user['referral_code']}"
    
    keyboard = [
        [InlineKeyboardButton("📱 Share", url=f"https://t.me/share/url?url={ref_link}&text=Join%20this%20bot%20and%20get%20points!")],
        [InlineKeyboardButton("🔙 Back", callback_data="view_referral")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔗 Your Referral Link:\n`{ref_link}`\n\nClick Share to send to friends!",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

# ==================== DAILY BONUS ====================
async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Claim daily bonus"""
    user_id = update.effective_user.id
    user = users_col.find_one({'user_id': user_id})
    lang = get_user_lang(user_id)
    
    if not user:
        return
    
    last_bonus = user.get('daily_bonus_last')
    now = get_ist()
    
    if last_bonus:
        last_date = last_bonus.date()
        today = now.date()
        
        if last_date == today:
            next_bonus = last_bonus + timedelta(days=1)
            next_time = next_bonus.strftime("%I:%M %p")
            await update.message.reply_text(
                LANG[lang]['already_claimed'].format(next_time)
            )
            return
    
    # Give bonus
    settings = settings_col.find_one({'key': 'bot_settings'})
    bonus = settings.get('daily_bonus', 5) if settings else 5
    
    new_balance = await add_points(user_id, bonus, "Daily bonus")
    
    users_col.update_one(
        {'user_id': user_id},
        {'$set': {'daily_bonus_last': now}}
    )
    
    next_bonus = now + timedelta(days=1)
    next_time = next_bonus.strftime("%I:%M %p")
    
    await update.message.reply_text(
        LANG[lang]['daily_bonus'].format(bonus, next_time)
    )

# ==================== HISTORY ====================
async def view_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View search history"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    
    # Get last 10 searches
    searches = list(search_history_col.find(
        {'user_id': user_id}
    ).sort('timestamp', -1).limit(10))
    
    if not searches:
        history_text = "📭 No search history yet!"
    else:
        history_text = ""
        for i, s in enumerate(searches, 1):
            time = format_ist(s['timestamp']).split()[1]
            history_text += f"{i}. 📱 {s['number']} - 🕐 {time}\n"
    
    keyboard = [
        [InlineKeyboardButton("📊 Transactions", callback_data="view_transactions")],
        [InlineKeyboardButton(LANG[lang]['back'], callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        LANG[lang]['search_history'].format(history_text),
        reply_markup=reply_markup
    )

async def view_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View transaction history"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    
    # Get last 10 transactions
    transactions = list(transactions_col.find(
        {'user_id': user_id}
    ).sort('timestamp', -1).limit(10))
    
    if not transactions:
        trans_text = "📭 No transactions yet!"
    else:
        trans_text = ""
        for t in transactions:
            emoji = "➕" if t['type'] == 'credit' else "➖"
            time = format_ist(t['timestamp']).split()[1]
            trans_text += f"{emoji} {t['amount']} pts - {t['reason'][:20]}... 🕐 {time}\n"
    
    keyboard = [[InlineKeyboardButton(LANG[lang]['back'], callback_data="view_history")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        LANG[lang]['transaction_history'].format(trans_text),
        reply_markup=reply_markup
    )

# ==================== HELP & SUPPORT ====================
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    
    keyboard = [
        [InlineKeyboardButton("❓ FAQ", callback_data="show_faq")],
        [InlineKeyboardButton("📞 Contact Admin", callback_data="contact_admin")],
        [InlineKeyboardButton("📝 Terms", callback_data="show_terms")],
        [InlineKeyboardButton(LANG[lang]['back'], callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        LANG[lang]['help_text'],
        reply_markup=reply_markup
    )

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show FAQ"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    
    faq_text = (
        "❓ FAQ\n\n"
        "Q: Points कैसे खरीदें?\n"
        "A: Buy Points पर क्लिक करें और पेमेंट करें\n\n"
        "Q: 1 सर्च में कितने पॉइंट लगते हैं?\n"
        "A: 1 सर्च = 1 पॉइंट\n\n"
        "Q: रेफरल से कितने पॉइंट मिलते हैं?\n"
        "A: 10 पॉइंट प्रति रेफरल\n\n"
        "Q: डेली बोनस कितने बजे मिलता है?\n"
        "A: हर 24 घंटे में एक बार\n\n"
        "Q: पेमेंट वेरिफाई होने में कितना समय?\n"
        "A: 5-10 मिनट"
    )
    
    keyboard = [[InlineKeyboardButton(LANG[lang]['back'], callback_data="show_help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(faq_text, reply_markup=reply_markup)

async def show_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show terms and conditions"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    
    terms_text = (
        "📝 Terms & Conditions\n\n"
        "1. No refund after points added\n"
        "2. Wrong number = point deducted\n"
        "3. Multiple accounts = ban\n"
        "4. API misuse = permanent ban\n"
        "5. Points have no cash value\n"
        "6. We can change prices anytime\n"
        "7. Owner decision is final"
    )
    
    keyboard = [[InlineKeyboardButton(LANG[lang]['back'], callback_data="show_help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(terms_text, reply_markup=reply_markup)

# ==================== CONTACT ADMIN ====================
async def contact_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start contact admin"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    
    await query.edit_message_text(
        LANG[lang]['contact_admin'],
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(LANG[lang]['back'], callback_data="back_to_menu")
        ]])
    )
    return CONTACT_ADMIN

async def handle_contact_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle contact message"""
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    message = update.message.text
    user = users_col.find_one({'user_id': user_id})
    
    # Forward to admin
    admin_msg = (
        f"📨 New Message from User\n\n"
        f"👤 User: {user.get('first_name')}\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Username: @{update.effective_user.username}\n"
        f"💰 Points: {user.get('points', 0)}\n"
        f"🕐 Time: {format_ist(get_ist())}\n\n"
        f"💬 Message:\n{message}"
    )
    
    keyboard = [[InlineKeyboardButton("💬 Reply", callback_data=f"reply_user_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(OWNER_ID, admin_msg, reply_markup=reply_markup)
    
    await update.message.reply_text(
        LANG[lang]['msg_sent'],
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")
        ]])
    )
    
    return ConversationHandler.END

# ==================== ADMIN PANEL ====================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel main menu"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        await query.edit_message_text("❌ Unauthorized!")
        return
    
    # Get stats
    total_users = users_col.count_documents({})
    active_today = users_col.count_documents({
        'last_active': {'$gte': get_ist() - timedelta(days=1)}
    })
    total_points = sum(u.get('points', 0) for u in users_col.find())
    total_transactions = transactions_col.count_documents({})
    total_searches = search_history_col.count_documents({})
    total_orders = orders_col.count_documents({'status': 'completed'})
    total_revenue = orders_col.aggregate([
        {'$match': {'status': 'completed'}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ])
    revenue = list(total_revenue)
    total_revenue = revenue[0]['total'] if revenue else 0
    
    settings = settings_col.find_one({'key': 'bot_settings'})
    maintenance = "🔴 ON" if settings and settings.get('maintenance_mode') else "🟢 OFF"
    
    stats = f"""
👑 ADMIN PANEL
🕐 {format_ist(get_ist())} IST

📊 STATISTICS:
👥 Total Users: {total_users}
📱 Active Today: {active_today}
💰 Total Points: {format_number(total_points)}
💳 Transactions: {total_transactions}
🔍 Total Searches: {total_searches}
🛒 Completed Orders: {total_orders}
💵 Total Revenue: ₹{format_number(total_revenue)}

⚙️ MAINTENANCE: {maintenance}

🔧 OPTIONS:
    """
    
    keyboard = [
        [InlineKeyboardButton("📊 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("💰 Point Management", callback_data="admin_points")],
        [InlineKeyboardButton("🎁 Gift Code Management", callback_data="admin_gift")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📈 Orders & Transactions", callback_data="admin_orders")],
        [InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("🚫 Blacklist", callback_data="admin_blacklist")],
        [InlineKeyboardButton("📤 Export Data", callback_data="admin_export")],
        [InlineKeyboardButton("💾 Backup Database", callback_data="admin_backup")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(stats, reply_markup=reply_markup)

# ==================== ADMIN: USER MANAGEMENT ====================
async def admin_users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin user management"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    keyboard = [
        [InlineKeyboardButton("📋 View All Users", callback_data="admin_view_users")],
        [InlineKeyboardButton("🔍 Search User", callback_data="admin_search_user")],
        [InlineKeyboardButton("⚠️ Warn User", callback_data="admin_warn_user")],
        [InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban_user")],
        [InlineKeyboardButton("✅ Unban User", callback_data="admin_unban_user")],
        [InlineKeyboardButton("🏆 Top Users", callback_data="admin_top_users")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "👥 User Management\n\nChoose option:",
        reply_markup=reply_markup
    )

async def admin_view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all users"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    # Get users (paginated)
    page = context.user_data.get('user_page', 0)
    users = list(users_col.find().sort('points', -1).skip(page*10).limit(10))
    
    if not users:
        await query.edit_message_text("No users found!")
        return
    
    msg = f"📋 Users (Page {page+1}):\n\n"
    for i, user in enumerate(users, 1):
        name = user.get('first_name', 'Unknown')[:15]
        points = user.get('points', 0)
        banned = "🚫" if blacklist_col.find_one({'user_id': user['user_id']}) else "✅"
        msg += f"{i}. {banned} {name} - {format_number(points)} pts\n"
    
    keyboard = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ Prev", callback_data="admin_users_prev"))
    nav.append(InlineKeyboardButton(f"{page+1}/{(users_col.count_documents({})//10)+1}", callback_data="noop"))
    if len(users) == 10:
        nav.append(InlineKeyboardButton("Next ▶️", callback_data="admin_users_next"))
    keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_users")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(msg, reply_markup=reply_markup)

# ==================== ADMIN: POINT MANAGEMENT ====================
async def admin_points_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin point management"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Points", callback_data="admin_add_points")],
        [InlineKeyboardButton("➖ Remove Points", callback_data="admin_remove_points")],
        [InlineKeyboardButton("📊 View All Transactions", callback_data="admin_all_trans")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💰 Point Management\n\nChoose option:",
        reply_markup=reply_markup
    )

async def admin_add_points_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add points process"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    await query.edit_message_text(
        "Enter user ID and points (format: user_id points)\nExample: `123456789 100`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Cancel", callback_data="admin_points")
        ]])
    )
    return ADD_POINTS

async def handle_add_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add points"""
    if update.effective_user.id != OWNER_ID:
        return ConversationHandler.END
    
    text = update.message.text.strip().split()
    if len(text) != 2:
        await update.message.reply_text("❌ Invalid format! Use: user_id points")
        return ADD_POINTS
    
    try:
        target_id = int(text[0])
        points = int(text[1])
    except:
        await update.message.reply_text("❌ Invalid numbers!")
        return ADD_POINTS
    
    user = users_col.find_one({'user_id': target_id})
    if not user:
        await update.message.reply_text("❌ User not found!")
        return ADD_POINTS
    
    new_balance = await add_points(target_id, points, "Admin added", update.effective_user.id)
    
    await update.message.reply_text(
        f"✅ Added {points} points to user {target_id}\n"
        f"New balance: {format_number(new_balance)}"
    )
    
    # Notify user
    try:
        await context.bot.send_message(
            target_id,
            f"🎉 Admin ने आपके {points} पॉइंट्स जोड़ दिए!\nनया बैलेंस: {format_number(new_balance)}"
        )
    except:
        pass
    
    return ConversationHandler.END

# ==================== ADMIN: GIFT CODE MANAGEMENT ====================
async def admin_gift_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin gift code management"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    keyboard = []
    for key, package in GIFT_PACKAGES.items():
        keyboard.append([InlineKeyboardButton(
            f"{package['emoji']} Generate {package['points']} Points Code",
            callback_data=f"admin_gen_gift_{package['points']}"
        )])
    
    keyboard.append([InlineKeyboardButton("📋 View All Codes", callback_data="admin_view_codes")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_panel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎁 Gift Code Generator\n\nSelect package:",
        reply_markup=reply_markup
    )

async def admin_generate_gift_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate gift code"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    points = int(query.data.split('_')[3])
    code = f"GIFT{generate_code()}"
    
    gift_codes_col.insert_one({
        'code': code,
        'points': points,
        'used': False,
        'created_by': OWNER_ID,
        'created_date': get_ist()
    })
    
    await query.edit_message_text(
        f"✅ Gift Code Generated!\n\n"
        f"Code: `{code}`\n"
        f"Points: {points}\n"
        f"Package: {GIFT_PACKAGES[str(points)]['emoji']}\n"
        f"Created: {format_ist(get_ist())}\n\n"
        f"Share this code with users!",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🎁 Generate More", callback_data="admin_gift"),
            InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")
        ]])
    )

# ==================== ADMIN: BROADCAST SYSTEM ====================
async def admin_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    keyboard = [
        [InlineKeyboardButton("📝 Text Message", callback_data="broadcast_text")],
        [InlineKeyboardButton("🖼️ Photo", callback_data="broadcast_photo")],
        [InlineKeyboardButton("🎥 Video", callback_data="broadcast_video")],
        [InlineKeyboardButton("🔙 Cancel", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📢 Broadcast System\n\nChoose broadcast type:",
        reply_markup=reply_markup
    )

async def broadcast_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast text"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    await query.edit_message_text(
        "Send the message to broadcast:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Cancel", callback_data="admin_broadcast")
        ]])
    )
    return BROADCAST_MSG

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast message"""
    if update.effective_user.id != OWNER_ID:
        return ConversationHandler.END
    
    message = update.message.text
    users = list(users_col.find({}, {'user_id': 1}))
    
    progress = await update.message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            await context.bot.send_message(
                user['user_id'],
                f"📢 **ANNOUNCEMENT**\n\n{message}"
            )
            success += 1
            await asyncio.sleep(0.05)  # Rate limit
        except:
            failed += 1
    
    await progress.edit_text(
        f"✅ Broadcast Complete!\n\n"
        f"Total: {len(users)}\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}"
    )
    
    return ConversationHandler.END

# ==================== ADMIN: SETTINGS ====================
async def admin_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin settings menu"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    settings = settings_col.find_one({'key': 'bot_settings'})
    
    maintenance = "🔴 ON" if settings.get('maintenance_mode') else "🟢 OFF"
    reactions = "✅ ON" if settings.get('reactions_enabled', True) else "❌ OFF"
    rate_limit = settings.get('rate_limit', 5)
    referral_bonus = settings.get('referral_bonus', 10)
    daily_bonus = settings.get('daily_bonus', 5)
    
    msg = f"""
⚙️ BOT SETTINGS

🔧 Current Settings:
🛠️ Maintenance: {maintenance}
🎭 Reactions: {reactions}
⏱️ Rate Limit: {rate_limit} msgs/sec
🤝 Referral Bonus: {referral_bonus} pts
🎁 Daily Bonus: {daily_bonus} pts

📝 Options:
    """
    
    keyboard = [
        [InlineKeyboardButton(f"🛠️ Toggle Maintenance", callback_data="admin_toggle_maintenance")],
        [InlineKeyboardButton(f"🎭 Toggle Reactions", callback_data="admin_toggle_reactions")],
        [InlineKeyboardButton("⚡ Set Rate Limit", callback_data="admin_set_rate")],
        [InlineKeyboardButton("🤝 Set Referral Bonus", callback_data="admin_set_ref")],
        [InlineKeyboardButton("🎁 Set Daily Bonus", callback_data="admin_set_daily")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(msg, reply_markup=reply_markup)

async def toggle_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle maintenance mode"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    settings = settings_col.find_one({'key': 'bot_settings'})
    current = settings.get('maintenance_mode', False)
    
    settings_col.update_one(
        {'key': 'bot_settings'},
        {'$set': {'maintenance_mode': not current}}
    )
    
    await admin_settings_menu(update, context)

# ==================== ADMIN: BLACKLIST ====================
async def admin_blacklist_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Blacklist menu"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    blacklisted = list(blacklist_col.find())
    
    msg = f"🚫 Blacklisted Users: {len(blacklisted)}\n\n"
    if blacklisted:
        for user in blacklisted[:10]:
            msg += f"• {user['user_id']} - {user.get('reason', 'No reason')}\n"
    else:
        msg += "No blacklisted users."
    
    keyboard = [
        [InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban_user")],
        [InlineKeyboardButton("✅ Unban User", callback_data="admin_unban_user")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(msg, reply_markup=reply_markup)

# ==================== ADMIN: EXPORT DATA ====================
async def admin_export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export data to CSV"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    await query.edit_message_text("📤 Exporting data... Please wait.")
    
    # Export users
    filename = f"users_export_{get_ist().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['User ID', 'Name', 'Username', 'Points', 'Joined', 'Last Active', 'Searches'])
        
        for user in users_col.find():
            writer.writerow([
                user['user_id'],
                user.get('first_name', ''),
                user.get('username', ''),
                user.get('points', 0),
                format_ist(user.get('joined_date', get_ist())),
                format_ist(user.get('last_active', get_ist())),
                user.get('total_searches', 0)
            ])
    
    # Send file
    with open(filename, 'rb') as f:
        await context.bot.send_document(
            OWNER_ID,
            f,
            caption=f"📊 Users Export - {format_ist(get_ist())}"
        )
    
    os.remove(filename)
    
    await query.edit_message_text(
        "✅ Data exported successfully!",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="admin_panel")
        ]])
    )

# ==================== ADMIN: BACKUP DATABASE ====================
async def admin_backup_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Backup database"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        return
    
    await query.edit_message_text("💾 Creating backup... Please wait.")
    
    # Create backup
    backup_data = {
        'timestamp': get_ist(),
        'users': list(users_col.find()),
        'transactions': list(transactions_col.find()),
        'gift_codes': list(gift_codes_col.find()),
        'orders': list(orders_col.find()),
        'settings': list(settings_col.find())
    }
    
    # Convert ObjectId to string
    def convert_objectid(obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return obj
    
    backup_json = json.dumps(backup_data, default=convert_objectid, indent=2)
    
    # Save to file
    filename = f"backup_{get_ist().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(backup_json)
    
    # Send file
    with open(filename, 'rb') as f:
        await context.bot.send_document(
            OWNER_ID,
            f,
            caption=f"💾 Database Backup - {format_ist(get_ist())}"
        )
    
    os.remove(filename)
    
    # Save to MongoDB backup collection
    backup_col.insert_one({
        'timestamp': get_ist(),
        'filename': filename,
        'size': len(backup_json)
    })
    
    await query.edit_message_text(
        "✅ Backup created successfully!",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="admin_panel")
        ]])
    )

# ==================== AUTO DAILY BONUS REMINDER ====================
async def daily_bonus_reminder():
    """Send daily bonus reminders"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    users = users_col.find()
    for user in users:
        try:
            await app.bot.send_message(
                user['user_id'],
                "🎁 **Daily Bonus Reminder**\n\nDon't forget to claim your daily bonus!\nUse /daily to get free points!"
            )
            await asyncio.sleep(0.05)
        except:
            pass

# ==================== MAIN FUNCTION ====================
def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Scheduler for daily reminders
    scheduler = AsyncIOScheduler(timezone=IST)
    scheduler.add_job(daily_bonus_reminder, 'cron', hour=10, minute=0)
    scheduler.start()
    
    # Conversation handlers
    contact_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(contact_admin_start, pattern="^contact_admin$")],
        states={CONTACT_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_message)]},
        fallbacks=[]
    )
    
    search_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(use_service, pattern="^use_service$")],
        states={SEARCH_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_number)]},
        fallbacks=[CommandHandler("start", start)]
    )
    
    redeem_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(enter_gift_code, pattern="^redeem_pkg_\\d+$")],
        states={REDEEM_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gift_code)]},
        fallbacks=[CommandHandler("start", start)]
    )
    
    add_points_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_add_points_start, pattern="^admin_add_points$")],
        states={ADD_POINTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_points)]},
        fallbacks=[CommandHandler("start", start)]
    )
    
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(broadcast_text, pattern="^broadcast_text$")],
        states={BROADCAST_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast)]},
        fallbacks=[CommandHandler("start", start)]
    )
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", daily_bonus))
    application.add_handler(CommandHandler("profile", lambda u,c: view_profile(u,c)))
    application.add_handler(CommandHandler("points", lambda u,c: check_points(u,c)))
    application.add_handler(CommandHandler("help", lambda u,c: show_help(u,c)))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^lang_.*$"))
    application.add_handler(CallbackQueryHandler(set_language, pattern="^set_lang_.*$"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^back_to_menu$"))
    
    # User handlers
    application.add_handler(CallbackQueryHandler(view_profile, pattern="^view_profile$"))
    application.add_handler(CallbackQueryHandler(user_settings, pattern="^user_settings$"))
    application.add_handler(CallbackQueryHandler(toggle_notification, pattern="^toggle_notif$"))
    application.add_handler(CallbackQueryHandler(toggle_private, pattern="^toggle_private$"))
    application.add_handler(CallbackQueryHandler(change_language, pattern="^change_lang$"))
    
    # Points handlers
    application.add_handler(CallbackQueryHandler(check_points, pattern="^check_points$"))
    application.add_handler(CallbackQueryHandler(buy_points_menu, pattern="^buy_points$"))
    application.add_handler(CallbackQueryHandler(process_purchase, pattern="^buy_pkg_\\d+$"))
    application.add_handler(CallbackQueryHandler(process_payment, pattern="^pay_.*_.*$"))
    application.add_handler(CallbackQueryHandler(verify_payment, pattern="^verify_pay_.*$"))
    
    # Gift code handlers
    application.add_handler(CallbackQueryHandler(redeem_code_menu, pattern="^redeem_code$"))
    
    # Referral handlers
    application.add_handler(CallbackQueryHandler(view_referral, pattern="^view_referral$"))
    application.add_handler(CallbackQueryHandler(share_referral, pattern="^share_referral$"))
    
    # History handlers
    application.add_handler(CallbackQueryHandler(view_history, pattern="^view_history$"))
    application.add_handler(CallbackQueryHandler(view_transactions, pattern="^view_transactions$"))
    
    # Help handlers
    application.add_handler(CallbackQueryHandler(show_help, pattern="^show_help$"))
    application.add_handler(CallbackQueryHandler(show_faq, pattern="^show_faq$"))
    application.add_handler(CallbackQueryHandler(show_terms, pattern="^show_terms$"))
    
    # Admin panel handlers
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_users_menu, pattern="^admin_users$"))
    application.add_handler(CallbackQueryHandler(admin_view_users, pattern="^admin_view_users$"))
    application.add_handler(CallbackQueryHandler(admin_view_users, pattern="^admin_users_(prev|next)$"))
    application.add_handler(CallbackQueryHandler(admin_points_menu, pattern="^admin_points$"))
    application.add_handler(CallbackQueryHandler(admin_gift_menu, pattern="^admin_gift$"))
    application.add_handler(CallbackQueryHandler(admin_generate_gift_code, pattern="^admin_gen_gift_\\d+$"))
    application.add_handler(CallbackQueryHandler(admin_broadcast_start, pattern="^admin_broadcast$"))
    application.add_handler(CallbackQueryHandler(admin_settings_menu, pattern="^admin_settings$"))
    application.add_handler(CallbackQueryHandler(toggle_maintenance, pattern="^admin_toggle_maintenance$"))
    application.add_handler(CallbackQueryHandler(toggle_maintenance, pattern="^admin_toggle_reactions$"))
    application.add_handler(CallbackQueryHandler(admin_blacklist_menu, pattern="^admin_blacklist$"))
    application.add_handler(CallbackQueryHandler(admin_export_data, pattern="^admin_export$"))
    application.add_handler(CallbackQueryHandler(admin_backup_db, pattern="^admin_backup$"))
    
    # Add conversation handlers
    application.add_handler(contact_conv)
    application.add_handler(search_conv)
    application.add_handler(redeem_conv)
    application.add_handler(add_points_conv)
    application.add_handler(broadcast_conv)
    
    # Message handler for language
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u,c: None))
    
    # Start bot
    print("="*50)
    print("🚀 BOT STARTED SUCCESSFULLY!")
    print("="*50)
    print(f"🕐 Time: {format_ist(get_ist())} IST")
    print(f"👑 Owner: {OWNER_ID}")
    print(f"📊 Database: Connected")
    print(f"💰 Point Packages: {len(POINT_PACKAGES)}")
    print(f"🎁 Gift Packages: {len(GIFT_PACKAGES)}")
    print(f"👥 Total Users: {users_col.count_documents({})}")
    print(f"💎 1 Search = 1 Point")
    print("="*50)
    print("✅ ALL FEATURES LOADED:")
    print("   ✓ User System")
    print("   ✓ Point System")
    print("   ✓ Purchase System")
    print("   ✓ Gift Code System")
    print("   ✓ SMS Service")
    print("   ✓ Referral System")
    print("   ✓ Daily Bonus")
    print("   ✓ Admin Panel (30+ features)")
    print("   ✓ Broadcast System")
    print("   ✓ Blacklist System")
    print("   ✓ Export/Backup")
    print("   ✓ Auto Reactions")
    print("   ✓ Bilingual Support")
    print("="*50)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
