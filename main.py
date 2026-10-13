"""
╔══════════════════════════════════════════════════════════╗
║           RODIX HACKER BOT  v4.1                         ║
║      NEW USER ALERTS • GLOBAL BROADCAST • FULL CTRL      ║
╚══════════════════════════════════════════════════════════╝
pip install pytelegrambotapi requests
"""

import telebot, requests, sqlite3, re, time, json, threading, os, random, string, io, html as _html
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,
    InlineKeyboardButton, KeyboardButtonRequestUser, ReactionTypeEmoji)
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from telebot import apihelper
apihelper.ENABLE_MIDDLEWARE = True

# ═══════════════ CONFIG ═══════════════
BOT_TOKEN       = "8984204596:AAHgZqPR1CoWXE0WAaHVXYVpt7pBI60ujks"
OWNER_ID        = 7373960749
LOG_CHANNEL_ID  = -1003294197090
FREE_CREDITS    = 3
REFERRAL_BONUS  = 2
LIKE_COOLDOWN_HRS = 12
LIKE_DAILY_MAX  = 10

FORCE_JOIN_CHANNELS = [
    ("-1003294197090", "RODIX HACKER", "https://t.me/+P6wvoBMsOUEyMzY1"),
]

DEFAULTS = {
    "bot_name":      "RODIX HACKER",
    "bot_username":  "Rodix_exploit",
    "dev_label":     "DEVELOPER",
    "bot_tagline":   "OSINT • FF • BOMBER • WALLET",
    "admin_alert":   "1",   # 1=ON, 0=OFF
    "global_bcast":  "",    # admin ka latest global message
    "global_bcast_time": "",
}

_BOT_APIS = [
    ("number",      "📱 Number Lookup",   "https://simran-num-info-api.vercel.app/api?number={}&format=2"),
    ("number2",     "📟 Number Backup",   "https://r-bot-number-to-info-api.vercel.app/api?number={}"),
    ("userid",      "🆔 UserID Info",     "https://user-to-num-info-zcpe.onrender.com/userid={}"),
    ("username",    "🔍 Username Info",   "https://user-to-num-info-zcpe.onrender.com/username/{}"),
    ("aadhar",      "🪪 Aadhar",          "https://adhar-to-info.vercel.app/?key=SH4DAW-D4DY&aadhar={}"),
    ("instagram",   "📸 Instagram",       "https://insta-info-eta.vercel.app/?username={}&key=SH4DAW-D4DY"),
    ("vehicle",     "🚗 Vehicle RC",      "https://vehicle-rc-to-num.vercel.app/?rc={}&key=SH4DAW-D4DY"),
    ("freefire",    "🎮 Free Fire Info",  "https://sextyinfo.vercel.app/player-info?uid={}"),
    ("ff_like1",    "❤️ FF Like 1",       "https://simran-like-r-bot-api.vercel.app/like?uid={}&server_name=ind"),
    ("ff_like2",    "❤️ FF Like 2",       "https://freefireautolikeservice.vercel.app/like?uid={}&server_name=ind"),
    ("ff_like3",    "❤️ FF Like 3",       "https://ff-like-api-azure.vercel.app/like?uid={}&server_name=ind"),
    ("ff_like4",    "❤️ FF Like 4",       "https://sexty-autolikes.vercel.app/like?uid={}&server_name=ind"),
    ("ff_like5",    "❤️ FF Like 5",       "https://verma-like-api.vercel.app/like?uid={}&region=ind&key=UDIT"),
    ("bomber1",     "💣 Bomber 1",        "https://bombar-api-2.vercel.app/all?num={}"),
    ("bomber2",     "💣 Bomber 2",        "https://rlxbomber.vercel.app/api/attack?number={}&key=rlxcoder"),
]

_BOT_API_KEYS = [
    ("key_sh4daw",     "🔑 SH4DAW Main",     "SH4DAW-D4DY"),
    ("key_rlx_bomber", "💥 RLX Bomber Key",  "rlxcoder"),
    ("key_aadhar",     "🪪 Aadhar Key",      "SH4DAW-D4DY"),
    ("key_instagram",  "📸 Instagram Key",   "SH4DAW-D4DY"),
    ("key_vehicle",    "🚗 Vehicle Key",     "SH4DAW-D4DY"),
    ("key_username",   "🔍 Username Key",    "SH4DAW-D4DY"),
]

# ═══════════════ BOT INIT ═══════════════
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_BOT_ID = BOT_TOKEN.split(":")[0]
DB_FILE = os.path.join(_SCRIPT_DIR, f"rodix_{_BOT_ID}.db")

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
_db_lock = threading.Lock()

class _Cursor:
    def __init__(self, c): self._c = c; self._cur = None
    def execute(self, sql, params=()):
        with _db_lock:
            self._cur = self._c.cursor(); self._cur.execute(sql, params); return self
    def executescript(self, sql):
        with _db_lock:
            self._cur = self._c.cursor(); self._cur.executescript(sql); return self
    def fetchone(self): return self._cur.fetchone() if self._cur else None
    def fetchall(self): return self._cur.fetchall() if self._cur else []
    @property
    def rowcount(self): return self._cur.rowcount if self._cur else 0

c = _Cursor(conn)

# ═══════════════ STYLED BUTTONS ═══════════════
class _StyledKB(KeyboardButton):
    def __init__(self, text, style=None, icon_custom_emoji_id=None, **kw):
        super().__init__(text, **kw)
        self.__style = style; self.__icon = icon_custom_emoji_id
    def to_dict(self):
        d = super().to_dict()
        if self.__style: d["style"] = self.__style
        if self.__icon: d["icon_custom_emoji_id"] = self.__icon
        return d

class _StyledIKB(InlineKeyboardButton):
    def __init__(self, text, style=None, icon_custom_emoji_id=None, **kw):
        super().__init__(text, **kw)
        self.__style = "success" if style == "active" else style
        self.__icon = icon_custom_emoji_id
    def to_dict(self):
        d = super().to_dict()
        try:
            if self.__style: d["style"] = self.__style
        except: pass
        try:
            if self.__icon: d["icon_custom_emoji_id"] = self.__icon
        except: pass
        return d

def _KB(text, style=None, icon_custom_emoji_id=None, **kw):
    if style == "active": style = "success"
    try: return _StyledKB(text, style=style, icon_custom_emoji_id=icon_custom_emoji_id, **kw)
    except:
        try: return KeyboardButton(text, **kw)
        except: return KeyboardButton(text)

def _IKB(text, style=None, icon_custom_emoji_id=None, **kw):
    try: return _StyledIKB(text, style=style, icon_custom_emoji_id=icon_custom_emoji_id, **kw)
    except:
        try: return InlineKeyboardButton(text, **kw)
        except:
            safe = {k: v for k, v in kw.items() if k in ("callback_data","url","switch_inline_query","switch_inline_query_current_chat")}
            return InlineKeyboardButton(text, **safe) if safe else InlineKeyboardButton(text, callback_data="noop")

# ═══════════════ AUTO REACTION ═══════════════
FREE_REACTIONS = ["⚡","🔥","💀","☠","🎯","💥","🗿","👾","🤖","😎","🤯","🦾","🧠","🎮",
                  "❤️‍🔥","⚔️","🛡️","💣","🌟","✨","🎲","🎰","👀","🚀","⭐","✅","⚜️","🔱",
                  "🏆","🥇","💎","👑","🍀","🌀","🌈","🎉","🥳","💯","🫡","🤝","🙌","✌️",
                  "🎁","🪄","🛸","🏴‍☠️","💫","🌊","🌪","⚡","🔥"]

def _auto_react(chat_id, msg_id, big=False):
    try:
        bot.set_message_reaction(chat_id, msg_id,
            [ReactionTypeEmoji(random.choice(FREE_REACTIONS))], is_big=big)
    except: pass

@bot.middleware_handler(update_types=['message'])
def react_every_message(bot_instance, message):
    try:
        if not message: return
        if message.chat.type == 'channel': return
        _auto_react(message.chat.id, message.message_id, big=False)
    except: pass

# ═══════════════ UI FRAMES ═══════════════
SEP     = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
SEP2    = "⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁⌁"
FRAME_T = "╔══════════════════════════════╗"
FRAME_B = "╚══════════════════════════════╝"

def pbar(pct):
    pct = max(0, min(100, int(pct)))
    f = int(round(pct / 100 * 10))
    return "▰" * f + "▱" * (10 - f) + f"  {pct}%"

def box_header(title): return f"┌────────────────────────────┐\n│  {title}\n└────────────────────────────┘"
def section(title): return f"◤ {title} ◢"

def prompt_box(icon, title, instruction, example, credits, cost=1, tip=None):
    tip_line = f"\n▸ ᴛɪᴘ: {tip}" if tip else ""
    return (
        f"<blockquote>{box_header(f'{icon} {title}')}\n\n"
        f"▸ ꜱᴇɴᴅ: <b>{instruction}</b>\n"
        f"▸ ᴇxᴀᴍᴘʟᴇ: <code>{example}</code>{tip_line}\n\n"
        f"{SEP}\n▸ ᴄʀᴇᴅɪᴛꜱ: <b>{credits}</b>\n▸ ᴄᴏꜱᴛ: <b>{cost}</b>\n{SEP}\n\n"
        f"{FOOTER()}</blockquote>"
    )

def card_wrap(title, body, credits=None):
    credit_line = f"\n▸ ᴄʀᴇᴅɪᴛꜱ ʟᴇꜰᴛ: <b>{credits}</b>" if credits is not None else ""
    return (f"<blockquote>{FRAME_T}\n║  ⚡ {title}\n{FRAME_B}\n\n"
            f"{body}\n{SEP2}{credit_line}\n{FOOTER()}\n{SEP2}</blockquote>")

def denied(title, reason):
    return (f"<blockquote>{FRAME_T}\n║  ☠ {title}\n{FRAME_B}\n\n"
            f"▸ ʀᴇᴀꜱᴏɴ: {reason}\n\n▸ ɢᴇᴛ ᴄʀᴇᴅɪᴛꜱ:\n"
            f"   • ʀᴇꜰᴇʀ ꜰʀɪᴇɴᴅꜱ\n   • ᴅᴀɪʟʏ ꜱᴘɪɴ\n   • ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ\n\n"
            f"{FOOTER()}</blockquote>")

def extract_anim(chat_id, msg_id, label):
    stop = [False]
    def _run():
        phases = [([5, 12, 20], "ʙʏᴘᴀꜱꜱɪɴɢ ꜰɪʀᴇᴡᴀʟʟ"),
                  ([35, 50, 65], "ʟᴏᴄᴀᴛɪɴɢ ᴛᴀʀɢᴇᴛ"),
                  ([75, 82, 88, 92, 95], label)]
        for pcts, txt in phases:
            for p in pcts:
                if stop[0]: return
                try: bot.edit_message_text(f"<blockquote>{pbar(p)}\n▸ {txt}...</blockquote>",
                                            chat_id, msg_id, parse_mode="HTML")
                except: pass
                time.sleep(0.35)
        i = 0
        while not stop[0] and i < 40:
            try: bot.edit_message_text(f"<blockquote>{pbar(min(96+i, 99))}\n▸ {label}...</blockquote>",
                                        chat_id, msg_id, parse_mode="HTML")
            except: pass
            i += 1; time.sleep(0.7)
    threading.Thread(target=_run, daemon=True).start()
    return stop

# ═══════════════ DB SCHEMA ═══════════════
conn.executescript("""
CREATE TABLE IF NOT EXISTS users(
  user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
  join_date TEXT, referrer INTEGER, credits INTEGER DEFAULT 3,
  is_blocked INTEGER DEFAULT 0, is_premium INTEGER DEFAULT 0,
  premium_until TEXT, joined_channel INTEGER DEFAULT 0, first_time INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS referrals(
  id INTEGER PRIMARY KEY AUTOINCREMENT, referrer INTEGER, referred INTEGER, date TEXT);
CREATE TABLE IF NOT EXISTS search_history(
  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, search_type TEXT,
  query TEXT, search_date TEXT, result TEXT);
CREATE TABLE IF NOT EXISTS daily_claims(
  user_id INTEGER, claim_date TEXT, PRIMARY KEY(user_id,claim_date));
CREATE TABLE IF NOT EXISTS redeem_codes(
  id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, credits INTEGER,
  redeem_limit INTEGER DEFAULT 0, used_count INTEGER DEFAULT 0,
  created_by INTEGER, created_date TEXT);
CREATE TABLE IF NOT EXISTS redeemed_users(
  code TEXT, user_id INTEGER, redeem_date TEXT, PRIMARY KEY(code,user_id));
CREATE TABLE IF NOT EXISTS premium_codes(
  id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, days INTEGER,
  redeem_limit INTEGER DEFAULT 1, used_count INTEGER DEFAULT 0,
  created_by INTEGER, created_date TEXT);
CREATE TABLE IF NOT EXISTS redeemed_premium(
  code TEXT, user_id INTEGER, redeem_date TEXT, PRIMARY KEY(code,user_id));
CREATE TABLE IF NOT EXISTS force_join_channels(
  id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, chat_title TEXT,
  chat_url TEXT, added_by INTEGER, added_date TEXT, is_active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS groups(
  group_id INTEGER PRIMARY KEY, group_title TEXT, added_date TEXT,
  added_by INTEGER, unlimited INTEGER DEFAULT 0, is_blocked INTEGER DEFAULT 0,
  searches INTEGER DEFAULT 0, is_muted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS welcome_settings(
  id INTEGER PRIMARY KEY CHECK(id=1), welcome_image TEXT, welcome_video TEXT,
  welcome_caption TEXT DEFAULT 'Welcome!', first_time_sticker TEXT);
CREATE TABLE IF NOT EXISTS group_welcome_settings(
  group_id INTEGER PRIMARY KEY, welcome_on INTEGER DEFAULT 1, bye_on INTEGER DEFAULT 1,
  group_rules TEXT DEFAULT '', welcome_text TEXT, welcome_image TEXT,
  welcome_video TEXT, video_list TEXT, group_sticker TEXT, updated_date TEXT);
CREATE TABLE IF NOT EXISTS blocked_identifiers(
  id INTEGER PRIMARY KEY AUTOINCREMENT, identifier TEXT UNIQUE,
  identifier_type TEXT, blocked_by INTEGER, blocked_date TEXT, reason TEXT);
CREATE TABLE IF NOT EXISTS feature_toggles(
  id INTEGER PRIMARY KEY AUTOINCREMENT, feature_name TEXT UNIQUE,
  is_enabled INTEGER DEFAULT 1, updated_by INTEGER, updated_date TEXT);
CREATE TABLE IF NOT EXISTS admins(
  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE,
  added_by INTEGER, added_date TEXT, is_active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS protected_users(
  id INTEGER PRIMARY KEY AUTOINCREMENT, identifier TEXT UNIQUE,
  identifier_type TEXT, protected_by INTEGER, protected_date TEXT);
CREATE TABLE IF NOT EXISTS ff_like_cooldown(
  key TEXT PRIMARY KEY, user_id INTEGER, uid TEXT, region TEXT,
  last_like REAL, timestamp TEXT);
CREATE TABLE IF NOT EXISTS ff_like_ratelimit(
  key TEXT PRIMARY KEY, user_id INTEGER, timestamps TEXT);
CREATE TABLE IF NOT EXISTS token_log(
  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, user_name TEXT,
  username TEXT, added INTEGER, total INTEGER, source TEXT,
  log_date TEXT, log_time TEXT);
CREATE TABLE IF NOT EXISTS api_keys(
  id INTEGER PRIMARY KEY AUTOINCREMENT, api_name TEXT UNIQUE,
  api_url TEXT, api_key TEXT, is_active INTEGER DEFAULT 1,
  added_by INTEGER, added_date TEXT);
CREATE TABLE IF NOT EXISTS bot_settings(
  key TEXT PRIMARY KEY, value TEXT);
""")
conn.commit()
c.execute("INSERT OR IGNORE INTO welcome_settings(id) VALUES(1)")
c.execute("INSERT OR IGNORE INTO admins(user_id,added_by,added_date) VALUES(?,?,?)",
          (OWNER_ID, OWNER_ID, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
for feat in ["number","username","tgid","aadhar","instagram","freefire","freefire_like","vehicle","bomber"]:
    c.execute("INSERT OR IGNORE INTO feature_toggles(feature_name,is_enabled) VALUES(?,1)", (feat,))
for k, v in DEFAULTS.items():
    c.execute("INSERT OR IGNORE INTO bot_settings(key,value) VALUES(?,?)", (k, v))
conn.commit()

# ═══════════════ BOT SETTINGS ═══════════════
_settings_cache = {}
def get_setting(key, default=""):
    if key in _settings_cache: return _settings_cache[key]
    try:
        c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
        r = c.fetchone()
        if r and r[0] is not None:
            _settings_cache[key] = r[0]; return r[0]
    except: pass
    val = DEFAULTS.get(key, default)
    _settings_cache[key] = val
    return val

def set_setting(key, value):
    try:
        c.execute("INSERT OR REPLACE INTO bot_settings(key,value) VALUES(?,?)", (key, str(value)))
        conn.commit()
        _settings_cache[key] = str(value)
        return True
    except Exception as e:
        print(f"[SET_SETTING] {e}"); return False

def FOOTER():
    dev_label = get_setting("dev_label", "DEVELOPER")
    bot_un = get_setting("bot_username", "Rodix_exploit")
    return f"⚡ {dev_label} • @{bot_un}"

def BOT_NAME(): return get_setting("bot_name", "RODIX HACKER")
def BOT_USERNAME(): return get_setting("bot_username", "Rodix_exploit")

def _pe(eid, fb="⭐"): return f"<tg-emoji emoji-id='{eid}'>{fb}</tg-emoji>"

# ═══════════════ STATE ═══════════════
S_NONE="none"; S_NUM="number"; S_USER="username"; S_TID="tgid"
S_ADH="adh"; S_INSTA="insta"; S_FF="ff"; S_FFLIKE="fflike"; S_VEH="veh"; S_BOMB="bomb"
S_REDEEM="redeem"; S_PREM="prem"
user_state = {}
bomber_jobs = {}
_join_dedup = {}
_admin_states = {}
_caches = {"users":{}, "groups":{}, "features":{}, "admins":{}}

# ═══════════════ USER / CREDIT HELPERS ═══════════════
def get_user(uid):
    if uid in _caches["users"]: return _caches["users"][uid]
    c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    row = c.fetchone(); _caches["users"][uid] = row
    return row

def add_user(uid, uname, fname, ref=None):
    _caches["users"].pop(uid, None)
    d = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT OR IGNORE INTO users(user_id,username,first_name,join_date,referrer,credits,first_time) VALUES(?,?,?,?,?,?,1)",
              (uid, uname, fname, d, ref, FREE_CREDITS))
    if ref and ref != uid:
        try:
            c.execute("INSERT INTO referrals(referrer,referred,date) VALUES(?,?,?)", (ref, uid, d))
            c.execute("UPDATE users SET credits=COALESCE(credits,0)+? WHERE user_id=?", (REFERRAL_BONUS, ref))
        except: pass
    conn.commit()

def get_credits(uid):
    if is_admin(uid): return "∞"
    u = get_user(uid)
    return u[5] if u else 0

def deduct_credit(uid, cost=1):
    if is_admin(uid): return True
    _caches["users"].pop(uid, None)
    c.execute("SELECT credits,is_premium,premium_until FROM users WHERE user_id=?", (uid,))
    u = c.fetchone()
    if not u: return False
    if u[1] == 1 and u[2]:
        try:
            if datetime.strptime(u[2], "%Y-%m-%d %H:%M:%S") > datetime.now(): return True
        except: pass
    if u[0] >= cost:
        c.execute("UPDATE users SET credits=credits-? WHERE user_id=?", (cost, uid))
        conn.commit(); _caches["users"].pop(uid, None); return True
    return False

def refund_credit(uid, cost=1):
    if is_admin(uid): return
    c.execute("UPDATE users SET credits=credits+? WHERE user_id=?", (cost, uid))
    conn.commit(); _caches["users"].pop(uid, None)

def is_admin(uid):
    if uid == OWNER_ID: return True
    if uid in _caches["admins"]: return _caches["admins"][uid]
    c.execute("SELECT COUNT(*) FROM admins WHERE user_id=? AND is_active=1", (uid,))
    r = c.fetchone()[0] > 0
    _caches["admins"][uid] = r
    return r

def get_referral_count(uid):
    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer=?", (uid,))
    return c.fetchone()[0] or 0

def can_claim_daily(uid):
    if is_admin(uid): return True
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM daily_claims WHERE user_id=? AND claim_date=?", (uid, today))
    return c.fetchone()[0] == 0

def is_feature_enabled(fn):
    if fn in _caches["features"]: return _caches["features"][fn]
    c.execute("SELECT is_enabled FROM feature_toggles WHERE feature_name=?", (fn,))
    r = c.fetchone()
    val = r[0] == 1 if r else True
    _caches["features"][fn] = val
    return val

def toggle_feature(fn, by):
    c.execute("SELECT is_enabled FROM feature_toggles WHERE feature_name=?", (fn,))
    r = c.fetchone()
    nv = 0 if (r and r[0] == 1) else 1
    if r:
        c.execute("UPDATE feature_toggles SET is_enabled=?,updated_by=?,updated_date=? WHERE feature_name=?",
                  (nv, by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fn))
    else:
        c.execute("INSERT INTO feature_toggles(feature_name,is_enabled,updated_by,updated_date) VALUES(?,?,?,?)",
                  (fn, nv, by, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); _caches["features"][fn] = (nv == 1); return nv == 1

def get_all_feature_states():
    c.execute("SELECT feature_name,is_enabled FROM feature_toggles ORDER BY feature_name")
    return c.fetchall()

# ═══════════════ NEW USER ALERT ═══════════════
def notify_admin_new_user(uid, uname, fname, is_new=True, ref_by=None):
    """New user start pe admin ko DM notification"""
    try:
        if get_setting("admin_alert", "1") != "1": return
        # Skip if user IS admin
        if uid == OWNER_ID or is_admin(uid): return

        now = datetime.now().strftime("%d %b %Y • %I:%M %p")
        try: total_users = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        except: total_users = "?"
        # Count as new today
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            c.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date)=?", (today,))
            today_count = c.fetchone()[0]
        except: today_count = "?"

        udisp = f"@{uname}" if uname else "ɴᴏ ᴜꜱᴇʀɴᴀᴍᴇ"
        ref_line = f"\n├ ʀᴇꜰ ʙʏ ▸ <code>{ref_by}</code>" if ref_by else ""

        header = "🆕 ɴᴇᴡ ᴜꜱᴇʀ ꜱᴛᴀʀᴛᴇᴅ!" if is_new else "👤 ᴜꜱᴇʀ ᴀᴄᴛɪᴠᴇ"

        txt = (
            f"<blockquote>{FRAME_T}\n║  🔔 {header}\n{FRAME_B}\n\n"
            f"{section('ᴜꜱᴇʀ ɪɴꜰᴏ')}\n"
            f"├ ɴᴀᴍᴇ ▸ <a href='tg://user?id={uid}'><b>{_html.escape(fname)}</b></a>\n"
            f"├ ᴜɴ ▸ {udisp}\n"
            f"├ ɪᴅ ▸ <code>{uid}</code>{ref_line}\n"
            f"└ ᴛɪᴍᴇ ▸ {now}\n\n"
            f"{section('ꜱᴛᴀᴛꜱ')}\n"
            f"├ ᴛᴏᴛᴀʟ ▸ <b>{total_users}</b>\n"
            f"└ ᴛᴏᴅᴀʏ ▸ <b>{today_count}</b>\n\n"
            f"{FOOTER()}</blockquote>"
        )

        mk = InlineKeyboardMarkup(row_width=2)
        mk.row(
            _IKB("💬 ᴍꜱɢ ᴋᴀʀᴏ", style="primary",
                 icon_custom_emoji_id="5258021357446268553",
                 url=f"tg://user?id={uid}"),
            _IKB("🚫 ʙʟᴏᴄᴋ", style="danger",
                 icon_custom_emoji_id="5471937446368975982",
                 callback_data=f"nalert_block_{uid}")
        )
        mk.row(
            _IKB("💰 +10 ᴄʀ", style="success",
                 icon_custom_emoji_id="5379600444098093058",
                 callback_data=f"nalert_credits_{uid}_10"),
            _IKB("💎 ᴘʀᴇᴍɪᴜᴍ 7ᴅ", style="success",
                 icon_custom_emoji_id="4956719506027185156",
                 callback_data=f"nalert_prem_{uid}_7")
        )
        mk.row(
            _IKB("🗑️ ᴅᴇʟᴇᴛᴇ ᴜꜱᴇʀ", style="danger",
                 icon_custom_emoji_id="5471937446368975982",
                 callback_data=f"nalert_del_{uid}")
        )

        # Send to OWNER
        try:
            bot.send_message(OWNER_ID, txt, parse_mode="HTML", reply_markup=mk)
        except Exception as e:
            print(f"[NALERT_OWNER] {e}")

        # Send to all admins (except owner)
        try:
            c.execute("SELECT user_id FROM admins WHERE is_active=1 AND user_id != ?", (OWNER_ID,))
            for (aid,) in c.fetchall():
                try: bot.send_message(aid, txt, parse_mode="HTML", reply_markup=mk)
                except: pass
        except: pass
    except Exception as e:
        print(f"[NALERT] {e}")

# ═══════════════ GLOBAL BROADCAST ═══════════════
def do_global_broadcast(sender_msg, admin_uid):
    """Admin ka message sab users ko bhejta hai + global_bcast mein save karta hai"""
    _admin_states.pop(admin_uid, None)
    c.execute("SELECT user_id FROM users WHERE is_blocked=0")
    users = [r[0] for r in c.fetchall()]
    total = len(users)
    sent = fail = 0
    sm = bot.reply_to(sender_msg,
        f"<blockquote>{SEP}\n📡 <b>ɢʟᴏʙᴀʟ ʙʀᴏᴀᴅᴄᴀꜱᴛ</b>\n{SEP}\n\n"
        f"▸ ꜱᴇɴᴅɪɴɢ ᴛᴏ <b>{total}</b> ᴜꜱᴇʀꜱ...\n\n{FOOTER()}</blockquote>",
        parse_mode="HTML")
    for target in users:
        try:
            bot.copy_message(target, sender_msg.chat.id, sender_msg.message_id)
            sent += 1
        except: fail += 1
        time.sleep(0.04)
    # Save as global announcement (text only for replay)
    if sender_msg.content_type == "text" and sender_msg.text:
        set_setting("global_bcast", sender_msg.text)
        set_setting("global_bcast_time", datetime.now().strftime("%d %b %Y • %I:%M %p"))
    # Summary
    try:
        bot.edit_message_text(
            f"<blockquote>{SEP}\n✅ <b>ɢʟᴏʙᴀʟ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴅᴏɴᴇ</b>\n{SEP}\n\n"
            f"├ ᴛᴏᴛᴀʟ ▸ {total}\n"
            f"├ ꜱᴇɴᴛ ▸ <b>{sent}</b>\n"
            f"└ ꜰᴀɪʟ ▸ <b>{fail}</b>\n\n"
            f"💡 ɴᴀʏᴇ ᴜꜱᴇʀꜱ ᴋᴏ /start ᴩᴇ ᴅɪᴋʜᴇɢᴀ!\n\n{FOOTER()}</blockquote>",
            sm.chat.id, sm.message_id, parse_mode="HTML")
    except: pass

def send_global_to_new_user(uid):
    """New user ko global broadcast dikhao agar set hai"""
    try:
        global_msg = get_setting("global_bcast", "")
        if not global_msg: return
        global_time = get_setting("global_bcast_time", "")
        txt = (f"<blockquote>{SEP}\n📢 <b>ᴀɴɴᴏᴜɴᴄᴇᴍᴇɴᴛ ꜰʀᴏᴍ ᴀᴅᴍɪɴ</b>\n{SEP}\n\n"
               f"{global_msg}\n\n"
               f"{SEP}\n▸ ᴩᴏꜱᴛᴇᴅ ▸ {global_time}\n\n{FOOTER()}</blockquote>")
        bot.send_message(uid, txt, parse_mode="HTML")
    except: pass

# ═══════════════ API MANAGER ═══════════════
def _get_custom_api_url(key):
    try:
        c.execute("SELECT api_url FROM api_keys WHERE api_name=? AND is_active=1 AND api_url != ''", (key,))
        r = c.fetchone(); return r[0] if r else None
    except: return None

def _get_custom_api_key(key_name):
    try:
        c.execute("SELECT api_key FROM api_keys WHERE api_name=? AND is_active=1 AND api_key != ''", (key_name,))
        r = c.fetchone(); return r[0] if r else None
    except: return None

def _save_api_url(key, url, by):
    try:
        c.execute("SELECT id FROM api_keys WHERE api_name=?", (key,))
        r = c.fetchone()
        if r:
            c.execute("UPDATE api_keys SET api_url=?,is_active=1,added_by=?,added_date=? WHERE api_name=?",
                      (url, by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), key))
        else:
            c.execute("INSERT INTO api_keys(api_name,api_url,api_key,is_active,added_by,added_date) VALUES(?,?,?,1,?,?)",
                      (key, url, "", by, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); return True
    except: return False

def _save_api_key_value(key_name, key_val, by):
    try:
        c.execute("SELECT id FROM api_keys WHERE api_name=?", (key_name,))
        r = c.fetchone()
        if r:
            c.execute("UPDATE api_keys SET api_key=?,is_active=1,added_by=?,added_date=? WHERE api_name=?",
                      (key_val, by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), key_name))
        else:
            c.execute("INSERT INTO api_keys(api_name,api_url,api_key,is_active,added_by,added_date) VALUES(?,?,?,1,?,?)",
                      (key_name, "", key_val, by, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); return True
    except: return False

def _reset_api(key):
    try:
        c.execute("DELETE FROM api_keys WHERE api_name=?", (key,)); conn.commit(); return True
    except: return False

def _get_live_api_url(key):
    custom = _get_custom_api_url(key)
    if custom: return custom
    info = next((a for a in _BOT_APIS if a[0] == key), None)
    return info[2] if info else ""

def _get_live_api_key(key_name):
    custom = _get_custom_api_key(key_name)
    if custom: return custom
    info = next((k for k in _BOT_API_KEYS if k[0] == key_name), None)
    return info[2] if info else ""

# ═══════════════ GROUP HELPERS ═══════════════
def get_group(gid):
    if gid in _caches["groups"]: return _caches["groups"][gid]
    c.execute("SELECT * FROM groups WHERE group_id=?", (gid,))
    r = c.fetchone(); _caches["groups"][gid] = r; return r

def add_group(gid, title):
    c.execute("INSERT OR IGNORE INTO groups(group_id,group_title,added_date,added_by) VALUES(?,?,?,?)",
              (gid, title, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), OWNER_ID))
    conn.commit(); _caches["groups"].pop(gid, None)

