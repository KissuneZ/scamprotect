import discord
import os
import pathlib
import asyncio
import json
import sys
import requests
import logging
import datetime
import shutil
import atexit
import subprocess
import shlex
from langs import languages

__version__ = "7.1.0"

info    = "<:info:863711569975967745>"
danger  = "<:danger:862303667465093140>"
vmark   = "<:vmark:862306691643342869>"
xmark   = "<:xmark:862308439136403488>"
waiting = "<a:waiting:868094543524937749>"

PRIMARY   = 0x8080ff
SECONDARY = 0xff6060

connection    = requests.Session()
api_key        = "HGAjJHshJHSkJSBBDdD"
api_url        = f"http://f0575604.xsph.ru/api/server.php?token={api_key}&"
base_url       = "http://f0575604.xsph.ru"
prefixes       = {}
default_prefix = "~"
sessioncache   = {"sc": 0, "dmc": 0}
copyright      = "© 2021, Ezz Development"
log_pattern    = '[%(asctime)s] [%(name)s / %(levelname)s]: %(message)s'
offline_mode   = False
langkeys       = {}

support = "https://discord.gg/GpedR6jeZR"
hook = "https://discord.com/api/webhooks/888444735289696317/9Y8C-BlwF-27VdrZDvO3CLxFNlqqkh2S29lEQidTntudhSk3A-0ecPU0RxtVEViZZSM2"

logger = None
bot_   = discord.ext.commands.Bot(None)

commands_ = discord.ext.commands
manual_scanner_args = {"notify": False, "dm": False, "cid": None, "noscup": True, "delete": False, "allowfetch": False}


def lang(ctx):
	key = ctx.guild.id
	lang_key = get_lang_key(ctx, key)
	return languages[lang_key]


def get_lang_key(ctx, key):
	lk = langkeys.get(key)

	if not lk:
		db = db_read()
		lk = db["langs"].get(str(key))

		if not lk:
			lk = "ru"
			if str(ctx.guild.region) != "russia":
				lk = "en"
			db["langs"][str(key)] = lk
			db_write(db)

		langkeys[key] = lk
	return lk


def download_ext_db():
	db = api_interact("getdb")
	sw = api_interact("getSW")
	eb = api_interact("getEB")
	local_api("setdb", db)
	local_api("setSW", sw)
	local_api("setEB", eb)


def local_api(do, data=None):

	with open("offline.json", "r+") as f:
		if do == "getdb":
			return json.loads(f.read())
		elif do == "setdb":
			f.truncate()
			f.write(json.dumps(data))
			return

	with open("blcache.json") as f: 
		text = f.read()
		db = json.loads(text)

		if do == "getSW":
			return db["suspicious"]
		elif do == "getEB":
			return db["embed_blacklist"]

	with open("blcache.json", "w+") as f:
		if do == "setEB":
			db["embed_blacklist"] = data
		elif do == "setSW":
			db["suspicious"] = data
		
		f.write(json.dumps(db))


def connection_check():
	global offline_mode

	try:
		r = connection.get(base_url, timeout=10)
	except:
		offline_mode = True
		if logger:
			logger.warn("Switched to offline mode. [Request failed]")
		return False

	allowed_codes = [404, 403]
	if r.status_code not in allowed_codes:
		offline_mode = True
		if logger:
			logger.warn(f"Switched to offline mode. [Code: {r.status_code}]")
		return False

	if logger:
		logger.warn(f"Connection check passed. Response code: {r.status_code}")
	offline_mode = False
	return True


def read_config():
	with open("config.json", "r") as f:
		return json.loads(f.read())


def purge_scanners():
	path = "./scanners/"
	files = [f for f in os.listdir(path)]
	for file in files:
		try:
			os.remove(path + file)
		except:
			continue


def is_scanner_running(key):
	if os.path.isfile(f"./scanners/{key}.json"):
		return True
	return False


async def run_async_scanner(data, channels, ctx, glimit=None):
	sid = ctx.guild.id
	with open(f"./scanners/{sid}.json", "w+") as f:
		data.append([c.id for c in channels])
		data.append(data[2].channel.id)
		data[2] = data[2].id
		if glimit:
			data.append(glimit)
		cmd = shlex.split(f"python scanner.py {sid}")
		f.write(json.dumps(data))
	subprocess.Popen(cmd)


