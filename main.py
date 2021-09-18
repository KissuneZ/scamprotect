import discord, requests, psutil, sys, time, datetime
from discord.ext import commands
from ezlib import *

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
			await done(ctx, "Логи будут отправляться в тот же канал, в котором будет удалено сообщение.")
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

	@commands.command(name="eval")
	@commands.is_owner()
	async def _eval(self, ctx, *, code):
		result = eval(code, locals(), globals())
		if result:
			await ctx.send(result)

	@commands.command(name="await")
	@commands.is_owner()
	async def _await(self, ctx, *, code):
		result = await eval(code, locals(), globals())
		if result:
			await ctx.send(result)




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
		e = discord.Embed(color=0x8080ff)
		e.add_field(name="Состояние бота", value=data)
		e.set_thumbnail(url="https://media.discordapp.net/attachments/832662675963510827/857631236355522650/logo.png")
		await ctx.send(embed=e)

	@commands.command()
	async def about(self, ctx):
		embed = discord.Embed(color=0x8080ff,
			    	  title="Информация",
			    	  description=f"""
{info} Данный бот предназначен для защиты вашего сервера от скама с «Бесплатным Nitro на 3 месяца от Steam» и людьми якобы раздающими свой инвентарь CS:GO. Если вы увидите подобные сообщения, не ведитесь на них!

Что-бы ваш аккаунт не взломали, не используйте BetterDiscord и не загружайте подозрительное ПО. Если вас уже взломали, удалите BetterDiscord с вашего ПК, поменяйте пароль и установите надежный антивирус (Например, [Kaspersky](https://kaspersky.ru)).

**Версия от**: [<t:{unix}>](https://github.com/ezz-dev/scamprotect)
**Разработчик**: https://github.com/Sweety187
**Исходный код**: https://github.com/ezz-dev/scamprotect
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
							  color=0x8080ff)
		await ctx.send(embed=embed)

	@commands.command()
	async def help(self, ctx):
		embed = discord.Embed(title="Добро пожаловать!", color=0x8080ff)
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
`~setlogs` - Установить канал для отправки уведомлений.
""".replace("~", ctx.prefix), inline=False)
		embed.set_footer(icon_url=self.bot.user.avatar_url,
						 text="© 2021, Ezz Development | https://github.com/ezz-dev")
		await ctx.send(embed=embed)




def setup(bot):
	bot.add_cog(Main(bot))
	bot.add_cog(Owner(bot))
	bot.add_cog(Info(bot))
 