def safe_g(g, i, d=0):
    try: return g[i] if g and len(g) > i else d
    except: return d

def is_group_muted(gid):
    g = get_group(gid); return safe_g(g, 6) == 1 if g else False

def is_group_blocked(gid):
    g = get_group(gid); return safe_g(g, 5) == 1 if g else False

def get_group_welcome_on(gid):
    c.execute("SELECT welcome_on FROM group_welcome_settings WHERE group_id=?", (gid,))
    r = c.fetchone()
    if r: return r[0]
    c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,bye_on,updated_date) VALUES(?,1,1,?)",
              (gid, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); return 1

def get_group_bye_on(gid):
    c.execute("SELECT bye_on FROM group_welcome_settings WHERE group_id=?", (gid,))
    r = c.fetchone(); return r[0] if r else 1

def set_group_welcome_on(gid, v):
    c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,bye_on,updated_date) VALUES(?,1,1,?)",
              (gid, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    c.execute("UPDATE group_welcome_settings SET welcome_on=?,updated_date=? WHERE group_id=?",
              (v, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), gid)); conn.commit()

def set_group_bye_on(gid, v):
    c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,bye_on,updated_date) VALUES(?,1,1,?)",
              (gid, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    c.execute("UPDATE group_welcome_settings SET bye_on=?,updated_date=? WHERE group_id=?",
              (v, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), gid)); conn.commit()

# ═══════════════ FORCE JOIN ═══════════════
_chat_id_cache = {}
def _resolve_chat_id(cid):
    s = str(cid).strip()
    if s.lstrip("-").isdigit(): return int(s)
    if s.startswith("https://") or s.startswith("+"): return None
    key = s.lower()
    if key in _chat_id_cache: return _chat_id_cache[key]
    try:
        ch = bot.get_chat(s); _chat_id_cache[key] = ch.id; return ch.id
    except: return None

def get_force_join_channels():
    seen = set(); rows = []
    for cid, title, url in FORCE_JOIN_CHANNELS:
        nk = str(cid).lower().lstrip("@")
        if nk not in seen:
            rows.append((cid, title, url)); seen.add(nk)
    c.execute("SELECT chat_id,chat_title,chat_url FROM force_join_channels WHERE is_active=1")
    for r in c.fetchall():
        nk = str(r[0]).lower().lstrip("@")
        if nk not in seen:
            rows.append((r[0], r[1], r[2])); seen.add(nk)
    return rows

def check_channels(uid):
    if is_admin(uid): return True
    chs = get_force_join_channels()
    if not chs: return True
    for entry in chs:
        cid_str = str(entry[0]).strip()
        if cid_str.startswith("https://") or cid_str.startswith("+"): continue
        cid_val = _resolve_chat_id(cid_str)
        if cid_val is None: continue
        try:
            mem = bot.get_chat_member(cid_val, uid)
            if mem.status in ("left","kicked"): return False
        except Exception as e:
            err = str(e).lower()
            if any(x in err for x in ("user_not_participant","not a member","not member")):
                return False
    return True

def channels_kb(uid=None):
    chs = get_force_join_channels()
    if not chs: return None
    mk = InlineKeyboardMarkup(row_width=1); added = False; seen = set()
    for entry in chs:
        cid_str = str(entry[0]).strip(); title = entry[1]; url = entry[2]
        nk = cid_str.lower().lstrip("@")
        if nk in seen: continue
        seen.add(nk)
        if uid and not (cid_str.startswith("https://") or cid_str.startswith("+")):
            cv = _resolve_chat_id(cid_str)
            if cv:
                try:
                    mem = bot.get_chat_member(cv, uid)
                    if mem.status not in ("left","kicked"): continue
                except: pass
        mk.add(_IKB(f"▸ ᴊᴏɪɴ {title[:22]}", style="primary",
                    icon_custom_emoji_id="5258021357446268553", url=url))
        added = True
    if not added: return None
    mk.add(_IKB("✅ ɪ ᴊᴏɪɴᴇᴅ — ᴠᴇʀɪꜰʏ", style="success",
                icon_custom_emoji_id="6147565374289220368", callback_data="verify_channels"))
    return mk

# ═══════════════ APIs ═══════════════
def api_number(num):
    try:
        url = _get_live_api_url("number").replace("{}", str(num))
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            d = r.json()
            if d and (d.get("data") or d.get("success") or d.get("name") or d.get("operator") or d.get("results")):
                d["success"] = True; d["_src"] = "primary"; return d
    except: pass
    try:
        url2 = _get_live_api_url("number2").replace("{}", str(num))
        r = requests.get(url2, timeout=12)
        if r.status_code == 200:
            d = r.json()
            if d.get("results") or d.get("success"): d["success"] = True; d["_src"] = "rbot"; return d
    except: pass
    return None

def _fetch_tg(uid):
    res = {}
    try:
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getChat", params={"chat_id": str(uid)}, timeout=8)
        if r.status_code == 200:
            d = r.json().get("result", {})
            res.update(first_name=d.get("first_name",""), last_name=d.get("last_name",""),
                       username=d.get("username",""), bio=d.get("bio",""), tg_id=str(d.get("id","")))
    except: pass
    return res

def api_full_user(query):
    query = str(query).strip()
    is_uid = query.lstrip("-").isdigit()
    cl = query.replace("@","").strip()
    tg_id = ""; phone = ""; country = "India"; cc = "+91"

    def _tg(): return _fetch_tg(re.sub(r"\D","",query) if is_uid else ("@" + cl))
    def _zcpe():
        try:
            url = _get_live_api_url("userid").replace("{}", str(query)) if is_uid else _get_live_api_url("username").replace("{}", cl)
            r = requests.get(url, timeout=20)
            if r.status_code == 200: return r.json()
        except: pass
        return None

    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(_tg); f2 = ex.submit(_zcpe)
        tg = f1.result() or {}; zd = f2.result() or {}

    if zd:
        _d = zd.get("data") or {}
        _p1 = _d.get("p1") if isinstance(_d, dict) else None
        recs = _p1.get("records") if isinstance(_p1, dict) else None
        if recs and isinstance(recs, list):
            rec0 = recs[0]
            _ph = str(rec0.get("number","") or "").strip()
            if _ph and len(_ph) >= 7 and _ph != query:
                phone = _ph
                country = str(rec0.get("country","India") or "India")
                cc = str(rec0.get("country_code","+91") or "+91")
                if cc.replace("+","") and phone.startswith(cc.replace("+","")):
                    stripped = phone[len(cc.replace("+","")):]
                    if len(stripped) >= 7: phone = stripped
        _id = str(zd.get("target_id","") or zd.get("telegram_id","") or "").strip()
        if _id.lstrip("-").isdigit(): tg_id = _id

    if tg.get("tg_id"): tg_id = tg["tg_id"]
    if not tg_id and is_uid: tg_id = re.sub(r"\D","",query)

    ud = {"telegram_id": tg_id,
          "first_name": tg.get("first_name","") or "", "last_name": tg.get("last_name","") or "",
          "username": tg.get("username","") or "", "bio": tg.get("bio","") or "",
          "phone": phone, "number": phone, "country": country, "country_code": cc}
    return {"success": True, "data": ud}

def api_ff(uid):
    try:
        url = _get_live_api_url("freefire").replace("{}", str(uid))
        r = requests.get(url, timeout=25)
        if r.status_code == 200:
            d = r.json()
            if d and d.get("basicInfo"): return {"success": True, "raw": d}
    except: pass
    return None

def api_ff_like(uid):
    urls = []
    for k in ["ff_like1","ff_like2","ff_like3","ff_like4","ff_like5"]:
        u = _get_live_api_url(k)
        if u and "{}" in u: urls.append(u.replace("{}", str(uid)))
    if not urls: return {"success": False, "likes_given": 0, "likes_before": 0, "likes_after": 0}
    def _call(u):
        try:
            r = requests.get(u, timeout=25)
            if r.status_code == 200: return r.json()
        except: pass
        return None
    with ThreadPoolExecutor(max_workers=5) as ex:
        results = [f.result() for f in [ex.submit(_call, u) for u in urls]]
    total = before = after = 0
    for d in results:
        if not d: continue
        if d.get("LikesGivenByAPI") or d.get("likes_given"):
            total += int(d.get("LikesGivenByAPI") or d.get("likes_given") or 0)
            before = int(d.get("LikesbeforeCommand") or d.get("likes_before") or before)
            after = int(d.get("LikesafterCommand") or d.get("likes_after") or after)
    return {"success": total > 0, "likes_given": total, "likes_before": before, "likes_after": after}

def api_aadhar(a):
    try:
        url = _get_live_api_url("aadhar").replace("{}", str(a))
        ck = _get_live_api_key("key_aadhar")
        if ck and "SH4DAW-D4DY" in url: url = url.replace("SH4DAW-D4DY", ck)
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") and d.get("results",{}).get("success"):
                return {"success": True, "data": d["results"].get("data", []), "total": d["results"].get("total_records", 0)}
    except: pass
    return None

def api_insta(u):
    try:
        url = _get_live_api_url("instagram").replace("{}", str(u))
        ck = _get_live_api_key("key_instagram")
        if ck and "SH4DAW-D4DY" in url: url = url.replace("SH4DAW-D4DY", ck)
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            d = r.json()
            if d.get("username"): d["success"] = True; return d
    except: pass
    return None

def api_vehicle(rc):
    try:
        url = _get_live_api_url("vehicle").replace("{}", str(rc))
        ck = _get_live_api_key("key_vehicle")
        if ck and "SH4DAW-D4DY" in url: url = url.replace("SH4DAW-D4DY", ck)
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            d = r.json()
            if d.get("success"): return d
    except: pass
    return None

def api_bomber(num):
    def _call(url):
        try:
            r = requests.get(url, timeout=35)
            if r.status_code == 200:
                try:
                    d = r.json()
                    return {"ok": True, "sms": int(d.get("sms",0) or d.get("count",0) or 0),
                            "calls": int(d.get("calls",0) or 0), "wa": int(d.get("wa",0) or 0)}
                except: return {"ok": True, "sms": 0, "calls": 0, "wa": 0}
        except: pass
        return {"ok": False, "sms": 0, "calls": 0, "wa": 0}
    u1 = _get_live_api_url("bomber1"); u2 = _get_live_api_url("bomber2")
    rk = _get_live_api_key("key_rlx_bomber")
    urls = []
    if u1 and "{}" in u1: urls.append(u1.replace("{}", str(num)))
    if u2 and "{}" in u2:
        u2_f = u2.replace("{}", str(num))
        if rk and "rlxcoder" in u2_f: u2_f = u2_f.replace("rlxcoder", rk)
        urls.append(u2_f)
    if not urls: return None
    with ThreadPoolExecutor(max_workers=2) as ex:
        results = [f.result() for f in [ex.submit(_call, u) for u in urls]]
    a = results[0] if len(results) > 0 else {"ok": False, "sms": 0, "calls": 0, "wa": 0}
    b = results[1] if len(results) > 1 else {"ok": False, "sms": 0, "calls": 0, "wa": 0}
    if not (a["ok"] or b["ok"]): return None
    return {"success": True, "sms": a["sms"]+b["sms"], "calls": a["calls"]+b["calls"],
            "wa": a["wa"]+b["wa"], "total": a["sms"]+b["sms"]+a["calls"]+b["calls"]+a["wa"]+b["wa"]}

