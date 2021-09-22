import discord
import requests
import psutil
import sys
import time
import datetime
from discord.ext import commands
from ezlib import *

print("[Command Listener] Initializing...")
nullTime = time.time()




class Main(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.cooldown(3, 10, commands.BucketType.guild)
	async def clear(self, ctx, limit: int):
		if 100 >= limit >= 10:
			messages = await ctx.channel.history(limit=limit).flatten()
			deleted = 0
			for message in messages:
				if await scan_message(message, notify=False):
					deleted += 1
			await done(ctx, f"Удалено {deleted} сообщений.")
		else:
			await fail(ctx, f"Количество сообщений должно быть в пределах от 10 до 100.")

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def clearall(self, ctx, limit: int):
		if 100 >= limit >= 10:
			deleted = 0
			for channel in ctx.guild.text_channels:
				messages = await channel.history(limit=limit).flatten()
				for message in messages:
					if await scan_message(message, notify=False):
						deleted += 1
			await done(ctx, f"Удалено {deleted} сообщений.")
		else:
			await fail(ctx, f"Количество сообщений должно быть в пределах от 10 до 100.")

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
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def disable(self, ctx):
		db = db_read()
		disabled = db.get("disabled", [])
		key = ctx.guild.id
		if key not in disabled:
			db["disabled"].append(key)
			db_write(db)
			await done(ctx, "Сканирование сообщений выключено.")
		else:
			return await fail(ctx, f"На данном сервере уже отключено сканирование сообщений.")


	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def enable(self, ctx):
		db = db_read()
		key = ctx.guild.id
		if key in db.get("disabled", []):
			db["disabled"].remove(key)
			db_write(db)
			await done(ctx, "Сканирование сообщений включено.")
		else:
			return await fail(ctx, f"На данном сервере уже включено сканирование сообщений.")


	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def remlogs(self, ctx):
		db = db_read()
		key = ctx.guild.id
		if key in db.get("logchannels", {}):
			del db["logchannels"][key]
			db_write(db)
			await done(ctx, "Логи будут отправляться в тот же канал, в котором удалено сообщение.")
		else:
			return await fail(ctx, f"На данном сервере уже выключена отправка логов в отдельный канал.")

	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def setlogs(self, ctx, channel: discord.TextChannel):
		db = db_read()
		key: int = ctx.guild.id
		cid = channel.id
		db["logchannels"].get(key)
		db["logchannels"][key] = cid
		db_write(db)
		await done(ctx, f"Логи будут отправляться в канал {channel.mention}.")


	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def disabledms(self, ctx):
		db = db_read()
		disabled = db.get("nodms", [])
		key = ctx.guild.id
		if key not in disabled:
			db["nodms"].append(key)
			db_write(db)
			await done(ctx, "Отправка личных сообщений пользователям отключена.")
		else:
			return await fail(ctx, f"На данном сервере уже отключена отправка личных сообщений пользователям.")

	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def enabledms(self, ctx):
		db = db_read()
		disabled = db.get("nodms", [])
		key = ctx.guild.id
		if key in disabled:
			db["nodms"].remove(key)
			db_write(db)
			await done(ctx, "Отправка личных сообщений пользователям включена.")
		else:
			return await fail(ctx, f"На данном сервере уже включена отправка личных сообщений пользователям.")


	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def disablenotify(self, ctx):
		db = db_read()
		disabled = db.get("dontnotify", [])
		key = ctx.guild.id
		if key not in disabled:
			db["dontnotify"].append(key)
			db_write(db)
			await done(ctx, "Уведомления об удалении сообщений на сервере выключены.")
		else:
			return await fail(ctx, f"На данном сервере уже выключены уведомления об удалении сообщений.")

	@commands.command()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 30, commands.BucketType.guild)
	async def enablenotify(self, ctx):
		db = db_read()
		disabled = db.get("dontnotify", [])
		key = ctx.guild.id
		if key in disabled:
			db["dontnotify"].remove(key)
			db_write(db)
			await done(ctx, "Уведомления об удалении сообщений на сервере включены.")
		else:
			return await fail(ctx, f"На данном сервере уже включены уведомления об удалении сообщений.")