def api_interact(do, data=None):
	if offline_mode:
		return local_api(do, data)

	result   = None
	response = None
	data     = json.dumps(data)
	try:
		response = connection.get(f"{api_url}do={do}&data={data}", timeout=10)
	except Exception as e:
		logger.error(f"API connection failed: {e}. Request: `{do} {data}`.")
		connection_check()
	if response.text:
		try:
			result = json.loads(response.text)
		except Exception as e:
			logger.error(f"API response parsing failed: {e}. Request: `{do} {data}`. Response: `{response.text}`")
			connection_check()
	return result




def version():
	return __version__


async def determine_prefix(bot, message):
	key = message.guild.id
	return commands_.when_mentioned_or(*get_prefix(key))(bot, message)


def get_prefix(key):
	prefix = prefixes.get(key)
	if prefix:
		return prefix

	db = db_read()
	prefix = db["prefixes"].get(str(key))
	if prefix:
		prefixes[key] = prefix
		return prefix

	prefixes[key] = default_prefix
	return default_prefix


def set_prefix(key, prefix):
	prefixes.get(id)
	prefixes[key] = prefix
	db = db_read()
	db["prefixes"].update({key: prefix})
	db_write(db)


def prefix(ctx):
	return get_prefix(ctx.guild.id)




def get_session():
	with open("session.json", "r") as session:
		content = session.read()
	return json.loads(content)


def reset_session():
	with open("session.json", "w+") as f:
		f.write(json.dumps({"sc": 0, "dmc": 0}))


def update_session():
	with open("session.json", "w+") as f:
		f.write(json.dumps(sessioncache))


def get_remote_session():
	if offline_mode:
		return {"sc": 0, "dmc": 0}
	response = connection.get(f"{base_url}/session.json", timeout=10)
	return json.loads(response.text)


def get_global_session():
	external_session = get_remote_session()
	local_session    = get_session()

	local_sc  = local_session["sc"]
	local_dmc = local_session["dmc"]

	external_sc  = external_session["sc"]
	external_dmc = external_session["dmc"]
	
	sc  = external_sc  + local_sc
	dmc = external_dmc + local_dmc

	return {"sc": sc, "dmc": dmc}


def send_session():
	cache = get_global_session()
	api_interact("setSession", cache)
	reset_session()


def send_stats(data: dict):
	api_interact("setStats", data)
	send_session()




def getsc():
	data = get_global_session()
	return data["sc"]


def getdmc():
	data = get_global_session()
	return data["dmc"]


def sc_up():
	sc = sessioncache["sc"]
	sessioncache["sc"] += 1
	update_session()


def dmc_up():
	dmc = sessioncache["dmc"]
	sessioncache["dmc"] += 1
	update_session()


def db_read():
	return api_interact("getdb")


def db_write(data: dict):
	api_interact("setdb", data)


def fetch_scanner_arguments(key):
	db = db_read()
	dm = key not in db["nodms"]
	notify = key not in db["dontnotify"]
	disabled = key in db.get("disabled", False)
	cid = db["logchannels"].get(str(key))
	data = {"dm": dm, "notify": notify, "disabled": disabled, "cid": cid, "noscup": False, "delete": True, "allowfetch": True}
	return data


def get_suspicious_words():
	return api_interact("getSW")


def get_eb():
	return api_interact("getEB")


def set_eb(data: list):
	api_interact("setEB", data)


def archive_logs():
	if os.path.isfile("./logs/latest.log"):
		cdate = int(pathlib.Path('./logs/latest.log').stat().st_mtime)
		fname = str(datetime.datetime.fromtimestamp(cdate))
		fname = fname.replace("-", ".").replace(":", "-").replace(" ", "_")
		os.rename("./logs/latest.log", f"./logs/{fname}.log")


def init_scanner():
	global embed_blacklist, suspicious
	embed_blacklist = get_eb()
	suspicious = get_suspicious_words()


def init():
	global logger

	logging.basicConfig(filename="./logs/latest.log", filemode="a",
				    	format=log_pattern,
				    	level=logging.INFO)
	logger = logging.getLogger("Wolverine")


	connection_check()

	if not offline_mode:
		download_ext_db()

	purge_scanners()
	atexit.register(exit_handler)
	init_scanner()

	logger.info(f"Loaded Wolverine {__version__}.")


