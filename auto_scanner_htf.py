#!/usr/bin/env python3
"""
TAWAQQUL HTF CONFIRMATION SCANNER - Multi-Timeframe (1H + 3min)
================================================================
SMC Fractal Strategy:
  Step 1: Detect 1H liquidity sweep → Send READY alert (Bot 1)
  Step 2: Check 3min sweep on same coin → Send CONFIRMED alert (Bot 2)

Exchange: Coinbase | Timezone: IST
24/7 AWS Auto Scanner + Dual Telegram Alerts
"""
import pandas as pd
import numpy as np
import time
import requests
import pytz
import logging
from datetime import datetime, timedelta

try:
    import ccxt
except ImportError:
    print("ERROR: ccxt not installed! Run: pip install ccxt")
    exit(1)

# ========== TELEGRAM CONFIG (2 BOTS) ==========
# Bot 1: READY alerts (1H sweep detected)
READY_BOT_TOKEN = "8740044507:AAEXMLNFjhtYYcsg4sfZ1843_czrdk2TFXI"
# Bot 2: CONFIRMED alerts (1H + 3min sweep)
CONFIRM_BOT_TOKEN = "8570208083:AAE5DguxpRHGGu3u0Tb3PwHY2RrU2Ry9X1E"
# Chat ID (same user)
CHAT_ID = "5428077566"

# ========== CONFIG ==========
SCAN_INTERVAL_SECONDS = 180  # 3 minutes (matches 3min TF)
HTF_TIMEFRAME = "1h"         # Higher timeframe
LTF_TIMEFRAME = "5m"         # Lower timeframe (entry)
HTF_CANDLE_LIMIT = 500       # ~20 days of 1H data
LTF_CANDLE_LIMIT = 500       # ~25 hours of 3min data
CONFIRM_WINDOW_HOURS = 6     # 3min sweep must happen within 6 hours of 1H sweep

# Scanner Settings
SWING_LENGTHS_HTF = [3, 5, 8]    # For 1H chart
SWING_LENGTHS_LTF = [3, 5]       # For 3min chart (shorter swings)
MIN_WICK_PERCENT = 20
MIN_DEPTH_PERCENT = 0.03
OB_LOOKBACK = 5

# ========== IST TIMEZONE ==========
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    return datetime.now(IST)

def format_ist(dt):
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(IST).strftime('%d-%b %H:%M IST')

