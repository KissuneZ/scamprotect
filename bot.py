import discord, asyncio, re
from discord.ext import commands

bot = commands.Bot(command_prefix='~',
		   intents=discord.Intents().all(),
		   case_insensitive=True,
		   help_command=None)
Token = "ODY3MDMwOTQ1MTIyNjE1Mjk3.YPbLfQ.Yvo95f-qmLF3wmHBXDkcnpXGv_M"

embed_blacklist = ["discord nitro бесплатно на 3 месяца от steam", "сделайте discord ещё круче с nitro",
		   "3 months of discord nitro free from steam", "get 3 months of discord nitro free from steam",
		   "discord nitro for 3 months with steam", "free discord nitro for 3 months from steam",
		   "make discord even cooler with nitro"]
patterns_blacklist = [r"i'm leaving.*skin.*http", r"i'm leaving.*inventory.*http",
                      r"i am leaving.*trade.*http", r"i leave.*trade.*http"]
reasons = ["blacklist.link: {}", "blacklist.embed: {}", "blacklist.pattern: {}"]

with open("blacklist.txt") as file:
	_text_ = file.read()
	blacklist = _text_.split("\n")


@bot.command()
async def invite(ctx):
	invite_link = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"
	embed = discord.Embed(description=f"<:info:863711569975967745> Добавить бота на свой сервер: [[Нажми]]({invite_link})",
						  color=0x8080ff)
	await ctx.send(embed=embed)


@bot.command()
async def help(ctx):
	embed = discord.Embed(color=0x8080ff,
		description=f"<:info:863711569975967745> К сожалению, на данный момент у бота нет команд для настройки и управления. Вы можете пригласить бота,  используя `{ctx.prefix}invite`, или просмотреть информацию о нем, используя `{ctx.prefix}about`.")
	await ctx.send(embed=embed)


@bot.command()
async def about(ctx):
	embed = discord.Embed(color=0x8080ff,
			      title="Информация",
			      description="""
<:info:863711569975967745> Данный бот предназначен для защиты вашего сервера от скама с «Бесплатным Nitro на 3 месяца от Steam» и людьми якобы раздающими свой инвентарь CS:GO. Если вы увидите подобные сообщения, не ведитесь на них!

Что-бы ваш аккаунт не взломали, не используйте BetterDiscord и не загружайте подозрительное ПО. Если вас уже взломали, удалите BetterDiscord с вашего ПК, поменяйте пароль и установите надежный антивирус (Например, [Kasperky](https://kaspersky.ru)).

**Разработчик**: https://github.com/Sweety187
**Исходный код**: https://github.com/ezz-dev/scamprotect
**Наш сервер**: https://discord.gg/GpedR6jeZR
**Пожертвовать**: https://qiwi.com/n/XF765
""")
	embed.set_footer(text="Спасибо, что используете нашего бота!")
	embed.set_image(url="https://media.discordapp.net/attachments/832662675963510827/885512255603605544/demo2.PNG")
	await ctx.send(embed=embed)


@bot.event
async def on_message(message):
	if message.author.bot:
		return
	await bot.process_commands(message)
	await scan_message(message)

async def scan_message(message):
	index = 0
	for elem in blacklist:
		if elem in message.content.lower() and elem != "":
			return await delete(message, index, 0, 0, "message.content")
		index += 1
	index = 0
	for elem in patterns_blacklist:
		if re.findall(elem, message.content.lower()):
			return await delete(message, index, 0, 2, "message.content")
		index += 1
	if not message.embeds and "http" in message.content:
		await asyncio.sleep(1)
		message = await message.channel.fetch_message(message.id)
	for embed in message.embeds:
		if await check_embed(embed, message):
			return


async def check_embed(embed, message):
	index = 0
	for elem in embed_blacklist:
		indexx = 0
		try:
			if elem in embed.title.lower() and elem != "":
				return await delete(message, index, indexx, 1, "title")
		except:
			return False
		try:
			if elem in embed.description.lower() and elem != "":
				return await delete(message, index, indexx, 1, "description")
		except:
			return False
		index += 1


async def delete(message, index, indexx, rindex, blkey):
	reason = reasons[rindex].format(f"{blkey}: {[indexx]}: {index}")
	embed1 = discord.Embed(description=f"<:danger:862303667465093140> Удалено сообщение от пользователя {message.author.mention}.\n \➡ **Причина**: **`{reason}`**.",
			       color=0xff6060)
	embed2 = discord.Embed(description=f"<:danger:862303667465093140> **Ваше сообщение было удалено**.\n```{message.content}```",
			       color=0xff6060)
	embed2.set_footer(text="Вероятнее всего, вы стали жертвой взлома и ваш аккаунт был использован для рассылки скама. Что-бы такое не повторилось, удалите BetterDiscord с вашего ПК, поменяйте пароль и используйте надежный антивирус.")
	try:
		await message.delete()
		await message.channel.send(embed=embed1)
		await message.author.send(embed=embed2)
	except:
		return False
	return True


@bot.event
async def on_ready():
	print("Logged in.")
	while True:
		presence = f"{bot.command_prefix}help | [{len(bot.guilds)}]"
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(presence))
		await asyncio.sleep(7)
		presence = f"{bot.command_prefix}invite | [{len(bot.guilds)}]"
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(presence))
		await asyncio.sleep(7)
		presence = f"{bot.command_prefix}about | [{len(bot.guilds)}]"
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(presence))
		await asyncio.sleep(7)


bot.run(Token)
