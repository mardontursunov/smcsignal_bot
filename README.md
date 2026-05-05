# 📡 XAU/USD SMC Signal Telegram Bot

A fully automated Telegram bot that generates **10–20 daily trading signals** for Gold (XAU/USD) using **Smart Money Concepts (SMC)** and **ICT** methodology on the M15 timeframe.

---

## 🧠 SMC Concepts Detected

| Concept | Description |
|---|---|
| 🟦 **Order Blocks (OB)** | Last opposing candle before a strong displacement |
| ⚡ **Fair Value Gaps (FVG)** | 3-candle price imbalance (inefficiency) |
| 🔄 **BOS / ChoCh** | Break of Structure / Change of Character |
| 💧 **Liquidity Sweeps** | Stop hunts above equal highs (BSL) or below equal lows (SSL) |
| 📍 **Premium / Discount** | 50% Fibonacci of the swing range |
| 🕐 **Kill Zones** | London Open (07–10 UTC) & NY Open (12–15 UTC) |

---

## 📦 Project Structure

```
xauusd_smc_bot/
├── bot.py               # Main Telegram bot + scheduler
├── market_data.py       # Twelve Data API fetcher + kill zone detection
├── smc_engine.py        # SMC/ICT detection engine
├── signal_generator.py  # Confluence scoring → BUY/SELL signals
├── requirements.txt
├── .env.example         # Copy to .env and fill in your keys
└── README.md
```

---

## 🚀 Quick Setup (5 minutes)

### 1. Clone / Download the project
```bash
cd ~/Desktop
# place the xauusd_smc_bot folder here
cd xauusd_smc_bot
```

### 2. Create Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate       # Linux/Mac
# OR
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get your API keys

#### Telegram Bot Token
1. Open Telegram → search **@BotFather**
2. Send `/newbot`, follow the prompts
3. Copy the token (looks like `123456789:AAFxxx...`)

#### Telegram Chat ID
- **Personal chat**: Message **@userinfobot**, it replies with your ID
- **Group**: Add **@getidsbot** to the group, it shows the group ID
- **Channel**: Use `@yourchannel` or add bot as admin and use `-100xxxxxxxxxx` format

#### Twelve Data API Key (Free)
1. Sign up at [twelvedata.com](https://twelvedata.com)
2. Go to Dashboard → API Key
3. Free plan gives **800 credits/day** (more than enough for M15 scans)

### 5. Configure .env
```bash
cp .env.example .env
# Edit .env with your actual values:
nano .env
```

```
TELEGRAM_TOKEN=123456789:AAFxxxxxxxxxxxxx
TELEGRAM_CHAT_ID=-1001234567890
TWELVE_API_KEY=abcd1234efgh5678
```

### 6. Run the bot
```bash
python bot.py
```

You should see:
```
🚀 XAU/USD SMC Signal Bot started
Signals per day: 10–20
Scan interval: every 15 minutes
```

---

## 📱 Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message & overview |
| `/signal` | Trigger an immediate scan and get signals now |
| `/status` | See signals sent today, last scan time, kill zone status |
| `/help` | Full guide on SMC concepts and how to trade the signals |

---

## 📊 Signal Format

```
━━━━━━━━━━━━━━━━━━━━━
🟢 SIGNAL #3 — XAU/USD BUY ↗️
━━━━━━━━━━━━━━━━━━━━━
📌 Setup: Bullish OB
🕐 Timeframe: M15
⏰ Kill Zone: 🇬🇧 London Open

💰 Entry:      2318.50
🛑 Stop Loss:  2311.20
🎯 TP1 (1:2):  2333.10
🎯 TP2 (1:3):  2340.40
📏 Risk:       7.30 pts

📊 SMC Confluences:
   ✅ Trend: Bullish structure (HH/HL)
   🟦 Bullish Order Block @ 2321.00–2318.00 (strength 0.31%)
   ⚡ FVG inside OB (2317.50–2319.00)
   🕐 Kill Zone: 🇬🇧 London Open
   💧 SSL Liquidity Sweep @ 2315.00 (stop hunt below lows)

🔋 Confidence: ▓▓▓▓░ 80%
🕰 Generated: 2024-11-01 08:15 UTC
```

---

## ⚙️ Configuration

Edit these constants in `bot.py`:

```python
MAX_SIGNALS_PER_DAY = 20     # cap per day
MIN_SIGNALS_PER_DAY = 10     # (informational)
SCAN_INTERVAL_SECONDS = 900  # 15 minutes
SCAN_START_HOUR = 6          # UTC — when to start scanning
SCAN_END_HOUR = 20           # UTC — when to stop scanning
```

Edit in `signal_generator.py`:
```python
MIN_CONFIDENCE = 50          # raise to 65+ for fewer, higher quality signals
SL_BUFFER_PTS = 3.0          # extra SL buffer in USD
TP1_RR = 2.0                 # Risk:Reward ratio TP1
TP2_RR = 3.0                 # Risk:Reward ratio TP2
```

---

## ⚠️ Risk Disclaimer

This bot is for **educational and informational purposes only**. It does not constitute financial advice. Always:
- Risk only **1–2% of your account** per trade
- Use your own analysis alongside any signals
- Never trade money you cannot afford to lose

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `TELEGRAM_TOKEN not set` | Check your `.env` file |
| `API error: You have run out of API credits` | Free tier exhausted — wait until midnight UTC |
| No signals sent | Price not at OB/FVG right now — normal, waits for setup |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in virtualenv |
