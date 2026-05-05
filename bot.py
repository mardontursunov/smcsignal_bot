"""
bot.py — XAU/USD SMC Signal Bot
Yangiliklar:
  - /start → bot haqida ma'lumot + til tanlash (EN/RU/UZ)
  - Kanal obunasi tekshiruvi (-1002298501211)
  - SL: 50-100 pips, RR: 1:1.5 / 1:2 / 1:3
  - TP1, TP2, SL hit → avtomatik ogohlantirish
  - Kuniga minimum 10 signal
"""

import asyncio
import logging
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError

from market_data import MarketData
from smc_engine import SMCEngine
from signal_generator import SignalGenerator, Signal
from translations import t, TEXTS

load_dotenv()
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")],
)
logger = logging.getLogger("XAU_BOT")


# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────

TELEGRAM_TOKEN  = os.getenv("TELEGRAM_TOKEN", "")
CHAT_ID         = os.getenv("TELEGRAM_CHAT_ID", "")
TWELVE_API_KEY  = os.getenv("TWELVE_API_KEY", "")

REQUIRED_CHANNEL_ID  = -1002298501211          # obuna tekshiriladigan kanal
CHANNEL_INVITE_LINK  = "https://t.me/+FUSgOGyTKvkwYjcy"  # o'z linkinigizga almashtiring

MIN_SIGNALS_PER_DAY  = 10
MAX_SIGNALS_PER_DAY  = 20
SCAN_INTERVAL        = 15 * 60   # 15 daqiqa
SCAN_START_HOUR      = 6         # UTC
SCAN_END_HOUR        = 20        # UTC

LANG_FILE            = "user_languages.json"
ACTIVE_SIGNALS_FILE  = "active_signals.json"


# ─────────────────────────────────────────────
# Language store
# ─────────────────────────────────────────────

def _load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

_lang_store: dict = _load_json(LANG_FILE, {})

def get_lang(uid) -> str:
    return _lang_store.get(str(uid), "uz")   # default: uzbek

def set_lang(uid, lang: str):
    _lang_store[str(uid)] = lang
    _save_json(LANG_FILE, _lang_store)


# ─────────────────────────────────────────────
# Active signal tracker (for TP/SL monitoring)
# ─────────────────────────────────────────────

class SignalTracker:
    """Keeps active signals in memory + persists to JSON for restarts."""

    def __init__(self):
        self._signals: dict[str, Signal] = {}  # signal.id → Signal
        self._chat_ids: dict[str, str]   = {}  # signal.id → chat_id where it was sent

    def add(self, sig: Signal, chat_id: str):
        self._signals[sig.id] = sig
        self._chat_ids[sig.id] = chat_id

    def all_active(self) -> list[tuple[Signal, str]]:
        return [(s, self._chat_ids[sid])
                for sid, s in self._signals.items() if s.active]

    def remove_inactive(self):
        dead = [sid for sid, s in self._signals.items() if not s.active]
        for sid in dead:
            self._signals.pop(sid, None)
            self._chat_ids.pop(sid, None)

tracker = SignalTracker()


# ─────────────────────────────────────────────
# Bot state
# ─────────────────────────────────────────────

class BotState:
    def __init__(self):
        self.signals_today = 0
        self.last_scan: datetime | None = None
        self.day = datetime.now(timezone.utc).day
        self.scan_count = 0

    def reset_if_new_day(self):
        today = datetime.now(timezone.utc).day
        if today != self.day:
            self.day = today
            self.signals_today = 0
            self.scan_count = 0
            logger.info("Yangi kun — hisoblagich nolga qaytdi")

state = BotState()


# ─────────────────────────────────────────────
# Subscription check
# ─────────────────────────────────────────────

async def is_subscribed(bot: Bot, user_id: int) -> bool:
    """Returns True if user is member of REQUIRED_CHANNEL_ID."""
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except TelegramError as e:
        logger.warning(f"Obuna tekshirishda xato: {e}")
        return False


def sub_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalga o'tish / Перейти / Go to Channel",
                              url=CHANNEL_INVITE_LINK)],
        [InlineKeyboardButton(t(lang, "check_sub_btn"),
                              callback_data="check_sub")],
    ])


