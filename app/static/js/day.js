	// dayjs -> https://day.js.org/docs/en/installation/installation
	// Maandag = 1
	// Dinsdag = 2
	// Woensdag = 3
	// Donderdag = 4
	// Vrijdag = 5
	// Zaterdag = 6
	// Zondag = 7

	const weekOfYear = window.dayjs_plugin_weekOfYear
	const weekday = window.dayjs_plugin_weekday
	const updateLocale = window.dayjs_plugin_updateLocale
	dayjs.extend(weekOfYear)
	dayjs.extend(weekday)
	dayjs.extend(updateLocale)

	// update months and days to dutch
	dayjs.updateLocale('en', {
	months: [
		"januari", "februari", "maart", "april", "mei", "juni", "juli",
		"augustus", "september", "oktober", "november", "december"
	],
	weekdays: [
		"zondag", "maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag"
	]
	})