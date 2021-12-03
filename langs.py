languages = {
	"ru": {
		"my_prefix": "{} Мой префикс: [`{}`].",
		"exception": "Произошла ошибка.",
		"not_owner": "Вы не владелец бота.",
		"missing_access": "У меня нет прав для выполнения данной команды.\n",
		"no_perms": "У вас нет прав для вызова этой команды.\n",
		"missing_reqarg": "Вы не указали обязательный аргумент.",
		"channel_nf": "Канал не найден.",
		"bad_arg": "Несовместимый тип аргумента.",
		"retry_after": "Команда будет доступна через {} секунд.",
		"lang_set": "Язык установлен.",
		"invalid_langcode": "Некорректный код языка.",
		"prefix_too_long": "Префикс не может быть длинее 5 символов.",
		"prefix_invalid": "Префикс содержит недопустимый символ.",
		"prefix_changed": "Префикс для этого сервера изменен на `{}`.",
		"scanner_already_running": "Дождитесь окончания сканирования или отмените его.",
		"invalid_limit": "Укажите число от 1 до 100.",
		"initializing": "{} Инициализация...",
		"sent_to_support": "Ваше сообщение отправлено на сервер поддержки.",
		"prot_on": "Защита включена.",
		"dms_on": "Уведомления в личных сообщениях включены.",
		"notify_on": "Уведомления на сервере включены.",
		"already_enabled": "Данный модуль уже включен.",
		"invalid_module_t_e": "Укажите правильный модуль для включения.",
		"prot_off": "Защита отключена.",
		"dms_off": "Уведомления в личных сообщениях выключены.",
		"notify_off": "Уведомления на сервере выключены.",
		"already_disabled": "Данный модуль уже выключен.",
		"invalid_module_t_d": "Укажите правильный модуль для выключения.",
		"diffcnotify_off": "Отдельный канал для уведомлений отключен.",
		"diffcnotify_notset": "Канал для уведомлений не установлен.",
		"diffcnotify_set": "Канал для уведомлений установлен на {}.",
		"sys_help": "`~eval <code>` - Выполнить код.\n`~exec <code>` - Выполнить код (динамически).\n`~await <coroutine>` - Вызвать асинхронную функцию.\n`~add_eb <string>` - Добавить элемент в блок-лист ембедов.\n`~set_eb <index> <string>` - Назначить элемент блок-листа ембедов.\n`~remove_eb <index>` - Удалить элемент из блок-листа ембедов.\n`~servers` - Список серверов, на которых есть бот.\n`~logs` - Список лог-файлов.\n`~purge_logs` - Удалить все лог-файлы.\n`~send_log <fname>` - Отправить лог-файл в чат.\n`~dm_log <fname>` - Отправить вам в ЛС лог-файл.\n`~restart` - Перезапустить бота.\n`~shutdown` - Выключить бота.",
		"sys_help_title": ":wrench: Системные команды",
		"deleted_files": "Удалено {} файлов.",
		"sent_to_dms": "Проверьте ваши личные сообщения.",
		"restarting": "{} Перезапуск...",
		"elem_setto": "Элемент с индексом {} установлен на значение `{}`.",
		"elem_deleted": "Элемент с индексом {} удален.",
		"status_pattern": """Серверов: {}
Пользователей: {}
Вызовов сканера: {}
Удалено сообщений: {}
Клиент: {}
ID: {}
Оперативная память: {}%
Процессор: {}%
Аптайм: {}
Задержка вебсокета: {} мс.
Python: {}
discord.py: {}
Wolverine: {}""",
		"bot_status": ":satellite: Состояние бота",
		"info": "Информация",
		"about": "{} Данный бот предназначен для защиты вашего сервера от скама с «Бесплатным Nitro на 3 месяца от Steam» и людьми якобы раздающими свой инвентарь CS:GO. Если вы увидите подобные сообщения, не ведитесь на них!\n\n{} Что-бы ваш аккаунт не взломали, не используйте BetterDiscord и не загружайте подозрительное ПО. Если же вас уже взломали, рекомендуем вам выполнить следующие действия:\nㆍУдалите BetterDiscord с вашего устройства;\nㆍПереустановите клиент Discord;\nㆍПоменяйте пароли всех ваших аккаунтов;\nㆍУстановите надежный антивирус и выполните полную проверку устройства.\n\nБерегите себя!\n\n**Версия ядра**: [Wolverine {}](https://scamprotect.ml/wolverine)\n**Разработчик**: [xshadowsexy#0141](https://discord.com/users/811976103673593856)\n**Вебсайт**: https://scamprotect.ml/\n**Наш сервер**: https://discord.gg/GpedR6jeZR\n**Пожертвовать**: https://qiwi.com/n/XF765",
		"invite": "{} Добавить бота на сервер: [[Нажми]]({})",
		"support": "{} Сервер поддержки: [[Присоединиться]]({})",
		"welcome": "Добро пожаловать!",
		"help_desc": ">>> {} Вы можете использовать упоминание бота в качестве префикса. Для выполнения команд настройки вам необходимо иметь право «Управлять сервером», а для команд очистки и сканирования «Управлять сообщениями». Что-бы отменить запущеное сканирование, удалите сообщение, выводящее его прогресс. Процесс сканирования может занять до нескольких часов в зависимости от заданого лимита и не может длиться более 4 часов, иначе он будет остановлен принудительно. Не нужно указывать `[]` и `<>` при вызове команды. Данные скобки обозначают необязательный и обязательный аргументы соответственно.",
		"help_t_info": ":compass: Информация",
		"help_t_tools": ":tools: Инструменты",
		"help_t_settings": ":gear: Настройка",
		"help_info": "`~help` - Выводит данное сообщение.\n`~status` - Техническое состояние бота и его статистика.\n`~invite` - Получить ссылку на добавление бота.\n`~about` - Информация о боте и ссылки на разработчиков.\n`~support` - Сервер поддержки.",
		"help_tools": "`~clear <limit>` - Очистить N сообщений в текущем канале.\n`~clearall <limit>` - Очистить N сообщений во всех каналах.\n`~scan <limit>` - Просканировать N сообщений в текущем канале.\n`~scanall <limit>` - Просканировать N сообщений во всех каналах.\n`~report <message>` - Пожаловаться на ссылку/сообщение.",
		"help_settings": "`~prefix <prefix>` - Изменить префикс бота на этом сервере.\n`~enable scan` - Включить защиту.\n`~enable dms` - Включить уведомления в личных сообщениях.\n`~enable notify` - Включить уведомления на сервере.\n`~disable scan` - Выключить защиту.\n`~disable dms` - Выключить уведомления в личных сообщениях.\n`~disable notify` - Выключить уведомления на сервере.\n`~notify remove` - Отключить отправку уведомлений в отдельный канал.\n`~notify <channel>` - Установить канал для отправки уведомлений.\n`~lang <ru/en>` - Установить язык бота на этом сервере.",
		"perms": {
			"administrator": "Администратор",
			"manage_channels": "Управлять каналами",
			"manage_messages": "Управлять сообщениями",
			"manage_guild": "Управлять сервером"
		},
		"scan_pattern": "{} Сканирование... [{} / {}]",
		"r_msgtext": "Текст сообщения",
		"r_etitle": "Заголовок",
		"r_edesc": "Содержимое",
		"reasons": ["Ембед: {}", "Счёт ИИ: {}"],
		"r_dm_pattern": "Причина: {}. | {}",
		"d_dm_pattern": "{} Ваше сообщение было удалено.\n```{}```",
		"d_srv_pattern": "{} Удалено сообщение от пользователя {}.\n » **Причина**: **`{}`**.",
		"restarted": "{} Бот перезагружен.",
		"msgs_deleted": "Удалено {} сообщений.",
		"s_cancelled": "{} Отменено. [{} / {}]",
		"s_done": "{} Завершено. [{} / {}]",
		"shutting_down": "Выключение..."
	},
	"en": {
		"my_prefix": "{} My prefix: [`{}`].",
		"exception": "Unhandled exception.",
		"not_owner": "You do not own this bot.",
		"missing_access": "I don't have permissions to execute this command.\n",
		"no_perms": "You don't have permissions to use this command.\n",
		"missing_reqarg": "Missing required argument.",
		"channel_nf": "Channel not found.",
		"bad_arg": "Bad argument.",
		"retry_after": "This command will be available in {} seconds.",
		"lang_set": "Language set.",
		"invalid_langcode": "Invalid language code.",
		"prefix_too_long": "Command prefix can't be longer than 5 symbols.",
		"prefix_invalid": "Your command prefix contains illegal charters.",
		"prefix_changed": "Command prefix for this server has been set to `{}`.",
		"scanner_already_running": "Wait for the scanner to finish or cancel it.",
		"invalid_limit": "Message limit must be in 1 to 100 range.",
		"initializing": "{} Initializing...",
		"sent_to_support": "Your message has been sent to support server.",
		"prot_on": "Protection has been enabled.",
		"dms_on": "DM notifications has been enabled.",
		"notify_on": "Notifications has been enabled.",
		"already_enabled": "This module is already enabled.",
		"invalid_module_t_e": "Please type a correct module to enable.",
		"prot_off": "Protection disabled.",
		"dms_off": "DM notifications has been disabled.",
		"notify_off": "Notifications has been disabled.",
		"already_disabled": "This module is already disbaled.",
		"invalid_module_t_d": "Pleasy type a correct module to disable.",
		"diffcnotify_off": "Notifications channel removed.",
		"diffcnotify_notset": "Notifications channel isn't set on this server yet.",
		"diffcnotify_set": "Notifications channel set to {}.",
		"sys_help": "\n`~eval <code>` - Execute code.\n`~exec <code>` - Execute code (dynamically).\n`~await <coroutine>` - Call async function.\n`~add_eb <string>` - Add element to embed blacklist.\n`~set_eb <index> <string>` - Replace embled blacklist element.\n`~remove_eb <index>` - Remove an element from embed blacklist.\n`~servers` - Server list.\n`~logs` - Log-files list.\n`~purge_logs` - Purge log-files.\n`~send_log <fname>` - Send log-file to the chat.\n`~dm_log <fname>` - Send log-file to your DMs.\n`~restart` - Restart the bot.\n`~shutdown` - Shut down.",
		"sys_help_title": ":wrench: System commands",
		"deleted_files": "Deleted {} files.",
		"sent_to_dms": "Please check your direct messages.",
		"restarting": "{} Restarting...",
		"elem_setto": "Element with index {} has been set to `{}`.",
		"elem_deleted": "Element with index {} has been deleted.",
		"status_pattern": """Servers: {}
Users: {}
Scanner calls: {}
Messages deleted: {}
Client: {}
ID: {}
RAM load: {}%
CPU load: {}%
Uptime: {}
Websocket ping: {} ms.
Python: {}
discord.py: {}
Wolverine: {}""",
		"bot_status": ":satellite: Bot status",
		"info": "Information",
		"about": "{} This bot is made to protect your server from «Free Nitro for 3 months from Steam» and people allegedly «distributing their CS:GO inventory» scams. If you see similar messages, don't get fooled by them!\n\n{} To prevent your account from being hacked, do not use BetterDiscord and do not download suspicious software. If you have already been hacked, we recommend you follow these steps:\nㆍRemove BetterDiscord from your device;\nㆍReinstall the Discord client;\nㆍChange the passwords of all your accounts;\nㆍInstall a reliable antivirus and perform a full device scan.\n\n Take care of yourself!\n\n**Core version**: [Wolverine {}](https://scamprotect.ml/wolverine )\n**Developer**: [xshadowsexy#0141](https://discord.com/users/811976103673593856 )\n**Source code**: [Outdated public version](https://github.com/ezz-dev/scamprotect )\n**Website**: https://scamprotect.ml/\n**Our server**: https://discord.gg/GpedR6jeZR\n**Donate**: https://qiwi.com/n/XF765",
		"invite": "{} Invite me to your server: [[Invite]]({})",
		"support": "{} Support server: [[Join]]({})",
		"welcome": "Welcome!",
		"help_desc": ">>> {} You can use the bot mention as command prefix. To execute configuration commands, you need to have the «Manage server», and, for cleaning and scanning commands, «Manage messages» permissions. To stop a running scanner, delete the message showing its progress. The scanning process can take up to several hours depending on the set limit and cannot last more than 4 hours, otherwise it will be stopped forcibly. Don't use `[]` and `<>` while calling the command. These brackets means optional and required arguments, respectively.",
		"help_t_info": ":compass: Information",
		"help_t_tools": ":tools: Tools",
		"help_t_settings": ":gear: Configuration",
		"help_info": "`~help` - Shows this message.\n`~status` - Bot status.\n`~invite` - Invite the bot.\n`~about` - About the bot.\n`~support` - Support server.",
		"help_tools": "`~clear <limit>` - Clear N messages in this channel.\n`~clearall <limit>` - Purge N channels in every channel.\n`~scan <limit>` - Scan N messages in this channel.\n`~scanall <limit>` - Scan N messages in every channel.\n`~report <message>` - Error report.",
		"help_settings": "`~prefix <prefix>` - Set command prefix for this server.\n`~enable scan` - Enable protection.\n`~enable dms` - Enable DM notifications.\n`~enable notify` - Enable notifications on the server.\n`~disable scan` - Disable protection.\n`~disable dms` - Disable DM notifications.\n`~disable notify` - Disable notifications on the server.\n`~notify remove` - Remove notifications channel.\n`~notify <channel>` - Set notifications channel.\n`~lang <ru/en>` - Set bot language on this server.",
		"perms": {
			"administrator": "Administrator",
			"manage_channels": "Manage channels",
			"manage_messages": "Manage messages",
			"manage_guild": "Manage server"
		},
		"scan_pattern": "{} Scanning... [{} / {}]",
		"r_msgtext": "Message content",
		"r_etitle": "Title",
		"r_edesc": "Description",
		"reasons": ["Embed: {}", "AI score: {}"],
		"r_dm_pattern": "Reason: {}. | {}",
		"d_dm_pattern": "{} Your message has been deleted.\n```{}```",
		"d_srv_pattern": "{} Deleted message from user {}.\n » **Reason**: **`{}`**.",
		"restarted": "{} Restarted.",
		"msgs_deleted": "Deleted {} messages.",
		"s_cancelled": "{} Cancelled. [{} / {}]",
		"s_done": "{} Done. [{} / {}]",
		"shutting_down": "Shutting down..."
	}
}