# ═══════════════ FF LIKE COOLDOWN ═══════════════
_uid_cd = {}; _rl = {}
def _like_cd_check(uid, ff_uid):
    if is_admin(uid): return True, 0
    key = f"{uid}:{ff_uid}"; now = time.time()
    if key in _uid_cd:
        if now - _uid_cd[key] < LIKE_COOLDOWN_HRS * 3600:
            return False, LIKE_COOLDOWN_HRS * 3600 - (now - _uid_cd[key])
    else:
        try:
            c.execute("SELECT last_like FROM ff_like_cooldown WHERE key=?", (key,))
            r = c.fetchone()
            if r:
                _uid_cd[key] = r[0]
                if now - r[0] < LIKE_COOLDOWN_HRS * 3600:
                    return False, LIKE_COOLDOWN_HRS * 3600 - (now - r[0])
        except: pass
    return True, 0

def _like_cd_set(uid, ff_uid, region):
    key = f"{uid}:{ff_uid}"; now = time.time()
    _uid_cd[key] = now
    c.execute("INSERT OR REPLACE INTO ff_like_cooldown(key,user_id,uid,region,last_like,timestamp) VALUES(?,?,?,?,?,?)",
              (key, uid, ff_uid, region, now, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

def _like_rl_check(uid):
    if is_admin(uid): return True
    key = f"{uid}:like"; now = time.time()
    if key not in _rl:
        try:
            c.execute("SELECT timestamps FROM ff_like_ratelimit WHERE key=?", (key,))
            r = c.fetchone()
            _rl[key] = [float(t) for t in r[0].split(",") if t] if r and r[0] else []
        except: _rl[key] = []
    _rl[key] = [t for t in _rl[key] if now - t < 86400]
    return len(_rl[key]) < LIKE_DAILY_MAX

def _like_rl_add(uid):
    if is_admin(uid): return
    key = f"{uid}:like"; _rl.setdefault(key, []).append(time.time())
    _rl[key] = [t for t in _rl[key] if time.time() - t < 86400]
    try:
        s = ",".join(str(t) for t in _rl[key])
        c.execute("INSERT OR REPLACE INTO ff_like_ratelimit(key,user_id,timestamps) VALUES(?,?,?)", (key, uid, s))
        conn.commit()
    except: pass

# ═══════════════ FORMATTERS ═══════════════
def fmt_number(res, num, credits=None):
    if not res or not res.get("success"):
        return card_wrap("ɴᴜᴍʙᴇʀ ɪɴꜰᴏ",
            f"{section('ꜱᴛᴀᴛᴜꜱ')}\n├ ᴛᴀʀɢᴇᴛ  ▸ <code>{num}</code>\n└ ʀᴇꜱᴜʟᴛ  ▸ ☠ ᴛᴀʀɢᴇᴛ ᴏꜰꜰʟɪɴᴇ", credits)
    recs = res.get("data", []) if isinstance(res.get("data"), list) else []
    if not recs and res.get("_src") == "rbot": recs = res.get("results", [])
    body = f"{section('ʟᴏᴄᴋᴇᴅ')}\n├ ɴᴜᴍʙᴇʀ ▸ <code>{num}</code>\n└ ʀᴇᴄᴏʀᴅꜱ ▸ <b>{len(recs)}</b>\n\n"
    for i, r in enumerate(recs[:5], 1):
        nm = r.get("name", "N/A") or "N/A"
        ft = r.get("fname", "") or r.get("father_name", "") or ""
        mob = r.get("mobile", num) or num
        addr = r.get("address", "") or ""
        circle = r.get("circle", "") or ""
        body += f"{section(f'ʀᴇᴄᴏʀᴅ {i}')}\n├ ɴᴀᴍᴇ ▸ <b>{nm}</b>\n├ ᴍᴏʙɪʟᴇ ▸ <code>{mob}</code>\n"
        if ft: body += f"├ ꜰᴀᴛʜᴇʀ ▸ {ft}\n"
        if circle: body += f"├ ᴄɪʀᴄʟᴇ ▸ {circle}\n"
        if addr: body += f"└ ᴀᴅᴅʀᴇꜱꜱ ▸ {addr[:60]}\n"
        body += "\n"
    return card_wrap("ɴᴜᴍʙᴇʀ ɪɴꜰᴏ", body.strip(), credits)

def fmt_user_card(res, query, credits=None):
    if not res or not res.get("success"):
        return card_wrap("ᴛᴀʀɢᴇᴛ", f"☠ ᴛᴀʀɢᴇᴛ ᴏꜰꜰʟɪɴᴇ\n▸ <code>{query}</code>", credits)
    ud = res.get("data", {}) or {}
    nm = f"{(ud.get('first_name','') or '').strip()} {(ud.get('last_name','') or '').strip()}".strip() or "—"
    un = (ud.get("username","") or "").replace("@","")
    un_disp = f"@{un}" if un else "ɴᴏᴛ ꜱᴇᴛ"
    tg_id = str(ud.get("telegram_id","") or query).strip()
    country = ud.get("country","India") or "India"
    cc = ud.get("country_code","+91") or "+91"
    phone = str(ud.get("phone","") or ud.get("number","") or "").strip()
    if phone and cc and phone.startswith(cc.replace("+","")):
        s = phone[len(cc.replace("+","")):]
        if len(s) >= 7: phone = s
    ph_disp = f"<code>+{cc.replace('+','')} {phone}</code>" if phone else "🔒 ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ"
    body = (f"{section('ᴘʀᴏꜰɪʟᴇ')}\n├ ɴᴀᴍᴇ ▸ <b>{nm}</b>\n├ ᴜꜱᴇʀɴᴀᴍᴇ ▸ {un_disp}\n"
            f"├ ᴛɢ ɪᴅ ▸ <code>{tg_id}</code>\n└ ꜱᴛᴀᴛᴜꜱ ▸ ᴀᴄᴛɪᴠᴇ\n\n"
            f"{section('ʟᴏᴄᴀᴛɪᴏɴ')}\n├ ᴄᴏᴜɴᴛʀʏ ▸ {country}\n├ ᴄᴏᴅᴇ ▸ {cc}\n└ ɴᴜᴍʙᴇʀ ▸ {ph_disp}")
    return card_wrap("ᴛᴀʀɢᴇᴛ ʟᴏᴄᴋᴇᴅ", body, credits)

def fmt_ff(res, uid, credits=None):
    if not res or not res.get("success"):
        return card_wrap("ꜰꜰ ɪɴꜰᴏ", f"☠ ᴛᴀʀɢᴇᴛ ᴏꜰꜰʟɪɴᴇ\n▸ <code>{uid}</code>", credits)
    d = res["raw"]; bi = d.get("basicInfo", {}); si = d.get("socialInfo", {})
    clan = d.get("clanBasicInfo", {})
    ban = "☠ ʙᴀɴɴᴇᴅ" if bi.get("isBanned") else "✔ ᴀᴄᴛɪᴠᴇ"
    body = (f"{section('ᴘʟᴀʏᴇʀ')}\n├ ɴᴀᴍᴇ ▸ <b>{bi.get('nickname','N/A')}</b>\n"
            f"├ ᴜɪᴅ ▸ <code>{bi.get('accountId', uid)}</code>\n"
            f"├ ʀᴇɢɪᴏɴ ▸ {bi.get('region','N/A')}\n├ ʟᴇᴠᴇʟ ▸ {bi.get('level',0)}\n"
            f"├ ʟɪᴋᴇꜱ ▸ {bi.get('liked',0):,}\n└ ꜱᴛᴀᴛᴜꜱ ▸ {ban}\n\n"
            f"{section('ᴄʟᴀɴ')}\n├ ɴᴀᴍᴇ ▸ {clan.get('clanName','No Clan')}\n└ ʟᴠʟ ▸ {clan.get('clanLevel',0)}\n\n"
            f"{section('ꜱᴏᴄɪᴀʟ')}\n└ ʙɪᴏ ▸ {si.get('signature','—') or '—'}")
    return card_wrap("ꜰꜰ ᴛᴀʀɢᴇᴛ", body, credits)

def fmt_aadhar(res, a, credits=None):
    if not res or not res.get("success"):
        return card_wrap("ᴀᴀᴅʜᴀʀ", f"☠ ᴛᴀʀɢᴇᴛ ᴏꜰꜰʟɪɴᴇ\n▸ <code>{a}</code>", credits)
    body = f"{section('ʟᴏᴄᴋᴇᴅ')}\n├ ᴀᴀᴅʜᴀʀ ▸ <code>{a}</code>\n└ ʀᴇᴄᴏʀᴅꜱ ▸ {res.get('total',0)}\n\n"
    for i, rec in enumerate(res.get("data", [])[:3], 1):
        body += (f"{section(f'ʀᴇᴄᴏʀᴅ {i}')}\n├ ɴᴀᴍᴇ ▸ {rec.get('name','N/A')}\n"
                 f"├ ꜰᴀᴛʜᴇʀ ▸ {rec.get('father_name','N/A')}\n"
                 f"└ ᴍᴏʙɪʟᴇ ▸ <code>{rec.get('mobile','N/A')}</code>\n\n")
    return card_wrap("ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ", body.strip(), credits)

def fmt_insta(res, u, credits=None):
    if not res or not res.get("success"):
        return card_wrap("ɪɴꜱᴛᴀɢʀᴀᴍ", f"☠ ᴛᴀʀɢᴇᴛ ᴏꜰꜰʟɪɴᴇ\n▸ @{u}", credits)
    v = "✔" if res.get("verified") else "✘"
    p = "🔒" if res.get("private") else "🔓"
    body = (f"{section('ᴘʀᴏꜰɪʟᴇ')}\n├ ᴜꜱᴇʀɴᴀᴍᴇ ▸ @{res.get('username','N/A')}\n"
            f"├ ɴᴀᴍᴇ ▸ {res.get('name','N/A')}\n├ ᴠᴇʀɪꜰɪᴇᴅ ▸ {v}\n└ ᴘʀɪᴠᴀᴛᴇ ▸ {p}\n\n"
            f"{section('ꜱᴛᴀᴛꜱ')}\n├ ꜰᴏʟʟᴏᴡᴇʀꜱ ▸ {res.get('followers',0):,}\n"
            f"├ ꜰᴏʟʟᴏᴡɪɴɢ ▸ {res.get('following',0):,}\n└ ᴘᴏꜱᴛꜱ ▸ {res.get('posts',0):,}")
    return card_wrap("ɪɴꜱᴛᴀɢʀᴀᴍ ᴛᴀʀɢᴇᴛ", body, credits)

def fmt_vehicle(res, rc, credits=None):
    if not res or not res.get("success"):
        return card_wrap("ᴠᴇʜɪᴄʟᴇ", f"☠ ᴛᴀʀɢᴇᴛ ᴏꜰꜰʟɪɴᴇ\n▸ <code>{rc}</code>", credits)
    body = (f"{section('ᴏᴡɴᴇʀ')}\n├ ɴᴀᴍᴇ ▸ {res.get('owner_name','N/A')}\n"
            f"└ ᴍᴏʙɪʟᴇ ▸ <code>{res.get('mobile_number','N/A')}</code>\n\n"
            f"{section('ᴠᴇʜɪᴄʟᴇ')}\n├ ᴍᴏᴅᴇʟ ▸ {res.get('vehicle_model','N/A')}\n"
            f"├ ʀᴇɢ ▸ {res.get('registration_date','N/A')}\n"
            f"├ ꜰᴜᴇʟ ▸ {res.get('fuel_type','N/A')}\n"
            f"└ ɪɴꜱᴜʀ ▸ {res.get('insurance_valid_till','N/A')}")
    return card_wrap("ᴠᴇʜɪᴄʟᴇ ɪɴꜰᴏ", body, credits)

# ═══════════════ WELCOME MEDIA ═══════════════
def _delete_old_welcome_file(path):
    try:
        if path and os.path.exists(path): os.remove(path)
    except: pass

def _fmt_size(b):
    if b < 1024: return f"{b}B"
    if b < 1024*1024: return f"{b//1024}KB"
    return f"{b/1024/1024:.1f}MB"

def get_welcome_media_info():
    c.execute("SELECT welcome_image,welcome_video FROM welcome_settings WHERE id=1")
    r = c.fetchone()
    img = r[0] if r else None; vid = r[1] if r else None
    def _info(path):
        if not path: return {"set": False, "exists": False, "path": None, "size": 0}
        exists = os.path.exists(path)
        return {"set": True, "exists": exists, "path": path, "size": os.path.getsize(path) if exists else 0}
    return {"video": _info(vid), "image": _info(img)}

def _welcome_kb_preview_mode():
    info = get_welcome_media_info()
    mk = InlineKeyboardMarkup(row_width=2)
    v = info["video"]; i = info["image"]
    def _status(d):
        if not d["set"]: return "❌"
        if not d["exists"]: return "⚠️"
        return f"✅ {_fmt_size(d['size'])}"
    mk.row(_IKB("🎥 ᴄʜᴀɴɢᴇ ᴠɪᴅᴇᴏ", style="success", icon_custom_emoji_id="5472159355853888315", callback_data="wmedia_change_video"),
           _IKB("🖼 ᴄʜᴀɴɢᴇ ɪᴍᴀɢᴇ", style="success", icon_custom_emoji_id="5281024850096301559", callback_data="wmedia_change_image"))
    if v["set"]:
        mk.add(_IKB(f"🗑️ ᴅᴇʟᴇᴛᴇ ᴠɪᴅᴇᴏ ({_status(v)})", style="danger", icon_custom_emoji_id="5471937446368975982", callback_data="wmedia_del_video"))
    if i["set"]:
        mk.add(_IKB(f"🗑️ ᴅᴇʟᴇᴛᴇ ɪᴍᴀɢᴇ ({_status(i)})", style="danger", icon_custom_emoji_id="5471937446368975982", callback_data="wmedia_del_image"))
    mk.add(_IKB("🔄 ʀᴇꜰʀᴇꜱʜ", style="primary", icon_custom_emoji_id="5341715473882955310", callback_data="wmedia_refresh"))
    mk.add(_IKB("⬅️ ʙᴀᴄᴋ", style="danger", icon_custom_emoji_id="6039366177541657", callback_data="wmedia_back"))
    return mk

def _welcome_panel_text():
    info = get_welcome_media_info()
    v = info["video"]; i = info["image"]
    def _line(label, d):
        if not d["set"]: return f"├ {label} ▸ ❌ ɴᴏᴛ ꜱᴇᴛ"
        if not d["exists"]: return f"├ {label} ▸ ⚠️ ꜰɪʟᴇ ᴍɪꜱꜱɪɴɢ"
        return f"├ {label} ▸ ✅ {_fmt_size(d['size'])}"
    if v["set"] and v["exists"]: active = "🎥 VIDEO"
    elif i["set"] and i["exists"]: active = "🖼 IMAGE"
    else: active = "📝 TEXT ONLY"
    return (f"<blockquote>{SEP}\n👋 <b>ᴡᴇʟᴄᴏᴍᴇ ꜱᴇᴛᴛɪɴɢꜱ</b>\n{SEP}\n\n"
            f"{_line('ᴠɪᴅᴇᴏ', v)}\n{_line('ɪᴍᴀɢᴇ', i)}\n"
            f"└ ᴀᴄᴛɪᴠᴇ ▸ <b>{active}</b>\n\n{FOOTER()}</blockquote>")

# ═══════════════ KEYBOARDS ═══════════════
def kb_main(uid):
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.row(_KB("⚡ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ", style="success", icon_custom_emoji_id="5465169893580086142"),
           _KB("🔍 ᴜꜱᴇʀɴᴀᴍᴇ ɪɴꜰᴏ", style="success", icon_custom_emoji_id="5258362837411045098"))
    mk.row(_KB("🆔 ᴛɢ ɪᴅ ɪɴꜰᴏ", style="success", icon_custom_emoji_id="5188217332748527444"),
           _KB("👤 ꜱᴇʟᴇᴄᴛ ᴛᴀʀɢᴇᴛ", style="success", icon_custom_emoji_id="6109432142079466939",
               request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False)))
    mk.row(_KB("🎮 ꜰꜰ ɪɴꜰᴏ", style="success", icon_custom_emoji_id="5472159355853888315"),
           _KB("❤️ ꜰꜰ ʟɪᴋᴇ", style="success", icon_custom_emoji_id="6208452093397699863"))
    mk.row(_KB("📸 ɪɴꜱᴛᴀɢʀᴀᴍ", style="success", icon_custom_emoji_id="5281024850096301559"),
           _KB("🚗 ᴠᴇʜɪᴄʟᴇ ʀᴄ", style="success", icon_custom_emoji_id="5372981976804366741"))
    mk.row(_KB("🪪 ᴀᴀᴅʜᴀʀ", style="success", icon_custom_emoji_id="5431577498364158238"),
           _KB("💣 ʙᴏᴍʙᴇʀ", style="danger", icon_custom_emoji_id="5469654973308476699"))
    mk.row(_KB("🎁 ᴅᴀɪʟʏ ꜱᴘɪɴ", style="success", icon_custom_emoji_id="5449800250032143374"),
           _KB("💰 ᴡᴀʟʟᴇᴛ", style="success", icon_custom_emoji_id="5224257782013769471"))
    mk.row(_KB("🎫 ʀᴇᴅᴇᴇᴍ", style="success", icon_custom_emoji_id="5418010521309815154"),
           _KB("🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", style="success", icon_custom_emoji_id="5409008750893734809"))
    if is_admin(uid):
        mk.row(_KB("⚙️ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", style="danger", icon_custom_emoji_id="6237699910150397736"))
    else:
        mk.row(_KB("⚠️ ꜱᴜᴘᴘᴏʀᴛ", style="success", icon_custom_emoji_id="6269490656779965144"))
    return mk

def kb_bomber():
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.row(_KB("💣 ɴᴇᴡ ʙᴏᴍʙᴇʀ", style="success", icon_custom_emoji_id="5469654973308476699"),
           _KB("🔴 ꜱᴛᴏᴘ ʙᴏᴍʙᴇʀ", style="danger", icon_custom_emoji_id="5471937446368975982"))
    mk.row(_KB("🔙 ᴍᴀɪɴ ᴍᴇɴᴜ", style="danger", icon_custom_emoji_id="6039366177541657"))
    return mk

def kb_select_user():
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add(_KB("👤 ꜱᴇʟᴇᴄᴛ ᴛᴀʀɢᴇᴛ", style="success", icon_custom_emoji_id="6109432142079466939",
        request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False)))
    mk.add(_KB("🔙 ᴍᴀɪɴ ᴍᴇɴᴜ", style="danger", icon_custom_emoji_id="6039366177541657"))
    return mk

def kb_admin():
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.row(_KB("📊 ᴅᴀꜱʜʙᴏᴀʀᴅ", style="success", icon_custom_emoji_id="6237699910150397736"),
           _KB("👥 ᴜꜱᴇʀ ʟɪꜱᴛ", style="success", icon_custom_emoji_id="6035084557378654059"))
    mk.row(_KB("📡 ɢʟᴏʙᴀʟ ʙᴄᴀꜱᴛ", style="danger", icon_custom_emoji_id="5258021357446268553"),
           _KB("📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ", style="success", icon_custom_emoji_id="5258021357446268553"))
    mk.row(_KB("🔔 ᴀʟᴇʀᴛ ᴏɴ/ᴏꜰꜰ", style="primary", icon_custom_emoji_id="5449800250032143374"),
           _KB("📜 ʜɪꜱᴛᴏʀʏ", style="success", icon_custom_emoji_id="5281024850096301559"))
    mk.row(_KB("⚙️ ꜰᴇᴀᴛᴜʀᴇ ᴛᴏɢɢʟᴇ", style="success", icon_custom_emoji_id="5341715473882955310"),
           _KB("📢 ᴄʜᴀɴɴᴇʟꜱ", style="success", icon_custom_emoji_id="5258021357446268553"))
    mk.row(_KB("🎨 ʙʀᴀɴᴅɪɴɢ ꜱᴇᴛᴛɪɴɢꜱ", style="primary", icon_custom_emoji_id="5341715473882955310"),
           _KB("🔗 ᴀᴘɪ ᴜʀʟꜱ", style="success", icon_custom_emoji_id="5258021357446268553"))
    mk.row(_KB("🔑 ᴀᴘɪ ᴋᴇʏꜱ", style="success", icon_custom_emoji_id="5379600444098093058"),
           _KB("👋 ᴡᴇʟᴄᴏᴍᴇ ꜱᴇᴛ", style="success", icon_custom_emoji_id="5449800250032143374"))
    mk.row(_KB("🎪 ꜱᴛɪᴄᴋᴇʀ ꜱᴇᴛ", style="success", icon_custom_emoji_id="5281024850096301559"),
           _KB("🎫 ɢᴇɴ ʀᴇᴅᴇᴇᴍ", style="success", icon_custom_emoji_id="5418010521309815154"))
    mk.row(_KB("🎁 ᴄᴏᴅᴇ ʟɪꜱᴛ", style="success", icon_custom_emoji_id="5409008750893734809"),
           _KB("💎 ɢᴇɴ ᴘʀᴇᴍɪᴜᴍ", style="success", icon_custom_emoji_id="6312104703815590263"))
    mk.row(_KB("💰 ᴀᴅᴅ ᴄʀᴇᴅɪᴛꜱ", style="success", icon_custom_emoji_id="5379600444098093058"),
           _KB("➖ ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛꜱ", style="success", icon_custom_emoji_id="5379600444098093058"))
    mk.row(_KB("💎 ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ", style="success", icon_custom_emoji_id="4956719506027185156"),
           _KB("💀 ʀᴇᴠᴏᴋᴇ ᴘʀᴇᴍɪᴜᴍ", style="danger", icon_custom_emoji_id="5469654973308476699"))
    mk.row(_KB("🚫 ʙʟᴏᴄᴋ ᴜꜱᴇʀ", style="danger", icon_custom_emoji_id="5471937446368975982"),
           _KB("✅ ᴜɴʙʟᴏᴄᴋ ᴜꜱᴇʀ", style="success", icon_custom_emoji_id="6147565374289220368"))
    mk.row(_KB("🔒 ᴘʀᴏᴛᴇᴄᴛ ᴜꜱᴇʀ", style="primary", icon_custom_emoji_id="5890882606668452641"),
           _KB("🧹 ᴄʟᴇᴀʀ ʜɪꜱᴛᴏʀʏ", style="danger", icon_custom_emoji_id="5471937446368975982"))
    mk.row(_KB("🔙 ᴍᴀɪɴ ᴍᴇɴᴜ", style="danger", icon_custom_emoji_id="6039366177541657"))
    return mk

