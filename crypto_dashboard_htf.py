#!/usr/bin/env python3
"""
TAWAQQUL HTF CONFIRMATION SCANNER - Multi-Timeframe (1H + 3min)
================================================================
Mode 1: 1H Sweep - Detects 1H liquidity sweeps (READY signals)
Mode 2: HTF Confirmation - 1H + 3min double sweep (CONFIRMED signals)
+ Dual Telegram Alerts (Ready Bot + Confirm Bot)

by @yousufkidiya17
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import requests
import hashlib
import json
from datetime import datetime, timedelta
import pytz
import base64
from PIL import Image

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

# ========== IST TIMEZONE ==========
IST = pytz.timezone('Asia/Kolkata')

def to_ist(dt):
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(IST).strftime('%d-%b %H:%M IST')

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

# ========== TELEGRAM CONFIG (2 BOTS) ==========
READY_BOT_TOKEN = "8740044507:AAEXMLNFjhtYYcsg4sfZ1843_czrdk2TFXI"
CONFIRM_BOT_TOKEN = "8570208083:AAE5DguxpRHGGu3u0Tb3PwHY2RrU2Ry9X1E"
TELEGRAM_CHAT_ID = "5428077566"
CONFIRM_WINDOW_HOURS = 3

# ========== USER DATABASE ==========
try:
    _dir = os.path.dirname(os.path.abspath(__file__))
except:
    _dir = os.getcwd()
USERS_FILE = os.path.join(_dir, "users.json")
ADMIN_USERNAME = "M.Yousuf"
DEFAULT_USERS = {
    "M.Yousuf": {"password": hashlib.sha256("MohdYousuf.17@".encode()).hexdigest(), "name": "M.Yousuf", "created": "2024-01-01"},
}

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_USERS.copy()
    return DEFAULT_USERS.copy()

def save_users(users):
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except:
        pass

def add_user(username, password, name=""):
    users = load_users()
    if username.lower() in [u.lower() for u in users.keys()]:
        return False, "Username already exists!"
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return False, error_msg
    users[username] = {
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "name": name if name else username,
        "created": datetime.now().strftime("%Y-%m-%d")
    }
    save_users(users)
    return True, "Account created successfully!"

def validate_password(password):
    import re
    if len(password) < 8:
        return False, "Password must be at least 8 characters!"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least 1 uppercase letter!"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least 1 lowercase letter!"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least 1 number!"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=]', password):
        return False, "Password must contain at least 1 special character!"
    return True, "Valid password"

def get_password_strength(password):
    import re
    if not password:
        return 0, "Enter password", "#6e7681"
    score = 0
    if len(password) >= 8: score += 1
    if len(password) >= 12: score += 1
    if re.search(r'[A-Z]', password): score += 1
    if re.search(r'[a-z]', password): score += 1
    if re.search(r'[0-9]', password): score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=]', password): score += 1
    if score <= 2: return score, "🔴 Weak", "#ff4444"
    elif score <= 4: return score, "🟡 Medium", "#ffaa00"
    else: return score, "🟢 Strong", "#00ff88"

def verify_user(username, password):
    users = load_users()
    actual_username = None
    for u in users.keys():
        if u.lower() == username.lower():
            actual_username = u
            break
    if actual_username:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return users[actual_username]["password"] == hashed
    return False

def get_user_count():
    return len(load_users())

def delete_user(username):
    if username == ADMIN_USERNAME:
        return False, "Cannot delete admin!"
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        return True, f"User '{username}' deleted!"
    return False, "User not found!"

def get_all_users():
    users = load_users()
    user_list = []
    for username, data in users.items():
        user_list.append({
            "username": username,
            "name": data.get("name", username),
            "created": data.get("created", "Unknown"),
            "is_admin": username == ADMIN_USERNAME
        })
    return user_list

def is_admin():
    return st.session_state.get('username', '').lower() == ADMIN_USERNAME.lower()


# ========== CRYPTO PAIRS (Coinbase - USD) ==========
CRYPTO_CATEGORIES = {
    "🔥 Top 10": [
        "BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD",
        "ADA/USD", "DOGE/USD", "AVAX/USD", "DOT/USD", "LINK/USD"
    ],
    "💎 Layer 1": [
        "BTC/USD", "ETH/USD", "SOL/USD", "AVAX/USD", "DOT/USD",
        "NEAR/USD", "APT/USD", "SUI/USD",
        "ATOM/USD", "ALGO/USD", "HBAR/USD", "ICP/USD"
    ],
    "🎭 Meme Coins": [
        "DOGE/USD", "SHIB/USD", "BONK/USD"
    ],
    "🏦 DeFi": [
        "UNI/USD", "AAVE/USD", "MKR/USD", "SNX/USD",
        "CRV/USD", "DYDX/USD"
    ],
    "🎮 Gaming & AI": [
        "IMX/USD", "GALA/USD", "AXS/USD", "SAND/USD", "MANA/USD",
        "RNDR/USD", "FET/USD"
    ],
    "📊 Layer 2": [
        "MATIC/USD", "OP/USD"
    ],
    "🌟 All Popular": [
        "BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD",
        "ADA/USD", "DOGE/USD", "AVAX/USD", "DOT/USD", "LINK/USD",
        "NEAR/USD", "APT/USD", "SUI/USD",
        "ATOM/USD", "ALGO/USD", "HBAR/USD", "ICP/USD",
        "UNI/USD", "AAVE/USD", "MKR/USD", "SNX/USD", "CRV/USD",
        "MATIC/USD", "OP/USD", "RNDR/USD", "FET/USD",
        "IMX/USD", "GALA/USD", "AXS/USD",
        "SAND/USD", "MANA/USD", "SHIB/USD",
        "LTC/USD", "BCH/USD", "ETC/USD", "FIL/USD",
        "DYDX/USD", "INJ/USD", "BONK/USD"
    ]
}

# ========== SCANNER SETTINGS ==========
SWING_LENGTHS_HTF = [3, 5, 8]   # For 1H chart
SWING_LENGTHS_LTF = [3, 5]      # For 3min chart
MIN_WICK_PERCENT = 25
MIN_DEPTH_PERCENT = 0.05
OB_LOOKBACK = 5


# ========== TELEGRAM FUNCTIONS ==========
def send_telegram_alert(bot_token, message):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, json=payload, timeout=10)
        return response.json().get("ok", False)
    except Exception as e:
        return False

def format_telegram_signal(signal, mode="ready"):
    if mode == "ready":
        grade_emoji = "🏆" if signal['grade'] == 'A+' else "✅" if signal['grade'] == 'B' else "⚠️"
        msg = (
            f"<b>🟡 {grade_emoji} 1H LIQUIDITY SWEEP — READY!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 <b>Pair:</b> {signal['ticker']}\n"
            f"⏰ <b>1H Sweep:</b> {to_ist(signal['date'])}\n"
            f"💰 <b>Close:</b> ${signal['close']:.4f}\n"
            f"📏 <b>Swing Low:</b> ${signal['swing_low']:.4f}\n"
            f"📐 <b>Depth:</b> {signal['depth_percent']:.3f}%\n"
            f"⭐ <b>Score:</b> {signal['score']:.0f}/100 ({signal['grade']})\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Waiting for 3min confirmation...\n"
            f"🤖 TAWAQQUL HTF Scanner (1H → 3min)"
        )
    else:
        msg = (
            f"<b>🟢🔥 CONFIRMED — DOUBLE SWEEP!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 <b>Pair:</b> {signal['ticker']}\n\n"
            f"<b>📈 1H Sweep:</b> {to_ist(signal['htf_date'])}\n"
            f"  Score: {signal['htf_score']:.0f}/100 | Depth: {signal['htf_depth']:.3f}%\n\n"
            f"<b>🎯 3min Sweep:</b> {to_ist(signal['ltf_date'])}\n"
            f"  Score: {signal['ltf_score']:.0f}/100 | Depth: {signal['ltf_depth']:.3f}%\n\n"
            f"💰 <b>Price:</b> ${signal['current_price']:.4f}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ 1H + 3min DOUBLE CONFIRMED!\n"
            f"🤖 TAWAQQUL HTF Scanner (1H → 3min)"
        )
    return msg


# ========== PAGE CONFIG ==========
favicon_path = os.path.join(_dir, "logo.png")
if os.path.exists(favicon_path):
    favicon = Image.open(favicon_path)
else:
    favicon = "🎯"

st.set_page_config(
    page_title="TAWAQQUL HTF Scanner",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=favicon
)

# ========== LOGIN STYLES ==========
st.markdown("""
<style>
    .login-container {
        max-width: 400px;
        margin: 50px auto;
        padding: 40px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 20px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
    }
    .login-header { text-align: center; margin-bottom: 30px; }
    .login-header h1 { color: #ffffff; font-size: 2em; margin: 10px 0; }
    .login-header .arabic { color: #ffd700; font-size: 1.3em; direction: rtl; }
    .login-logo {
        width: 80px; height: 80px; margin: 0 auto 20px;
        background: #000; border-radius: 15px;
        display: flex; align-items: center; justify-content: center;
        animation: logoGlow 3s ease-in-out infinite;
    }
    @keyframes logoGlow {
        0%, 100% { box-shadow: 0 0 10px #ffd700, 0 0 20px rgba(255,215,0,0.3); }
        50% { box-shadow: 0 0 20px #ffd700, 0 0 40px rgba(255,215,0,0.5); }
    }
    @keyframes textGlow {
        0%, 100% { text-shadow: 0 0 5px #ffd700, 0 0 10px rgba(255,215,0,0.3); }
        50% { text-shadow: 0 0 15px #ffd700, 0 0 25px rgba(255,215,0,0.5), 0 0 35px rgba(255,215,0,0.3); }
    }
    .welcome-text { text-align: center; color: #00ff88; font-size: 1.1em; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)


# ========== AUTH FUNCTIONS ==========
def check_password(username, password):
    return verify_user(username, password)

def get_logo_base64():
    logo_path = os.path.join(_dir, "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# ========== LOGIN PAGE ==========
def show_login_page():
    logo_b64 = get_logo_base64()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div style="text-align: center; margin-top: 50px;">""", unsafe_allow_html=True)
        
        if logo_b64:
            st.markdown(f"""
            <div style="text-align: center;">
                <div class="login-logo">
                    <img src="data:image/png;base64,{logo_b64}" style="width: 50px; filter: invert(1);">
                </div>
                <h1 style="color: #ffffff; margin: 10px 0;">🔐 TAWAQQUL CRYPTO</h1>
                <p style="color: #ffd700; font-size: 1.2em; direction: rtl; animation: textGlow 3s ease-in-out infinite;">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</p>
                <p style="color: #a0c4e8;">Multi-Timeframe Confirmation (1H → 3min)</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center;">
                <h1 style="color: #ffffff; margin: 10px 0;">🔐 TAWAQQUL CRYPTO</h1>
                <p style="color: #ffd700; font-size: 1.2em; direction: rtl; animation: textGlow 3s ease-in-out infinite;">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</p>
                <p style="color: #a0c4e8;">Multi-Timeframe Confirmation (1H → 3min)</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                st.markdown("### 👤 Login to Continue")
                username = st.text_input("Username", placeholder="Enter username", key="login_user")
                password = st.text_input("Password", type="password", placeholder="Enter password", key="login_pass")
                submit = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
                
                if submit:
                    if username and password:
                        if check_password(username, password):
                            st.session_state['authenticated'] = True
                            st.session_state['username'] = username
                            success_container = st.empty()
                            success_container.markdown(f"""
                            <div style="background: linear-gradient(135deg, #0d4f3c 0%, #1a7f5a 100%); padding: 30px; border-radius: 20px; text-align: center; border: 2px solid #00ff88; box-shadow: 0 0 30px rgba(0,255,136,0.4); margin: 20px 0;">
                                <div style="font-size: 60px; margin-bottom: 15px;">✅</div>
                                <h2 style="color: #00ff88; margin: 0 0 10px 0;">Welcome back, {username}!</h2>
                                <p style="color: #a0c4e8; margin: 0;">🚀 Redirecting to dashboard...</p>
                            </div>
                            """, unsafe_allow_html=True)
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password!")
                    else:
                        st.warning("⚠️ Please enter both username and password!")
        
        with tab2:
            with st.form("signup_form"):
                st.markdown("### 📝 Create New Account")
                new_username = st.text_input("Choose Username", placeholder="Enter username", key="signup_user")
                new_name = st.text_input("Your Name (Optional)", placeholder="Enter your name", key="signup_name")
                new_password = st.text_input("Create Password", type="password", placeholder="Min 8 chars, A-Z, a-z, 0-9, special", key="signup_pass")
                
                if new_password:
                    strength_score, strength_text, strength_color = get_password_strength(new_password)
                    st.markdown(f"""
                    <div style="margin: -10px 0 10px 0;">
                        <div style="background: #1e2530; border-radius: 10px; padding: 3px; margin-bottom: 5px;">
                            <div style="width: {min(strength_score * 16.66, 100)}%; height: 6px; background: {strength_color}; border-radius: 8px; transition: all 0.3s;"></div>
                        </div>
                        <span style="color: {strength_color}; font-size: 0.85em; font-weight: 600;">{strength_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background: rgba(0,212,255,0.1); padding: 10px; border-radius: 8px; margin: 5px 0 15px 0; font-size: 0.8em; color: #a0c4e8;">
                    <strong>📋 Password Requirements:</strong><br>
                    ✓ Minimum 8 characters<br>
                    ✓ At least 1 uppercase (A-Z)<br>
                    ✓ At least 1 lowercase (a-z)<br>
                    ✓ At least 1 number (0-9)<br>
                    ✓ At least 1 special character (!@#$%^&*)
                </div>
                """, unsafe_allow_html=True)
                
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="signup_confirm")
                signup_btn = st.form_submit_button("✨ Create Account", use_container_width=True, type="primary")
                
                if signup_btn:
                    if not new_username or not new_password:
                        st.warning("⚠️ Username and Password are required!")
                    elif len(new_username) < 3:
                        st.warning("⚠️ Username must be at least 3 characters!")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords don't match!")
                    else:
                        success, message = add_user(new_username, new_password, new_name)
                        if success:
                            st.success(f"✅ {message}")
                            st.info("👆 Now go to Login tab and login!")
                        else:
                            st.error(f"❌ {message}")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 30px; color: #6e7681; font-size: 0.85em;">
            <p>📧 kidiyayousuf17@gmail.com</p>
            <p>🔒 Secure Login System</p>
        </div>
        """, unsafe_allow_html=True)


# ========== LOGOUT BUTTON ==========
def show_logout_button():
    with st.sidebar:
        st.markdown(f"**👤 Welcome, {st.session_state.get('username', 'User')}!**")
        if is_admin():
            st.markdown("🔑 **Admin Access**")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state['authenticated'] = False
            st.session_state['username'] = None
            st.rerun()
        st.markdown("---")

# ========== ADMIN PANEL ==========
def show_admin_panel():
    if not is_admin():
        return
    with st.sidebar:
        with st.expander("🛡️ ADMIN PANEL", expanded=False):
            st.markdown("### 👥 User Management")
            users = get_all_users()
            st.metric("Total Users", len(users))
            st.markdown("---")
            st.markdown("**Registered Users:**")
            for user in users:
                col1, col2 = st.columns([3, 1])
                with col1:
                    badge = "👑" if user['is_admin'] else "👤"
                    st.markdown(f"{badge} **{user['username']}**")
                    st.caption(f"📅 {user['created']}")
                with col2:
                    if not user['is_admin']:
                        if st.button("🗑️", key=f"del_{user['username']}", help=f"Delete {user['username']}"):
                            success, msg = delete_user(user['username'])
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
            st.markdown("---")
            st.caption("🔒 Only admin can see this panel")


# ========== CHECK AUTHENTICATION ==========
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    show_login_page()
    st.stop()

show_logout_button()
show_admin_panel()


# ========== SCANNER SETTINGS ==========
HTF_CANDLE_LIMIT = 200    # 200 x 1H = ~8 days
LTF_CANDLE_LIMIT = 500    # 500 x 3min = ~25 hours

# ========== STYLES ==========
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 5px #ffd700; }
        50% { text-shadow: 0 0 15px #ffd700, 0 0 25px #ffd700; }
    }
    @keyframes fadeText {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; }
    }
    @keyframes logoGlowMain {
        0%, 100% { box-shadow: 0 0 5px #ffd700, 0 0 10px rgba(255,215,0,0.3); }
        50% { box-shadow: 0 0 15px #ffd700, 0 0 25px rgba(255,215,0,0.5), 0 0 35px rgba(255,215,0,0.3); }
    }
    @keyframes borderGlow {
        0%, 100% { box-shadow: 0 0 5px #00d4ff, 0 0 10px rgba(0,212,255,0.3); }
        50% { box-shadow: 0 0 15px #00d4ff, 0 0 25px rgba(0,212,255,0.5), 0 0 35px rgba(0,212,255,0.2); }
    }
    @keyframes cryptoPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .logo-container {
        width: 80px; height: 80px; border-radius: 12px;
        background: #000000; display: flex; align-items: center; justify-content: center;
        padding: 10px; animation: logoGlowMain 3s ease-in-out infinite;
    }
    .logo-container img { height: 60px; width: 60px; object-fit: contain; filter: invert(1); }
    
    [data-testid="stSidebar"] .stImage { display: flex; justify-content: center; margin-bottom: 15px; }
    [data-testid="stSidebar"] .stImage img {
        width: 45px !important; height: 45px !important; padding: 8px;
        background: #000000; border-radius: 10px; filter: invert(1);
        box-shadow: 0 0 10px rgba(255,215,0,0.4);
    }
    
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 25px 30px; border-radius: 20px; margin-bottom: 25px;
        border: 1px solid rgba(255, 165, 0, 0.3);
        box-shadow: 0 8px 32px rgba(255, 165, 0, 0.15), inset 0 0 60px rgba(255, 165, 0, 0.05);
    }
    .main-header h1 { 
        color: #ffffff; font-size: 2.2em; margin: 0; font-weight: 800;
        letter-spacing: 1px; text-shadow: 0 2px 10px rgba(255,165,0,0.3);
    }
    .main-header .arabic { 
        font-size: 1.5em; color: #ffd700; font-family: 'Traditional Arabic', serif;
        direction: rtl; margin: 12px 0; animation: glow 3s ease-in-out infinite;
    }
    .main-header .tagline { 
        color: #a0c4e8; margin: 8px 0 0 0; font-size: 1em;
        animation: fadeText 4s ease-in-out infinite; letter-spacing: 0.5px;
    }
    .main-header .tagline .highlight { color: #ff9500; font-weight: 600; }
    
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #131722 0%, #1e222d 100%);
        border-right: 1px solid rgba(255, 165, 0, 0.3);
    }
    
    .metric-card {
        background: #1e2530; padding: 15px 20px; border-radius: 8px;
        border-left: 3px solid #ff9500; margin: 5px 0;
    }
    .metric-card h3 { color: #8b949e; font-size: 0.85em; margin: 0; font-weight: 400; }
    .metric-card .value { color: #ffffff; font-size: 1.5em; font-weight: 600; margin: 5px 0 0 0; }
    
    .signal-good { background: rgba(0,200,83,0.15); border-left: 4px solid #00c853; padding: 12px; border-radius: 5px; margin: 8px 0; }
    .signal-medium { background: rgba(255,193,7,0.15); border-left: 4px solid #ffc107; padding: 12px; border-radius: 5px; margin: 8px 0; }
    
    .fp-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 20px; border-radius: 12px; margin: 10px 0; border-left: 4px solid #00ff88;
    }
    .fp-card h3 { color: #00ff88; margin: 0 0 10px 0; font-size: 1.3em; }
    .fp-card .ticker { color: #ffffff; font-size: 1.5em; font-weight: 700; }
    .fp-card .zone { color: #ffd700; font-size: 1.1em; }
    
    .at-fp { background: linear-gradient(135deg, #0d4f3c 0%, #1a7f5a 100%); border-left: 4px solid #00ff88; }
    
    .mode-tag {
        display: inline-block; padding: 8px 18px; border-radius: 25px;
        font-size: 0.9em; font-weight: 700; margin: 5px 5px 5px 0;
        letter-spacing: 0.5px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .mode-sweep { background: linear-gradient(90deg, #ff9500, #cc7700); color: #000; }
    .mode-fp { background: linear-gradient(90deg, #00ff88, #00cc6a); color: #000; }
    
    .crypto-badge {
        display: inline-block; padding: 4px 12px; border-radius: 15px;
        font-size: 0.8em; font-weight: 600; margin: 2px;
        background: rgba(255,165,0,0.2); color: #ff9500;
        border: 1px solid rgba(255,165,0,0.3);
    }
    
    .live-dot {
        display: inline-block; width: 8px; height: 8px; border-radius: 50%;
        background: #00ff88; margin-right: 5px;
        animation: cryptoPulse 1.5s ease-in-out infinite;
        box-shadow: 0 0 5px #00ff88;
    }
</style>
""", unsafe_allow_html=True)


# ========== HEADER ==========
logo_b64 = get_logo_base64()
if logo_b64:
    st.markdown(f"""
    <div class="main-header" style="display: flex; align-items: center; gap: 30px;">
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_b64}">
        </div>
        <div>
            <h1>₿ TAWAQQUL CRYPTO SCANNER</h1>
            <p class="arabic">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</p>
            <p class="tagline"><span class="live-dot"></span> Real-Time Crypto Liquidity Detection • <span class="highlight">5-Minute Timeframe</span></p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="main-header">
        <h1>₿ TAWAQQUL CRYPTO SCANNER</h1>
        <p class="arabic">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</p>
        <p class="tagline"><span class="live-dot"></span> Real-Time Crypto Liquidity Detection • <span class="highlight">5-Minute Timeframe</span></p>
    </div>
    """, unsafe_allow_html=True)


# ========== DATA DOWNLOAD (CCXT - REAL TIME) ==========
@st.cache_data(ttl=60)
def download_crypto_data(symbol, timeframe='1h', limit=500):
    """Fetch OHLCV data from Coinbase via ccxt with pagination"""
    try:
        exchange = ccxt.coinbase({'enableRateLimit': True})
        
        # Coinbase max 300 per request - paginate if needed
        all_ohlcv = []
        batch_size = 300
        remaining = limit
        
        # Calculate timeframe in milliseconds
        tf_map = {'1m': 60000, '5m': 300000, '15m': 900000, '1h': 3600000, '6h': 21600000, '1d': 86400000}
        tf_ms = tf_map.get(timeframe, 300000)
        
        # Start from (limit * tf_ms) ago
        since = int((datetime.utcnow() - timedelta(milliseconds=limit * tf_ms)).timestamp() * 1000)
        
        while remaining > 0:
            fetch_count = min(batch_size, remaining)
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=fetch_count)
            
            if not ohlcv:
                break
            
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + tf_ms  # Next batch starts after last candle
            remaining -= len(ohlcv)
            
            if len(ohlcv) < fetch_count:
                break  # No more data available
            
            time.sleep(0.1)  # Rate limit
        
        if not all_ohlcv:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df.set_index('Timestamp', inplace=True)
        df = df[~df.index.duplicated(keep='last')]  # Remove duplicates
        
        return df
    except Exception as e:
        return pd.DataFrame()


# ========== SWING DETECTION ==========
def detect_pivot_lows_multi(df, lengths=[3, 5, 8]):
    """Detect pivot lows with multiple swing lengths"""
    pivot_lows = []
    
    for length in lengths:
        for i in range(length, len(df) - length):
            is_pivot = True
            current_low = df['Low'].iloc[i]
            
            for j in range(1, length + 1):
                if df['Low'].iloc[i - j] <= current_low or df['Low'].iloc[i + j] <= current_low:
                    is_pivot = False
                    break
            
            if is_pivot:
                already_exists = any(
                    abs(p['index'] - i) <= 2 and abs(p['price'] - current_low) / current_low < 0.001
                    for p in pivot_lows
                )
                if not already_exists:
                    pivot_lows.append({
                        'index': i,
                        'date': df.index[i],
                        'price': current_low,
                        'swing_type': length
                    })
    
    return sorted(pivot_lows, key=lambda x: x['index'])


# ========== LIQUIDITY SWEEP DETECTION ==========
def detect_liquidity_sweep(df, pivot_lows):
    """Detect bullish liquidity sweeps"""
    sweeps = []
    
    for pivot in pivot_lows:
        pivot_idx = pivot['index']
        swing_low = pivot['price']
        swing_type = pivot['swing_type']
        
        for i in range(pivot_idx + 1, min(pivot_idx + 15, len(df))):
            candle_low = df['Low'].iloc[i]
            candle_close = df['Close'].iloc[i]
            candle_open = df['Open'].iloc[i]
            candle_high = df['High'].iloc[i]
            
            if candle_low < swing_low and candle_close > swing_low:
                body = abs(candle_close - candle_open)
                total_range = candle_high - candle_low
                lower_wick = min(candle_open, candle_close) - candle_low
                
                if total_range > 0:
                    wick_percent = (lower_wick / total_range) * 100
                    depth_percent = ((swing_low - candle_low) / swing_low) * 100
                else:
                    continue
                
                if wick_percent >= MIN_WICK_PERCENT and depth_percent >= MIN_DEPTH_PERCENT:
                    close_position = (candle_close - candle_low) / total_range * 100 if total_range > 0 else 0
                    score = calculate_score(wick_percent, depth_percent, close_position, swing_type)
                    
                    sweeps.append({
                        'ticker': '',
                        'date': df.index[i],
                        'sweep_idx': i,
                        'swing_low': swing_low,
                        'sweep_low': candle_low,
                        'close': candle_close,
                        'wick_percent': wick_percent,
                        'depth_percent': depth_percent,
                        'swing_type': swing_type,
                        'score': score,
                        'grade': get_grade(score)
                    })
                break
    
    return sweeps

def calculate_score(wick_pct, depth_pct, close_pos, swing_type):
    score = 0
    score += min(wick_pct / 2, 30)
    score += min(depth_pct * 20, 30)
    score += min(close_pos / 5, 20)
    if swing_type >= 8:
        score += 20
    elif swing_type >= 5:
        score += 15
    else:
        score += 10
    return min(score, 100)

def get_grade(score):
    if score >= 70: return "A+"
    elif score >= 55: return "B"
    elif score >= 40: return "C"
    else: return "D"

def get_swing_label(swing_type):
    if swing_type >= 8: return "Major"
    elif swing_type >= 5: return "Medium"
    else: return "Minor"


# ========== FAIR PRICE (ORDER BLOCK) DETECTION ==========
def detect_fair_price_zone(df, sweep):
    """Detect Fair Price zone (Order Block) after liquidity sweep"""
    sweep_idx = sweep['sweep_idx']
    
    for i in range(sweep_idx, max(sweep_idx - OB_LOOKBACK, 0), -1):
        if df['Close'].iloc[i] < df['Open'].iloc[i]:
            return {
                'fp_idx': i,
                'fp_date': df.index[i],
                'fp_high': df['High'].iloc[i],
                'fp_low': df['Low'].iloc[i]
            }
    
    return {
        'fp_idx': sweep_idx,
        'fp_date': df.index[sweep_idx],
        'fp_high': df['High'].iloc[sweep_idx],
        'fp_low': df['Low'].iloc[sweep_idx]
    }

def is_price_at_fp(current_price, fp_high, fp_low, tolerance=1.0):
    """Check if price is at Fair Price zone"""
    zone_range = fp_high - fp_low
    extended_high = fp_high + (zone_range * tolerance / 100)
    extended_low = fp_low - (zone_range * tolerance / 100)
    return extended_low <= current_price <= extended_high

def scan_fair_price_setups(df, ticker, max_candles=200):
    """Scan for Fair Price setups"""
    if len(df) < 30:
        return []
    
    pivot_lows = detect_pivot_lows_multi(df, SWING_LENGTHS_HTF)
    if not pivot_lows:
        return []
    
    sweeps = detect_liquidity_sweep(df, pivot_lows)
    if not sweeps:
        return []
    
    setups = []
    current_price = df['Close'].iloc[-1]
    current_date = df.index[-1]
    
    for sweep in sweeps:
        fp = detect_fair_price_zone(df, sweep)
        candles_ago = len(df) - 1 - df.index.get_loc(fp['fp_date']) if fp['fp_date'] in df.index else 999
        
        if candles_ago > max_candles:
            continue
        
        fp_valid = True
        for i in range(fp['fp_idx'] + 1, len(df)):
            if df['Close'].iloc[i] < fp['fp_low']:
                fp_valid = False
                break
        
        if fp_valid:
            at_fp = is_price_at_fp(current_price, fp['fp_high'], fp['fp_low'])
            distance = 0
            if current_price > fp['fp_high']:
                distance = ((current_price - fp['fp_high']) / fp['fp_high']) * 100
            elif current_price < fp['fp_low']:
                distance = ((fp['fp_low'] - current_price) / fp['fp_low']) * 100
            
            # Calculate hours ago
            time_diff = current_date - fp['fp_date']
            hours_ago = time_diff.total_seconds() / 3600
            
            setups.append({
                'ticker': ticker,
                'sweep_date': sweep['date'],
                'sweep_score': sweep['score'],
                'fp_date': fp['fp_date'],
                'fp_high': fp['fp_high'],
                'fp_low': fp['fp_low'],
                'current_price': current_price,
                'at_fp_zone': at_fp,
                'hours_ago': hours_ago,
                'distance': distance
            })
    
    return setups


# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### ⚙️ Crypto Scan Settings")
    
    # Live indicator
    st.markdown("""
    <div style="background: rgba(0,255,136,0.1); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(0,255,136,0.3); margin-bottom: 15px;">
        <span class="live-dot"></span> <strong style="color: #00ff88;">REAL-TIME DATA</strong>
        <span style="color: #8b949e; font-size: 0.8em;"> via Coinbase</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 🎯 Select Mode")
    scan_mode = st.radio(
        "Choose what to scan:",
        ["🟡 1H Sweep (Ready)", "🟢 HTF Confirmation (1H+3min)"],
        horizontal=False,
        help="1H Sweep = 1H sweeps only | HTF Confirmation = 1H + 3min double confirmed"
    )
    
    if scan_mode == "🟡 1H Sweep (Ready)":
        st.info("🔍 Finds crypto where 1H liquidity was swept")
    else:
        st.success("🎯 Finds crypto with DOUBLE confirmation (1H + 3min)")
    
    st.markdown("---")
    
    # Category selection
    st.markdown("#### 📁 Select Category")
    selected_category = st.selectbox(
        "Crypto Category",
        list(CRYPTO_CATEGORIES.keys()),
        index=0
    )
    
    # Show selected pairs
    available_pairs = CRYPTO_CATEGORIES[selected_category]
    selected_pairs = st.multiselect(
        "Select Pairs to Scan",
        available_pairs,
        default=available_pairs
    )
    
    st.markdown(f"**Selected:** {len(selected_pairs)} pairs")
    
    st.markdown("---")
    
    # Time filter
    st.markdown("#### ⏰ Time Filter")
    hours_filter = st.slider("Show signals from last (hours)", 1, 168, 24, help="168h = 7 days")
    
    st.markdown("---")
    
    # Telegram toggle
    st.markdown("#### 📱 Telegram Alerts")
    send_telegram = st.checkbox("Send alerts to Telegram", value=True)
    
    st.markdown("---")
    scan_clicked = st.button("🚀 Start Scan", use_container_width=True, type="primary")


# ========== MAIN SCAN LOGIC ==========
if scan_clicked:
    if not selected_pairs:
        st.error("⚠️ Please select at least one crypto pair!")
    elif not CCXT_AVAILABLE:
        st.error("⚠️ ccxt not installed! Run: `pip install ccxt`")
    else:
        progress = st.progress(0)
        status = st.empty()
        
        if scan_mode == "🟡 1H Sweep (Ready)":
            all_signals = []
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_filter)
            
            for i, pair in enumerate(selected_pairs):
                status.text(f"⏳ Scanning {pair} (1H)...")
                df = download_crypto_data(pair, '1h', HTF_CANDLE_LIMIT)
                
                if df.empty or len(df) < 30:
                    progress.progress((i + 1) / len(selected_pairs))
                    continue
                
                pivot_lows = detect_pivot_lows_multi(df, SWING_LENGTHS_HTF)
                sweeps = detect_liquidity_sweep(df, pivot_lows)
                
                for sweep in sweeps:
                    sweep['ticker'] = pair
                    if sweep['date'] >= pd.Timestamp(cutoff_time):
                        all_signals.append(sweep)
                
                progress.progress((i + 1) / len(selected_pairs))
            
            progress.empty()
            status.empty()
            
            st.markdown("---")
            st.markdown(f"""
            <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 20px;">
                <span class="mode-tag mode-sweep">🟡 1H LIQUIDITY SWEEP (Ready Signals)</span>
                <span class="crypto-badge"><span class="live-dot"></span> Real-Time</span>
            </div>
            """, unsafe_allow_html=True)
            
            all_signals.sort(key=lambda x: (x['date'], x['score']), reverse=True)
            
            a_signals = [s for s in all_signals if s['grade'] == 'A+']
            b_signals = [s for s in all_signals if s['grade'] == 'B']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Total Signals", len(all_signals))
            with col2: st.metric("🏆 A+ Signals", len(a_signals))
            with col3: st.metric("✅ B Signals", len(b_signals))
            with col4: st.metric("Pairs Scanned", len(selected_pairs))
            
            st.markdown("---")
            
            if all_signals:
                st.markdown("## 📊 1H Sweep Results (READY Signals)")
                
                if send_telegram and a_signals:
                    telegram_count = 0
                    for sig in a_signals[:5]:
                        msg = format_telegram_signal(sig, "ready")
                        if send_telegram_alert(READY_BOT_TOKEN, msg):
                            telegram_count += 1
                    if telegram_count > 0:
                        st.success(f"📱 {telegram_count} A+ alerts sent to Telegram!")
                
                if a_signals:
                    st.markdown("### 🏆 Grade A+ (Score ≥ 70) - BEST SETUPS")
                    for sig in a_signals:
                        st.markdown(f"""<div class="signal-good">
                        <strong>{sig['ticker']}</strong> | {to_ist(sig['date'])} | Score: {sig['score']:.0f}/100 | Swing: ${sig['swing_low']:.4f} ({get_swing_label(sig['swing_type'])}) | Depth: {sig['depth_percent']:.3f}% | Wick: {sig['wick_percent']:.0f}%
                        </div>""", unsafe_allow_html=True)
                
                if b_signals:
                    st.markdown("### ✅ Grade B (Score 55-69)")
                    for sig in b_signals:
                        st.markdown(f"""<div class="signal-medium">
                        <strong>{sig['ticker']}</strong> | {to_ist(sig['date'])} | Score: {sig['score']:.0f}/100 | Depth: {sig['depth_percent']:.3f}%
                        </div>""", unsafe_allow_html=True)
                
                # Show all signals in table
                c_signals = [s for s in all_signals if s['grade'] in ['C', 'D']]
                if c_signals:
                    with st.expander(f"📋 Other Signals ({len(c_signals)})"):
                        data = []
                        for s in c_signals:
                            data.append({
                                'Pair': s['ticker'],
                                'Time': s['date'].strftime('%d-%b %H:%M'),
                                'Score': f"{s['score']:.0f}",
                                'Grade': s['grade'],
                                'Depth': f"{s['depth_percent']:.3f}%",
                                'Wick': f"{s['wick_percent']:.0f}%"
                            })
                        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            else:
                st.info(f"No liquidity sweep signals found in last {hours_filter} hours.")
        
        else:
            # HTF CONFIRMATION MODE (1H + 3min)
            all_confirmed = []
            all_ready = []
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_filter)
            
            for i, pair in enumerate(selected_pairs):
                status.text(f"⏳ Scanning {pair} (1H + 3min)...")
                
                # Step 1: Get 1H data
                df_1h = download_crypto_data(pair, '1h', HTF_CANDLE_LIMIT)
                if df_1h.empty or len(df_1h) < 30:
                    progress.progress((i + 1) / len(selected_pairs))
                    continue
                
                pivot_lows_1h = detect_pivot_lows_multi(df_1h, SWING_LENGTHS_HTF)
                sweeps_1h = detect_liquidity_sweep(df_1h, pivot_lows_1h)
                
                htf_recent = []
                for sweep in sweeps_1h:
                    sweep['ticker'] = pair
                    if sweep['date'] >= pd.Timestamp(cutoff_time):
                        htf_recent.append(sweep)
                        all_ready.append(sweep)
                
                # Step 2: If 1H sweep found, check 3min
                if htf_recent:
                    df_3m = download_crypto_data(pair, '5m', LTF_CANDLE_LIMIT)
                    if not df_3m.empty and len(df_3m) >= 20:
                        pivot_lows_3m = detect_pivot_lows_multi(df_3m, SWING_LENGTHS_LTF)
                        sweeps_3m = detect_liquidity_sweep(df_3m, pivot_lows_3m)
                        
                        for htf_sweep in htf_recent:
                            for ltf_sweep in sweeps_3m:
                                ltf_sweep['ticker'] = pair
                                time_diff = (ltf_sweep['date'] - htf_sweep['date']).total_seconds()
                                if time_diff >= -300 and time_diff <= CONFIRM_WINDOW_HOURS * 3600:
                                    all_confirmed.append({
                                        'ticker': pair,
                                        'htf_date': htf_sweep['date'],
                                        'htf_score': htf_sweep['score'],
                                        'htf_grade': htf_sweep['grade'],
                                        'htf_depth': htf_sweep['depth_percent'],
                                        'htf_swing_low': htf_sweep['swing_low'],
                                        'ltf_date': ltf_sweep['date'],
                                        'ltf_score': ltf_sweep['score'],
                                        'ltf_grade': ltf_sweep['grade'],
                                        'ltf_depth': ltf_sweep['depth_percent'],
                                        'ltf_swing_low': ltf_sweep['swing_low'],
                                        'current_price': df_3m['Close'].iloc[-1]
                                    })
                                    break
                
                progress.progress((i + 1) / len(selected_pairs))
            
            progress.empty()
            status.empty()
            
            st.markdown("---")
            st.markdown(f"""
            <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 20px;">
                <span class="mode-tag mode-fp">🟢 HTF CONFIRMATION (1H + 3min)</span>
                <span class="crypto-badge"><span class="live-dot"></span> Real-Time</span>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("🟡 1H Ready", len(all_ready))
            with col2: st.metric("🟢 Confirmed", len(all_confirmed))
            with col3: st.metric("Pairs Scanned", len(selected_pairs))
            with col4: st.metric("⏰ Filter", f"{hours_filter}h")
            
            st.markdown("---")
            
            if all_confirmed:
                st.markdown("## 🔥 CONFIRMED ENTRIES — 1H + 3min DOUBLE SWEEP!")
                st.caption("These pairs have BOTH 1H and 3min liquidity sweeps — highest probability entries!")
                
                if send_telegram:
                    telegram_count = 0
                    for sig in all_confirmed[:5]:
                        msg = format_telegram_signal(sig, "confirmed")
                        if send_telegram_alert(CONFIRM_BOT_TOKEN, msg):
                            telegram_count += 1
                    if telegram_count > 0:
                        st.success(f"📱 {telegram_count} Confirmed alerts sent to Telegram!")
                
                for sig in all_confirmed:
                    st.markdown(f"""
                    <div class="fp-card at-fp">
                        <div class="ticker">{sig['ticker']}</div>
                        <div style="color: #ffd700; margin-top: 8px; font-size: 1.1em;">
                            📈 <b>1H Sweep:</b> {to_ist(sig['htf_date'])} | Score: {sig['htf_score']:.0f}/100 | Depth: {sig['htf_depth']:.3f}%
                        </div>
                        <div style="color: #00ff88; margin-top: 5px; font-size: 1.1em;">
                            🎯 <b>3min Sweep:</b> {to_ist(sig['ltf_date'])} | Score: {sig['ltf_score']:.0f}/100 | Depth: {sig['ltf_depth']:.3f}%
                        </div>
                        <div style="color: #ffffff; margin-top: 8px;">
                            💰 Current Price: ${sig['current_price']:.4f}
                        </div>
                        <div style="color: #00ff88; margin-top: 10px; font-weight: 600;">
                            ✅ 1H + 3min DOUBLE CONFIRMED — SMC FRACTAL ENTRY! 🔥
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show ready-only signals
                ready_only = [r for r in all_ready if r['ticker'] not in [c['ticker'] for c in all_confirmed]]
                if ready_only:
                    st.markdown("---")
                    st.markdown("## 🟡 1H Sweep Ready (Waiting 3min Confirmation)")
                    data = []
                    for s in ready_only:
                        data.append({
                            'Pair': s['ticker'],
                            'Time': to_ist(s['date']),
                            'Score': f"{s['score']:.0f}/100",
                            'Grade': s['grade'],
                            'Depth': f"{s['depth_percent']:.3f}%"
                        })
                    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            else:
                st.info(f"No HTF confirmed signals found in last {hours_filter} hours.")
                if all_ready:
                    st.warning(f"🟡 {len(all_ready)} pairs have 1H sweep but no 3min confirmation yet.")


# ========== HOW IT WORKS ==========
with st.expander("ℹ️ How It Works"):
    st.markdown("""
    ### 🟡 1H Sweep Mode (Ready)
    Detects when price sweeps below a swing low on the **1-Hour chart** — institutional liquidity grab.
    
    ### 🟢 HTF Confirmation Mode (1H + 3min)
    **SMC Fractal Strategy:**
    1. First detects **1H liquidity sweep** (higher timeframe context)
    2. Then checks **3min chart** for a matching sweep (precision entry)
    3. When **BOTH** timeframes show a sweep = **CONFIRMED ENTRY** 🔥
    
    ### 📱 Dual Telegram Alerts
    - **Ready Bot** 🟡 — sends alert when 1H sweep detected
    - **Confirm Bot** 🟢 — sends alert when both 1H + 3min sweep confirmed
    
    ### ⏰ Real-Time Data
    Data is fetched directly from Coinbase via ccxt — **zero delay**, real-time prices!
    """)

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""<div style="text-align: center; color: #6e7681; padding: 20px; font-size: 0.85em;">
    TAWAQQUL HTF SCANNER v1.0 • Multi-Timeframe Confirmation (1H → 3min) • SMC Fractal • Real-Time via Coinbase • by @yousufkidiya17
</div>""", unsafe_allow_html=True)
