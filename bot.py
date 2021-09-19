import discord
from discord.ext import commands
from ezlib import *

bot = commands.Bot(command_prefix=determine_prefix,
		   intents=discord.Intents().all(),
		   case_insensitive=True,
		   help_command=None)
Token = "ODY3MDMwOTQ1MTIyNjE1Mjk3.YPbLfQ.Yvo95f-qmLF3wmHBXDkcnpXGv_M"
bot.load_extension("main")


@bot.command()
@commands.has_permissions(manage_guild=True)
@commands.cooldown(1, 30, commands.BucketType.guild)
async def prefix(ctx, prefix):
	if len(prefix) > 5:
		return await fail(ctx, "Префикс не может быть длиннее 5 символов.")
	if "`" in prefix:
		return await fail(ctx, "Префикс содержит недопустимый символ.")
	key = ctx.guild.id
	set_prefix(key, prefix)
	await done(ctx, f"Префикс для этого сервера иземенен на `{prefix}`.")


@bot.event
async def on_ready():
	print("Logged in.")
	await presence_loop(bot)


@bot.event
async def on_command_error(ctx, error):
	msg = error
	if isinstance(error, commands.errors.CommandInvokeError):
		_error = str(error).replace("Command raised an exception: ", "")
		msg = f"Произошла ошибка.\n```{_error}```"
	if isinstance(error, commands.errors.CommandNotFound):
		return
	if isinstance(error, commands.CommandOnCooldown):
		msg = f"Команда будет доступна через {int(error.retry_after)} секунд."
	if isinstance(error, commands.errors.BotMissingPermissions):
		msg = "У меня нет прав для выполнения данной команды."
	if isinstance(error, commands.errors.MissingRequiredArgument):
		msg = "Вы не указали обязательный аргумент."
	if isinstance(error, commands.MissingPermissions):
		msg = f'У вас нет прав для вызова этой команды.'
	return await fail(ctx, msg)


@bot.event
async def on_message(message):
	if message.author.bot:
		return
	if message.content == f"<@{bot.user.id}>":
		p = get_prefix(message.guild.id)
		await message.reply(f"{vmark} Мой префикс: [`{p}`].")
	await bot.process_commands(message)
	db = db_read()
	key = str(message.guild.id)
	key_ = message.guild.id
	dm = key_ not in db["nodms"]
	notify = key_ not in db["dontnotify"]
	disabled = db.get("disabled", [])
	cid = db["logchannels"].get(key)
	if key_ not in disabled:
		await scan_message(message, notify=notify, cid=cid, dm=dm)


bot.run(Token)