def kb_branding():
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add(_KB("✏️ ᴄʜᴀɴɢᴇ ʙᴏᴛ ɴᴀᴍᴇ", style="success", icon_custom_emoji_id="5341715473882955310"))
    mk.add(_KB("🔗 ᴄʜᴀɴɢᴇ ᴜꜱᴇʀɴᴀᴍᴇ", style="success", icon_custom_emoji_id="5258021357446268553"))
    mk.add(_KB("🏷 ᴄʜᴀɴɢᴇ ᴅᴇᴠ ʟᴀʙᴇʟ", style="success", icon_custom_emoji_id="5379600444098093058"))
    mk.add(_KB("🎯 ᴄʜᴀɴɢᴇ ᴛᴀɢʟɪɴᴇ", style="success", icon_custom_emoji_id="5281024850096301559"))
    mk.add(_KB("👁 ᴩʀᴇᴠɪᴇᴡ ᴄᴜʀʀᴇɴᴛ", style="primary", icon_custom_emoji_id="5890882606668452641"))
    mk.add(_KB("🔄 ʀᴇꜱᴇᴛ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ", style="danger", icon_custom_emoji_id="5471937446368975982"))
    mk.add(_KB("⬅️ ʙᴀᴄᴋ ᴛᴏ ᴀᴅᴍɪɴ", style="danger", icon_custom_emoji_id="6039366177541657"))
    return mk

def kb_features_inline():
    states = {n: e for n, e in get_all_feature_states()}
    feats = [("number","⚡ Number"),("username","🔍 Username"),("tgid","🆔 TG ID"),
             ("aadhar","🪪 Aadhar"),("instagram","📸 Instagram"),("freefire","🎮 FF"),
             ("freefire_like","❤️ FF Like"),("vehicle","🚗 Vehicle"),("bomber","💣 Bomber")]
    mk = InlineKeyboardMarkup(row_width=2); btns = []
    for fn, lb in feats:
        on = states.get(fn, True)
        btns.append(_IKB(f"{'✔' if on else '✘'} {lb}", style="success" if on else "danger", callback_data=f"ftog_{fn}"))
    for i in range(0, len(btns), 2): mk.row(*btns[i:i+2])
    return mk

# ═══════════════ LOG ═══════════════
def log_activity(uid, fname, uname, source, added=0, total=0):
    try:
        now = datetime.now()
        c.execute("INSERT INTO token_log(user_id,user_name,username,added,total,source,log_date,log_time) VALUES(?,?,?,?,?,?,?,?)",
                  (uid, fname, uname, added, total, source, now.strftime("%d %b %Y"), now.strftime("%I:%M %p")))
        conn.commit()
        txt = (f"<blockquote><b>📡 ᴛᴏᴋᴇɴ ʟᴏɢ</b>\n{SEP}\n"
               f"├ ᴜꜱᴇʀ ▸ {fname}\n├ ɪᴅ ▸ <code>{uid}</code>\n├ ᴜɴ ▸ @{uname or 'none'}\n"
               f"├ ꜱʀᴄ ▸ {source}\n└ ᴛɪᴍᴇ ▸ {now.strftime('%d %b %I:%M %p')}\n{SEP}\n{FOOTER()}</blockquote>")
        bot.send_message(LOG_CHANNEL_ID, txt, parse_mode="HTML")
    except: pass

def is_identifier_blocked(x):
    c.execute("SELECT COUNT(*) FROM blocked_identifiers WHERE identifier=?", (str(x).lower(),))
    return c.fetchone()[0] > 0

def _is_protected(identifier):
    try:
        c.execute("SELECT COUNT(*) FROM protected_users WHERE identifier=?", (str(identifier).lower().strip(),))
        return c.fetchone()[0] > 0
    except: return False

# ═══════════════ SEARCH FLOW ═══════════════
def _do_search(uid, uname, fname, stype, query, m):
    user = get_user(uid)
    if not user: add_user(uid, uname, fname); user = get_user(uid)
    if is_identifier_blocked(str(uid)): return
    if not is_admin(uid):
        qc = str(query).lower().lstrip("@")
        if _is_protected(query) or _is_protected(qc):
            bot.reply_to(m, card_wrap("ᴘʀᴏᴛᴇᴄᴛᴇᴅ",
                f"{section('ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ')}\n▸ ᴛᴀʀɢᴇᴛ ɪꜱ ᴘʀᴏᴛᴇᴄᴛᴇᴅ"), parse_mode="HTML"); return
    cost = 4 if stype == S_BOMB else 1
    if not deduct_credit(uid, cost):
        bot.reply_to(m, denied("ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ", f"ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ᴄʀᴇᴅɪᴛꜱ (ɴᴇᴇᴅ {cost})"), parse_mode="HTML"); return
    sm = bot.reply_to(m, f"<blockquote>{pbar(0)}\n▸ ɪɴɪᴛɪᴀʟɪᴢɪɴɢ...</blockquote>", parse_mode="HTML")
    try: bot.send_chat_action(m.chat.id, "typing")
    except: pass
    anim_label = {"number":"ᴇxᴛʀᴀᴄᴛɪɴɢ ɴᴜᴍʙᴇʀ","username":"ʟᴏᴄᴀᴛɪɴɢ ᴜꜱᴇʀ","tgid":"ꜰᴇᴛᴄʜɪɴɢ ᴛɢ ᴅᴀᴛᴀ",
                  "adh":"ᴅᴇᴄᴏᴅɪɴɢ ᴀᴀᴅʜᴀʀ","insta":"ꜱᴄᴀɴɴɪɴɢ ɪɴꜱᴛᴀ","ff":"ʟᴏᴀᴅɪɴɢ ꜰꜰ","fflike":"ꜱᴇɴᴅɪɴɢ ʟɪᴋᴇꜱ",
                  "veh":"ᴠᴇʜɪᴄʟᴇ ʟᴏᴏᴋᴜᴘ","bomb":"ʟᴀᴜɴᴄʜɪɴɢ ʙᴏᴍʙᴇʀ"}.get(stype, "ᴇxᴛʀᴀᴄᴛɪɴɢ")
    stop = extract_anim(m.chat.id, sm.message_id, anim_label)
    res = None; rtxt = None
    try:
        if stype == S_NUM:
            res = api_number(query); stop[0]=True
            rtxt = fmt_number(res, query, get_credits(uid))
        elif stype in (S_USER, S_TID):
            res = api_full_user(query); stop[0]=True
            rtxt = fmt_user_card(res, query, get_credits(uid))
        elif stype == S_ADH:
            res = api_aadhar(query); stop[0]=True
            rtxt = fmt_aadhar(res, query, get_credits(uid))
        elif stype == S_INSTA:
            res = api_insta(query); stop[0]=True
            rtxt = fmt_insta(res, query, get_credits(uid))
        elif stype == S_FF:
            res = api_ff(query); stop[0]=True
            rtxt = fmt_ff(res, query, get_credits(uid))
        elif stype == S_VEH:
            res = api_vehicle(query); stop[0]=True
            rtxt = fmt_vehicle(res, query, get_credits(uid))
        elif stype == S_FFLIKE:
            ok, rem = _like_cd_check(uid, query)
            if not ok:
                stop[0]=True
                h = int(rem//3600); mn = int((rem%3600)//60)
                bot.edit_message_text(card_wrap("ᴄᴏᴏʟᴅᴏᴡɴ",
                    f"{section('ᴜɪᴅ ᴏɴ ᴄᴏᴏʟᴅᴏᴡɴ')}\n├ ᴜɪᴅ ▸ <code>{query}</code>\n└ ʀᴇᴛʀʏ ɪɴ ▸ <b>{h}h {mn}m</b>"),
                    m.chat.id, sm.message_id, parse_mode="HTML")
                refund_credit(uid, cost); user_state[uid]=S_NONE; return
            res = api_ff_like(query); stop[0]=True
            if res and res.get("success"):
                _like_cd_set(uid, query, "ind"); _like_rl_add(uid)
                body = (f"{section('ʟɪᴋᴇꜱ ꜱᴇɴᴛ')}\n├ ᴜɪᴅ ▸ <code>{query}</code>\n"
                        f"├ ʙᴇꜰᴏʀᴇ ▸ {res.get('likes_before',0)}\n"
                        f"├ ᴀꜰᴛᴇʀ ▸ {res.get('likes_after',0)}\n"
                        f"└ ɢɪᴠᴇɴ ▸ <b>+{res.get('likes_given',0)}</b>")
                rtxt = card_wrap("❤️ ꜰꜰ ʟɪᴋᴇ", body, get_credits(uid))
            else:
                rtxt = card_wrap("❤️ ꜰꜰ ʟɪᴋᴇ", f"{section('ꜱᴛᴀᴛᴜꜱ')}\n▸ ☠ ʟɪᴋᴇ ꜰᴀɪʟᴇᴅ", get_credits(uid))
                refund_credit(uid, cost)
        elif stype == S_BOMB:
            stop[0]=True
            threading.Thread(target=run_bomber, args=(uid, m.chat.id, query, sm.message_id), daemon=True).start()
            user_state[uid] = S_NONE; return
        if rtxt:
            try: bot.edit_message_text(rtxt, m.chat.id, sm.message_id, parse_mode="HTML")
            except:
                try: bot.send_message(m.chat.id, rtxt, parse_mode="HTML")
                except: pass
        if res and (res.get("success") if isinstance(res, dict) else True):
            c.execute("INSERT INTO search_history(user_id,search_type,query,search_date,result) VALUES(?,?,?,?,?)",
                      (uid, stype, query, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), json.dumps(res)[:2000]))
            conn.commit()
            log_activity(uid, fname, uname, stype.upper(), 0, 0)
        else:
            if not is_admin(uid): refund_credit(uid, cost)
    except Exception as e:
        stop[0]=True
        try: bot.edit_message_text(f"<blockquote>☠ ᴇʀʀᴏʀ\n▸ {str(e)[:200]}\n\n{FOOTER()}</blockquote>",
                                   m.chat.id, sm.message_id, parse_mode="HTML")
        except: pass
        if not is_admin(uid): refund_credit(uid, cost)
    user_state[uid] = S_NONE

# ═══════════════ BOMBER ═══════════════
def run_bomber(uid, chat_id, num, msg_id):
    MAX = 600; start = time.time(); sms = calls = wa = rounds = 0
    bomber_jobs[uid] = {"running": True}
    try:
        bot.edit_message_text(
            f"<blockquote>{FRAME_T}\n║  💣 ʙᴏᴍʙᴇʀ ᴀᴄᴛɪᴠᴇ\n{FRAME_B}\n\n"
            f"▸ ᴛᴀʀɢᴇᴛ ▸ <code>+91{num}</code>\n{pbar(0)}\n\n▸ /stopbomb to stop\n{FOOTER()}</blockquote>",
            chat_id, msg_id, parse_mode="HTML")
    except: pass
    res = api_bomber(num)
    if res and res.get("success"):
        sms = res.get("sms",0); calls = res.get("calls",0); wa = res.get("wa",0); rounds = 1
    while bomber_jobs.get(uid, {}).get("running", False):
        el = time.time() - start
        if el >= MAX: break
        time.sleep(20)
        el = time.time() - start
        if el >= MAX: break
        r2 = api_bomber(num)
        if r2 and r2.get("success"):
            sms = max(sms, r2.get("sms",0)); calls = max(calls, r2.get("calls",0))
            wa = max(wa, r2.get("wa",0)); rounds += 1
        rem = int(MAX - el); m_ = rem//60; s_ = rem%60; pct = min(int(el/MAX*100), 99)
        try:
            bot.edit_message_text(
                f"<blockquote>{FRAME_T}\n║  💣 ʙᴏᴍʙɪɴɢ\n{FRAME_B}\n\n"
                f"▸ ᴛᴀʀɢᴇᴛ ▸ <code>+91{num}</code>\n▸ ᴛɪᴍᴇ ▸ {int(el)}s | ʀᴇᴍᴀɪɴ ▸ {m_}m {s_}s\n"
                f"{pbar(pct)}\n\n{section('ꜱᴛᴀᴛꜱ')}\n"
                f"├ ꜱᴍꜱ ▸ {sms}\n├ ᴄᴀʟʟꜱ ▸ {calls}\n├ ᴡᴀ ▸ {wa}\n└ ʀᴏᴜɴᴅꜱ ▸ {rounds}\n\n{FOOTER()}</blockquote>",
                chat_id, msg_id, parse_mode="HTML")
        except: pass
    bomber_jobs.pop(uid, None)
    el = int(time.time()-start)
    reason = "ᴀᴜᴛᴏ-ꜱᴛᴏᴘ (10ᴍ)" if el >= MAX else "ᴜꜱᴇʀ ꜱᴛᴏᴘ"
    try:
        bot.edit_message_text(
            f"<blockquote>{FRAME_T}\n║  💣 ʙᴏᴍʙᴇʀ ᴇɴᴅᴇᴅ\n{FRAME_B}\n\n"
            f"▸ ʀᴇᴀꜱᴏɴ ▸ {reason}\n▸ ᴛɪᴍᴇ ▸ {el}s\n\n"
            f"{section('ꜰɪɴᴀʟ')}\n├ ꜱᴍꜱ ▸ {sms}\n├ ᴄᴀʟʟꜱ ▸ {calls}\n└ ᴡᴀ ▸ {wa}\n\n{FOOTER()}</blockquote>",
            chat_id, msg_id, parse_mode="HTML")
    except: pass

# ═══════════════ WELCOME ═══════════════
_wel_fileid_cache = {}

def format_welcome(uid, fname, credits, uname=""):
    fname = _html.escape(fname)
    udisp = f"@{uname}" if uname else "ɴᴏ ᴜꜱᴇʀɴᴀᴍᴇ"
    cr = "∞" if is_admin(uid) else str(credits)
    bn = BOT_NAME(); b_u = BOT_USERNAME()
    tagline = get_setting("bot_tagline", "OSINT • FF • BOMBER • WALLET")
    dev_label = get_setting("dev_label", "DEVELOPER")

    E_MOON  = "6284979958116786100"
    E_LOOP  = "5465629669829128119"
    E_SKULL = "4956461073550017373"
    E_HI    = "4958469026595472714"
    E_CR    = "6312104703815590263"
    E_GIFT  = "5361552478416986392"
    E_PREM  = "4956719506027185156"
    E_HELP  = "6147422674000808494"
    E_DEV   = "4958900559139570572"
    E_CHECK = "6147565374289220368"
    E_USER  = "6035084557378654059"
    E_ID    = "5888781182249738113"
    E_STAR  = "5465144557568010803"
    E_TROPHY= "5409008750893734809"

    LOOP = _pe(E_LOOP, "➿") * 10

    return (
        f"<blockquote>"
        f"{_pe(E_MOON,'🌙')} <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {bn}</b>\n"
        f"{LOOP}\n\n"
        f"{_pe(E_SKULL,'💀')}{_pe(E_HI,'👋')} ʜᴇʟʟᴏ <a href='tg://user?id={uid}'><b>{fname}</b></a>\n"
        f"{_pe(E_STAR,'⭐')} <i>{tagline}</i>\n\n"
        f"{LOOP}\n"
        f"{_pe(E_USER,'👤')} ᴜꜱᴇʀ   ▸ {udisp}\n"
        f"{_pe(E_ID,'🆔')} ɪᴅ     ▸ <code>{uid}</code>\n"
        f"{_pe(E_CR,'💎')} ᴄʀᴇᴅɪᴛꜱ ▸ <b>{cr}</b>\n"
        f"{_pe(E_GIFT,'🎁')} ꜱᴘɪɴ    ▸ ᴀᴠᴀɪʟᴀʙʟᴇ\n"
        f"{_pe(E_PREM,'👑')} ᴛɪᴇʀ    ▸ {'ᴘʀᴇᴍɪᴜᴍ' if not is_admin(uid) else 'ᴏᴡɴᴇʀ'}\n"
        f"{LOOP}\n\n"
        f"{_pe(E_HELP,'❓')} /help ꜰᴏʀ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ\n"
        f"{_pe(E_TROPHY,'🏆')} ʀᴇꜰᴇʀ & ᴇᴀʀɴ +{REFERRAL_BONUS} ᴄʀᴇᴅɪᴛꜱ\n\n"
        f"{LOOP}\n"
        f"{_pe(E_DEV,'👨‍💻')} {dev_label} ▸ @{b_u} {_pe(E_CHECK,'✅')}\n"
        f"{LOOP}"
        f"</blockquote>"
    )

def _welcome_plain_caption(uid, fname, credits, uname=""):
    fname = _html.escape(fname)
    udisp = f"@{uname}" if uname else "ɴᴏ ᴜꜱᴇʀɴᴀᴍᴇ"
    cr = "∞" if is_admin(uid) else str(credits)
    bn = BOT_NAME(); b_u = BOT_USERNAME()
    tagline = get_setting("bot_tagline", "OSINT • FF • BOMBER • WALLET")
    dev_label = get_setting("dev_label", "DEVELOPER")
    return (
        f"🌙 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {bn}\n➿➿➿➿➿➿➿➿➿➿\n\n"
        f"💀👋 ʜᴇʟʟᴏ <a href='tg://user?id={uid}'><b>{fname}</b></a>\n"
        f"⭐ <i>{tagline}</i>\n\n"
        f"➿➿➿➿➿➿➿➿➿➿\n"
        f"👤 ᴜꜱᴇʀ ▸ {udisp}\n🆔 ɪᴅ ▸ <code>{uid}</code>\n"
        f"💎 ᴄʀᴇᴅɪᴛꜱ ▸ <b>{cr}</b>\n🎁 ꜱᴘɪɴ ▸ ᴀᴠᴀɪʟᴀʙʟᴇ\n"
        f"👑 ᴛɪᴇʀ ▸ {'ᴘʀᴇᴍɪᴜᴍ' if not is_admin(uid) else 'ᴏᴡɴᴇʀ'}\n\n"
        f"➿➿➿➿➿➿➿➿➿➿\n"
        f"❓ /help ꜰᴏʀ ᴄᴏᴍᴍᴀɴᴅꜱ\n🏆 ʀᴇꜰᴇʀ & ᴇᴀʀɴ +{REFERRAL_BONUS} ᴄʀᴇᴅɪᴛꜱ\n\n"
        f"➿➿➿➿➿➿➿➿➿➿\n"
        f"👨‍💻 {dev_label} ▸ @{b_u} ✅\n➿➿➿➿➿➿➿➿➿➿"
    )