class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.is_owner()
	async def root(self, ctx):
		help_ = f"""
`~eval <code>` - Выполнить код.
`~await <coroutine>` - Вызвать асинхронную функцию.
`~add_pattern <pattern>` - Добавить элемент в блок-листа паттернов.
`~set_pattern <index> <pattern>` - Заменить элемент блок-листа паттернов.
`~remove_pattern <index>` - Удалить элемент блок-листа паттернов.
`~add_eb <string>` - Добавить элемент в блок-листа ембедов.
`~set_eb <index> <string>` - Заменить элемент блок-листа ембедов.
`~remove_eb <index>` - Удалить элемент из блок-листа ембедов.
"""
		embed = discord.Embed(color=PRIMARY)
		embed.add_field(name="🔧 Системные команды", value=help_)
		embed.set_footer(text="Данные команды может вызывать только владелец бота.",
						 icon_url=self.bot.user.avatar_url)
		await ctx.send(embed=embed)

	@commands.command(name="eval")
	@commands.is_owner()
	async def _eval(self, ctx, *, code):
		result = eval(code, locals(), globals())
		if result:
			await ctx.send(f"```py\n{result}```")

	@commands.command(name="await")
	@commands.is_owner()
	async def _await(self, ctx, *, code):
		result = await eval(code, locals(), globals())
		if result:
			await ctx.send(f"```py\n{result}```")

	@commands.command()
	@commands.is_owner()
	async def add_pattern(self, ctx, *, pattern):
		patterns = get_patterns()
		patterns.append(pattern)
		set_patterns(patterns)
		await done(ctx, f"Паттерн с индексом {len(patterns) + 1} установлен на значение `{pattern}`.")

	@commands.command()
	@commands.is_owner()
	async def set_pattern(self, ctx, index: int, *, pattern):
		patterns = get_patterns()
		patterns[index] = pattern
		set_patterns(patterns)
		await done(ctx, f"Паттерн с индексом {index} установлен на значение `{pattern}`.")

	@commands.command()
	@commands.is_owner()
	async def remove_pattern(self, ctx, *, index: int):
		patterns = get_patterns()
		del patterns[index]
		set_patterns(patterns)
		await done(ctx, f"Паттерн с индексом {index} удален.")

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
		embed = discord.Embed(color=PRIMARY,
				      title="Информация",
				      description=f"""
{info} Данный бот предназначен для защиты вашего сервера от скама с «Бесплатным Nitro на 3 месяца от Steam» и людьми якобы раздающими свой инвентарь CS:GO. Если вы увидите подобные сообщения, не ведитесь на них!

Что-бы ваш аккаунт не взломали, не используйте BetterDiscord и не загружайте подозрительное ПО. Если вас уже взломали, удалите BetterDiscord с вашего ПК, поменяйте пароль и установите надежный антивирус (Например, [Kaspersky](https://kaspersky.ru)).

**Версия от**: [<t:{unix}>](https://github.com/ezz-dev/scamprotect)
**Разработчик**: https://github.com/Sweety187
**Исходный код**: https://github.com/ezz-dev/scamprotect
**Сайт бота**: https://scamprotect.ml
**Наш сервер**: https://discord.gg/GpedR6jeZR
**Пожертвовать**: https://qiwi.com/n/XF765
""")
		embed.set_footer(text="Спасибо, что используете нашего бота!")
		embed.set_image(url="https://media.discordapp.net/attachments/832662675963510827/888101822370308117/unknown.png")
		await ctx.send(embed=embed)

	@commands.command()
	async def invite(self, ctx):
		link = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot"
		embed = discord.Embed(description=f"{info} Добавить меня на свой сервер: [[Нажми]]({link})",
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
""".replace("~", ctx.prefix), inline=False)
		embed.add_field(name="🛠️ Инструменты", value=f"""
`~clear <limit>` - Просканировать N сообщений в текущем канале.
`~clearall <limit>` - Просканировать N сообщений во всех каналах.
`~report <message>` - Пожаловаться на ссылку/сообщение.
""".replace("~", ctx.prefix), inline=False)
		embed.add_field(name="⚙️ Настройка", value=f"""
`~prefix` - Изменить префикс бота на этом сервере.
`~enable` - Включить сканирование сообщений.
`~disable` - Выключить сканирование сообщений.
`~enabledms` - Включить уведомления в личных сообщениях.
`~disabledms` - Выключить уведомления в личных сообщениях.
`~enablenotify` - Включить уведомления на сервере.
`~disablenotify` - Выключить уведомления на сервере.
`~remlogs` - Отключить отправку уведомлений в отдельный канал.
`~setlogs <channel>` - Установить канал для отправки уведомлений.
""".replace("~", ctx.prefix), inline=False)
		embed.set_footer(icon_url=self.bot.user.avatar_url,
						 text="© 2021, Ezz Development | https://github.com/ezz-dev")
		await ctx.send(embed=embed)




def setup(bot):
	bot.add_cog(Main(bot))
	bot.add_cog(Owner(bot))
	bot.add_cog(Info(bot))
	print("[Command Listener] Loaded successful.")
