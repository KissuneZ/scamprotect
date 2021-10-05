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
		    format='[%(asctime)s | %(name)s / %(levelname)s]: %(message)s', level=logging.INFO)
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
			return await fail(ctx, "Префикс не может быть длиннее 5 символов.")
		if "`" in prefix:
			return await fail(ctx, "Префикс содержит недопустимый символ.")
		key = ctx.guild.id
		set_prefix(key, prefix)
		await done(ctx, f"Префикс для этого сервера иземенен на `{prefix}`.")

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.cooldown(1, 60, commands.BucketType.guild)
	async def clear(self, ctx, limit: int):
		key = ctx.guild.id

		if channel_scanners.get(key):
			return await fail(ctx, "Дождитесь окончания сканирования или отмените его, удалив вообщение.")
		if 100 >= limit >= 1:
			m = await ctx.send(pattern.format(waiting, 0, limit))
			i = 0
			channel_scanners.update({key: [0, limit, m]})
			deleted = await ctx.channel.purge(limit=limit, check=is_scam)
			deleted = len(deleted)
			await done(ctx, f"Удалено {deleted} сообщений.")
			del channel_scanners[key]
		else:
			await fail(ctx, f"Количество сообщений должно быть в пределах от 1 до 100.")

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.cooldown(1, 300, commands.BucketType.guild)
	async def clearall(self, ctx, limit: int):
		key = ctx.guild.id

		if channel_scanners.get(key):
			return await fail(ctx, "Дождитесь окончания сканирования или отмените его, удалив вообщение.")
		if 100 >= limit >= 1:
			channels = ctx.guild.text_channels
			limit_   = limit * len(channels)
			key      = ctx.guild.id
			deleted  = 0

			m = await ctx.send(pattern.format(waiting, 0, limit_))
			channel_scanners.update({key: [0, limit_, m]})

			for channel in channels:
				deleted_ = await ctx.channel.purge(limit=limit, check=is_scam)
				deleted += len(deleted_)

			del channel_scanners[key]
			await done(ctx, f"Удалено {deleted} сообщений.")
		else:
			await fail(ctx, f"Количество сообщений должно быть в пределах от 1 до 100.")

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
		await done(ctx, "Ваше сообщение отправлено на сервер поддержки.")

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
					return await done(ctx, "Защита включена.")
			if module == "dms":
				if key in db.get("nodms"):
					db["nodms"].remove(key)
					db_write(db)
					return await done(ctx, "Отправка личных сообщений включена.")
			if module == "notify":
				if key in db.get("nodms"):
					db["dontnotify"].remove(key)
					db_write(db)
					return await done(ctx, "Отправка уведомлений включена.")
			await fail(ctx, "Данный модуль уже включен.")
		else:
			await fail(ctx, "Укажите правильный модуль для включения.")

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
					return await done(ctx, "Защита отключена.")
			if module == "dms":
				if key not in db.get("nodms"):
					db["nodms"].append(key)
					db_write(db)
					return await done(ctx, "Отправка личных сообщений выключена.")
			if module == "notify":
				if key not in db.get("nodms"):
					db["dontnotify"].append(key)
					db_write(db)
					return await done(ctx, "Отправка уведомлений выключена.")
			await fail(ctx, "Данный модуль уже выключен.")
		else:
			await fail(ctx, "Укажите правильный модуль для выключения.")

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
				return await done(ctx, "Отправка уведомлений в отдельный канал отключена.")
			else:
				return await fail(ctx, "На этом сервере ещё не назначен канал для уведомлений.")
		channel: discord.TextChannel = arg
		cid = channel.id
		db["logchannels"].get(key)
		db["logchannels"][key] = cid
		db_write(db)
		await done(ctx, f"Уведомления будут отправляться в канал {channel.mention}.")