# ═══════════════ COMMANDS ═══════════════
@bot.message_handler(commands=["start"])
def cmd_start(m):
    if m.chat.type == "channel": return
    uid = m.from_user.id
    uname = m.from_user.username or ""
    fname = m.from_user.first_name or "User"

    # Group
    if m.chat.type in ("group","supergroup"):
        add_group(m.chat.id, m.chat.title or "Group")
        if not get_user(uid): add_user(uid, uname, fname)
        cr = get_credits(uid)
        txt = (f"<blockquote>{FRAME_T}\n║  ⚡ ᴍᴇɴᴜ ᴏᴩᴇɴᴇᴅ\n{FRAME_B}\n\n"
               f"▸ ᴜꜱᴇʀ ▸ <a href='tg://user?id={uid}'><b>{fname}</b></a>\n"
               f"▸ ᴄʀᴇᴅɪᴛꜱ ▸ {cr}\n\n▸ /help ꜰᴏʀ ᴄᴏᴍᴍᴀɴᴅꜱ\n\n{FOOTER()}</blockquote>")
        try: bot.reply_to(m, txt, parse_mode="HTML")
        except: pass
        return

    # Check if new user
    is_new = not bool(get_user(uid))

    # Parse ref param
    ref = None
    try:
        parts = m.text.split()
        if len(parts) > 1:
            try:
                ref = int(parts[1])
                if ref == uid: ref = None
            except: pass
    except: pass

    # Force join check
    chs = get_force_join_channels()
    if chs:
        try: not_joined = not check_channels(uid)
        except: not_joined = False
        if not_joined:
            mk = channels_kb(uid)
            if mk:
                try:
                    bot.send_message(uid,
                        f"<blockquote>{FRAME_T}\n║  ⚠️ ᴊᴏɪɴ ʀᴇqᴜɪʀᴇᴅ\n{FRAME_B}\n\n"
                        f"▸ ʙᴏᴛ ᴜꜱᴇ ᴋᴀʀɴᴇ ꜱᴇ ᴩᴇʜʟᴇ ᴄʜᴀɴɴᴇʟ ᴊᴏɪɴ ᴋᴀʀᴏ\n"
                        f"▸ ᴊᴏɪɴ ᴋᴇ ʙᴀᴀᴅ ✔ <b>ɪ ᴊᴏɪɴᴇᴅ — ᴠᴇʀɪꜰʏ</b> ᴅᴀʙᴀᴏ\n\n{FOOTER()}</blockquote>",
                        reply_markup=mk, parse_mode="HTML")
                    # Still register for tracking
                    if is_new: add_user(uid, uname, fname, ref)
                    if is_new: notify_admin_new_user(uid, uname, fname, True, ref)
                    return
                except: pass

    # Register
    if is_new:
        add_user(uid, uname, fname, ref)
        # NOTIFY ADMIN (new user alert)
        threading.Thread(target=notify_admin_new_user,
                         args=(uid, uname, fname, True, ref), daemon=True).start()
        # Send global broadcast to new user
        try: send_global_to_new_user(uid)
        except: pass

    cr = get_credits(uid)
    full_txt = format_welcome(uid, fname, cr, uname)
    plain_cap = _welcome_plain_caption(uid, fname, cr, uname)
    kb = kb_main(uid)

    c.execute("SELECT welcome_video,welcome_image,first_time_sticker FROM welcome_settings WHERE id=1")
    wrow = c.fetchone() or (None, None, None)
    wvid, wimg, stk = wrow
    sent = False
    if stk:
        try: bot.send_sticker(uid, stk)
        except: pass
    if wvid and os.path.exists(wvid):
        cached_vid = _wel_fileid_cache.get("video")
        if cached_vid:
            try:
                bot.send_video(uid, cached_vid, caption=plain_cap, parse_mode="HTML", reply_markup=kb); sent = True
            except: _wel_fileid_cache.pop("video", None)
        if not sent:
            try:
                with open(wvid, "rb") as f:
                    sv = bot.send_video(uid, f, caption=plain_cap, parse_mode="HTML", reply_markup=kb)
                sent = True
                if sv.video: _wel_fileid_cache["video"] = sv.video.file_id
            except: pass
    if not sent and wimg and os.path.exists(wimg):
        cached_img = _wel_fileid_cache.get("image")
        if cached_img:
            try:
                bot.send_photo(uid, cached_img, caption=plain_cap, parse_mode="HTML", reply_markup=kb); sent = True
            except: _wel_fileid_cache.pop("image", None)
        if not sent:
            try:
                with open(wimg, "rb") as f:
                    sp = bot.send_photo(uid, f, caption=plain_cap, parse_mode="HTML", reply_markup=kb)
                sent = True
                if sp.photo: _wel_fileid_cache["image"] = sp.photo[-1].file_id
            except: pass
    if not sent:
        try: bot.send_message(uid, full_txt, reply_markup=kb, parse_mode="HTML")
        except: pass

@bot.message_handler(commands=["help"])
def cmd_help(m):
    if m.chat.type == "channel": return
    txt = (f"<blockquote>{FRAME_T}\n║  ⚡ ᴄᴏᴍᴍᴀɴᴅꜱ\n{FRAME_B}\n\n"
           f"{section('ᴛᴀʀɢᴇᴛ ʟᴏᴏᴋᴜᴘ')}\n├ /numinfo <num>\n├ /user <@u|id>\n├ /insta <user>\n└ /ffinfo <uid>\n\n"
           f"{section('ꜰꜰ')}\n├ /like <uid>\n└ /like ind <uid>\n\n"
           f"{section('ʙᴏᴍʙᴇʀ')}\n├ /bomb <num>\n└ /stopbomb\n\n"
           f"{section('ᴡᴀʟʟᴇᴛ')}\n├ /spin\n├ /redeem <code>\n└ /premium <code>\n\n"
           f"{section('ᴀᴜᴛᴏ ᴅᴇᴛᴇᴄᴛ')}\n├ <code>9876543210</code> ▸ ɴᴜᴍ\n└ <code>@username</code> ▸ ᴜꜱᴇʀ\n\n"
           f"{FOOTER()}</blockquote>")
    bot.reply_to(m, txt, parse_mode="HTML")

@bot.message_handler(commands=["numinfo"])
def cmd_numinfo(m):
    parts = m.text.split()
    if len(parts) < 2: return
    num = re.sub(r"\D","",parts[1])
    if len(num) == 12 and num.startswith("91"): num = num[2:]
    if not re.match(r"^[6-9]\d{9}$", num): return
    _do_search(m.from_user.id, m.from_user.username or "", m.from_user.first_name or "", S_NUM, num, m)

@bot.message_handler(commands=["user","usernum"])
def cmd_user(m):
    parts = m.text.split()
    if len(parts) < 2: return
    q = parts[1].strip()
    st = S_TID if q.lstrip("-").isdigit() else S_USER
    _do_search(m.from_user.id, m.from_user.username or "", m.from_user.first_name or "", st, q, m)

@bot.message_handler(commands=["insta"])
def cmd_insta(m):
    parts = m.text.split()
    if len(parts) < 2: return
    u = parts[1].replace("@","").strip()
    _do_search(m.from_user.id, m.from_user.username or "", m.from_user.first_name or "", S_INSTA, u, m)

@bot.message_handler(commands=["ffinfo","info"])
def cmd_ff(m):
    parts = m.text.split()
    if len(parts) < 2: return
    u = re.sub(r"\D","",parts[1])
    _do_search(m.from_user.id, m.from_user.username or "", m.from_user.first_name or "", S_FF, u, m)

@bot.message_handler(commands=["like"])
def cmd_like(m):
    parts = m.text.split()
    if len(parts) < 2: return
    uid = m.from_user.id
    if not _like_rl_check(uid):
        bot.reply_to(m, card_wrap("ᴅᴀɪʟʏ ʟɪᴍɪᴛ", f"▸ ᴍᴀx {LIKE_DAILY_MAX}/ᴅᴀʏ"), parse_mode="HTML"); return
    ff_uid = re.sub(r"\D","",parts[-1])
    _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_FFLIKE, ff_uid, m)

@bot.message_handler(commands=["bomb"])
def cmd_bomb(m):
    parts = m.text.split()
    if len(parts) < 2: return
    num = re.sub(r"\D","",parts[1])
    if len(num) == 12 and num.startswith("91"): num = num[2:]
    if not re.match(r"^[6-9]\d{9}$", num): return
    _do_search(m.from_user.id, m.from_user.username or "", m.from_user.first_name or "", S_BOMB, num, m)

@bot.message_handler(commands=["stopbomb"])
def cmd_stopbomb(m):
    uid = m.from_user.id
    if uid in bomber_jobs: bomber_jobs[uid]["running"] = False
    bot.reply_to(m, card_wrap("ʙᴏᴍʙᴇʀ", "▸ ꜱᴛᴏᴘ ꜱɪɢɴᴀʟ ꜱᴇɴᴛ"), parse_mode="HTML")

@bot.message_handler(commands=["spin"])
def cmd_spin(m):
    uid = m.from_user.id
    if not get_user(uid): add_user(uid, m.from_user.username or "", m.from_user.first_name or "")
    if not can_claim_daily(uid):
        bot.reply_to(m, card_wrap("ꜱᴘɪɴ", "▸ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ ᴛᴏᴅᴀʏ"), parse_mode="HTML"); return
    dm = bot.send_dice(m.chat.id, emoji="🎲")
    time.sleep(4)
    won = {1:1,2:1,3:2,4:3,5:4,6:5}.get(dm.dice.value, 1)
    c.execute("UPDATE users SET credits=credits+? WHERE user_id=?", (won, uid))
    c.execute("INSERT OR IGNORE INTO daily_claims VALUES(?,?)", (uid, datetime.now().strftime("%Y-%m-%d")))
    conn.commit(); _caches["users"].pop(uid, None)
    u = get_user(uid); tot = u[5] if u else won
    bot.send_message(m.chat.id, card_wrap("🎁 ᴅᴀɪʟʏ ꜱᴘɪɴ",
        f"{section('ʀᴇꜱᴜʟᴛ')}\n├ ᴡᴏɴ ▸ <b>+{won}</b>\n└ ᴛᴏᴛᴀʟ ▸ <b>{tot}</b>", tot), parse_mode="HTML")

# ═══════════════ REDEEM ═══════════════
def _generate_credit_code():
    while True:
        code = "RODIX-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        c.execute("SELECT code FROM redeem_codes WHERE code=?", (code,))
        if not c.fetchone(): return code

def _generate_premium_code():
    while True:
        code = "RPREM-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        c.execute("SELECT code FROM premium_codes WHERE code=?", (code,))
        if not c.fetchone(): return code

def _normalize_code(raw):
    if not raw: return ""
    return raw.strip().upper().replace(" ", "").replace("\n","").replace("\t","")