# ─────────────────────────────────────────────
# Formatting
# ─────────────────────────────────────────────

CONF_BARS = {
    (0,  60):  "▓░░░░",
    (60, 70):  "▓▓░░░",
    (70, 80):  "▓▓▓░░",
    (80, 90):  "▓▓▓▓░",
    (90, 101): "▓▓▓▓▓",
}

def conf_bar(score: int) -> str:
    for (lo, hi), bar in CONF_BARS.items():
        if lo <= score < hi:
            return bar
    return "▓▓▓▓▓"


def fmt_signal(sig: Signal, index: int, lang: str) -> str:
    emoji     = "🟢" if sig.direction == "BUY" else "🔴"
    dir_str   = t(lang, "direction_buy") if sig.direction == "BUY" else t(lang, "direction_sell")
    kz_line   = f"{t(lang, 'kill_zone_lbl')} {sig.kill_zone}\n" if sig.kill_zone else ""
    conf_str  = f"{conf_bar(sig.confidence)} {sig.confidence}%"
    conf_list = "\n".join(f"   {c}" for c in sig.confluences)
    rr1_str   = f"{sig.rr1:.1f}".rstrip("0").rstrip(".")
    rr2_str   = f"{sig.rr2:.1f}".rstrip("0").rstrip(".")

    return (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} *{t(lang, 'signal_title', index=index, direction=dir_str)}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t(lang, 'signal_id')} `{sig.id}`\n"
        f"{t(lang, 'setup')} {sig.ob_type}\n"
        f"{t(lang, 'timeframe')} {sig.timeframe}\n"
        f"{kz_line}"
        f"\n"
        f"{t(lang, 'entry')}      `{sig.entry:.2f}`\n"
        f"{t(lang, 'stop_loss')}  `{sig.stop_loss:.2f}` ({sig.sl_pips} {t(lang, 'pips')})\n"
        f"{t(lang, 'tp1', rr1=rr1_str)}  `{sig.take_profit_1:.2f}`\n"
        f"{t(lang, 'tp2', rr2=rr2_str)}  `{sig.take_profit_2:.2f}`\n"
        f"\n"
        f"{t(lang, 'confluences')}\n"
        f"{conf_list}\n"
        f"\n"
        f"{t(lang, 'confidence')} {conf_str}\n"
        f"{t(lang, 'generated')} {sig.timestamp.strftime('%Y-%m-%d %H:%M')} UTC\n"
        f"\n"
        f"{t(lang, 'disclaimer')}"
    )


def fmt_header(count: int, lang: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"{t(lang, 'signal_header')}\n"
        f"🕐 {now}\n"
        f"{t(lang, 'signal_count', count=count)}\n"
        f"{t(lang, 'total_today', total=state.signals_today)}\n"
    )


# ─────────────────────────────────────────────
# Core scan
# ─────────────────────────────────────────────

async def run_scan(bot: Bot, chat_id: str, lang: str = "uz") -> int:
    state.reset_if_new_day()

    if state.signals_today >= MAX_SIGNALS_PER_DAY:
        return 0

    now_utc = datetime.now(timezone.utc)
    if not (SCAN_START_HOUR <= now_utc.hour < SCAN_END_HOUR):
        return 0

    try:
        md  = MarketData(TWELVE_API_KEY)
        df  = md.get_candles("XAU/USD", "15min", outputsize=200)
        kz  = md.is_kill_zone()

        gen     = SignalGenerator(SMCEngine())
        signals = gen.generate(df, kz)
        signals = signals[:2]

        state.last_scan  = now_utc
        state.scan_count += 1

        if not signals:
            # Agar bugun hali 10 ta signal bo'lmasa va soat kech bo'lsa — warning
            if state.signals_today < MIN_SIGNALS_PER_DAY and now_utc.hour >= 18:
                logger.warning(f"Bugun faqat {state.signals_today} signal — minimum {MIN_SIGNALS_PER_DAY}")
            return 0

        header  = fmt_header(len(signals), lang)
        await bot.send_message(chat_id=chat_id, text=header, parse_mode=ParseMode.MARKDOWN)

        remaining = MAX_SIGNALS_PER_DAY - state.signals_today
        to_send   = signals[:remaining]

        for i, sig in enumerate(to_send, start=state.signals_today + 1):
            msg = fmt_signal(sig, i, lang)
            await bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)
            tracker.add(sig, chat_id)
            await asyncio.sleep(1)

        state.signals_today += len(to_send)
        logger.info(f"Yuborildi: {len(to_send)} ta signal. Bugun jami: {state.signals_today}")
        return len(to_send)

    except Exception as e:
        logger.error(f"Skan xatosi: {e}", exc_info=True)
        return 0