async def ai_scanner(message, **kwargs):
	score = 0.0
	text  = message.content.lower()

	for item in list(suspicious.items()):
		if item[0] in text:
			score += item[1]

	if score >= 1.0:
		score = round(score, 2)
		return await delete(message, score, 0, 1, lang(message)["r_msgtext"], **kwargs)


async def scan_message(message, **kwargs):
	if not kwargs["noscup"]:
		sc_up()

	if await ai_scanner(message, **kwargs):
		return True

	if not message.embeds and kwargs["allowfetch"]:
		await asyncio.sleep(1)
		message = await message.channel.fetch_message(message.id)

	indexx = 0
	for embed in message.embeds:
		if await check_embed(embed, message, indexx, **kwargs):
			return True
		indexx += 1


async def check_embed(embed, message, indexx, **kwargs):
	index = 0
	for elem in embed_blacklist:
		try:
			if elem in embed.title.lower() and elem != "":
				return await delete(message, index, indexx, 0, lang(message)["r_etitle"], **kwargs)
		except:
			pass
		try:
			if elem in embed.description.lower() and elem != "":
				return await delete(message, index, indexx, 0, lang(message)["r_edesc"], **kwargs)
		except:
			return False
		index += 1


async def delete(message, index, indexx, rindex, blkey, **kwargs):
	if not kwargs["delete"]:
		return True

	reason = lang(message)["reasons"][rindex].format(f"{blkey}: {[indexx]}: {index}")
	embed = discord.Embed(description=lang(message)["d_srv_pattern"].format(danger, message.author.mention, reason),
			       		  color=SECONDARY)
	embed_dm = discord.Embed(description=lang(message)["d_dm_pattern"].format(danger, message.content),
			       		     color=SECONDARY)
	embed_dm.set_footer(text=lang(message)["r_dm_pattern"].format(reason, message.guild.name), icon_url=message.guild.icon_url)
	try:
		await message.delete()
		if kwargs["notify"]:
			channel = message.channel
			if kwargs["cid"]:
				channels = message.guild.text_channels
				channel  = discord.utils.get(channels, id=kwargs["cid"])
			if not channel or not kwargs["cid"]:
				channel  = message.channel
			await channel.send(embed=embed)
		if kwargs["dm"]:
			await message.author.send(embed=embed_dm)
	except Exception as e:
		logger.error(e)
		return False

	dmc_up()
	logger.warn(f"Deleted message from {message.author}. Reason: {reason}. Message content:\n{message.content}")
	return True




def exit_handler():
	if not offline_mode:
		logger.info("Sending data before shutting down...")
		stats = {"guilds": len(bot_.guilds), "users": len(bot_.users)}
		send_stats(stats)

	logger.info("Process exited.")


async def is_restarted(bot):
	if os.path.isfile(".restarted"):
		with open(".restarted", "r") as f:
			data: int = f.read().split(":")
			channel = bot.get_channel(int(data[0]))
			msg = await channel.fetch_message(int(data[1]))
			await msg.edit(content=lang(msg)["restarted"].format(vmark))
		os.remove(".restarted")


async def auto_restart(bot):
	uptime = 0
	while True:
		if uptime >= 240:
			logger.info("Restarting...")
			await bot.change_presence(status=discord.Status.idle,
								  	  activity=discord.Activity(name="Перезапуск...",
								  	  type=discord.ActivityType.watching))
			exit_handler()
			python = sys.executable
			os.execl(python, python, *sys.argv)
		await asyncio.sleep(60)
		uptime += 1



async def done(ctx, message):
	return await ctx.send(f"{vmark} {message}")


async def fail(ctx, message):
	return await ctx.send(f"{xmark} {message}")


async def logout(bot):
	atexit.unregister(exit_handler)
	await bot.close()
	exit(0)


async def presence_loop(bot):
	global bot_
	bot_ = bot

	while True:
		stats = {"guilds": len(bot.guilds), "users": len(bot.users)}
		send_stats(stats)

		status   = discord.Status.online
		presence = f"{default_prefix}help | [{len(bot.guilds)}]"

		if offline_mode:
			presence = "Автономный режим"
			status = discord.Status.idle
		await bot.change_presence(status=status,
								  activity=discord.Activity(name=presence,
								  							type=discord.ActivityType.watching))
		await asyncio.sleep(300)