def _do_redeem_credit(uid, raw_code):
    code = _normalize_code(raw_code)
    if not code: return False, "ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ"
    try:
        c.execute("SELECT credits,redeem_limit,used_count FROM redeem_codes WHERE code=?", (code,))
        r = c.fetchone()
        if not r: return False, f"☠ ᴄᴏᴅᴇ ɴᴏᴛ ꜰᴏᴜɴᴅ\n<code>{code}</code>"
        credits, rl, uc = r
        c.execute("SELECT COUNT(*) FROM redeemed_users WHERE code=? AND user_id=?", (code, uid))
        if c.fetchone()[0] > 0: return False, "ᴀʟʀᴇᴀᴅʏ ʀᴇᴅᴇᴇᴍᴇᴅ"
        if rl > 0 and uc >= rl: return False, "ᴄᴏᴅᴇ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ"
        c.execute("UPDATE users SET credits=COALESCE(credits,0)+? WHERE user_id=?", (credits, uid))
        c.execute("UPDATE redeem_codes SET used_count=used_count+1 WHERE code=?", (code,))
        c.execute("INSERT INTO redeemed_users(code,user_id,redeem_date) VALUES(?,?,?)",
                  (code, uid, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); _caches["users"].pop(uid, None)
        u = get_user(uid); tot = u[5] if u else credits
        return True, f"+{credits} ᴄʀᴇᴅɪᴛꜱ | ɴᴇᴡ ᴛᴏᴛᴀʟ: <b>{tot}</b>"
    except Exception as e:
        return False, f"sᴇʀᴠᴇʀ ᴇʀʀᴏʀ: {str(e)[:60]}"

def _do_redeem_premium(uid, raw_code):
    code = _normalize_code(raw_code)
    if not code: return False, "ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ"
    try:
        c.execute("SELECT days,redeem_limit,used_count FROM premium_codes WHERE code=?", (code,))
        r = c.fetchone()
        if not r: return False, f"☠ ᴄᴏᴅᴇ ɴᴏᴛ ꜰᴏᴜɴᴅ\n<code>{code}</code>"
        days, rl, uc = r
        c.execute("SELECT COUNT(*) FROM redeemed_premium WHERE code=? AND user_id=?", (code, uid))
        if c.fetchone()[0] > 0: return False, "ᴀʟʀᴇᴀᴅʏ ʀᴇᴅᴇᴇᴍᴇᴅ"
        if rl > 0 and uc >= rl: return False, "ᴄᴏᴅᴇ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ"
        until = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE users SET is_premium=1,premium_until=? WHERE user_id=?", (until, uid))
        c.execute("UPDATE premium_codes SET used_count=used_count+1 WHERE code=?", (code,))
        c.execute("INSERT INTO redeemed_premium(code,user_id,redeem_date) VALUES(?,?,?)",
                  (code, uid, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); _caches["users"].pop(uid, None)
        return True, f"ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴛɪᴠᴇ ꜰᴏʀ <b>{days} ᴅᴀʏꜱ</b>\nᴠᴀʟɪᴅ ᴛɪʟʟ: <code>{until}</code>"
    except Exception as e:
        return False, f"sᴇʀᴠᴇʀ ᴇʀʀᴏʀ: {str(e)[:60]}"

@bot.message_handler(commands=["redeem"])
def cmd_redeem(m):
    uid = m.from_user.id
    parts = m.text.split()
    if len(parts) < 2:
        user_state[uid] = S_REDEEM
        bot.reply_to(m, f"<blockquote>{SEP}\n🎫 <b>ʀᴇᴅᴇᴇᴍ ᴄʀᴇᴅɪᴛ ᴄᴏᴅᴇ</b>\n{SEP}\n\n"
                        f"▸ ᴄᴏᴅᴇ ʙʜᴇᴊᴏ (ᴇx: <code>RODIX-ABC123</code>)\n\n{FOOTER()}</blockquote>",
                    parse_mode="HTML"); return
    ok, msg = _do_redeem_credit(uid, parts[1])
    if ok:
        user = get_user(uid); cr = user[5] if user else 0
        bot.reply_to(m, card_wrap("✅ ʀᴇᴅᴇᴇᴍ ꜱᴜᴄᴄᴇꜱꜱ", f"{section('ᴀᴅᴅᴇᴅ')}\n{msg}", cr), parse_mode="HTML")
        log_activity(uid, m.from_user.first_name or "User", m.from_user.username or "", "REDEEM_CREDIT", 0, 0)
    else:
        bot.reply_to(m, card_wrap("☠ ꜰᴀɪʟᴇᴅ", f"{section('ᴇʀʀᴏʀ')}\n▸ {msg}"), parse_mode="HTML")

@bot.message_handler(commands=["premium"])
def cmd_premium(m):
    uid = m.from_user.id
    parts = m.text.split()
    if len(parts) < 2:
        user_state[uid] = S_PREM
        bot.reply_to(m, f"<blockquote>{SEP}\n💎 <b>ʀᴇᴅᴇᴇᴍ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ</b>\n{SEP}\n\n"
                        f"▸ ᴄᴏᴅᴇ ʙʜᴇᴊᴏ (ᴇx: <code>RPREM-ABC123</code>)\n\n{FOOTER()}</blockquote>",
                    parse_mode="HTML"); return
    ok, msg = _do_redeem_premium(uid, parts[1])
    if ok:
        bot.reply_to(m, card_wrap("💎 ᴀᴄᴛɪᴠᴇ", f"{section('ʀᴇᴅᴇᴇᴍᴇᴅ')}\n{msg}"), parse_mode="HTML")
        log_activity(uid, m.from_user.first_name or "User", m.from_user.username or "", "REDEEM_PREMIUM", 0, 0)
    else:
        bot.reply_to(m, card_wrap("☠ ꜰᴀɪʟᴇᴅ", f"{section('ᴇʀʀᴏʀ')}\n▸ {msg}"), parse_mode="HTML")

# ═══════════════ BUTTON HANDLERS ═══════════════
def _check_access(m, feature=None):
    uid = m.from_user.id
    if is_identifier_blocked(str(uid)): return False
    if not get_user(uid): add_user(uid, m.from_user.username or "", m.from_user.first_name or "")
    if feature and not is_feature_enabled(feature):
        bot.reply_to(m, card_wrap("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ", "▸ ꜰᴇᴀᴛᴜʀᴇ ᴏꜰꜰʟɪɴᴇ"), parse_mode="HTML"); return False
    return True

@bot.message_handler(func=lambda m: m.text == "⚡ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ")
def btn_num(m):
    if not _check_access(m, "number"): return
    user_state[m.from_user.id] = S_NUM
    bot.reply_to(m, prompt_box("⚡","ɴᴜᴍʙᴇʀ ɪɴꜰᴏ","10-ᴅɪɢɪᴛ ɴᴜᴍʙᴇʀ","9876543210", get_credits(m.from_user.id), 1, "+91 ᴏᴩᴛɪᴏɴᴀʟ"), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🔍 ᴜꜱᴇʀɴᴀᴍᴇ ɪɴꜰᴏ")
def btn_user(m):
    if not _check_access(m, "username"): return
    user_state[m.from_user.id] = S_USER
    bot.reply_to(m, prompt_box("🔍","ᴜꜱᴇʀɴᴀᴍᴇ ɪɴꜰᴏ","@username ᴏʀ ᴛɢ ɪᴅ","@durov", get_credits(m.from_user.id), 1), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🆔 ᴛɢ ɪᴅ ɪɴꜰᴏ")
def btn_tgid(m):
    if not _check_access(m, "tgid"): return
    user_state[m.from_user.id] = S_TID
    bot.reply_to(m, prompt_box("🆔","ᴛɢ ɪᴅ ɪɴꜰᴏ","ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ","123456789", get_credits(m.from_user.id), 1), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👤 ꜱᴇʟᴇᴄᴛ ᴛᴀʀɢᴇᴛ")
def btn_select(m):
    if not _check_access(m): return
    bot.reply_to(m, f"<blockquote>▸ ᴛᴀʀɢᴇᴛ ꜱᴇʟᴇᴄᴛ ᴋᴀʀᴏ:\n{FOOTER()}</blockquote>",
                 reply_markup=kb_select_user(), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🎮 ꜰꜰ ɪɴꜰᴏ")
def btn_ff(m):
    if not _check_access(m, "freefire"): return
    user_state[m.from_user.id] = S_FF
    bot.reply_to(m, prompt_box("🎮","ꜰꜰ ɪɴꜰᴏ","ꜰʀᴇᴇ ꜰɪʀᴇ ᴜɪᴅ","1382401870", get_credits(m.from_user.id), 1), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "❤️ ꜰꜰ ʟɪᴋᴇ")
def btn_fflike(m):
    if not _check_access(m, "freefire_like"): return
    user_state[m.from_user.id] = S_FFLIKE
    bot.reply_to(m, prompt_box("❤️","ꜰꜰ ʟɪᴋᴇ","ꜰʀᴇᴇ ꜰɪʀᴇ ᴜɪᴅ","1382401870", get_credits(m.from_user.id), 1, "ʀᴇɢɪᴏɴ: /like ind UID"), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📸 ɪɴꜱᴛᴀɢʀᴀᴍ")
def btn_insta(m):
    if not _check_access(m, "instagram"): return
    user_state[m.from_user.id] = S_INSTA
    bot.reply_to(m, prompt_box("📸","ɪɴꜱᴛᴀɢʀᴀᴍ","ɪɴꜱᴛᴀ ᴜꜱᴇʀɴᴀᴍᴇ","cristiano", get_credits(m.from_user.id), 1), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🚗 ᴠᴇʜɪᴄʟᴇ ʀᴄ")
def btn_veh(m):
    if not _check_access(m, "vehicle"): return
    user_state[m.from_user.id] = S_VEH
    bot.reply_to(m, prompt_box("🚗","ᴠᴇʜɪᴄʟᴇ ʀᴄ","ʀᴄ ɴᴜᴍʙᴇʀ","MH12AB1234", get_credits(m.from_user.id), 1), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🪪 ᴀᴀᴅʜᴀʀ")
def btn_adh(m):
    if not _check_access(m, "aadhar"): return
    user_state[m.from_user.id] = S_ADH
    bot.reply_to(m, prompt_box("🪪","ᴀᴀᴅʜᴀʀ","12-ᴅɪɢɪᴛ ᴀᴀᴅʜᴀʀ","649964855626", get_credits(m.from_user.id), 1), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💣 ʙᴏᴍʙᴇʀ")
def btn_bomber(m):
    if not _check_access(m, "bomber"): return
    bot.reply_to(m, card_wrap("💣 ʙᴏᴍʙᴇʀ", f"{section('ᴍᴇɴᴜ')}\n├ ꜱᴍꜱ + ᴄᴀʟʟ + ᴡᴀ\n└ ᴀᴜᴛᴏ-ꜱᴛᴏᴘ 10ᴍ"),
                 reply_markup=kb_bomber(), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💣 ɴᴇᴡ ʙᴏᴍʙᴇʀ")
def btn_new_bomber(m):
    if not _check_access(m, "bomber"): return
    if bomber_jobs.get(m.from_user.id, {}).get("running"):
        bot.reply_to(m, card_wrap("ʙᴏᴍʙᴇʀ", "▸ ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ"), parse_mode="HTML"); return
    user_state[m.from_user.id] = S_BOMB
    bot.reply_to(m, prompt_box("💣","ɴᴇᴡ ʙᴏᴍʙᴇʀ","10-ᴅɪɢɪᴛ ɴᴜᴍʙᴇʀ","9876543210", get_credits(m.from_user.id), 4), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🔴 ꜱᴛᴏᴘ ʙᴏᴍʙᴇʀ")
def btn_stop_bomber(m):
    uid = m.from_user.id
    if uid in bomber_jobs: bomber_jobs[uid]["running"] = False
    bot.reply_to(m, card_wrap("ꜱᴛᴏᴩᴩᴇᴅ", "▸ ꜱɪɢɴᴀʟ ꜱᴇɴᴛ"), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🎁 ᴅᴀɪʟʏ ꜱᴘɪɴ")
def btn_spin(m): cmd_spin(m)

@bot.message_handler(func=lambda m: m.text == "💰 ᴡᴀʟʟᴇᴛ")
def btn_wallet(m):
    uid = m.from_user.id
    u = get_user(uid)
    if not u: add_user(uid, m.from_user.username or "", m.from_user.first_name or ""); u = get_user(uid)
    cr = get_credits(uid); refs = get_referral_count(uid)
    try: rl = f"https://t.me/{bot.get_me().username}?start={uid}"
    except: rl = f"https://t.me/{BOT_USERNAME()}?start={uid}"
    body = (f"{section('ᴡᴀʟʟᴇᴛ')}\n├ ᴄʀᴇᴅɪᴛꜱ ▸ <b>{cr}</b>\n├ ʀᴇꜰꜱ ▸ {refs}\n"
            f"└ ᴛɪᴇʀ ▸ {'ᴘʀᴇᴍɪᴜᴍ' if (u and u[7]) else 'ꜰʀᴇᴇ'}\n\n"
            f"{section('ʀᴇꜰᴇʀ ʟɪɴᴋ')}\n<code>{rl}</code>\n\n"
            f"▸ +{REFERRAL_BONUS} ᴄʀᴇᴅɪᴛ ᴩᴇʀ ʀᴇꜰ")
    mk = InlineKeyboardMarkup()
    mk.add(_IKB("📤 ꜱʜᴀʀᴇ ʟɪɴᴋ", style="success", icon_custom_emoji_id="5253804796589402657",
                url=f"https://t.me/share/url?url={rl}&text=Join+{BOT_NAME()}!"))
    bot.reply_to(m, card_wrap("💰 ᴡᴀʟʟᴇᴛ", body, cr), reply_markup=mk, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🎫 ʀᴇᴅᴇᴇᴍ")
def btn_redeem(m):
    uid = m.from_user.id
    user_state[uid] = S_REDEEM
    bot.reply_to(m, f"<blockquote>{SEP}\n🎫 <b>ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ</b>\n{SEP}\n\n"
                    f"▸ ꜱᴇɴᴅ ᴄᴏᴅᴇ\n▸ ᴇx: <code>RODIX-XXXXXX</code>\n\n{FOOTER()}</blockquote>",
                parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ")
def btn_lb(m):
    c.execute("""SELECT u.user_id,u.first_name,u.username,COUNT(r.id) cnt
                 FROM users u LEFT JOIN referrals r ON u.user_id=r.referrer
                 GROUP BY u.user_id ORDER BY cnt DESC LIMIT 10""")
    rows = c.fetchall()
    body = section("ᴛᴏᴩ 10 ʀᴇꜰᴇʀʀᴇʀꜱ") + "\n"
    for i, r in enumerate(rows, 1):
        un = f"@{r[2]}" if r[2] else (r[1] or "User")[:15]
        you = " ◂ ʏᴏᴜ" if r[0] == m.from_user.id else ""
        body += f"├ {i}. {un} ▸ {r[3]}{you}\n"
    if not rows: body += "└ (ᴇᴍᴩᴛʏ)\n"
    bot.reply_to(m, card_wrap("🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", body), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "⚠️ ꜱᴜᴘᴘᴏʀᴛ")
def btn_support(m):
    mk = InlineKeyboardMarkup()
    mk.add(_IKB("📩 ᴄᴏɴᴛᴀᴄᴛ", style="primary", url=f"https://t.me/{BOT_USERNAME()}"))
    bot.reply_to(m, card_wrap("ꜱᴜᴘᴘᴏʀᴛ", f"▸ ᴄᴏɴᴛᴀᴄᴛ\n▸ @{BOT_USERNAME()}"), reply_markup=mk, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🔙 ᴍᴀɪɴ ᴍᴇɴᴜ")
def btn_back(m):
    user_state[m.from_user.id] = S_NONE
    bot.send_message(m.chat.id, card_wrap("ᴍᴇɴᴜ", "▸ ʙᴀᴄᴋ"), reply_markup=kb_main(m.from_user.id), parse_mode="HTML")

# ═══════════════ USERS_SHARED ═══════════════
@bot.message_handler(content_types=["users_shared"])
def on_shared(m):
    uid = m.from_user.id
    if not m.users_shared or not m.users_shared.user_ids: return
    obj = m.users_shared.user_ids[0]
    if hasattr(obj, "user_id"): target = obj.user_id
    elif isinstance(obj, dict): target = obj.get("user_id") or obj.get("id")
    else: target = obj
    try: target = int(target)
    except: return
    _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_TID, str(target), m)

# ═══════════════ GROUP ═══════════════
@bot.message_handler(func=lambda m: m.chat.type in ("group","supergroup"), content_types=["new_chat_members"])
def on_new_member(m):
    cid = m.chat.id
    add_group(cid, m.chat.title or "Group")
    for mb in m.new_chat_members:
        if mb.is_bot and mb.id == bot.get_me().id: continue
        if not get_group_welcome_on(cid): continue
        key = f"{cid}:{mb.id}"; now = time.time()
        if now - _join_dedup.get(key, 0) < 5: continue
        _join_dedup[key] = now
        fname = _html.escape(mb.first_name or "User")
        try: mem = bot.get_chat_members_count(cid)
        except: mem = "?"
        txt = (f"<blockquote>{FRAME_T}\n║  ⚡ ᴡᴇʟᴄᴏᴍᴇ\n{FRAME_B}\n\n"
               f"▸ <a href='tg://user?id={mb.id}'><b>{fname}</b></a>\n▸ ᴍᴇᴍʙᴇʀꜱ ▸ {mem}\n\n{FOOTER()}</blockquote>")
        try: bot.send_message(cid, txt, parse_mode="HTML")
        except: pass

@bot.message_handler(func=lambda m: m.chat.type in ("group","supergroup"), content_types=["left_chat_member"])
def on_left_member(m):
    cid = m.chat.id; mb = m.left_chat_member
    if not mb or mb.is_bot: return
    if not get_group_bye_on(cid): return
    fname = _html.escape(mb.first_name or "User")
    txt = (f"<blockquote>{FRAME_T}\n║  👋 ɢᴏᴏᴅʙʏᴇ\n{FRAME_B}\n\n▸ <b>{fname}</b> ᴄʜʜᴏᴅ ᴅɪʏᴀ\n\n{FOOTER()}</blockquote>")
    try: bot.send_message(cid, txt, parse_mode="HTML")
    except: pass

@bot.message_handler(func=lambda m: m.chat.type in ("group","supergroup") and m.text and not m.text.startswith("/"))
def group_auto(m):
    cid = m.chat.id; uid = m.from_user.id; txt = m.text.strip()
    add_group(cid, m.chat.title or "Group")
    if not get_user(uid): add_user(uid, m.from_user.username or "", m.from_user.first_name or "")
    if is_group_muted(cid) or is_group_blocked(cid): return
    if re.match(r"^[6-9]\d{9}$", txt):
        _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_NUM, txt, m)
    elif re.match(r"^@[a-zA-Z0-9_.]{4,}$", txt):
        _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_USER, txt, m)

@bot.message_handler(func=lambda m: m.chat.type in ("group","supergroup") and m.text and m.text.startswith("/"))
def group_cmds(m):
    cid = m.chat.id; uid = m.from_user.id; txt = m.text.strip()
    add_group(cid, m.chat.title or "Group")
    if not get_user(uid): add_user(uid, m.from_user.username or "", m.from_user.first_name or "")
    if is_group_muted(cid) or is_group_blocked(cid): return
    if txt.startswith("/wel"):
        try:
            cm = bot.get_chat_member(cid, uid)
            if cm.status not in ("administrator","creator") and not is_admin(uid): return
        except: return
        parts = txt.split(); arg = parts[1].lower() if len(parts) > 1 else ""
        if arg == "off": set_group_welcome_on(cid, 0); bot.reply_to(m, card_wrap("ᴡᴇʟᴄᴏᴍᴇ ᴏꜰꜰ", "▸ ʙᴀɴᴅ"), parse_mode="HTML")
        elif arg == "on": set_group_welcome_on(cid, 1); bot.reply_to(m, card_wrap("ᴡᴇʟᴄᴏᴍᴇ ᴏɴ", "▸ ᴄʜᴀʟᴜ"), parse_mode="HTML")
        return
    if txt.startswith("/leave"):
        try:
            cm = bot.get_chat_member(cid, uid)
            if cm.status not in ("administrator","creator") and not is_admin(uid): return
        except: return
        parts = txt.split(); arg = parts[1].lower() if len(parts) > 1 else ""
        if arg == "off": set_group_bye_on(cid, 0); bot.reply_to(m, card_wrap("ʙʏᴇ ᴏꜰꜰ", "▸ ʙᴀɴᴅ"), parse_mode="HTML")
        elif arg == "on": set_group_bye_on(cid, 1); bot.reply_to(m, card_wrap("ʙʏᴇ ᴏɴ", "▸ ᴄʜᴀʟᴜ"), parse_mode="HTML")
        return

# ═══════════════ ADMIN ROUTER ═══════════════
def _admin_router(m, txt):
    uid = m.from_user.id
    st = _admin_states.get(uid)
    if st:
        # REDEEM CREATE
        if isinstance(st, dict) and st.get("action") == "redeem_create":
            try:
                parts = txt.split()
                cr = int(parts[0]); lim = int(parts[1]) if len(parts) > 1 else 0
                code = st["code"]
                c.execute("INSERT INTO redeem_codes(code,credits,redeem_limit,used_count,created_by,created_date) VALUES(?,?,?,0,?,?)",
                          (code, cr, lim, uid, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit(); _admin_states.pop(uid, None)
                bot.reply_to(m, f"<blockquote>{SEP}\n✅ <b>ᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ!</b>\n{SEP}\n\n"
                                f"🎫 ᴄᴏᴅᴇ ▸ <code>{code}</code>\n💰 ᴄʀᴇᴅɪᴛꜱ ▸ <b>{cr}</b>\n🔢 ʟɪᴍɪᴛ ▸ {lim or '∞'}\n\n"
                                f"💡 ᴜꜱᴇʀ <code>/redeem {code}</code> ᴋᴀʀᴇɢᴀ\n{FOOTER()}</blockquote>", parse_mode="HTML")
                return True
            except Exception as e:
                bot.reply_to(m, f"<blockquote>☠ <b>ɪɴᴠᴀʟɪᴅ</b>\n▸ ꜰᴏʀᴍᴀᴛ: <code>credits limit</code>\n▸ ᴇʀʀᴏʀ: {str(e)[:80]}\n\n{FOOTER()}</blockquote>", parse_mode="HTML")
                return True
        # PREMIUM CREATE
        if isinstance(st, dict) and st.get("action") == "premium_create":
            try:
                parts = txt.split()
                days = int(parts[0]); lim = int(parts[1]) if len(parts) > 1 else 1
                code = st["code"]
                c.execute("INSERT INTO premium_codes(code,days,redeem_limit,used_count,created_by,created_date) VALUES(?,?,?,0,?,?)",
                          (code, days, lim, uid, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit(); _admin_states.pop(uid, None)
                bot.reply_to(m, f"<blockquote>{SEP}\n💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ!</b>\n{SEP}\n\n"
                                f"🎫 ᴄᴏᴅᴇ ▸ <code>{code}</code>\n📅 ᴅᴀʏꜱ ▸ <b>{days}</b>\n🔢 ʟɪᴍɪᴛ ▸ {lim}\n\n"
                                f"💡 ᴜꜱᴇʀ <code>/premium {code}</code> ᴋᴀʀᴇɢᴀ\n{FOOTER()}</blockquote>", parse_mode="HTML")
                return True
            except Exception as e:
                bot.reply_to(m, f"<blockquote>☠ <b>ɪɴᴠᴀʟɪᴅ</b>\n▸ ꜰᴏʀᴍᴀᴛ: <code>days limit</code>\n\n{FOOTER()}</blockquote>", parse_mode="HTML")
                return True
        if st == "addcredits" or st == "remcredits":
            try:
                parts = txt.split(); tu = int(parts[0]); amt = int(parts[1])
                if st == "addcredits": c.execute("UPDATE users SET credits=credits+? WHERE user_id=?", (amt, tu))
                else: c.execute("UPDATE users SET credits=MAX(0,credits-?) WHERE user_id=?", (amt, tu))
                conn.commit(); _caches["users"].pop(tu, None)
                bot.reply_to(m, card_wrap("ᴅᴏɴᴇ", f"▸ ᴜꜱᴇʀ {tu} ▸ {'+' if st=='addcredits' else '-'}{amt}"), parse_mode="HTML")
            except: bot.reply_to(m, card_wrap("ᴇʀʀᴏʀ", "▸ ɪɴᴠᴀʟɪᴅ"), parse_mode="HTML")
            _admin_states.pop(uid, None); return True
        if st == "addpremium":
            try:
                parts = txt.split(); tu = int(parts[0]); days = int(parts[1])
                until = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
                c.execute("UPDATE users SET is_premium=1,premium_until=? WHERE user_id=?", (until, tu))
                conn.commit(); _caches["users"].pop(tu, None)
                bot.reply_to(m, card_wrap("ᴅᴏɴᴇ", f"▸ {tu} ᴘʀᴇᴍɪᴜᴍ {days}ᴅ"), parse_mode="HTML")
            except: bot.reply_to(m, card_wrap("ᴇʀʀᴏʀ", "▸ ɪɴᴠᴀʟɪᴅ"), parse_mode="HTML")
            _admin_states.pop(uid, None); return True
        if st == "block" or st == "unblock":
            try:
                tu = int(txt.strip())
                if st == "block":
                    c.execute("INSERT OR REPLACE INTO blocked_identifiers(identifier,identifier_type,blocked_by,blocked_date,reason) VALUES(?,?,?,?,?)",
                              (str(tu), "user_id", uid, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "admin")); conn.commit()
                    bot.reply_to(m, card_wrap("ʙʟᴏᴄᴋᴇᴅ", f"▸ {tu}"), parse_mode="HTML")
                else:
                    c.execute("DELETE FROM blocked_identifiers WHERE identifier=?", (str(tu),)); conn.commit()
                    bot.reply_to(m, card_wrap("ᴜɴʙʟᴏᴄᴋᴇᴅ", f"▸ {tu}"), parse_mode="HTML")
            except: bot.reply_to(m, card_wrap("ᴇʀʀᴏʀ", "▸ ɪɴᴠᴀʟɪᴅ"), parse_mode="HTML")
            _admin_states.pop(uid, None); return True
        if st == "protect":
            ident = txt.strip().lower().lstrip("@")
            c.execute("INSERT OR REPLACE INTO protected_users(identifier,identifier_type,protected_by,protected_date) VALUES(?,?,?,?)",
                      (ident, "generic", uid, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))); conn.commit()
            _admin_states.pop(uid, None)
            bot.reply_to(m, card_wrap("ᴘʀᴏᴛᴇᴄᴛᴇᴅ", f"▸ {ident}"), parse_mode="HTML"); return True
        if st == "set_sticker": return True
        if st == "global_bcast":
            # Save + forward to ALL users
            try:
                txt_content = m.text or m.caption or ""
                if txt_content:
                    set_setting("global_bcast", _html.escape(txt_content)[:3000])
                    set_setting("global_bcast_time", datetime.now().strftime("%d %b %Y • %I:%M %p"))
            except: pass
            threading.Thread(target=do_global_broadcast, args=(m, uid), daemon=True).start()
            return True
        if isinstance(st, dict) and st.get("action") == "apiurl_input":
            key = st["key"]; label = st["label"]; new_url = txt.strip()
            if "{}" not in new_url:
                bot.reply_to(m, f"<blockquote>⚠️ {{}} ᴢᴀʀᴜʀɪ ʜᴀɪ\n{FOOTER()}</blockquote>", parse_mode="HTML"); return True
            if not new_url.startswith("http"):
                bot.reply_to(m, f"<blockquote>⚠️ <code>http</code> ꜱᴇ ꜱʜᴜʀᴜ\n{FOOTER()}</blockquote>", parse_mode="HTML"); return True
            ok = _save_api_url(key, new_url, uid); _admin_states.pop(uid, None)
            if ok:
                bot.reply_to(m, f"<blockquote>✅ ᴜʀʟ ꜱᴀᴠᴇᴅ: {label}\n{FOOTER()}</blockquote>", parse_mode="HTML")
            return True
        if isinstance(st, dict) and st.get("action") == "apikey_input":
            k_name = st["key"]; label = st["label"]; new_key = txt.strip()
            if len(new_key) < 3:
                bot.reply_to(m, f"<blockquote>⚠️ ᴄʜʜᴏᴛɪ ᴋᴇʏ\n{FOOTER()}</blockquote>", parse_mode="HTML"); return True
            ok = _save_api_key_value(k_name, new_key, uid); _admin_states.pop(uid, None)
            if ok: bot.reply_to(m, f"<blockquote>✅ ᴋᴇʏ ꜱᴀᴠᴇᴅ: {label}\n{FOOTER()}</blockquote>", parse_mode="HTML")
            return True
        if isinstance(st, dict) and st.get("action") == "branding":
            field = st.get("field", ""); new_val = txt.strip()
            if not new_val or len(new_val) > 60:
                bot.reply_to(m, f"<blockquote>⚠️ ɪɴᴠᴀʟɪᴅ\n{FOOTER()}</blockquote>", parse_mode="HTML"); return True
            ok = set_setting(field, new_val); _admin_states.pop(uid, None)
            labels = {"bot_name":"ʙᴏᴛ ɴᴀᴍᴇ", "bot_username":"ᴜꜱᴇʀɴᴀᴍᴇ", "dev_label":"ᴅᴇᴠ ʟᴀʙᴇʟ", "bot_tagline":"ᴛᴀɢʟɪɴᴇ"}
            if ok:
                bot.reply_to(m, f"<blockquote>✅ <b>{labels.get(field, field)} ᴜᴘᴅᴀᴛᴇᴅ!</b>\n\n▸ ɴᴇᴡ: <b>{new_val}</b>\n\n{FOOTER()}</blockquote>",
                             reply_markup=kb_branding(), parse_mode="HTML")
            return True

    # ── PANEL BUTTONS ──
    if txt == "📊 ᴅᴀꜱʜʙᴏᴀʀᴅ":
        c.execute("SELECT COUNT(*) FROM users"); tu = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM groups"); tg = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM search_history"); ts = c.fetchone()[0]
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date)=?", (today,))
        tn = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM redeem_codes"); trc = c.fetchone()[0]
        body = (f"{section('ꜱᴛᴀᴛꜱ')}\n├ ᴜꜱᴇʀꜱ    ▸ {tu}\n├ ᴛᴏᴅᴀʏ     ▸ {tn}\n├ ɢʀᴏᴜᴩꜱ   ▸ {tg}\n"
                f"├ ꜱᴇᴀʀᴄʜᴇꜱ ▸ {ts}\n└ ᴄᴏᴅᴇꜱ    ▸ {trc}")
        bot.reply_to(m, card_wrap("ᴅᴀꜱʜʙᴏᴀʀᴅ", body), parse_mode="HTML"); return True
    if txt == "👥 ᴜꜱᴇʀ ʟɪꜱᴛ":
        c.execute("SELECT user_id,first_name,credits,is_premium FROM users ORDER BY join_date DESC LIMIT 15")
        rows = c.fetchall(); body = section("ʟᴀꜱᴛ 15") + "\n"
        for u in rows:
            p = "💎" if u[3] else "▸"
            body += f"├ {p} <code>{u[0]}</code> {(u[1] or '')[:15]} ▸ {u[2]}\n"
        bot.reply_to(m, card_wrap("ᴜꜱᴇʀꜱ", body), parse_mode="HTML"); return True
    if txt == "📡 ɢʟᴏʙᴀʟ ʙᴄᴀꜱᴛ":
        cur = get_setting("global_bcast", "")
        cur_time = get_setting("global_bcast_time", "")
        txt_cur = f"\n\n📌 ᴩʀᴇᴠɪᴏᴜꜱ: {_html.escape(cur)[:100]}\n🕐 {cur_time}" if cur else "\n\n📌 ᴀʙʜɪ ᴋᴏɪ ɢʟᴏʙᴀʟ ᴍꜱɢ ɴᴀʜɪ"
        bot.reply_to(m,
            f"<blockquote>{SEP}\n📡 <b>ɢʟᴏʙᴀʟ ʙʀᴏᴀᴅᴄᴀꜱᴛ</b>\n{SEP}\n\n"
            f"▸ ᴊᴏ ʙʜɪ ʙʜᴇᴊᴏɢᴇ, <b>ꜱᴀʙ ᴜꜱᴇʀꜱ</b> ᴋᴏ ᴊᴀᴀʏᴇɢᴀ\n"
            f"▸ ɴᴀʏᴇ ᴜꜱᴇʀꜱ ᴋᴏ /start ᴩᴇ ʙʜɪ ᴅɪᴋʜᴇɢᴀ\n{SEP}{txt_cur}\n\n"
            f"📤 ᴀʙ ᴍꜱɢ ʙʜᴇᴊᴏ\n\n{FOOTER()}</blockquote>",
            parse_mode="HTML")
        _admin_states[uid] = "global_bcast"
        return True
    if txt == "📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ":
        _admin_states[uid] = "broadcast"
        bot.reply_to(m, card_wrap("ʙʀᴏᴀᴅᴄᴀꜱᴛ", "▸ ꜱᴇɴᴅ ᴍꜱɢ ᴛᴏ ᴀʟʟ"), parse_mode="HTML"); return True
    if txt == "🔔 ᴀʟᴇʀᴛ ᴏɴ/ᴏꜰꜰ":
        cur = get_setting("admin_alert", "1")
        new = "0" if cur == "1" else "1"
        set_setting("admin_alert", new)
        status = "🟢 ᴏɴ" if new == "1" else "🔴 ᴏꜰꜰ"
        bot.reply_to(m, f"<blockquote>{SEP}\n🔔 <b>ɴᴇᴡ ᴜꜱᴇʀ ᴀʟᴇʀᴛ</b>\n{SEP}\n\n"
                        f"▸ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>\n\n{FOOTER()}</blockquote>",
                     reply_markup=kb_admin(), parse_mode="HTML")
        return True
    if txt == "📜 ʜɪꜱᴛᴏʀʏ":
        c.execute("SELECT user_id,search_type,query FROM search_history ORDER BY id DESC LIMIT 10")
        rows = c.fetchall(); body = section("ʟᴀꜱᴛ 10") + "\n"
        for r in rows: body += f"├ <code>{r[0]}</code> ▸ {r[1]} ▸ {str(r[2])[:25]}\n"
        if not rows: body += "└ (ᴇᴍᴩᴛʏ)\n"
        bot.reply_to(m, card_wrap("ʜɪꜱᴛᴏʀʏ", body), parse_mode="HTML"); return True
    if txt == "⚙️ ꜰᴇᴀᴛᴜʀᴇ ᴛᴏɢɢʟᴇ":
        bot.reply_to(m, card_wrap("ᴛᴏɢɢʟᴇ", "▸ ᴛᴀᴩ ᴛᴏ ᴛᴏɢɢʟᴇ"), reply_markup=kb_features_inline(), parse_mode="HTML"); return True
    if txt == "📢 ᴄʜᴀɴɴᴇʟꜱ":
        chs = get_force_join_channels(); body = section("ꜰᴏʀᴄᴇ ᴊᴏɪɴ") + "\n"
        for cid2, t, u2 in chs: body += f"├ {t} ▸ <code>{cid2}</code>\n"
        body += "\n▸ /addchannel link\n▸ /removechannel id"
        bot.reply_to(m, card_wrap("ᴄʜᴀɴɴᴇʟꜱ", body), parse_mode="HTML"); return True
    if txt == "🎨 ʙʀᴀɴᴅɪɴɢ ꜱᴇᴛᴛɪɴɢꜱ":
        user_state[uid] = S_NONE; _admin_states.pop(uid, None)
        bot.reply_to(m,
            f"<blockquote>{SEP}\n🎨 <b>ʙʀᴀɴᴅɪɴɢ</b>\n{SEP}\n\n"
            f"├ ɴᴀᴍᴇ ▸ <b>{BOT_NAME()}</b>\n├ ᴜɴ ▸ <b>@{BOT_USERNAME()}</b>\n"
            f"├ ᴅᴇᴠ ʟᴀʙᴇʟ ▸ <b>{get_setting('dev_label')}</b>\n└ ᴛᴀɢʟɪɴᴇ ▸ <i>{get_setting('bot_tagline')}</i>\n\n"
            f"💡 ɴᴇᴇᴄʜᴇ ꜱᴇ ᴄʜᴀɴɢᴇ ᴋᴀʀ\n\n{FOOTER()}</blockquote>",
            reply_markup=kb_branding(), parse_mode="HTML")
        return True
    if txt == "✏️ ᴄʜᴀɴɢᴇ ʙᴏᴛ ɴᴀᴍᴇ":
        _admin_states[uid] = {"action":"branding","field":"bot_name"}
        bot.reply_to(m, f"<blockquote>✏️ ɴᴀʏᴀ ʙᴏᴛ ɴᴀᴍᴇ ʙʜᴇᴊ\n{FOOTER()}</blockquote>", parse_mode="HTML"); return True
    if txt == "🔗 ᴄʜᴀɴɢᴇ ᴜꜱᴇʀɴᴀᴍᴇ":
        _admin_states[uid] = {"action":"branding","field":"bot_username"}
        bot.reply_to(m, f"<blockquote>🔗 ɴᴀʏᴀ ᴜꜱᴇʀɴᴀᴍᴇ ʙʜᴇᴊ (@ ʙᴀɢʜᴀɪʀ)\n{FOOTER()}</blockquote>", parse_mode="HTML"); return True
    if txt == "🏷 ᴄʜᴀɴɢᴇ ᴅᴇᴠ ʟᴀʙᴇʟ":
        _admin_states[uid] = {"action":"branding","field":"dev_label"}
        bot.reply_to(m, f"<blockquote>🏷 ɴᴀʏᴀ ᴅᴇᴠ ʟᴀʙᴇʟ ʙʜᴇᴊ\n▸ ᴇx: <code>OWNER</code>\n{FOOTER()}</blockquote>", parse_mode="HTML"); return True
    if txt == "🎯 ᴄʜᴀɴɢᴇ ᴛᴀɢʟɪɴᴇ":
        _admin_states[uid] = {"action":"branding","field":"bot_tagline"}
        bot.reply_to(m, f"<blockquote>🎯 ɴᴀʏɪ ᴛᴀɢʟɪɴᴇ ʙʜᴇᴊ\n{FOOTER()}</blockquote>", parse_mode="HTML"); return True
    if txt == "👁 ᴩʀᴇᴠɪᴇᴡ ᴄᴜʀʀᴇɴᴛ":
        preview = format_welcome(uid, m.from_user.first_name or "User", get_credits(uid), m.from_user.username or "")
        bot.reply_to(m, preview, parse_mode="HTML"); return True
    if txt == "🔄 ʀᴇꜱᴇᴛ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ":
        for k, v in DEFAULTS.items():
            if k not in ("admin_alert", "global_bcast", "global_bcast_time"):
                set_setting(k, v)
        bot.reply_to(m, f"<blockquote>🔄 ᴅᴇꜰᴀᴜʟᴛ ᴩᴇ ʀᴇꜱᴇᴛ\n{FOOTER()}</blockquote>", reply_markup=kb_branding(), parse_mode="HTML"); return True
    if txt == "⬅️ ʙᴀᴄᴋ ᴛᴏ ᴀᴅᴍɪɴ":
        user_state[uid] = S_NONE; _admin_states.pop(uid, None)
        bot.reply_to(m, card_wrap("ᴀᴅᴍɪɴ", "▸ ʙᴀᴄᴋ"), reply_markup=kb_admin(), parse_mode="HTML"); return True
    if txt == "🔗 ᴀᴘɪ ᴜʀʟꜱ":
        mk = InlineKeyboardMarkup(row_width=1)
        for key, label, _ in _BOT_APIS:
            custom = _get_custom_api_url(key)
            icon = "✏️" if custom else "🗂️"
            mk.add(_IKB(f"{icon} {label}", style="primary", callback_data=f"apiurl_sel_{key}"))
        mk.add(_IKB("🔙 ʙᴀᴄᴋ", style="danger", callback_data="apiurl_back"))
        bot.reply_to(m, f"<blockquote>{SEP}\n🔗 <b>ᴀᴘɪ ᴜʀʟꜱ</b>\n{SEP}\n\n💡 ᴄʜᴀɴɢᴇ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ ꜱᴇʟᴇᴄᴛ\n{FOOTER()}</blockquote>",
                    reply_markup=mk, parse_mode="HTML"); return True
    if txt == "🔑 ᴀᴘɪ ᴋᴇʏꜱ":
        mk = InlineKeyboardMarkup(row_width=1)
        for k_name, label, _ in _BOT_API_KEYS:
            custom = _get_custom_api_key(k_name)
            icon = "✏️" if custom else "🗂️"
            mk.add(_IKB(f"{icon} {label}", style="primary", callback_data=f"apikey_sel_{k_name}"))
        mk.add(_IKB("🔙 ʙᴀᴄᴋ", style="danger", callback_data="apikey_back"))
        bot.reply_to(m, f"<blockquote>{SEP}\n🔑 <b>ᴀᴘɪ ᴋᴇʏꜱ</b>\n{SEP}\n\n💡 ꜱᴇʟᴇᴄᴛ ᴛᴏ ᴄʜᴀɴɢᴇ\n{FOOTER()}</blockquote>",
                    reply_markup=mk, parse_mode="HTML"); return True
    if txt == "👋 ᴡᴇʟᴄᴏᴍᴇ ꜱᴇᴛ":
        info = get_welcome_media_info()
        v = info["video"]; i = info["image"]
        if v["set"] and v["exists"]:
            try:
                with open(v["path"], "rb") as f:
                    bot.send_video(uid, f, caption=f"🎥 ᴄᴜʀʀᴇɴᴛ ▸ {_fmt_size(v['size'])}", parse_mode="HTML")
            except: pass
        if i["set"] and i["exists"]:
            try:
                with open(i["path"], "rb") as f:
                    bot.send_photo(uid, f, caption=f"🖼 ᴄᴜʀʀᴇɴᴛ ▸ {_fmt_size(i['size'])}", parse_mode="HTML")
            except: pass
        bot.send_message(uid, _welcome_panel_text(), reply_markup=_welcome_kb_preview_mode(), parse_mode="HTML")
        return True
    if txt == "🎪 ꜱᴛɪᴄᴋᴇʀ ꜱᴇᴛ":
        _admin_states[uid] = "set_sticker"
        bot.reply_to(m, card_wrap("ꜱᴛɪᴄᴋᴇʀ", "▸ ᴋᴏɪ ʙʜɪ ꜱᴛɪᴄᴋᴇʀ ʙʜᴇᴊᴏ"), parse_mode="HTML"); return True
    if txt == "🎫 ɢᴇɴ ʀᴇᴅᴇᴇᴍ":
        code = _generate_credit_code()
        _admin_states[uid] = {"action":"redeem_create","code":code}
        bot.reply_to(m, f"<blockquote>{SEP}\n🎫 <b>ɢᴇɴ ʀᴇᴅᴇᴇᴍ</b>\n{SEP}\n\n🎫 ᴄᴏᴅᴇ: <code>{code}</code>\n\n"
                        f"📤 ᴀʙ ʙʜᴇᴊᴏ: <code>credits limit</code>\n▸ ᴇx: <code>10 50</code>\n\n{FOOTER()}</blockquote>",
                    parse_mode="HTML"); return True
    if txt == "🎁 ᴄᴏᴅᴇ ʟɪꜱᴛ":
        c.execute("SELECT code,credits,redeem_limit,used_count FROM redeem_codes ORDER BY id DESC LIMIT 20")
        rows = c.fetchall(); body = section("ᴄʀᴇᴅɪᴛ ᴄᴏᴅᴇꜱ") + "\n"
        for r in rows: body += f"├ <code>{r[0]}</code> ▸ {r[1]}ᴄ ▸ {r[3]}/{r[2] or '∞'}\n"
        if not rows: body += "└ (ᴇᴍᴩᴛʏ)\n"
        body += "\n" + section("ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇꜱ") + "\n"
        c.execute("SELECT code,days,redeem_limit,used_count FROM premium_codes ORDER BY id DESC LIMIT 10")
        rows2 = c.fetchall()
        for r in rows2: body += f"├ <code>{r[0]}</code> ▸ {r[1]}ᴅ ▸ {r[3]}/{r[2] or '∞'}\n"
        if not rows2: body += "└ (ᴇᴍᴩᴛʏ)\n"
        bot.reply_to(m, card_wrap("ᴄᴏᴅᴇ ʟɪꜱᴛ", body), parse_mode="HTML"); return True
    if txt == "💎 ɢᴇɴ ᴘʀᴇᴍɪᴜᴍ":
        code = _generate_premium_code()
        _admin_states[uid] = {"action":"premium_create","code":code}
        bot.reply_to(m, f"<blockquote>{SEP}\n💎 <b>ɢᴇɴ ᴘʀᴇᴍɪᴜᴍ</b>\n{SEP}\n\n🎫 ᴄᴏᴅᴇ: <code>{code}</code>\n\n"
                        f"📤 ᴀʙ ʙʜᴇᴊᴏ: <code>days limit</code>\n▸ ᴇx: <code>30 1</code>\n\n{FOOTER()}</blockquote>",
                    parse_mode="HTML"); return True
    if txt == "💰 ᴀᴅᴅ ᴄʀᴇᴅɪᴛꜱ":
        _admin_states[uid] = "addcredits"
        bot.reply_to(m, card_wrap("ᴀᴅᴅ ᴄʀ", "▸ ꜱᴇɴᴅ: <code>uid amount</code>"), parse_mode="HTML"); return True
    if txt == "➖ ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛꜱ":
        _admin_states[uid] = "remcredits"
        bot.reply_to(m, card_wrap("ʀᴇᴍ ᴄʀ", "▸ ꜱᴇɴᴅ: <code>uid amount</code>"), parse_mode="HTML"); return True
    if txt == "💎 ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ":
        _admin_states[uid] = "addpremium"
        bot.reply_to(m, card_wrap("ᴀᴅᴅ ᴩʀ", "▸ ꜱᴇɴᴅ: <code>uid days</code>"), parse_mode="HTML"); return True
    if txt == "💀 ʀᴇᴠᴏᴋᴇ ᴘʀᴇᴍɪᴜᴍ":
        c.execute("UPDATE users SET is_premium=0,premium_until=NULL")
        c.execute("DELETE FROM premium_codes"); c.execute("DELETE FROM redeemed_premium")
        conn.commit()
        bot.reply_to(m, card_wrap("ʀᴇᴠᴏᴋᴇᴅ", "▸ ꜱᴀʙ ᴘʀᴇᴍɪᴜᴍ ʀᴇᴠᴏᴋᴇᴅ"), parse_mode="HTML"); return True
    if txt == "🚫 ʙʟᴏᴄᴋ ᴜꜱᴇʀ":
        _admin_states[uid] = "block"
        bot.reply_to(m, card_wrap("ʙʟᴏᴄᴋ", "▸ ꜱᴇɴᴅ ᴜꜱᴇʀ ɪᴅ"), parse_mode="HTML"); return True
    if txt == "✅ ᴜɴʙʟᴏᴄᴋ ᴜꜱᴇʀ":
        _admin_states[uid] = "unblock"
        bot.reply_to(m, card_wrap("ᴜɴʙʟᴏᴄᴋ", "▸ ꜱᴇɴᴅ ᴜꜱᴇʀ ɪᴅ"), parse_mode="HTML"); return True
    if txt == "🔒 ᴘʀᴏᴛᴇᴄᴛ ᴜꜱᴇʀ":
        _admin_states[uid] = "protect"
        bot.reply_to(m, card_wrap("ᴘʀᴏᴛᴇᴄᴛ", "▸ ꜱᴇɴᴅ ɪᴅ/@ᴜɴ/ɴᴜᴍ"), parse_mode="HTML"); return True
    if txt == "🧹 ᴄʟᴇᴀʀ ʜɪꜱᴛᴏʀʏ":
        c.execute("DELETE FROM search_history"); conn.commit()
        bot.reply_to(m, card_wrap("ᴄʟᴇᴀʀ", "▸ ʜɪꜱᴛᴏʀʏ ᴄʟᴇᴀʀᴇᴅ"), parse_mode="HTML"); return True
    return False

# BROADCAST (simple)
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and _admin_states.get(m.from_user.id) == "broadcast",
                     content_types=["text","photo","video","document","animation","sticker"])
def do_broadcast(m):
    _admin_states.pop(m.from_user.id, None)
    c.execute("SELECT user_id FROM users WHERE is_blocked=0"); users = [r[0] for r in c.fetchall()]
    c.execute("SELECT group_id FROM groups WHERE is_blocked=0"); groups = [r[0] for r in c.fetchall()]
    sent = fail = 0
    sm = bot.reply_to(m, card_wrap("ʙʀᴏᴀᴅᴄᴀꜱᴛ", f"▸ ꜱᴇɴᴅɪɴɢ... {len(users)+len(groups)}"), parse_mode="HTML")
    for target in users + groups:
        try: bot.copy_message(target, m.chat.id, m.message_id); sent += 1
        except: fail += 1
        time.sleep(0.04)
    try: bot.edit_message_text(card_wrap("ᴅᴏɴᴇ", f"▸ ꜱᴇɴᴛ ▸ {sent}\n▸ ꜰᴀɪʟ ▸ {fail}"), sm.chat.id, sm.message_id, parse_mode="HTML")
    except: pass

# GLOBAL BROADCAST (also handles content types)
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and _admin_states.get(m.from_user.id) == "global_bcast",
                     content_types=["text","photo","video","document","animation","sticker"])
def do_global_bcast_content(m):
    # Save text
    try:
        txt_content = m.text or m.caption or ""
        if txt_content:
            set_setting("global_bcast", _html.escape(txt_content)[:3000])
            set_setting("global_bcast_time", datetime.now().strftime("%d %b %Y • %I:%M %p"))
    except: pass
    threading.Thread(target=do_global_broadcast, args=(m, m.from_user.id), daemon=True).start()

# STICKER
@bot.message_handler(content_types=["sticker"], func=lambda m: is_admin(m.from_user.id) and _admin_states.get(m.from_user.id) == "set_sticker")
def on_set_sticker(m):
    _admin_states.pop(m.from_user.id, None)
    c.execute("UPDATE welcome_settings SET first_time_sticker=? WHERE id=1", (m.sticker.file_id,))
    conn.commit()
    bot.reply_to(m, card_wrap("ꜱᴛɪᴄᴋᴇʀ", "▸ ɴᴀʏᴀ ꜱᴛɪᴄᴋᴇʀ ʟᴀɢᴀ"), parse_mode="HTML")

# WELCOME MEDIA
@bot.message_handler(content_types=["video"], func=lambda m: is_admin(m.from_user.id) and user_state.get(m.from_user.id) == "ADMIN_WELCOME")
def handle_welcome_video(m):
    uid = m.from_user.id
    c.execute("SELECT welcome_video FROM welcome_settings WHERE id=1")
    r = c.fetchone()
    if r and r[0]: _delete_old_welcome_file(r[0])
    try:
        fi = bot.get_file(m.video.file_id); data = bot.download_file(fi.file_path)
        fn = os.path.join(_SCRIPT_DIR, f"wvid_{_BOT_ID}_{int(time.time())}.mp4")
        with open(fn, "wb") as f: f.write(data)
        c.execute("UPDATE welcome_settings SET welcome_video=? WHERE id=1", (fn,))
        conn.commit(); _wel_fileid_cache.pop("video", None)
        bot.reply_to(m, f"<blockquote>✅ ᴠɪᴅᴇᴏ ᴜᴘᴅᴀᴛᴇᴅ ▸ {_fmt_size(os.path.getsize(fn))}\n{FOOTER()}</blockquote>", parse_mode="HTML")
        bot.send_message(uid, _welcome_panel_text(), reply_markup=_welcome_kb_preview_mode(), parse_mode="HTML")
    except Exception as e: bot.reply_to(m, f"<blockquote>☠ {str(e)[:100]}</blockquote>", parse_mode="HTML")
    user_state[uid] = S_NONE

@bot.message_handler(content_types=["photo"], func=lambda m: is_admin(m.from_user.id) and user_state.get(m.from_user.id) == "ADMIN_WELCOME")
def handle_welcome_image(m):
    uid = m.from_user.id
    c.execute("SELECT welcome_image FROM welcome_settings WHERE id=1")
    r = c.fetchone()
    if r and r[0]: _delete_old_welcome_file(r[0])
    try:
        fi = bot.get_file(m.photo[-1].file_id); data = bot.download_file(fi.file_path)
        fn = os.path.join(_SCRIPT_DIR, f"wimg_{_BOT_ID}_{int(time.time())}.jpg")
        with open(fn, "wb") as f: f.write(data)
        c.execute("UPDATE welcome_settings SET welcome_image=? WHERE id=1", (fn,))
        conn.commit(); _wel_fileid_cache.pop("image", None)
        bot.reply_to(m, f"<blockquote>✅ ɪᴍᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ ▸ {_fmt_size(os.path.getsize(fn))}\n{FOOTER()}</blockquote>", parse_mode="HTML")
        bot.send_message(uid, _welcome_panel_text(), reply_markup=_welcome_kb_preview_mode(), parse_mode="HTML")
    except Exception as e: bot.reply_to(m, f"<blockquote>☠ {str(e)[:100]}</blockquote>", parse_mode="HTML")
    user_state[uid] = S_NONE

# ═══════════════ PRIVATE ROUTER ═══════════════
@bot.message_handler(func=lambda m: m.chat.type == "private" and m.text and not m.text.startswith("/"))
def private_router(m):
    uid = m.from_user.id; txt = m.text.strip(); st = user_state.get(uid, S_NONE)
    if is_identifier_blocked(str(uid)): return

    if is_admin(uid) and uid in _admin_states:
        if _admin_router(m, txt): return
    if is_admin(uid) and txt == "⚙️ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ":
        bot.send_message(uid, card_wrap("ᴀᴅᴍɪɴ", "▸ ᴩᴀɴᴇʟ"), reply_markup=kb_admin(), parse_mode="HTML"); return
    if is_admin(uid) and _admin_router(m, txt): return

    if st == S_NONE:
        if re.match(r"^[6-9]\d{9}$", txt) and is_feature_enabled("number"):
            if not get_user(uid): add_user(uid, m.from_user.username or "", m.from_user.first_name or "")
            _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_NUM, txt, m); return
        if re.match(r"^@[a-zA-Z0-9_.]{5,}$", txt) and is_feature_enabled("username"):
            if not get_user(uid): add_user(uid, m.from_user.username or "", m.from_user.first_name or "")
            _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_USER, txt, m); return

    if st == S_NUM:
        num = re.sub(r"\D","",txt)
        if len(num) == 12 and num.startswith("91"): num = num[2:]
        if re.match(r"^[6-9]\d{9}$", num): _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_NUM, num, m)
    elif st == S_USER:
        if txt.startswith("@") and len(txt) > 1: _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_USER, txt, m)
        elif txt.lstrip("-").isdigit(): _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_TID, re.sub(r"\D","",txt), m)
    elif st == S_TID:
        if txt.lstrip("-").isdigit(): _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_TID, re.sub(r"\D","",txt), m)
    elif st == S_ADH:
        a = re.sub(r"\D","",txt)
        if len(a) == 12: _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_ADH, a, m)
    elif st == S_INSTA:
        u = txt.replace("@","").strip()
        if re.match(r"^[a-zA-Z0-9_.]{1,30}$", u): _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_INSTA, u, m)
    elif st == S_FF:
        u = re.sub(r"\D","",txt)
        if len(u) >= 5: _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_FF, u, m)
    elif st == S_FFLIKE:
        u = re.sub(r"\D","",txt)
        if len(u) >= 5: _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_FFLIKE, u, m)
    elif st == S_VEH:
        rc = txt.upper().replace(" ","")
        if re.match(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$", rc):
            _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_VEH, rc, m)
    elif st == S_BOMB:
        n = re.sub(r"\D","",txt)
        if len(n) == 12 and n.startswith("91"): n = n[2:]
        if re.match(r"^[6-9]\d{9}$", n): _do_search(uid, m.from_user.username or "", m.from_user.first_name or "", S_BOMB, n, m)
    elif st == S_REDEEM:
        user_state[uid] = S_NONE
        ok, msg = _do_redeem_credit(uid, txt)
        if ok:
            u = get_user(uid); cr = u[5] if u else 0
            bot.reply_to(m, card_wrap("✅ ʀᴇᴅᴇᴇᴍ", f"{section('ᴀᴅᴅᴇᴅ')}\n{msg}", cr), parse_mode="HTML")
        else: bot.reply_to(m, card_wrap("☠ ꜰᴀɪʟ", f"{section('ᴇʀʀᴏʀ')}\n▸ {msg}"), parse_mode="HTML")
    elif st == S_PREM:
        user_state[uid] = S_NONE
        ok, msg = _do_redeem_premium(uid, txt)
        if ok: bot.reply_to(m, card_wrap("💎 ᴀᴄᴛɪᴠᴇ", f"{section('ᴏᴋ')}\n{msg}"), parse_mode="HTML")
        else: bot.reply_to(m, card_wrap("☠ ꜰᴀɪʟ", f"{section('ᴇʀʀᴏʀ')}\n▸ {msg}"), parse_mode="HTML")

# ═══════════════ CHANNEL CMDS ═══════════════
@bot.message_handler(commands=["addchannel"])
def cmd_addchannel(m):
    if not is_admin(m.from_user.id): return
    parts = m.text.split()
    if len(parts) < 2: return
    lnk = parts[1]
    if not (lnk.startswith("https://t.me/") or lnk.startswith("@")): return
    cid_str = lnk; title = "Channel"
    try:
        if lnk.startswith("@"):
            try: ch = bot.get_chat(lnk); cid_str = str(ch.id); title = ch.title or lnk
            except: cid_str = lnk
        elif "+" not in lnk:
            u = lnk.split("t.me/")[1].strip("/")
            try: ch = bot.get_chat(f"@{u}"); cid_str = str(ch.id); title = ch.title or u
            except: cid_str = f"@{u}"; title = u
    except: pass
    url_val = lnk if lnk.startswith("http") else f"https://t.me/{lnk.lstrip('@')}"
    c.execute("INSERT OR REPLACE INTO force_join_channels(chat_id,chat_title,chat_url,added_by,added_date,is_active) VALUES(?,?,?,?,?,1)",
              (cid_str, title, url_val, m.from_user.id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    bot.reply_to(m, card_wrap("ᴀᴅᴅᴇᴅ", f"▸ {title}\n▸ <code>{cid_str}</code>"), parse_mode="HTML")

@bot.message_handler(commands=["removechannel"])
def cmd_removechannel(m):
    if not is_admin(m.from_user.id): return
    parts = m.text.split()
    if len(parts) < 2: return
    c.execute("UPDATE force_join_channels SET is_active=0 WHERE chat_id=?", (parts[1],)); conn.commit()
    bot.reply_to(m, card_wrap("ʀᴇᴍᴏᴠᴇᴅ", f"▸ {parts[1]}"), parse_mode="HTML")

# ═══════════════ CALLBACKS ═══════════════
@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("nalert_") and is_admin(c.from_user.id))
def cb_nalert(call):
    """New user alert inline buttons"""
    uid_admin = call.from_user.id; d = call.data
    try:
        parts = d.split("_")
        action = parts[1]; target_uid = int(parts[2])
    except:
        bot.answer_callback_query(call.id); return

    if action == "block":
        c.execute("INSERT OR REPLACE INTO blocked_identifiers(identifier,identifier_type,blocked_by,blocked_date,reason) VALUES(?,?,?,?,?)",
                  (str(target_uid), "user_id", uid_admin, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "new-user-alert"))
        try: c.execute("UPDATE users SET is_blocked=1 WHERE user_id=?", (target_uid,))
        except: pass
        conn.commit()
        bot.answer_callback_query(call.id, f"✅ {target_uid} ʙʟᴏᴄᴋᴇᴅ")
        try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except: pass
        return

    if action == "credits":
        try:
            amt = int(parts[3])
            c.execute("UPDATE users SET credits=credits+? WHERE user_id=?", (amt, target_uid))
            conn.commit(); _caches["users"].pop(target_uid, None)
            bot.answer_callback_query(call.id, f"✅ +{amt} ᴄʀᴇᴅɪᴛꜱ")
            try:
                bot.send_message(target_uid,
                    f"<blockquote>{SEP}\n🎁 <b>ʙᴏɴᴜꜱ ᴄʀᴇᴅɪᴛꜱ!</b>\n{SEP}\n\n"
                    f"▸ ᴀᴅᴍɪɴ ɴᴇ ᴛᴜᴊʜᴇ <b>+{amt} ᴄʀᴇᴅɪᴛꜱ</b> ᴅɪʏᴇ\n\n{FOOTER()}</blockquote>",
                    parse_mode="HTML")
            except: pass
        except: pass
        return

    if action == "prem":
        try:
            days = int(parts[3])
            until = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE users SET is_premium=1,premium_until=? WHERE user_id=?", (until, target_uid))
            conn.commit(); _caches["users"].pop(target_uid, None)
            bot.answer_callback_query(call.id, f"✅ ᴘʀᴇᴍɪᴜᴍ {days}ᴅ")
            try:
                bot.send_message(target_uid,
                    f"<blockquote>{SEP}\n💎 <b>ᴘʀᴇᴍɪᴜᴍ!</b>\n{SEP}\n\n"
                    f"▸ ᴀᴅᴍɪɴ ɴᴇ ᴛᴜᴊʜᴇ <b>{days} ᴅᴀʏꜱ ᴘʀᴇᴍɪᴜᴍ</b> ᴅɪʏᴀ\n"
                    f"▸ ᴠᴀʟɪᴅ ᴛɪʟʟ: <code>{until}</code>\n\n{FOOTER()}</blockquote>",
                    parse_mode="HTML")
            except: pass
        except: pass
        return

    if action == "del":
        try:
            c.execute("UPDATE users SET is_blocked=1 WHERE user_id=?", (target_uid,)); conn.commit()
            bot.answer_callback_query(call.id, f"✅ ᴅᴇʟᴇᴛᴇᴅ")
            try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            except: pass
        except: pass
        return
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("apiurl_") and is_admin(c.from_user.id))
def cb_apiurl(call):
    uid = call.from_user.id; d = call.data
    if d == "apiurl_back":
        bot.answer_callback_query(call.id)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(uid, card_wrap("ᴀᴅᴍɪɴ", "▸ ʙᴀᴄᴋ"), reply_markup=kb_admin(), parse_mode="HTML"); return
    if d.startswith("apiurl_sel_"):
        key = d[len("apiurl_sel_"):]
        info = next((a for a in _BOT_APIS if a[0] == key), None)
        if not info: bot.answer_callback_query(call.id, "❌"); return
        _, label, default_url = info
        custom = _get_custom_api_url(key)
        current = custom if custom else default_url
        source = "✏️ ᴄᴜꜱᴛᴏᴍ" if custom else "🗂️ ᴅᴇꜰᴀᴜʟᴛ"
        txt = (f"<blockquote>{SEP}\n🔗 <b>{label}</b>\n{SEP}\n\n"
               f"├ ᴋᴇʏ ▸ <code>{key}</code>\n├ ꜱᴏᴜʀᴄᴇ ▸ {source}\n\n"
               f"📎 <b>ᴄᴜʀʀᴇɴᴛ:</b>\n<code>{current}</code>\n\n"
               f"💡 {{}} ᴢᴀʀᴜʀɪ ʜᴀɪ\n{FOOTER()}</blockquote>")
        mk = InlineKeyboardMarkup(row_width=1)
        mk.add(_IKB("✏️ ᴄʜᴀɴɢᴇ ᴜʀʟ", style="success", icon_custom_emoji_id="5341715473882955310", callback_data=f"apiurl_change_{key}"))
        if custom: mk.add(_IKB("🗑️ ʀᴇꜱᴇᴛ", style="danger", icon_custom_emoji_id="5471937446368975982", callback_data=f"apiurl_reset_{key}"))
        mk.add(_IKB("⬅️ ʙᴀᴄᴋ", style="primary", callback_data="apiurl_list"))
        try: bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=mk, parse_mode="HTML")
        except: bot.send_message(uid, txt, reply_markup=mk, parse_mode="HTML")
        bot.answer_callback_query(call.id); return
    if d == "apiurl_list":
        bot.answer_callback_query(call.id)
        mk = InlineKeyboardMarkup(row_width=1)
        for key, label, _ in _BOT_APIS:
            custom = _get_custom_api_url(key); icon = "✏️" if custom else "🗂️"
            mk.add(_IKB(f"{icon} {label}", style="primary", callback_data=f"apiurl_sel_{key}"))
        mk.add(_IKB("🔙 ʙᴀᴄᴋ", style="danger", callback_data="apiurl_back"))
        try: bot.edit_message_text(f"<blockquote>🔗 ᴀᴘɪ ᴜʀʟꜱ\n\n💡 ꜱᴇʟᴇᴄᴛ\n{FOOTER()}</blockquote>",
                                    call.message.chat.id, call.message.message_id, reply_markup=mk, parse_mode="HTML")
        except: pass
        return
    if d.startswith("apiurl_change_"):
        key = d[len("apiurl_change_"):]
        info = next((a for a in _BOT_APIS if a[0] == key), None)
        if not info: bot.answer_callback_query(call.id, "❌"); return
        _, label, _ = info
        _admin_states[uid] = {"action": "apiurl_input", "key": key, "label": label}
        bot.answer_callback_query(call.id, "✏️ ʙʜᴇᴊ")
        bot.send_message(uid, f"<blockquote>✏️ <b>{label}</b>\n\n▸ ɴᴀʏᴀ ᴜʀʟ ʙʜᴇᴊ\n▸ {{}} ᴢᴀʀᴜʀɪ\n\n{FOOTER()}</blockquote>", parse_mode="HTML")
        return
    if d.startswith("apiurl_reset_"):
        key = d[len("apiurl_reset_"):]
        _reset_api(key); bot.answer_callback_query(call.id, "✅ ʀᴇꜱᴇᴛ"); return
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("apikey_") and is_admin(c.from_user.id))
def cb_apikey(call):
    uid = call.from_user.id; d = call.data
    if d == "apikey_back":
        bot.answer_callback_query(call.id)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(uid, card_wrap("ᴀᴅᴍɪɴ", "▸ ʙᴀᴄᴋ"), reply_markup=kb_admin(), parse_mode="HTML"); return
    if d.startswith("apikey_sel_"):
        k_name = d[len("apikey_sel_"):]
        info = next((k for k in _BOT_API_KEYS if k[0] == k_name), None)
        if not info: bot.answer_callback_query(call.id, "❌"); return
        _, label, default_key = info
        custom = _get_custom_api_key(k_name); current = custom if custom else default_key
        source = "✏️ ᴄᴜꜱᴛᴏᴍ" if custom else "🗂️ ᴅᴇꜰᴀᴜʟᴛ"
        masked = current[:5] + "•" * (len(current) - 9) + current[-4:] if len(current) > 12 else current
        txt = (f"<blockquote>{SEP}\n🔑 <b>{label}</b>\n{SEP}\n\n"
               f"├ ᴋᴇʏ ▸ <code>{k_name}</code>\n├ ꜱᴏᴜʀᴄᴇ ▸ {source}\n\n"
               f"🔑 <b>ᴄᴜʀʀᴇɴᴛ:</b>\n<code>{masked}</code>\n\n{FOOTER()}</blockquote>")
        mk = InlineKeyboardMarkup(row_width=1)
        mk.add(_IKB("✏️ ᴄʜᴀɴɢᴇ", style="success", icon_custom_emoji_id="5341715473882955310", callback_data=f"apikey_change_{k_name}"))
        if custom: mk.add(_IKB("🗑️ ʀᴇꜱᴇᴛ", style="danger", icon_custom_emoji_id="5471937446368975982", callback_data=f"apikey_reset_{k_name}"))
        mk.add(_IKB("⬅️ ʙᴀᴄᴋ", style="primary", callback_data="apikey_list"))
        try: bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=mk, parse_mode="HTML")
        except: bot.send_message(uid, txt, reply_markup=mk, parse_mode="HTML")
        bot.answer_callback_query(call.id); return
    if d == "apikey_list":
        bot.answer_callback_query(call.id)
        mk = InlineKeyboardMarkup(row_width=1)
        for k_name, label, _ in _BOT_API_KEYS:
            custom = _get_custom_api_key(k_name); icon = "✏️" if custom else "🗂️"
            mk.add(_IKB(f"{icon} {label}", style="primary", callback_data=f"apikey_sel_{k_name}"))
        mk.add(_IKB("🔙 ʙᴀᴄᴋ", style="danger", callback_data="apikey_back"))
        try: bot.edit_message_text(f"<blockquote>🔑 ᴋᴇʏꜱ\n\n💡 ꜱᴇʟᴇᴄᴛ\n{FOOTER()}</blockquote>",
                                    call.message.chat.id, call.message.message_id, reply_markup=mk, parse_mode="HTML")
        except: pass
        return
    if d.startswith("apikey_change_"):
        k_name = d[len("apikey_change_"):]
        info = next((k for k in _BOT_API_KEYS if k[0] == k_name), None)
        if not info: bot.answer_callback_query(call.id, "❌"); return
        _, label, _ = info
        _admin_states[uid] = {"action": "apikey_input", "key": k_name, "label": label}
        bot.answer_callback_query(call.id, "✏️ ʙʜᴇᴊ")
        bot.send_message(uid, f"<blockquote>✏️ <b>{label}</b>\n\n▸ ɴᴀʏɪ ᴋᴇʏ ʙʜᴇᴊ\n\n{FOOTER()}</blockquote>", parse_mode="HTML")
        return
    if d.startswith("apikey_reset_"):
        k_name = d[len("apikey_reset_"):]
        _reset_api(k_name); bot.answer_callback_query(call.id, "✅ ʀᴇꜱᴇᴛ"); return
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("wmedia_") and is_admin(c.from_user.id))
def cb_wmedia(call):
    uid = call.from_user.id; d = call.data
    if d == "wmedia_refresh":
        bot.answer_callback_query(call.id, "🔄")
        try: bot.edit_message_text(_welcome_panel_text(), call.message.chat.id, call.message.message_id,
                                   reply_markup=_welcome_kb_preview_mode(), parse_mode="HTML")
        except: pass
        return
    if d == "wmedia_back":
        bot.answer_callback_query(call.id)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(uid, card_wrap("ᴀᴅᴍɪɴ", "▸ ʙᴀᴄᴋ"), reply_markup=kb_admin(), parse_mode="HTML"); return
    if d == "wmedia_change_video":
        bot.answer_callback_query(call.id, "🎥 ʙʜᴇᴊ")
        user_state[uid] = "ADMIN_WELCOME"
        bot.send_message(uid, f"<blockquote>🎥 ᴠɪᴅᴇᴏ ʙʜᴇᴊ\n{FOOTER()}</blockquote>", parse_mode="HTML"); return
    if d == "wmedia_change_image":
        bot.answer_callback_query(call.id, "🖼 ʙʜᴇᴊ")
        user_state[uid] = "ADMIN_WELCOME"
        bot.send_message(uid, f"<blockquote>🖼 ɪᴍᴀɢᴇ ʙʜᴇᴊ\n{FOOTER()}</blockquote>", parse_mode="HTML"); return
    if d == "wmedia_del_video":
        bot.answer_callback_query(call.id, "🗑️")
        c.execute("SELECT welcome_video FROM welcome_settings WHERE id=1"); r = c.fetchone()
        if r and r[0]:
            _delete_old_welcome_file(r[0])
            c.execute("UPDATE welcome_settings SET welcome_video=NULL WHERE id=1"); conn.commit()
            _wel_fileid_cache.pop("video", None)
        try: bot.edit_message_text(_welcome_panel_text(), call.message.chat.id, call.message.message_id,
                                   reply_markup=_welcome_kb_preview_mode(), parse_mode="HTML")
        except: pass
        return
    if d == "wmedia_del_image":
        bot.answer_callback_query(call.id, "🗑️")
        c.execute("SELECT welcome_image FROM welcome_settings WHERE id=1"); r = c.fetchone()
        if r and r[0]:
            _delete_old_welcome_file(r[0])
            c.execute("UPDATE welcome_settings SET welcome_image=NULL WHERE id=1"); conn.commit()
            _wel_fileid_cache.pop("image", None)
        try: bot.edit_message_text(_welcome_panel_text(), call.message.chat.id, call.message.message_id,
                                   reply_markup=_welcome_kb_preview_mode(), parse_mode="HTML")
        except: pass
        return
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "verify_channels")
def cb_verify(call):
    uid = call.from_user.id
    if check_channels(uid):
        bot.answer_callback_query(call.id, "✔ ᴠᴇʀɪꜰɪᴇᴅ")
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        if not get_user(uid):
            add_user(uid, call.from_user.username or "", call.from_user.first_name or "")
            threading.Thread(target=notify_admin_new_user,
                             args=(uid, call.from_user.username or "", call.from_user.first_name or "", True, None),
                             daemon=True).start()
        cr = get_credits(uid)
        full_txt = format_welcome(uid, call.from_user.first_name or "User", cr, call.from_user.username or "")
        plain_cap = _welcome_plain_caption(uid, call.from_user.first_name or "User", cr, call.from_user.username or "")
        kb = kb_main(uid)
        c.execute("SELECT welcome_video,welcome_image,first_time_sticker FROM welcome_settings WHERE id=1")
        wrow = c.fetchone() or (None, None, None)
        wvid, wimg, stk = wrow
        sent = False
        if stk:
            try: bot.send_sticker(uid, stk)
            except: pass
        if wvid and os.path.exists(wvid):
            try:
                with open(wvid, "rb") as f:
                    bot.send_video(uid, f, caption=plain_cap, parse_mode="HTML", reply_markup=kb); sent = True
            except: pass
        if not sent and wimg and os.path.exists(wimg):
            try:
                with open(wimg, "rb") as f:
                    bot.send_photo(uid, f, caption=plain_cap, parse_mode="HTML", reply_markup=kb); sent = True
            except: pass
        if not sent:
            try: bot.send_message(uid, full_txt, reply_markup=kb, parse_mode="HTML")
            except: pass
    else:
        bot.answer_callback_query(call.id, "⚠ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ꜰɪʀꜱᴛ")
        mk = channels_kb(uid)
        if mk:
            try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=mk)
            except: pass

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("ftog_") and is_admin(c.from_user.id))
def cb_ftog(call):
    fn = call.data[5:]
    valid = {"number","username","tgid","aadhar","instagram","freefire","freefire_like","vehicle","bomber"}
    if fn not in valid: bot.answer_callback_query(call.id, "❌"); return
    new = toggle_feature(fn, call.from_user.id)
    bot.answer_callback_query(call.id, f"{fn} ▸ {'✔' if new else '✘'}")
    try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb_features_inline())
    except: pass