# ─────────────────────────────────────────────
# TP / SL monitor job
# ─────────────────────────────────────────────

async def monitor_signals(context: ContextTypes.DEFAULT_TYPE):
    """Every 5 min: check if any active signal hit TP or SL."""
    active = tracker.all_active()
    if not active:
        return

    try:
        md = MarketData(TWELVE_API_KEY)
        df = md.get_candles("XAU/USD", "15min", outputsize=5)
        current_price = float(df["close"].iloc[-1])
    except Exception as e:
        logger.warning(f"Monitor: narx olishda xato: {e}")
        return

    gen = SignalGenerator()

    for sig, chat_id in active:
        event = gen.check_tp_sl(sig, current_price)
        if not event:
            continue

        lang = get_lang(chat_id)

        if event == "tp1":
            text = t(lang, "tp1_hit",
                     sid=sig.id,
                     direction=t(lang, "direction_buy") if sig.direction == "BUY" else t(lang, "direction_sell"),
                     tp=sig.take_profit_1,
                     rr=sig.rr1,
                     entry=sig.entry)
        elif event == "tp2":
            text = t(lang, "tp2_hit",
                     sid=sig.id,
                     direction=t(lang, "direction_buy") if sig.direction == "BUY" else t(lang, "direction_sell"),
                     tp=sig.take_profit_2,
                     rr=sig.rr2,
                     entry=sig.entry)
        else:  # sl
            text = t(lang, "sl_hit",
                     sid=sig.id,
                     direction=t(lang, "direction_buy") if sig.direction == "BUY" else t(lang, "direction_sell"),
                     sl=sig.stop_loss,
                     entry=sig.entry)

        try:
            await context.bot.send_message(
                chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Signal {sig.id}: {event} xabari yuborildi → {chat_id}")
        except TelegramError as e:
            logger.warning(f"Monitor xabar yuborishda xato: {e}")

    tracker.remove_inactive()


# ─────────────────────────────────────────────
# Scheduled scan job
# ─────────────────────────────────────────────

async def scheduled_scan(context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(CHAT_ID)
    await run_scan(context.bot, CHAT_ID, lang)


# ─────────────────────────────────────────────
# Language keyboard
# ─────────────────────────────────────────────

def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇺🇿 O'zbek",   callback_data="lang_uz"),
        InlineKeyboardButton("🇷🇺 Русский",   callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English",   callback_data="lang_en"),
    ]])