# ========== LOGGING ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('htf_scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== CRYPTO PAIRS (Coinbase) ==========
ALL_PAIRS = [
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

# Track state
sent_ready_alerts = {}      # Track ready alerts sent
sent_confirm_alerts = {}    # Track confirmed alerts sent
htf_sweeps_active = {}      # Store active 1H sweeps waiting for 3min confirmation


# ========== TELEGRAM ==========
def send_telegram(bot_token, message):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
        r = requests.post(url, json=payload, timeout=10)
        return r.json().get("ok", False)
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False

def send_ready_alert(signal):
    """Send READY alert to Bot 1 (1H sweep detected)"""
    msg = (
        f"<b>🟡 1H LIQUIDITY SWEEP — READY!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Pair:</b> {signal['ticker']}\n"
        f"⏰ <b>1H Sweep Time:</b> {format_ist(signal['date'])}\n"
        f"💰 <b>Close:</b> ${signal['close']:.4f}\n"
        f"📏 <b>Swing Low:</b> ${signal['swing_low']:.4f}\n"
        f"📐 <b>Depth:</b> {signal['depth_percent']:.3f}%\n"
        f"🕯 <b>Wick:</b> {signal['wick_percent']:.0f}%\n"
        f"⭐ <b>Score:</b> {signal['score']:.0f}/100 ({signal['grade']})\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏳ <b>Waiting for 3min confirmation...</b>\n"
        f"🔍 Will check 3min chart for entry sweep\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 TAWAQQUL HTF Scanner (1H → 3min)"
    )
    return send_telegram(READY_BOT_TOKEN, msg)

def send_confirmed_alert(htf_signal, ltf_signal):
    """Send CONFIRMED alert to Bot 2 (1H + 3min both swept)"""
    msg = (
        f"<b>🟢🔥 CONFIRMED ENTRY — DOUBLE SWEEP!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Pair:</b> {htf_signal['ticker']}\n\n"
        f"<b>📈 1H SWEEP (Higher TF):</b>\n"
        f"  ⏰ {format_ist(htf_signal['date'])}\n"
        f"  📏 Swing Low: ${htf_signal['swing_low']:.4f}\n"
        f"  📐 Depth: {htf_signal['depth_percent']:.3f}%\n"
        f"  ⭐ Score: {htf_signal['score']:.0f}/100 ({htf_signal['grade']})\n\n"
        f"<b>🎯 3min SWEEP (Entry TF):</b>\n"
        f"  ⏰ {format_ist(ltf_signal['date'])}\n"
        f"  📏 Swing Low: ${ltf_signal['swing_low']:.4f}\n"
        f"  📐 Depth: {ltf_signal['depth_percent']:.3f}%\n"
        f"  ⭐ Score: {ltf_signal['score']:.0f}/100 ({ltf_signal['grade']})\n\n"
        f"💰 <b>Current Price:</b> ${ltf_signal['close']:.4f}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>1H + 3min DOUBLE CONFIRMATION!</b>\n"
        f"🎯 <b>PRECISE ENTRY — SMC FRACTAL CONFIRMED</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 TAWAQQUL HTF Scanner (1H → 3min)"
    )
    return send_telegram(CONFIRM_BOT_TOKEN, msg)


# ========== DETECTION FUNCTIONS ==========
def fetch_data(exchange, symbol, timeframe, limit):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        if not ohlcv:
            return pd.DataFrame()
        df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df.set_index('Timestamp', inplace=True)
        return df
    except Exception as e:
        logger.warning(f"{symbol} ({timeframe}): {e}")
        return pd.DataFrame()


def detect_pivot_lows(df, lengths):
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
                already = any(
                    abs(p['index'] - i) <= 2 and abs(p['price'] - current_low) / current_low < 0.001
                    for p in pivot_lows
                )
                if not already:
                    pivot_lows.append({
                        'index': i, 'date': df.index[i],
                        'price': current_low, 'swing_type': length
                    })
    return sorted(pivot_lows, key=lambda x: x['index'])


def detect_sweeps(df, pivot_lows):
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
                total_range = candle_high - candle_low
                lower_wick = min(candle_open, candle_close) - candle_low
                if total_range > 0:
                    wick_percent = (lower_wick / total_range) * 100
                    depth_percent = ((swing_low - candle_low) / swing_low) * 100
                else:
                    continue
                if wick_percent >= MIN_WICK_PERCENT and depth_percent >= MIN_DEPTH_PERCENT:
                    close_pos = (candle_close - candle_low) / total_range * 100
                    score = calculate_score(wick_percent, depth_percent, close_pos, swing_type)
                    grade = get_grade(score)
                    sweeps.append({
                        'ticker': '', 'date': df.index[i], 'sweep_idx': i,
                        'swing_low': swing_low, 'sweep_low': candle_low,
                        'close': candle_close, 'wick_percent': wick_percent,
                        'depth_percent': depth_percent, 'swing_type': swing_type,
                        'score': score, 'grade': grade
                    })
                break
    return sweeps


def calculate_score(wick_pct, depth_pct, close_pos, swing_type):
    score = 0
    score += min(wick_pct / 2, 30)
    score += min(depth_pct * 20, 30)
    score += min(close_pos / 5, 20)
    if swing_type >= 8: score += 20
    elif swing_type >= 5: score += 15
    else: score += 10
    return min(score, 100)

def get_grade(score):
    if score >= 70: return "A+"
    elif score >= 55: return "B"
    elif score >= 40: return "C"
    else: return "D"

def get_alert_key(ticker, date_str, tf):
    return f"{tf}_{ticker}_{date_str}"


# ========== MAIN SCAN LOOP ==========
def run_scan():
    global sent_ready_alerts, sent_confirm_alerts, htf_sweeps_active
    
    exchange = ccxt.coinbase({'enableRateLimit': True})
    ist_now = get_ist_now().strftime('%d-%b %H:%M IST')
    logger.info(f"Scanning {len(ALL_PAIRS)} pairs... ({ist_now})")
    
    ready_count = 0
    confirm_count = 0
    cutoff_1h = datetime.utcnow() - timedelta(hours=48)  # 1H sweeps in last 48 hours
    
    # ===== STEP 1: Scan 1H for sweeps =====
    for pair in ALL_PAIRS:
        try:
            # 1H DATA
            df_1h = fetch_data(exchange, pair, HTF_TIMEFRAME, HTF_CANDLE_LIMIT)
            if df_1h.empty or len(df_1h) < 30:
                continue
            
            pivot_lows_1h = detect_pivot_lows(df_1h, SWING_LENGTHS_HTF)
            sweeps_1h = detect_sweeps(df_1h, pivot_lows_1h)
            
            for sweep in sweeps_1h:
                sweep['ticker'] = pair
                
                # Only recent 1H sweeps
                if sweep['date'] >= pd.Timestamp(cutoff_1h):
                    alert_key = get_alert_key(pair, sweep['date'].strftime('%Y%m%d%H'), "1h")
                    
                    # Send READY alert (Bot 1)
                    if alert_key not in sent_ready_alerts:
                        if sweep['grade'] in ['A+', 'B', 'C']:
                            if send_ready_alert(sweep):
                                ready_count += 1
                                logger.info(f"🟡 READY: {pair} 1H sweep ({sweep['grade']}) Score: {sweep['score']:.0f}")
                            sent_ready_alerts[alert_key] = time.time()
                            
                            # Store for 3min confirmation check
                            htf_sweeps_active[pair] = {
                                'sweep': sweep,
                                'timestamp': time.time()
                            }
                    
                    # If already sent ready but not yet confirmed, keep it active
                    elif pair not in htf_sweeps_active:
                        htf_sweeps_active[pair] = {
                            'sweep': sweep,
                            'timestamp': sent_ready_alerts.get(alert_key, time.time())
                        }
            
            time.sleep(0.1)
            
        except Exception as e:
            logger.warning(f"{pair} (1H): {e}")
            continue
    
    # ===== STEP 2: Check 3min for confirmation =====
    if htf_sweeps_active:
        logger.info(f"Checking 3min confirmation for {len(htf_sweeps_active)} pairs...")
        
        pairs_to_check = list(htf_sweeps_active.keys())
        
        for pair in pairs_to_check:
            htf_data = htf_sweeps_active[pair]
            htf_sweep = htf_data['sweep']
            htf_time = htf_data['timestamp']
            
            # Skip if too old (beyond confirmation window)
            if time.time() - htf_time > CONFIRM_WINDOW_HOURS * 3600:
                logger.info(f"⏰ {pair} expired (>{CONFIRM_WINDOW_HOURS}h old)")
                del htf_sweeps_active[pair]
                continue
            
            try:
                # 3min DATA
                df_3m = fetch_data(exchange, pair, LTF_TIMEFRAME, LTF_CANDLE_LIMIT)
                if df_3m.empty or len(df_3m) < 20:
                    continue
                
                pivot_lows_3m = detect_pivot_lows(df_3m, SWING_LENGTHS_LTF)
                sweeps_3m = detect_sweeps(df_3m, pivot_lows_3m)
                
                # Look for recent 3min sweeps (after the 1H sweep)
                for sweep_3m in sweeps_3m:
                    sweep_3m['ticker'] = pair
                    
                    # 3min sweep should be after or around the 1H sweep time
                    htf_sweep_time = htf_sweep['date']
                    ltf_sweep_time = sweep_3m['date']
                    
                    # Check if 3min sweep is within window
                    time_diff = (ltf_sweep_time - htf_sweep_time).total_seconds()
                    if time_diff >= -300 and time_diff <= CONFIRM_WINDOW_HOURS * 3600:
                        # 3min sweep after 1H sweep (within window)
                        confirm_key = get_alert_key(pair, ltf_sweep_time.strftime('%Y%m%d%H%M'), "confirm")
                        
                        if confirm_key not in sent_confirm_alerts:
                            if sweep_3m['grade'] in ['A+', 'B', 'C']:
                                if send_confirmed_alert(htf_sweep, sweep_3m):
                                    confirm_count += 1
                                    logger.info(f"🟢🔥 CONFIRMED: {pair} 1H+3min sweep! Scores: {htf_sweep['score']:.0f}/{sweep_3m['score']:.0f}")
                                sent_confirm_alerts[confirm_key] = time.time()
                                
                                # Remove from active (confirmed)
                                if pair in htf_sweeps_active:
                                    del htf_sweeps_active[pair]
                            break
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"{pair} (3min): {e}")
                continue
    
    # Clean old alerts (older than 48 hours)
    current_time = time.time()
    sent_ready_alerts = {k: v for k, v in sent_ready_alerts.items() if current_time - v < 172800}
    sent_confirm_alerts = {k: v for k, v in sent_confirm_alerts.items() if current_time - v < 172800}
    
    active = len(htf_sweeps_active)
    logger.info(f"Scan done! Ready: {ready_count} | Confirmed: {confirm_count} | Waiting: {active}")
    return ready_count, confirm_count