# ═══════════════ MAIN ═══════════════
if __name__ == "__main__":
    print("╔══════════════════════════════════════╗")
    print("║       RODIX HACKER BOT v4.1          ║")
    print("╚══════════════════════════════════════╝")
    print(f"  Owner ID:      {OWNER_ID}")
    print(f"  Log Channel:   {LOG_CHANNEL_ID}")
    print(f"  Bot Name:      {BOT_NAME()}")
    print(f"  Bot Username:  @{BOT_USERNAME()}")
    print(f"  Dev Label:     {get_setting('dev_label')}")
    print(f"  Alert Status:  {'ON' if get_setting('admin_alert','1')=='1' else 'OFF'}")
    try: bot.remove_webhook()
    except: pass
    time.sleep(0.5)
    while True:
        try:
            print("⚡ ʀᴏᴅɪx ʜᴀᴄᴋᴇʀ ᴏɴʟɪɴᴇ")
            bot.infinity_polling(timeout=30, long_polling_timeout=30,
                allowed_updates=["message","edited_message","callback_query","chat_member","my_chat_member"])
        except KeyboardInterrupt:
            print("ꜱʜᴜᴛᴅᴏᴡɴ"); break
        except Exception as e:
            print(f"ᴇʀʀᴏʀ: {e}"); time.sleep(5)