# ─────────────────────────────────────────────
# /start handler
# ─────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang    = get_lang(user_id)

    # 1. Obuna tekshiruvi
    if not await is_subscribed(context.bot, user_id):
        await update.message.reply_text(
            t(lang, "must_subscribe"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=sub_keyboard(lang)
        )
        return

    # 2. Bot haqida ma'lumot + til tanlash (faqat birinchi kirish yoki /start qayta bosish)
    await update.message.reply_text(
        t(lang, "bot_info"),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=lang_keyboard()
    )


# ─────────────────────────────────────────────
# Callback handlers
# ─────────────────────────────────────────────

async def cb_check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks subscription after user claims they subscribed."""
    query   = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang    = get_lang(user_id)

    if await is_subscribed(context.bot, user_id):
        await query.edit_message_text(
            t(lang, "sub_confirmed"),
            parse_mode=ParseMode.MARKDOWN
        )
        # Show bot info + language picker
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t(lang, "bot_info"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=lang_keyboard()
        )
    else:
        await query.answer(t(lang, "still_not_subbed"), show_alert=True)


async def cb_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chosen  = query.data.replace("lang_", "")

    if chosen not in TEXTS:
        return

    set_lang(user_id, chosen)
    await query.edit_message_text(
        t(chosen, "lang_set"),
        parse_mode=ParseMode.MARKDOWN
    )
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=t(chosen, "start"),
        parse_mode=ParseMode.MARKDOWN
    )


# ─────────────────────────────────────────────
# Command handlers (all require subscription)
# ─────────────────────────────────────────────

async def require_sub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Returns True if user is subscribed, else sends warning and returns False."""
    user_id = update.effective_user.id
    lang    = get_lang(user_id)
    if not await is_subscribed(context.bot, user_id):
        await update.message.reply_text(
            t(lang, "must_subscribe"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=sub_keyboard(lang)
        )
        return False
    return True


async def cmd_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_sub(update, context):
        return
    user_id  = update.effective_user.id
    lang     = get_lang(user_id)
    chat_id  = str(update.effective_chat.id)
    await update.message.reply_text(t(lang, "scanning"), parse_mode=ParseMode.MARKDOWN)
    count = await run_scan(context.bot, chat_id, lang)
    if count == 0:
        await update.message.reply_text(t(lang, "no_signal"), parse_mode=ParseMode.MARKDOWN)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_sub(update, context):
        return
    user_id  = update.effective_user.id
    lang     = get_lang(user_id)

    last     = state.last_scan.strftime("%H:%M UTC") if state.last_scan else t(lang, "never")
    remaining = MAX_SIGNALS_PER_DAY - state.signals_today
    now_utc  = datetime.now(timezone.utc)
    in_trade = t(lang, "yes") if SCAN_START_HOUR <= now_utc.hour < SCAN_END_HOUR else t(lang, "no")
    active_count = len(tracker.all_active())

    md = MarketData(TWELVE_API_KEY)
    kz, kz_name = md.is_kill_zone()
    kz_str = f"✅ {kz_name}" if kz else t(lang, "not_in_kz")

    text = (
        f"{t(lang, 'status_title')}\n\n"
        f"{t(lang, 'last_scan')} `{last}`\n"
        f"{t(lang, 'signals_today')} `{state.signals_today}/{MAX_SIGNALS_PER_DAY}`\n"
        f"{t(lang, 'remaining')} `{remaining}`\n"
        f"{t(lang, 'active_signals')} `{active_count}`\n"
        f"{t(lang, 'total_scans')} `{state.scan_count}`\n"
        f"{t(lang, 'trading_hours')} {in_trade}\n"
        f"{t(lang, 'kill_zone_status')} {kz_str}\n"
        f"{t(lang, 'current_utc')} `{now_utc.strftime('%H:%M')}`"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_sub(update, context):
        return
    lang = get_lang(update.effective_user.id)
    await update.message.reply_text(t(lang, "help"), parse_mode=ParseMode.MARKDOWN)


async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_sub(update, context):
        return
    lang = get_lang(update.effective_user.id)
    await update.message.reply_text(
        t(lang, "choose_lang"),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=lang_keyboard()
    )


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN .env da yo'q!")
    if not TWELVE_API_KEY:
        raise ValueError("TWELVE_API_KEY .env da yo'q!")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("signal",   cmd_signal))
    app.add_handler(CommandHandler("status",   cmd_status))
    app.add_handler(CommandHandler("help",     cmd_help))
    app.add_handler(CommandHandler("language", cmd_language))

    # Callbacks
    app.add_handler(CallbackQueryHandler(cb_check_sub, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(cb_language,  pattern="^lang_"))

    # Auto scan: har 15 daqiqa
    app.job_queue.run_repeating(scheduled_scan,  interval=SCAN_INTERVAL, first=15)

    # TP/SL monitor: har 5 daqiqa
    app.job_queue.run_repeating(monitor_signals, interval=5 * 60, first=60)

    logger.info("🚀 XAU/USD SMC Signal Bot ishga tushdi!")
    logger.info(f"📊 Kunlik signallar: {MIN_SIGNALS_PER_DAY}–{MAX_SIGNALS_PER_DAY}")
    logger.info(f"🔒 Kanal tekshiruvi: {REQUIRED_CHANNEL_ID}")
    logger.info(f"🕐 Skan oralig'i: har {SCAN_INTERVAL // 60} daqiqa")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
