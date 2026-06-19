<div align="center">

# ðŸ“Š Smart Trading Scanner

### _Institutional-Grade Smart Money Concept Scanner for Indian Markets_

[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![NSE](https://img.shields.io/badge/NSE-Indian_Stocks-2962FF?style=for-the-badge)](#)
[![Crypto](https://img.shields.io/badge/Crypto-BTC_ETH_SOL-F7931A?style=for-the-badge&logo=bitcoin&logoColor=white)](#)

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:161b22,100:0d1117&height=120&section=header" width="100%"/>

**Smart Trading Scanner** detects **liquidity sweeps**, **order blocks**, **fair value gaps**, and **institutional money flow** across Indian stocks (NSE) and top cryptocurrencies in real-time. Built for traders who follow **Smart Money Concepts (SMC)**.

[ðŸ“– **Features**](#-features) Â· [ðŸš€ **Quick Start**](#-quick-start) Â· [ðŸ› **Report Bug**](https://github.com/yousufkidiya17/smart-trading-scanner/issues)

</div>

---

## ðŸŽ¯ Overview

> _"See what the institutions see â€” before the crowd catches on."_

Smart Trading Scanner combines **Smart Money Concepts (SMC)** with real-time market data to identify high-probability setups. It scans for liquidity grabs, order block formations, and institutional accumulation/distribution patterns across **NSE stocks** and **crypto markets**.

<div align="center">

| ðŸ’§ Liquidity Sweeps | ðŸ“¦ Order Blocks | ðŸ“‰ Fair Value Gaps |
|:---:|:---:|:---:|
| Detect stop-hunt wicks & liquidity grabs | Identify institutional supply/demand zones | Spot imbalanced price action for entries |

| ðŸ”„ Break of Structure | ðŸ“Š Multi-Timeframe | âš¡ Real-Time Alerts |
|:---:|:---:|:---:|
| BOS/CHoCH detection for trend shifts | Scan from 1H to Daily timeframes | Instant notifications on setups |

</div>

---

## âœ¨ Features

### ðŸ“ˆ Smart Money Concept Detection
- **Liquidity Sweep** detection â€” identify institutional stop hunts
- **Order Block (OB)** identification â€” supply & demand zones
- **Fair Value Gap (FVG)** scanning â€” imbalanced price zones
- **Break of Structure (BOS)** â€” trend reversal detection
- **Change of Character (CHoCH)** â€” momentum shift signals

### ðŸ‡®ðŸ‡³ Indian Stock Market (NSE)
- Full **NSE stock universe** scanning
- **Sector-wise filtering** (Banking, IT, Pharma, FMCG, etc.)
- **NIFTY 50, NIFTY BANK, NIFTY IT** index support
- Pre-built **sector cache** for lightning-fast scans

### ðŸª™ Cryptocurrency Markets
- **BTC, ETH, SOL** and top altcoins
- Higher timeframe (HTF) analysis
- Cross-exchange data aggregation

### ðŸ–¥ï¸ Interactive Dashboard
- **Streamlit-powered** real-time dashboard
- Visual **candlestick charts** with annotations
- **Sector heatmaps** for market breadth
- One-click scan results with signal strength

---

## ðŸ—ï¸ Architecture

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              SMART TRADING SCANNER                     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                        â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚  â”‚  NSE Data   â”‚  â”‚  Crypto Data â”‚  â”‚  Sector Data â”‚ â”‚
â”‚  â”‚  (yfinance) â”‚  â”‚  (ccxt/API)  â”‚  â”‚  (Cached)    â”‚ â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â”‚         â”‚                â”‚                  â”‚          â”‚
â”‚         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜          â”‚
â”‚                          â”‚                             â”‚
â”‚              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”                â”‚
â”‚              â”‚   SMC Analysis Engine   â”‚                â”‚
â”‚              â”‚  â”œ Liquidity Scanner    â”‚                â”‚
â”‚              â”‚  â”œ Order Block Finder   â”‚                â”‚
â”‚              â”‚  â”œ FVG Detector         â”‚                â”‚
â”‚              â”‚  â”” BOS/CHoCH Tracker    â”‚                â”‚
â”‚              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                â”‚
â”‚                          â”‚                             â”‚
â”‚              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”                â”‚
â”‚              â”‚  Streamlit Dashboard    â”‚                â”‚
â”‚              â”‚  Charts + Alerts + UI   â”‚                â”‚
â”‚              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ðŸš€ Quick Start

### Prerequisites

- **Python** 3.10+
- **pip** (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/yousufkidiya17/smart-trading-scanner.git
cd smart-trading-scanner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Build sector caches (first run only)
python build_all_caches.py

# Launch the dashboard
streamlit run dashboard.py
```

The scanner will be live at `http://localhost:8501` ðŸŽ‰

---

## ðŸ“ Project Structure

```
smart-trading-scanner/
â”œâ”€â”€ dashboard.py              # Main Streamlit dashboard
â”œâ”€â”€ dashboard_simple.py       # Simplified dashboard variant
â”œâ”€â”€ crypto_dashboard_htf.py   # Crypto HTF analysis dashboard
â”œâ”€â”€ auto_scanner_htf.py       # Automated HTF scanner
â”œâ”€â”€ smc_alerts.py             # SMC alert generation v1
â”œâ”€â”€ smc_alerts_v2.py          # SMC alert generation v2
â”œâ”€â”€ build_all_caches.py       # Build all sector caches
â”œâ”€â”€ build_cache_smart.py      # Smart incremental cache builder
â”œâ”€â”€ refresh_sectors.py        # Refresh sector classifications
â”œâ”€â”€ check_volume.py           # Volume analysis utilities
â”œâ”€â”€ test_samhi.py             # Individual stock test runner
â”œâ”€â”€ INDEX CSV/                # Index constituent data
â”œâ”€â”€ SECTORS CSV/              # Sector classification data
â”œâ”€â”€ logo.png                  # Brand logo
â”œâ”€â”€ requirements.txt          # Python dependencies
â”œâ”€â”€ users.json                # User preferences
â”œâ”€â”€ LICENSE                   # MIT License
â””â”€â”€ README.md
```

---

## ðŸ› ï¸ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Dashboard** | Streamlit | Interactive web UI |
| **Analysis** | smartmoneyconcepts, pandas | SMC pattern detection |
| **Data** | yfinance, ccxt | Market data feeds |
| **Charts** | Plotly, mplfinance | Candlestick visualization |
| **Alerts** | Custom engine | Real-time notifications |

</div>

---

## ðŸ“Š Supported Scanners

| Scanner | Timeframe | Markets | Description |
|---------|-----------|---------|-------------|
| **Liquidity Scanner** | 1H | NSE + Crypto | Detects liquidity sweeps & stop hunts |
| **HTF Scanner** | 4H / Daily | NSE + Crypto | Higher timeframe structure analysis |
| **Crypto HTF** | 4H / Daily | Crypto only | Dedicated crypto pattern scanner |
| **Volume Check** | 1H+ | NSE | Unusual volume spike detection |

---

## âš ï¸ Disclaimer

> This tool is for **educational and informational purposes only**. It does not constitute financial advice. Trading involves significant risk of loss. Always do your own research before making investment decisions.

---

## ðŸ“œ License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

## ðŸ‘¨â€ðŸ’» Author

**Yousuf Kidiya**

[![GitHub](https://img.shields.io/badge/GitHub-yousufkidiya17-181717?style=for-the-badge&logo=github)](https://github.com/yousufkidiya17)

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:161b22,100:0d1117&height=100&section=footer" width="100%"/>

**Made with ðŸ“ˆ for Indian Traders**

_If you found this project useful, please consider giving it a â­!_

</div>