class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.is_owner()
	async def root(self, ctx):
		help_ = f"""
`~eval <code>` - Выполнить код.
`~exec <code>` - Выполнить код (динамически).
`~await <coroutine>` - Вызвать асинхронную функцию.
`~add_eb <string>` - Добавить элемент в блок-лист ембедов.
`~set_eb <index> <string>` - Заменить элемент блок-листа ембедов.
`~remove_eb <index>` - Удалить элемент из блок-листа ембедов.
`~servers` - Список серверв, на которых есть бот.
`~leave <gid>` - Покинуть сервер с указаным ID.
`~logs` - Список лог-файлов.
`~purge_logs` - Удалить все лог-файлы.
`~send_log <fname>` - Отправить лог-файл в чат.
`~dm_log <fname>` - Отправить лог-файл вам в ЛС.
`~restart` - Перезапустить бота.
`~shutdown` - Выключить бота.
""".replace("~", prefix(ctx))
		embed = discord.Embed(color=PRIMARY)
		embed.add_field(name="🔧 Системные команды", value=help_)
		embed.set_footer(text="© 2021, Ezz Development | https://github.com/ezz-dev",
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
		await done(ctx, f"Удалено {deleted} файлов.")

	@commands.command()
	@commands.is_owner()
	async def send_log(self, ctx, fname):
		await ctx.send(file=discord.File(fr"./logs/{fname}"))

	@commands.command()
	@commands.is_owner()
	async def dm_log(self, ctx, fname):
		await ctx.author.send(file=discord.File(fr"./logs/{fname}"))
		await done(ctx, "Файл отправлен вам в личные сообщения.")
	
	@commands.command()
	@commands.is_owner()
	async def leave(self, ctx, gid: int):
		logger.info(f"Manually forced to leave server [ID: {gid}].")
		await discord.utils.get(self.bot.guilds, id=gid).leave()
		await done(ctx, f"Бот покинул сервер {gid}.")

	@commands.command()
	@commands.is_owner()
	async def shutdown(self, ctx):
		await done(ctx, "Выключение...")
		logger.info("Manual shudown.")
		await self.bot.change_presence(status=discord.Status.idle,
					       activity=discord.Activity(name="Выключение...",
									 type=discord.ActivityType.watching))
		await logout(self.bot)

	@commands.command()
	@commands.is_owner()
	async def restart(self, ctx):
		m = await ctx.send(f"{waiting} Перезапуск...")
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
		await done(ctx, f"Элемент с индексом {len(ebs) + 1} установлен на значение `{string}`.")

	@commands.command()
	@commands.is_owner()
	async def set_eb(self, ctx, index: int, *, string):
		ebs = get_ebs()
		ebs[index] = string
		set_eb(patterns)
		await done(ctx, f"Элемент с индексом {index} установлен на значение `{pattern}`.")

	@commands.command()
	@commands.is_owner()
	async def remove_eb(self, ctx, *, index: int):
		ebs = get_eb()
		del ebs[index]
		set_patterns(ebs)
		await done(ctx, f"Элемент с индексом {index} удален.")




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
		data = f"""
```
Серверов:                 {len(self.bot.guilds)}
Пользователей:            {len(self.bot.users)}
``````
Вызовов сканера:          {scanner_calls}
Удалено сообщений:        {deleted_messages}
``````
Клиент:                   {self.bot.user}
ID:                       {self.bot.user.id}
``````
Оперативная память:       {psutil.virtual_memory().percent}%
Нагрузка на ЦП:           {psutil.cpu_percent()}%
``````
Аптайм:                   {up}
Задержка вебсокета:       {ping} мс.
``````
Python:                   {sys.version.split('(')[0]}
discord.py:               {discord.__version__}
```
"""
		e = discord.Embed(color=PRIMARY)
		e.add_field(name="Состояние бота", value=data)
		e.set_thumbnail(url="https://media.discordapp.net/attachments/832662675963510827/857631236355522650/logo.png")
		await ctx.send(embed=e)

	@commands.command()
	async def about(self, ctx):
		embed = discord.Embed(color=PRIMARY, title="Информация",
				      description=f"""
{info} Данный бот предназначен для защиты вашего сервера от скама с «Бесплатным Nitro на 3 месяца от Steam» и людьми якобы раздающими свой инвентарь CS:GO. Если вы увидите подобные сообщения, не ведитесь на них!

{danger} Что-бы ваш аккаунт не взломали, не используйте BetterDiscord и не загружайте подозрительное ПО. Если же вас уже взломали, рекомендуем вам выполнить следующие действия:
ㆍУдалите BetterDiscord с вашего устройства;
ㆍПереустановите клиент Discord;
ㆍПоменяйте пароли всех ваших аккаунтов;
ㆍУстановите надежный антивирус и выполните полную проверку устройства.

Берегите себя!

**Версия ядра**: [Wolverine {version()}](https://scamprotect.ml/wolverine)
**Разработчик**: [xshadowsexy#0141](https://discord.com/users/811976103673593856)
**Исходный код**: [Устаревшая публичная версия](https://github.com/ezz-dev/scamprotect)
**Сайт бота**: https://scamprotect.ml/
**Наш сервер**: https://discord.gg/GpedR6jeZR
**Пожертвовать**: https://qiwi.com/n/XF765
""")
		embed.set_footer(text="Спасибо, что используете нашего бота!")
		await ctx.send(embed=embed)

	@commands.command()
	async def invite(self, ctx):
		link = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot"
		embed = discord.Embed(description=f"{info} Добавить меня на свой сервер: [[Нажми]]({link})",
				      color=PRIMARY)
		await ctx.send(embed=embed)

	@commands.command()
	async def support(self, ctx):
		embed = discord.Embed(description=f"{info} Сервер поддержки: [[Присоединиться]]({support})",
				      color=PRIMARY)
		await ctx.send(embed=embed)

	@commands.command()
	async def help(self, ctx):
		embed = discord.Embed(title="Добро пожаловать!", color=PRIMARY)
		embed.add_field(name="🧭 Информация", value=f"""
`~help` - Выводит данное сообщение.
`~status` - Техническое состояние бота и его статистика.
`~invite` - Получить ссылку на добавление бота.
`~about` - Информация о боте и ссылки на разработчиков.
`~support` - Сервер поддержки.
""".replace("~", prefix(ctx)), inline=False)
		embed.add_field(name="🛠️ Инструменты", value=f"""
`~clear <limit>` - Просканировать N сообщений в текущем канале.
`~clearall <limit>` - Просканировать N сообщений во всех каналах.
`~report <message>` - Сообщить об ошибке.
""".replace("~", prefix(ctx)), inline=False)
		embed.add_field(name="⚙️ Настройка", value=f"""
`~prefix <prefix>` - Изменить префикс бота на этом сервере.
`~enable scan` - Включить сканирование сообщений.
`~enable dms` - Включить уведомления в личных сообщениях.
`~enable notify` - Включить уведомления на сервере.
`~disable scan` - Выключить сканирование сообщений.
`~disable dms` - Выключить уведомления в личных сообщениях.
`~disable notify` - Выключить уведомления на сервере.
`~notify remove` - Отключить отправку уведомлений в отдельный канал.
`~notify <channel>` - Установить канал для отправки уведомлений.
""".replace("~", prefix(ctx)), inline=False)
		embed.set_footer(icon_url=self.bot.user.avatar_url,
				 text="© 2021, Ezz Development | https://github.com/ezz-dev")
		await ctx.send(embed=embed)




def setup(bot):
	bot.add_cog(Main(bot))
	bot.add_cog(Owner(bot))
	bot.add_cog(Info(bot))
	logger.info("Loaded successful.")
