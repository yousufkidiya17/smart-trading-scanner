# 📊 Smart Trading Scanner

<div align="center">

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![yfinance](https://img.shields.io/badge/yfinance-0.2.36+-brightgreen.svg)](https://pypi.org/project/yfinance/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](#)
[![Trading](https://img.shields.io/badge/Type-Stocks%20%2B%20Crypto-orange.svg)](#)

*Advanced Smart Money Concept (SMC) scanners for Indian Stocks & Cryptocurrency trading*

</div>

---

## 📋 Table of Contents

- [Features](#features)
- [Scanners](#scanners)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Configuration](#configuration)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## ✨ Features

### Core Features

| Feature | Description |
|---------|-------------|
| 📈 **Liquidity Sweep Detection** | Detect swing low/high sweeps |
| 🎯 **Fair Price Zones** | Identify Order Block zones |
| 📊 **Multi-Timeframe** | 1H, 4H, Daily analysis |
| 🔄 **Auto-Scan** | Automated scanning with alerts |
| 📱 **Telegram Alerts** | Real-time notifications |
| 🏭 **Sector Scanning** | 19+ Indian market sectors |
| 📑 **Index Scanning** | Nifty 50, 100, 200, 500, etc. |

### Supported Markets

- 🇮🇳 **Indian Stocks** - NSE/BSE
- ₿ **Cryptocurrency** - Binance, Bybit, OKX

---

## 🔍 Scanners

### 1. Stock Liquidity Scanner (1H)
**File:** `dashboard_simple.py`

Hourly liquidity sweep detection for Indian stocks with fair price zone detection.

- Scan Nifty 50, 100, 200, 500
- Scan 19+ sectors
- Telegram alerts
- CSV/JSON export

### 2. Crypto HTF Scanner
**File:** `crypto_dashboard_htf.py`

Multi-timeframe (1H + 3min) crypto scanner with dual confirmation.

- 1H Sweep detection
- HTF Confirmation (1H + 3min)
- Dual Telegram bots
- Multiple exchanges support

### 3. SMC Liquidity Grab Scanner
**File:** `dashboard.py`, `smc_alerts.py`

Smart Money Concepts based liquidity grab detection.

- Liquidity grab patterns
- Order block zones
- Fair value gaps
- Smart money tracking

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yousufkidiya17/smart-trading-scanner.git
cd smart-trading-scanner

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 📖 Usage

```bash
# Stock Scanner
streamlit run dashboard_simple.py

# Crypto Scanner  
streamlit run crypto_dashboard_htf.py

# SMC Scanner
streamlit run dashboard.py
```

---

## ⚠️ Disclaimer

**This tool is for educational purposes only. Not financial advice.**

---

## 📄 License

MIT License - See LICENSE file