# ========== ENTRY POINT ==========
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("TAWAQQUL HTF CONFIRMATION SCANNER v1.0")
    logger.info("Multi-Timeframe: 1H + 3min | SMC Fractal")
    logger.info(f"Exchange: Coinbase | Timezone: IST")
    logger.info(f"Pairs: {len(ALL_PAIRS)} | Interval: {SCAN_INTERVAL_SECONDS}s")
    logger.info(f"HTF: {HTF_TIMEFRAME} | LTF: {LTF_TIMEFRAME}")
    logger.info(f"Confirm Window: {CONFIRM_WINDOW_HOURS}h")
    logger.info("=" * 60)
    
    # Startup notification to both bots
    send_telegram(READY_BOT_TOKEN,
        "🟡 <b>TAWAQQUL HTF Scanner STARTED!</b>\n\n"
        f"📊 Scanning {len(ALL_PAIRS)} crypto pairs\n"
        f"🏦 Exchange: Coinbase (Real-Time)\n"
        f"📏 HTF: {HTF_TIMEFRAME} | LTF: {LTF_TIMEFRAME}\n"
        f"⏰ Every {SCAN_INTERVAL_SECONDS // 60} minutes\n"
        f"🕐 Started: {get_ist_now().strftime('%d-%b-%Y %H:%M IST')}\n\n"
        "🟡 This bot sends READY alerts (1H sweep detected)"
    )
    
    send_telegram(CONFIRM_BOT_TOKEN,
        "🟢 <b>TAWAQQUL HTF Scanner STARTED!</b>\n\n"
        f"📊 Scanning {len(ALL_PAIRS)} crypto pairs\n"
        f"🏦 Exchange: Coinbase (Real-Time)\n"
        f"📏 HTF: {HTF_TIMEFRAME} | LTF: {LTF_TIMEFRAME}\n"
        f"⏰ Every {SCAN_INTERVAL_SECONDS // 60} minutes\n"
        f"🕐 Started: {get_ist_now().strftime('%d-%b-%Y %H:%M IST')}\n\n"
        "🟢 This bot sends CONFIRMED alerts (1H + 3min double sweep)"
    )
    
    scan_count = 0
    while True:
        try:
            scan_count += 1
            logger.info(f"\n--- Scan #{scan_count} at {get_ist_now().strftime('%H:%M:%S IST')} ---")
            
            ready, confirmed = run_scan()
            
            logger.info(f"Next scan in {SCAN_INTERVAL_SECONDS}s...")
            time.sleep(SCAN_INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            logger.info("Scanner stopped by user.")
            send_telegram(READY_BOT_TOKEN, "🔴 <b>TAWAQQUL HTF Scanner STOPPED!</b>")
            send_telegram(CONFIRM_BOT_TOKEN, "🔴 <b>TAWAQQUL HTF Scanner STOPPED!</b>")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(60)
