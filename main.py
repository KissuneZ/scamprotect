import discord
import requests
import psutil
import sys
import time
import datetime
import logging
from discord.ext import commands
from wolverine import *
from os import listdir
from os.path import isfile, join
from typing import Union


logging.basicConfig(filename="./logs/latest.log", filemode="a",
				    format=log_pattern, level=logging.INFO)
logger = logging.getLogger("CommandListener")
nullTime = time.time()




class Main(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def prefix(self, ctx, prefix):
		if len(prefix) > 5:
			return await fail(ctx, lang(ctx)["prefix_too_long"])
		if "`" in prefix:
			return await fail(ctx, lang(ctx)["prefix_invalid"])
		key = ctx.guild.id
		set_prefix(key, prefix)
		await done(ctx, lang(ctx)["prefix_changed"].format(prefix))

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def clear(self, ctx, limit: int):
		key = ctx.guild.id

		if is_scanner_running(key):
			return await fail(ctx, lang(ctx)["scanner_already_running"])
		if 100 >= limit >= 1:
			await ctx.channel.purge(limit=limit)
		else:
			await fail(ctx, lang(ctx)["invalid_limit"])

	@commands.command()
	@commands.has_permissions(manage_channels=True, manage_messages=True)
	@commands.bot_has_permissions(administrator=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def clearall(self, ctx, limit: int):
		key = ctx.guild.id

		if is_scanner_running(key):
			return await fail(ctx, lang(ctx)["scanner_already_running"])
		if 100 >= limit >= 1:
			channels = ctx.guild.text_channels
			for channel in channels:
				try:
					await channel.purge(limit=limit)
				except:
					continue
		else:
			await fail(ctx, lang(ctx)["invalid_limit"])

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.cooldown(1, 60, commands.BucketType.guild)
	async def scan(self, ctx, limit: int):
		key = ctx.guild.id

		if is_scanner_running(key):
			return await fail(ctx, lang(ctx)["scanner_already_running"])
		if 100 >= limit >= 1:
			m = await ctx.send(lang(ctx)["initializing"].format(waiting))
			data = [0, limit, m]
			channels = [ctx.channel]
			await run_async_scanner(data, channels, ctx)
		else:
			await fail(ctx, lang(ctx)["invalid_limit"])

	@commands.command()
	@commands.has_permissions(manage_channels=True, manage_messages=True)
	@commands.bot_has_permissions(administrator=True)
	@commands.cooldown(1, 300, commands.BucketType.guild)
	async def scanall(self, ctx, limit: int):
		key = ctx.guild.id

		if is_scanner_running(key):
			return await fail(ctx, lang(ctx)["scanner_already_running"])
		if 100 >= limit >= 1:
			m = await ctx.send(lang(ctx)["initializing"].format(waiting))
			channels = ctx.guild.text_channels
			limit_   = limit * len(channels)
			data = [0, limit, m]

			await run_async_scanner(data, channels, ctx, glimit=limit_)
		else:
			await fail(ctx, lang(ctx)["invalid_limit"])

	@commands.command()
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def report(self, ctx, *, message):
		avatar = str(ctx.author.avatar_url)
		payload = {"embeds": [{"description": message,
				   "color": 0xff6060, "footer": {
						"text": str(ctx.author),
						"icon_url": avatar
						}}]}
		requests.post(hook, json=payload)
		await done(ctx, lang(ctx)["sent_to_support"])

	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def enable(self, ctx, module):
		if module in ["dms", "notify", "scan"]:
			db = db_read()
			key = ctx.guild.id
			if module == "scan":
				if key in db.get("disabled", []):
					db["disabled"].remove(key)
					db_write(db)
					return await done(ctx, lang(ctx)["prot_on"])
			if module == "dms":
				if key in db.get("nodms"):
					db["nodms"].remove(key)
					db_write(db)
					return await done(ctx, lang(ctx)["dms_on"])
			if module == "notify":
				if key in db.get("dontnotify"):
					db["dontnotify"].remove(key)
					db_write(db)
					return await done(ctx, lang(ctx)["notify_on"])
			await fail(ctx, lang(ctx)["already_enabled"])
		else:
			await fail(ctx, lang(ctx)["invalid_module_t_e"])

	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def disable(self, ctx, module):
		if module in ["dms", "notify", "scan"]:
			db = db_read()
			key = ctx.guild.id
			if module == "scan":
				if key not in db.get("disabled", []):
					db["disabled"].append(key)
					db_write(db)
					return await done(ctx, lang(ctx)["prot_off"])
			if module == "dms":
				if key not in db.get("nodms"):
					db["nodms"].append(key)
					db_write(db)
					return await done(ctx, lang(ctx)["dms_off"])
			if module == "notify":
				if key not in db.get("nodms"):
					db["dontnotify"].append(key)
					db_write(db)
					return await done(ctx, lang(ctx)["notify_off"])
			await fail(ctx, lang(ctx)["already_disabled"])
		else:
			await fail(ctx, lang(ctx)["invalid_module_t_d"])

	@commands.command(aliases=["notify"])
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def notifications(self, ctx, arg: Union[discord.TextChannel, str]):
		db = db_read()
		key = str(ctx.guild.id)

		if arg in ["off", "remove"]:
			if key in db.get("logchannels", {}):
				del db["logchannels"][key]
				db_write(db)
				return await done(ctx, lang(ctx)["diffcnotify_off"])
			else:
				return await fail(ctx, lang(ctx)["diffcnotify_notset"])
		elif type(arg) == str:
			raise ValueError("Argument must be <discord.TextChannel object> or ['off', 'remove'].")
		channel: discord.TextChannel = arg
		cid = channel.id
		db["logchannels"].get(key)
		db["logchannels"][key] = cid
		db_write(db)
		await done(ctx, lang(ctx)["diffcnotify_set"].format(channel.mention))

	@commands.command(aliases=["lang"])
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def languange(self, ctx, lk: str):
		if lk in ["ru", "en"]:
			key = ctx.guild.id
			db = db_read()
			langkeys[key] = lk
			db.update({"langs": {key: lk}})
			db_write(db)
			await done(ctx, lang(ctx)["lang_set"])
		else:
			return await fail(ctx, lang(ctx)["invalid_langcode"])





class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.is_owner()
	async def root(self, ctx):
		help_ = lang(ctx)["sys_help"].replace("~", prefix(ctx))
		embed = discord.Embed(color=PRIMARY)
		embed.add_field(name=lang(ctx)["sys_help_title"], value=help_)
		embed.set_footer(text=copyright,
						 icon_url=self.bot.user.avatar_url)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.is_owner()
	async def servers(self, ctx):
		servers = []
		for guild in self.bot.guilds:
			servers.append(f"{guild.id} | {guild.name}: {guild.member_count}")
		string = '\n'.join(servers)
		result = f"```{string}```"
		await ctx.send(result)

	@commands.command()
	@commands.is_owner()
	async def logs(self, ctx):
		path = "./logs/"
		files = [f for f in listdir(path)]
		string = '\n'.join(files)
		result = f"```{string}```"
		await ctx.send(result)

	@commands.command()
	@commands.is_owner()
	async def purge_logs(self, ctx):
		path = "./logs/"
		files = [f for f in listdir(path)]
		deleted = 0
		for file in files:
			try:
				os.remove(path + file)
				deleted += 1
			except:
				continue
		await done(ctx, lang(ctx)["deleted_files"].format(deleted))

	@commands.command()
	@commands.is_owner()
	async def send_log(self, ctx, fname):
		await ctx.send(file=discord.File(fr"./logs/{fname}"))

	@commands.command()
	@commands.is_owner()
	async def dm_log(self, ctx, fname):
		await ctx.author.send(file=discord.File(fr"./logs/{fname}"))
		await done(ctx, lang(ctx)["sent_to_dms"])

	@commands.command()
	@commands.is_owner()
	async def shutdown(self, ctx):
		await done(ctx, lang(ctx)["shutting_down"])
		logger.info("Manual shudown.")
		await self.bot.change_presence(status=discord.Status.idle,
								  	   activity=discord.Activity(name="Выключение...",
								  	   type=discord.ActivityType.watching))
		await logout(self.bot)

	@commands.command()
	@commands.is_owner()
	async def restart(self, ctx):
		m = await ctx.send(lang(ctx)["restarting"].format(waiting))
		logger.info("Manual restart.")
		await self.bot.change_presence(status=discord.Status.idle,
								  	   activity=discord.Activity(name="Перезапуск...",
								  	   type=discord.ActivityType.watching))
		with open(".restarted", "w+") as f:
			f.write(f"{ctx.channel.id}:{m.id}")
		exit_handler()
		python = sys.executable
		os.execl(python, python, *sys.argv)

	@commands.command(name="eval")
	@commands.is_owner()
	async def _eval(self, ctx, *, code):
		result = eval(code, globals(), locals())
		if result:
			await ctx.send(f"```py\n{result}```")

	@commands.command(name="exec")
	@commands.is_owner()
	async def _exec(self, ctx, *, code):
		exec(code, globals(), locals())

	@commands.command(name="await")
	@commands.is_owner()
	async def _await(self, ctx, *, code):
		result = await eval(code, globals(), locals())
		if result:
			await ctx.send(f"```py\n{result}```")

	@commands.command()
	@commands.is_owner()
	async def add_eb(self, ctx, *, string):
		ebs = get_eb()
		ebs.append(string)
		set_eb(ebs)
		await done(ctx, lang(ctx)["elem_setto"].format(len(ebs) + 1, string))

	@commands.command()
	@commands.is_owner()
	async def set_eb(self, ctx, index: int, *, string):
		ebs = get_ebs()
		ebs[index] = string
		set_eb(patterns)
		await done(ctx, lang(ctx)["elem_setto"].format(index, pattern))

	@commands.command()
	@commands.is_owner()
	async def remove_eb(self, ctx, *, index: int):
		ebs = get_eb()
		del ebs[index]
		set_patterns(ebs)
		await done(ctx, lang(ctx)["elem_deleted"].format(index))




class Info(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def status(self, ctx):
		scanner_calls = getsc()
		deleted_messages = getdmc()
		up = int(time.time() - nullTime)
		up = datetime.timedelta(seconds=up)
		ping = round(self.bot.latency * 1000, 2)

		data = lang(ctx)["status_pattern"].format(len(self.bot.guilds), len(self.bot.users),
										   		  scanner_calls, deleted_messages, self.bot.user,
										   		  self.bot.user.id, psutil.virtual_memory().percent,
										   		  psutil.cpu_percent(), up, ping, sys.version.split('(')[0],
										   		  discord.__version__)
		e = discord.Embed(color=PRIMARY)
		e.add_field(name=lang(ctx)["bot_status"], value=data)
		e.set_thumbnail(url="https://media.discordapp.net/attachments/832662675963510827/857631236355522650/logo.png")
		await ctx.send(embed=e)

	@commands.command()
	async def about(self, ctx):
		embed = discord.Embed(color=PRIMARY,
			    	  title=lang(ctx)["info"],
			    	  description=lang(ctx)["about"].format(version()))
		embed.set_footer(text=copyright)
		await ctx.send(embed=embed)

	@commands.command()
	async def invite(self, ctx):
		link = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot"
		embed = discord.Embed(description=lang(ctx)["invite"].format(info, link),
							  color=PRIMARY)
		await ctx.send(embed=embed)

	@commands.command()
	async def support(self, ctx):
		embed = discord.Embed(description=lang(ctx)["support"].format(info, support),
							  color=PRIMARY)
		await ctx.send(embed=embed)

	@commands.command()
	async def help(self, ctx):
		text = lang(ctx)["help_desc"].format(info)
		embed = discord.Embed(title=lang(ctx)["welcome"],
							  description=text,
							  color=PRIMARY)
		embed.add_field(name=lang(ctx)["help_t_info"],
						value=lang(ctx)["help_info"].replace("~", prefix(ctx)),
						inline=False)
		embed.add_field(name=lang(ctx)["help_t_tools"],
						value=lang(ctx)["help_tools"].replace("~", prefix(ctx)),
						inline=False)
		embed.add_field(name=lang(ctx)["help_t_settings"],
						value=lang(ctx)["help_settings"].replace("~", prefix(ctx)),
						inline=False)
		embed.set_footer(icon_url=self.bot.user.avatar_url,
						 text=copyright)
		await ctx.send(embed=embed)




def setup(bot):
	bot.add_cog(Main(bot))
	bot.add_cog(Owner(bot))
	bot.add_cog(Info(bot))
	logger.info("Loaded successful.")
