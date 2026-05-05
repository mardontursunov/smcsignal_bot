"""
translations.py — EN / RU / UZ
"""

TEXTS = {
    "en": {
        "lang_name": "🇬🇧 English",
        "lang_set": "✅ Language set to *English*.",

        "bot_info": (
            "📡 *XAU/USD SMC Signal Bot*\n\n"
            "🤖 This bot provides *10+ daily signals* for Gold (XAU/USD) "
            "using Smart Money Concepts & ICT methodology.\n\n"
            "📊 *What the bot does:*\n"
            "• Scans M15 charts every 15 minutes\n"
            "• Detects Order Blocks, FVGs, Liquidity Sweeps\n"
            "• Sends BUY/SELL signals with Entry, SL, TP1, TP2\n"
            "• Notifies when TP or SL is hit ✅\n"
            "• Risk-Reward: 1:1.5 / 1:2 / 1:3\n"
            "• Stop Loss: 50–100 pips range\n\n"
            "🕐 *Active hours:* 06:00 – 20:00 UTC\n"
            "💰 *Pair:* XAU/USD (Gold)\n"
            "📈 *Timeframe:* M15\n\n"
            "⚠️ _Educational use only. Not financial advice._\n\n"
            "🌐 *Choose your language:*"
        ),

        "must_subscribe": (
            "⛔ *Access Denied*\n\n"
            "To use this bot you must subscribe to our main channel first.\n\n"
            "👇 Subscribe here, then press the button below:"
        ),
        "check_sub_btn": "✅ I subscribed — Check again",
        "sub_confirmed": "✅ Subscription confirmed! Welcome to XAU/USD SMC Bot 🎉",
        "still_not_subbed": "❌ You are not subscribed yet. Please join the channel first.",

        "start": (
            "🏆 *XAU/USD SMC Signal Bot*\n\n"
            "I provide 10+ daily signals for Gold (XAU/USD) "
            "based on *Smart Money Concepts (SMC)* & *ICT* methodology.\n\n"
            "*Commands:*\n"
            "/signal — Get latest signals now\n"
            "/status — Bot stats\n"
            "/language — Change language\n"
            "/help   — How to use signals\n\n"
            "⚠️ _Educational use only. Not financial advice._"
        ),

        "scanning": "🔍 Scanning XAU/USD M15 for SMC setups...",
        "no_signal": (
            "📭 No qualifying setups found right now.\n"
            "Price may not be at any OB or FVG with sufficient confluence.\n"
            "Try again at the next London or NY kill zone."
        ),

        "signal_header": "📡 *XAU/USD SMC Signal Report*",
        "signal_count": "📈 Found *{count}* signal(s) this scan",
        "total_today": "📊 Total today: *{total}*",
        "signal_title": "SIGNAL #{index} — XAU/USD {direction}",
        "setup": "📌 *Setup:*",
        "timeframe": "🕐 *Timeframe:*",
        "kill_zone_lbl": "⏰ *Kill Zone:*",
        "entry": "💰 *Entry:*",
        "stop_loss": "🛑 *Stop Loss:*",
        "tp1": "🎯 *TP1 (1:{rr1}):*",
        "tp2": "🎯 *TP2 (1:{rr2}):*",
        "risk": "📏 *Risk:*",
        "pips": "pips",
        "confluences": "📊 *SMC Confluences:*",
        "confidence": "🔋 *Confidence:*",
        "generated": "🕰 *Generated:*",
        "disclaimer": "⚠️ _Educational purposes only. Always use proper risk management._",
        "signal_id": "🆔 *Signal ID:*",

        "tp1_hit": (
            "✅ *TP1 Hit! — Signal #{sid}*\n\n"
            "🎯 XAU/USD {direction} — *TP1 @ {tp:.2f}*\n"
            "📈 Risk-Reward: *1:{rr}* ✅\n"
            "💰 Entry: `{entry:.2f}`\n\n"
            "💡 _TP1 olindi! SL ni B/E ga o'tkazing._"
        ),
        "tp2_hit": (
            "🏆 *TP2 Hit! — Signal #{sid}*\n\n"
            "🎯 XAU/USD {direction} — *TP2 @ {tp:.2f}*\n"
            "📈 Risk-Reward: *1:{rr}* ✅\n"
            "💰 Entry: `{entry:.2f}`\n\n"
            "🎉 _TP2 olindi! To'liq maqsad, tabriklaymiz!_"
        ),
        "sl_hit": (
            "❌ *Stop Loss — Signal #{sid}*\n\n"
            "🛑 XAU/USD {direction} — *SL @ {sl:.2f}*\n"
            "💰 Entry: `{entry:.2f}`\n\n"
            "📌 _Stop loss olindi. Keyingi setapni kuting._"
        ),

        "status_title": "📊 *Bot Status*",
        "last_scan": "🕐 Last scan:",
        "signals_today": "📈 Signals today:",
        "remaining": "🎯 Remaining:",
        "total_scans": "🔁 Total scans today:",
        "trading_hours": "📡 Trading hours:",
        "kill_zone_status": "⏰ Kill Zone:",
        "current_utc": "🌐 Current UTC:",
        "yes": "✅ Yes",
        "no": "❌ No",
        "not_in_kz": "❌ Not in kill zone",
        "never": "Never",
        "active_signals": "📋 Active signals:",

        "help": (
            "📖 *How to Use XAU/USD SMC Signals*\n\n"
            "*Signal Components:*\n"
            "• *Entry* — Limit order at OB/FVG level\n"
            "• *Stop Loss* — 50–100 pips beyond OB/FVG\n"
            "• *TP1* — 1:1.5 or 1:2 Risk-Reward\n"
            "• *TP2* — 1:2 or 1:3 Risk-Reward (runner)\n\n"
            "*You will be notified when:*\n"
            "✅ TP1 is hit — take partial profit\n"
            "🏆 TP2 is hit — full target reached\n"
            "❌ SL is hit — trade invalidated\n\n"
            "*SMC Concepts:*\n"
            "🟦 *OB* — Order Block: last opposing candle before strong move\n"
            "⚡ *FVG* — Fair Value Gap: 3-candle price imbalance\n"
            "💧 *Liquidity* — Stop hunts above/below equal highs/lows\n"
            "🔄 *BOS/ChoCh* — Structure shifts\n\n"
            "*Risk Management:*\n"
            "• Risk only 1–2% per trade\n"
            "• Move SL to BE after TP1 hit\n"
            "• Best entries at Kill Zones\n\n"
            "⚠️ _Educational purposes only._"
        ),

        "choose_lang": "🌐 *Choose your language:*",
        "direction_buy": "BUY ↗️",
        "direction_sell": "SELL ↘️",
        "utc": "UTC",
    },

    "ru": {
        "lang_name": "🇷🇺 Русский",
        "lang_set": "✅ Язык установлен: *Русский*.",

        "bot_info": (
            "📡 *Бот SMC Сигналов XAU/USD*\n\n"
            "🤖 Этот бот предоставляет *10+ сигналов в день* для Gold (XAU/USD) "
            "на основе Smart Money Concepts и методологии ICT.\n\n"
            "📊 *Что умеет бот:*\n"
            "• Сканирует M15 каждые 15 минут\n"
            "• Определяет ордер-блоки, FVG, сметание ликвидности\n"
            "• Отправляет BUY/SELL с входом, SL и TP\n"
            "• Уведомляет при достижении TP или SL ✅\n"
            "• Соотношение риск/прибыль: 1:1.5 / 1:2 / 1:3\n"
            "• Стоп-лосс: 50–100 пипсов\n\n"
            "🕐 *Активные часы:* 06:00 – 20:00 UTC\n"
            "💰 *Пара:* XAU/USD (Золото)\n"
            "📈 *Таймфрейм:* M15\n\n"
            "⚠️ _Только в образовательных целях. Не является финансовым советом._\n\n"
            "🌐 *Выберите язык:*"
        ),

        "must_subscribe": (
            "⛔ *Доступ запрещён*\n\n"
            "Для использования бота необходимо подписаться на наш основной канал.\n\n"
            "👇 Подпишитесь и нажмите кнопку ниже:"
        ),
        "check_sub_btn": "✅ Я подписался — Проверить",
        "sub_confirmed": "✅ Подписка подтверждена! Добро пожаловать в XAU/USD SMC Bot 🎉",
        "still_not_subbed": "❌ Вы ещё не подписаны. Пожалуйста, сначала вступите в канал.",

        "start": (
            "🏆 *Бот SMC Сигналов XAU/USD*\n\n"
            "Я предоставляю 10+ торговых сигналов в день для Gold (XAU/USD).\n\n"
            "*Команды:*\n"
            "/signal — Получить сигналы сейчас\n"
            "/status — Статус бота\n"
            "/language — Сменить язык\n"
            "/help   — Как использовать сигналы\n\n"
            "⚠️ _Только в образовательных целях._"
        ),

        "scanning": "🔍 Сканирую XAU/USD M15 в поисках SMC-сетапов...",
        "no_signal": (
            "📭 Подходящих сетапов пока нет.\n"
            "Попробуйте снова в следующую Kill Zone."
        ),

        "signal_header": "📡 *Отчёт по сигналам XAU/USD SMC*",
        "signal_count": "📈 Найдено *{count}* сигнал(ов)",
        "total_today": "📊 Всего сегодня: *{total}*",
        "signal_title": "СИГНАЛ #{index} — XAU/USD {direction}",
        "setup": "📌 *Сетап:*",
        "timeframe": "🕐 *Таймфрейм:*",
        "kill_zone_lbl": "⏰ *Kill Zone:*",
        "entry": "💰 *Вход:*",
        "stop_loss": "🛑 *Стоп-лосс:*",
        "tp1": "🎯 *TP1 (1:{rr1}):*",
        "tp2": "🎯 *TP2 (1:{rr2}):*",
        "risk": "📏 *Риск:*",
        "pips": "пипсов",
        "confluences": "📊 *SMC Подтверждения:*",
        "confidence": "🔋 *Уверенность:*",
        "generated": "🕰 *Создан:*",
        "disclaimer": "⚠️ _Только в образовательных целях. Соблюдайте риск-менеджмент._",
        "signal_id": "🆔 *ID сигнала:*",

        "tp1_hit": (
            "✅ *TP1 взят! — Сигнал #{sid}*\n\n"
            "🎯 XAU/USD {direction} — *TP1 @ {tp:.2f}*\n"
            "📈 Risk-Reward: *1:{rr}* ✅\n"
            "💰 Вход: `{entry:.2f}`\n\n"
            "💡 _TP1 взят! Перенесите SL в B/E._"
        ),
        "tp2_hit": (
            "🏆 *TP2 взят! — Сигнал #{sid}*\n\n"
            "🎯 XAU/USD {direction} — *TP2 @ {tp:.2f}*\n"
            "📈 Risk-Reward: *1:{rr}* ✅\n"
            "💰 Вход: `{entry:.2f}`\n\n"
            "🎉 _TP2 взят! Полная цель, поздравляем!_"
        ),
        "sl_hit": (
            "❌ *Стоп-лосс — Сигнал #{sid}*\n\n"
            "🛑 XAU/USD {direction} — *SL @ {sl:.2f}*\n"
            "💰 Вход: `{entry:.2f}`\n\n"
            "📌 _Стоп-лосс взят. Ждите следующий сетап._"
        ),

        "status_title": "📊 *Статус бота*",
        "last_scan": "🕐 Последний скан:",
        "signals_today": "📈 Сигналов сегодня:",
        "remaining": "🎯 Осталось:",
        "total_scans": "🔁 Сканов сегодня:",
        "trading_hours": "📡 Торговые часы:",
        "kill_zone_status": "⏰ Kill Zone:",
        "current_utc": "🌐 Текущее UTC:",
        "yes": "✅ Да",
        "no": "❌ Нет",
        "not_in_kz": "❌ Не в Kill Zone",
        "never": "Никогда",
        "active_signals": "📋 Активных сигналов:",

        "help": (
            "📖 *Как использовать SMC сигналы XAU/USD*\n\n"
            "*Компоненты сигнала:*\n"
            "• *Вход* — Лимитный ордер на уровне OB/FVG\n"
            "• *Стоп-лосс* — 50–100 пипсов за OB/FVG\n"
            "• *TP1* — Соотношение 1:1.5 или 1:2\n"
            "• *TP2* — Соотношение 1:2 или 1:3\n\n"
            "*Вы получите уведомление когда:*\n"
            "✅ Достигнут TP1 — зафиксируйте часть прибыли\n"
            "🏆 Достигнут TP2 — полная цель\n"
            "❌ Сработал SL — сделка закрыта\n\n"
            "⚠️ _Только в образовательных целях._"
        ),

        "choose_lang": "🌐 *Выберите язык:*",
        "direction_buy": "BUY ↗️",
        "direction_sell": "SELL ↘️",
        "utc": "UTC",
    },

    "uz": {
        "lang_name": "🇺🇿 O'zbek",
        "lang_set": "✅ Til o'rnatildi: *O'zbek*.",

        "bot_info": (
            "📡 *XAU/USD SMC Signal Bot*\n\n"
            "🤖 Bu bot Smart Money Concepts va ICT metodologiyasiga asoslanib "
            "XAU/USD (Oltin) uchun *kuniga 10+ signal* beradi.\n\n"
            "📊 *Bot nima qiladi:*\n"
            "• Har 15 daqiqada M15 chartni skanerlaydi\n"
            "• Order Block, FVG, Likvidlik o'g'irlashni aniqlaydi\n"
            "• Kirish, SL va TP bilan BUY/SELL signal yuboradi\n"
            "• TP yoki SL tekkanda xabar beradi ✅\n"
            "• Risk-Reward: 1:1.5 / 1:2 / 1:3\n"
            "• Stop Loss: 50–100 pips oralig'ida\n\n"
            "🕐 *Faol soatlar:* 06:00 – 20:00 UTC\n"
            "💰 *Juftlik:* XAU/USD (Oltin)\n"
            "📈 *Vaqt oralig'i:* M15\n\n"
            "⚠️ _Faqat ta'lim maqsadida. Moliyaviy maslahat emas._\n\n"
            "🌐 *Tilni tanlang:*"
        ),

        "must_subscribe": (
            "⛔ *Kirish taqiqlangan*\n\n"
            "Botdan foydalanish uchun avval asosiy kanalimizga obuna bo'lishingiz kerak.\n\n"
            "👇 Obuna bo'ling va quyidagi tugmani bosing:"
        ),
        "check_sub_btn": "✅ Obuna bo'ldim — Tekshirish",
        "sub_confirmed": "✅ Obuna tasdiqlandi! XAU/USD SMC Bot ga xush kelibsiz 🎉",
        "still_not_subbed": "❌ Siz hali obuna bo'lmagansiz. Avval kanalga qo'shiling.",

        "start": (
            "🏆 *XAU/USD SMC Signal Bot*\n\n"
            "Men kuniga 10+ ta XAU/USD signali beraman.\n\n"
            "*Buyruqlar:*\n"
            "/signal — Hozir signal olish\n"
            "/status — Bot statistikasi\n"
            "/language — Tilni o'zgartirish\n"
            "/help   — Signallardan foydalanish\n\n"
            "⚠️ _Faqat ta'lim maqsadida._"
        ),

        "scanning": "🔍 XAU/USD M15 da SMC ssetaplarini qidiryapman...",
        "no_signal": (
            "📭 Hozircha mos keladigan ssetap topilmadi.\n"
            "Keyingi Kill Zone vaqtida qayta urinib ko'ring."
        ),

        "signal_header": "📡 *XAU/USD SMC Signal Hisoboti*",
        "signal_count": "📈 Bu skanda *{count}* ta signal topildi",
        "total_today": "📊 Bugun jami: *{total}*",
        "signal_title": "SIGNAL #{index} — XAU/USD {direction}",
        "setup": "📌 *Ssetap:*",
        "timeframe": "🕐 *Vaqt oralig'i:*",
        "kill_zone_lbl": "⏰ *Kill Zone:*",
        "entry": "💰 *Kirish:*",
        "stop_loss": "🛑 *Stop Loss:*",
        "tp1": "🎯 *TP1 (1:{rr1}):*",
        "tp2": "🎯 *TP2 (1:{rr2}):*",
        "risk": "📏 *Risk:*",
        "pips": "pips",
        "confluences": "📊 *SMC Tasdiqlashlar:*",
        "confidence": "🔋 *Ishonch darajasi:*",
        "generated": "🕰 *Yaratildi:*",
        "disclaimer": "⚠️ _Faqat ta'lim maqsadida. Har doim risk-managementdan foydalaning._",
        "signal_id": "🆔 *Signal ID:*",

        "tp1_hit": (
            "✅ *TP1 olindi! — Signal #{sid}*\n\n"
            "🎯 XAU/USD {direction} — *TP1 @ {tp:.2f}*\n"
            "📈 Risk-Reward: *1:{rr}* ✅\n"
            "💰 Kirish: `{entry:.2f}`\n\n"
            "💡 _TP1 olindi! SL ni B/E ga o'tkazing._"
        ),
        "tp2_hit": (
            "🏆 *TP2 olindi! — Signal #{sid}*\n\n"
            "🎯 XAU/USD {direction} — *TP2 @ {tp:.2f}*\n"
            "📈 Risk-Reward: *1:{rr}* ✅\n"
            "💰 Kirish: `{entry:.2f}`\n\n"
            "🎉 _TP2 olindi! To'liq maqsad, tabriklaymiz!_"
        ),
        "sl_hit": (
            "❌ *Stop loss olindi — Signal #{sid}*\n\n"
            "🛑 XAU/USD {direction} — *SL @ {sl:.2f}*\n"
            "💰 Kirish: `{entry:.2f}`\n\n"
            "📌 _Stop loss olindi. Keyingi setapni kuting._"
        ),

        "status_title": "📊 *Bot Holati*",
        "last_scan": "🕐 Oxirgi skan:",
        "signals_today": "📈 Bugungi signallar:",
        "remaining": "🎯 Qoldi:",
        "total_scans": "🔁 Bugungi skanlar:",
        "trading_hours": "📡 Savdo soatlari:",
        "kill_zone_status": "⏰ Kill Zone:",
        "current_utc": "🌐 Hozirgi UTC:",
        "yes": "✅ Ha",
        "no": "❌ Yo'q",
        "not_in_kz": "❌ Kill Zone da emas",
        "never": "Hech qachon",
        "active_signals": "📋 Faol signallar:",

        "help": (
            "📖 *XAU/USD SMC Signallaridan Foydalanish*\n\n"
            "*Signal tarkibi:*\n"
            "• *Kirish* — OB/FVG darajasida limit order\n"
            "• *Stop Loss* — OB/FVG dan 50–100 pips narida\n"
            "• *TP1* — 1:1.5 yoki 1:2 Risk-Reward\n"
            "• *TP2* — 1:2 yoki 1:3 Risk-Reward\n\n"
            "*Qachon xabar olasiz:*\n"
            "✅ TP1 tekkanda — qisman foyda oling\n"
            "🏆 TP2 tekkanda — to'liq maqsad\n"
            "❌ SL tekkanda — pozitsiya yopildi\n\n"
            "⚠️ _Faqat ta'lim maqsadida._"
        ),

        "choose_lang": "🌐 *Tilni tanlang:*",
        "direction_buy": "BUY ↗️",
        "direction_sell": "SELL ↘️",
        "utc": "UTC",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    text = TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text
