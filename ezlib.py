import discord
import re
import pathlib
import asyncio
import json
import requests


reasons = ["Ссылка: {}", "Ембед: {}", "Шаблон: {}", "Счёт ИИ: {}"]
unix    = int(pathlib.Path('bot.py').stat().st_mtime)

__version__ = "5.0.2"

info   = "<:info:863711569975967745>"
danger = "<:danger:862303667465093140>"
vmark  = "<:vmark:862306691643342869>"
xmark  = "<:xmark:862308439136403488>"

PRIMARY   = 0x8080ff
SECONDARY = 0xff6060

InetSession    = requests.Session()
api_key        = "HGAjJHshJHSkJSBBDdD"
api_url        = f"http://f0575604.xsph.ru/api/server.php?token={api_key}&"
base_url       = "http://f0575604.xsph.ru"
prefixes       = {}
default_prefix = "~"
sessioncache   = {"sc": 0, "dmc": 0}

support = "https://discord.gg/GpedR6jeZR"
hook = "https://discord.com/api/webhooks/888444735289696317/9Y8C-BlwF-27VdrZDvO3CLxFNlqqkh2S29lEQidTntudhSk3A-0ecPU0RxtVEViZZSM2"


def api_interact(do: str, data=None):
	print(f"[API interaction] {do}: {data}")
	result   = None
	data     = json.dumps(data)
	response = InetSession.get(f"{api_url}do={do}&data={data}", timeout=10)
	if response.text:
		result = json.loads(response.text)
	return result




async def determine_prefix(bot, message):
	key = message.guild.id
	return get_prefix(key)


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




with open("blacklist.txt") as file:
	_text_ = file.read()
	blacklist = _text_.split("\n")




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
	print("[EzLib] Getting remote session...")
	response = InetSession.get(f"{base_url}/session.json", timeout=10)
	return json.loads(response.text)


def get_global_session():
	print("[EzLib] Getting global session...")
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
	print("[EzLib] Sending statistics...")
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
	disabled = db.get("disabled", [])
	cid = db["logchannels"].get(str(key))
	return dm, notify, disabled, cid




def get_patterns():
	print("[EzLib] Fetching patterns blacklist...")
	return api_interact("getPatterns")


def set_patterns(data: list):
	api_interact("setPatterns", data)


def get_eb():
	print("[EzLib] Fetching embed blacklist...")
	return api_interact("getEB")


def set_eb(data: list):
	api_interact("setEB", data)


embed_blacklist    = get_eb()
patterns_blacklist = get_patterns()
print("[EzLib] Defined blacklists.")




async def ai_scanner(message, notify=None, cid=None, dm=None):
	suspicious = {"steam": 0.38, "nitro": 0.22, "free": 0.23,
	"everyone": 0.56, "skin": 0.31, "trade": 0.39, "http": 0.27,
	"нитро": 0.22, "эпик": 0.38, "стим": 0.38, "разда": 0.11,
	"offer": 0.14, "distribution": 0.17, "3 months": 0.30, "giving": 0.11,
	"discord": 0.14, "бесплатн": 0.23, "epic": 0.38, "epik": 0.38}

	score = 0.0
	text  = message.content.lower()

	for item in list(suspicious.items()):
		if item[0] in text:
			score += item[1]

	if score >= 1.0:
		score = round(score, 2)
		return await delete(message, score, 0, 3, "Текст сообщения", notify=notify, cid=cid, dm=dm)


async def scan_message(message, notify=None, cid=None, dm=None):
	sc_up()

	if await ai_scanner(message, notify=notify, cid=cid, dm=dm):
		return

	index = 0
	for elem in blacklist:
		if elem in message.content.lower() and elem != "":
			return await delete(message, index, 0, 0, "Текст сообщения", notify=notify, cid=cid, dm=dm)
		index += 1

	index = 0
	for elem in patterns_blacklist:
		if re.findall(elem, message.content.lower().replace("\n", " ")):
			return await delete(message, index, 0, 2, "Текст сообещния", notify=notify, cid=cid, dm=dm)
		index += 1

	if not message.embeds and "http" in message.content:
		await asyncio.sleep(1)
		message = await message.channel.fetch_message(message.id)
	elif not "http" in message.content:
		return

	indexx = 0
	for embed in message.embeds:
		if await check_embed(embed, message, 0, notify=notify, cid=cid, dm=dm):
			return True
		indexx += 1


async def check_embed(embed, message, indexx, notify=None, cid=None, dm=None):
	index = 0
	for elem in embed_blacklist:
		try:
			if elem in embed.title.lower() and elem != "":
				return await delete(message, index, indexx, 1, "Заголовок", notify=notify, cid=cid, dm=dm)
		except:
			return False
		try:
			if elem in embed.description.lower() and elem != "":
				return await delete(message, index, indexx, 1, "Описание", notify=notify, cid=cid, dm=dm)
		except:
			return False
		index += 1


async def delete(message, index, indexx, rindex, blkey, notify=None, cid=None, dm=None):
	reason = reasons[rindex].format(f"{blkey}: {[indexx]}: {index}")
	embed1 = discord.Embed(description=f"{danger} Удалено сообщение от пользователя {message.author.mention}.\n » **Причина**: **`{reason}`**.",
			       		   color=SECONDARY)
	embed2 = discord.Embed(description=f"{danger} **Ваше сообщение было удалено**.\n```{message.content}```",
			       		   color=SECONDARY)
	embed2.set_footer(text="Вероятнее всего, вы стали жертвой взлома и ваш аккаунт был использован для рассылки скама. Что-бы такое не повторилось, удалите BetterDiscord с вашего ПК, поменяйте пароль и используйте надежный антивирус.")
	
	try:
		await message.delete()
		if notify:
			channel = message.channel
			if cid:
				channels = message.guild.text_channels
				channel  = discord.utils.get(channels, id=cid)
			if not channel or not cid:
				channel  = message.channel
			await channel.send(embed=embed1)
			if dm:
				await message.author.send(embed=embed2)
	except Exception as e:
		print(e)
		return False

	dmc_up()
	print(f"[EzLib] Deleted message from {message.author}: {reason}.")
	return True




async def done(ctx, message):
	return await ctx.send(f"{vmark} {message}")


async def fail(ctx, message):
	return await ctx.send(f"{xmark} {message}")




async def presence_loop(bot):
	while True:
		stats = {"guilds": len(bot.guilds), "users": len(bot.users)}
		send_stats(stats)

		presence = f"{default_prefix}help | [{len(bot.guilds)}]"
		await bot.change_presence(status=discord.Status.dnd,
								  activity=discord.Activity(name=presence,
								  							type=discord.ActivityType.watching))
		await asyncio.sleep(60)


print(f"[EzLib] Loaded EzLib {__version__}")
