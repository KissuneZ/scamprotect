import discord
import re
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
import nest_asyncio


nest_asyncio.apply()

reasons = ["Ембед: {}", "Счёт ИИ: {}"]
unix    = int(pathlib.Path('bot.py').stat().st_mtime)

__version__ = "6.3.0"

info    = "<:info:863711569975967745>"
danger  = "<:danger:862303667465093140>"
vmark   = "<:vmark:862306691643342869>"
xmark   = "<:xmark:862308439136403488>"
waiting = "<a:waiting:868094543524937749>"

PRIMARY   = 0x8080ff
SECONDARY = 0xff6060

InetSession    = requests.Session()
api_key        = "HGAjJHshJHSkJSBBDdD"
api_url        = f"http://f0575604.xsph.ru/api/server.php?token={api_key}&"
base_url       = "http://f0575604.xsph.ru"
prefixes       = {}
default_prefix = "~"
sessioncache   = {"sc": 0, "dmc": 0}
pattern        = "{} Сканирование... [{} / {}]"

support = "https://discord.gg/GpedR6jeZR"
hook = "https://discord.com/api/webhooks/888444735289696317/9Y8C-BlwF-27VdrZDvO3CLxFNlqqkh2S29lEQidTntudhSk3A-0ecPU0RxtVEViZZSM2"

channel_scanners = {}
logger = None
bot_   = discord.ext.commands.Bot(None)

commands_ = discord.ext.commands
manual_scanner_args = {"notify": False, "dm": False, "cid": None, "noscup": True, "delete": False}


def api_interact(do: str, data=None):
	result   = None
	data     = json.dumps(data)
	try:
		response = InetSession.get(f"{api_url}do={do}&data={data}", timeout=10)
	except Exception as e:
		logger.error(f"API Connection Failed: {e}. Request: `{do} {data}`.")
	if response.text:
		result = json.loads(response.text)
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
	with open("session.json", "w+") as session:
		session.truncate()
		session.write(json.dumps({"sc": 0, "dmc": 0}))


def update_session():
	with open("session.json", "w+") as session:
		session.truncate()
		session.write(json.dumps(sessioncache))


def get_remote_session():
	response = InetSession.get(f"{base_url}/session.json", timeout=10)
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
	data = {"dm": dm, "notify": notify, "disabled": disabled, "cid": cid, "noscup": False, "delete": True}
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


def init():
	global logger, embed_blacklist, suspicious

	logging.basicConfig(filename="./logs/latest.log", filemode="a",
				    	format='[%(asctime)s | %(name)s / %(levelname)s]: %(message)s',
				    	level=logging.INFO)
	logger = logging.getLogger("Wolverine")

	atexit.register(exit_handler)
	embed_blacklist = get_eb()
	suspicious = get_suspicious_words()

	logger.info(f"Loaded Wolverine {__version__}.")


def is_scam(message):
	key = message.guild.id
	channel_scanners[key][0] += 1
	i = channel_scanners[key][0]
	l = channel_scanners[key][1]
	m = channel_scanners[key][2]
	text = pattern.format(waiting, i, l)
	if i < l:
		try:
			asyncio.run(m.edit(content=text))
		except:
			text = f"{vmark} Отменено. [{i} / {l}]"
			asyncio.run(m.channel.send(content=text))
			del channel_scanners[key]
			raise commands_.errors.CommandNotFound

	else:
		text = f"{vmark} Завершено. [{i} / {l}]"
		asyncio.run(m.edit(content=text))

	if "http" in message.content:
		task = scan_message(message, **manual_scanner_args)
		result = asyncio.run(task)
		return result

	return False


async def ai_scanner(message, **args):
	score = 0.0
	text  = message.content.lower()

	for item in list(suspicious.items()):
		if item[0] in text:
			score += item[1]

	if score >= 1.0:
		score = round(score, 2)
		return await delete(message, score, 0, 1, "Текст сообщения", **args)


async def scan_message(message, **args):
	if not args["noscup"]:
		sc_up()

	if await ai_scanner(message, **args):
		return True

	if not message.embeds:
		await asyncio.sleep(1)
		message = await message.channel.fetch_message(message.id)

	indexx = 0
	for embed in message.embeds:
		if await check_embed(embed, message, indexx, **args):
			return True
		indexx += 1


async def check_embed(embed, message, indexx, **args):
	index = 0
	for elem in embed_blacklist:
		try:
			if elem in embed.title.lower() and elem != "":
				return await delete(message, index, indexx, 0, "Заголовок", **args)
		except:
			pass
		try:
			if elem in embed.description.lower() and elem != "":
				return await delete(message, index, indexx, 0, "Описание", **args)
		except:
			return False
		index += 1


async def delete(message, index, indexx, rindex, blkey, **args):
	if not args["delete"]:
		return True

	reason = reasons[rindex].format(f"{blkey}: {[indexx]}: {index}")
	embed = discord.Embed(description=f"{danger} Удалено сообщение от пользователя {message.author.mention}.\n » **Причина**: **`{reason}`**.",
			       		  color=SECONDARY)
	embed_dm = discord.Embed(description=f"{danger} **Ваше сообщение было удалено**.\n```{message.content}```",
			       		     color=SECONDARY)
	embed_dm.set_footer(text=f"Причина: {reason}. | {message.guild.name}", icon_url=message.guild.icon_url)
	try:
		await message.delete()
		if args["notify"]:
			channel = message.channel
			if args["cid"]:
				channels = message.guild.text_channels
				channel  = discord.utils.get(channels, id=args["cid"])
			if not channel or not args["cid"]:
				channel  = message.channel
			await channel.send(embed=embed)
		if args["dm"]:
			await message.author.send(embed=embed_dm)
	except Exception as e:
		logger.error(e)
		return False

	dmc_up()
	logger.warn(f"Deleted message from {message.author}: {reason}.\nMessage content: {message.content}")
	return True




def exit_handler():
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
			await msg.edit(content=f"{vmark} Бот перезагружен.")
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

		presence = f"{default_prefix}help | [{len(bot.guilds)}]"
		await bot.change_presence(status=discord.Status.dnd,
								  activity=discord.Activity(name=presence,
								  							type=discord.ActivityType.watching))
		await asyncio.sleep(300)
