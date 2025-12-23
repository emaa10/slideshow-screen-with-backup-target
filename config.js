let config = {
	address: "0.0.0.0",
	ipWhitelist: ["127.0.0.1", "::ffff:127.0.0.1", "::1", "::ffff:192.168.0.1/120", "10.10.10.0/24"],
	port: 8080,
	language: "de",
	locale: "de-DE",
	logLevel: ["INFO", "LOG", "WARN", "ERROR"],
	timeFormat: 24,
	units: "metric",

	modules: [
		// ==== System ====
		{ module: "alert" },
		{ module: "updatenotification", position: "top_bar", disabled: true },

		// ==== Uhrzeit ====
		{
			module: "clock",
			position: "top_left",
			config: {
				dateFormat: "dddd, D. MMMM YYYY",
				showWeek: false,
				displayType: "digital",
				timezone: "Europe/Berlin",
			}
		},

		{
			module: 'MMM-Remote-Control',
			// uncomment the following line to show the URL of the remote control on the mirror
			// position: 'bottom_left',
			// you can hide this module afterwards from the remote control itself
			config: {
				apiKey: 'XXXXXXXXXXXX'
			}
		},

		// ==== Hintergrund ====

		/*{
			module: 'MMM-EasyBack',
			position: 'fullscreen_below',
			classes: "stateA",
			config: {
				bgName: "wallpaper.jpg",   // "Example.jpg", the file name of your background image (case sensitive)
				videoName: "",       // "baboon.mp4",         // file name of your local video
				youTubeID: "", //"SkeNMoDlHUU", // "So3vH9FY2H4", // ID from any YouTube video. ID comes after the = sign of YouTube url
				height: "600px",    // your display's resolution in pixels. Enter in config.js
				width: "1024px",     // your display's resolution in pixels. Enter in config.js
			}
		},*/

		// ==== Hintergrund statisch (für Infos) ====
		/*{
		  module: "MMM-BackgroundSlideshow",
		  position: "fullscreen_below",
		  classes: "bg-static stateA",
		  config: {
			imagePaths: ["/home/pi/MagicMirror"],
			validImageFileExtensions: "jpg",
			randomizeImageOrder: false,
			slideshowSpeed: 999999999, // praktisch nie wechseln
			transitionImages: false,
			backgroundSize: "cover",
			backgroundPosition: "center",
			imagePathsRecursive: false
		  }
		},*/

		// ==== Hintergrund Slideshow (für Foto-Modus) ====
		{
		  module: "MMM-BackgroundSlideshow",
		  position: "fullscreen_below",
		  //classes: "bg-slideshow stateB",
		  //classes: "stateB",
		  config: {
			imagePaths: ["/home/pi/icloud/images"],
			validImageFileExtensions: "jpg,png,jpeg",
			randomizeImageOrder: true,
			slideshowSpeed: 999999, // 15 Minuten pro Bild
			transitionImages: false,
			backgroundSize: "cover",
			backgroundPosition: "center",
			imagePathsRecursive: false
		  }
		},


		// ==== Wetter ====
		{
			module: "MMM-Regenradar",
			position: "bottom_left",
			classes: "stateA",
			config: {
				width: "400px",
				height: "auto",
				plz: "85229",
				delay: "70",
				type: "1",
				zoomlvl: "6",
				bar: "0",
				map: "0",
				textcol: "ffffff",
				bgcol: "00000",
				updateInterval: 5
			}
		},

		// ==== Wetter (Open-Meteo) ====
		{
		  module: "weather",
		  position: "top_right",
		  header: "Wetterbericht",
		  classes: "custom-weather stateA",
		  config: {
			weatherProvider: "openmeteo",
			type: "forecast",                 // "current", "forecast" oder "both"
			lat: 48.00000000000000,          // Breitengrad
			lon: 11.00000000000000,          // Längengrad
			roundTemp: false,              // ganze Zahlen
			//showFeelsLike: true,
			//showHumidity: "wind",
			showSun: true,                // Sonnenauf-/untergang
			colored: true,
			updateInterval: 10 * 60 * 1000, // alle 10 Minuten
			units: "metric",
			degreeLabel: true,
			//showPrecipitationAmount: true,
			showPrecipitationProbability: true,
			fade: true,
			fadePoint: 0.3,
			maxNumberOfDays: 4,
			showWindDirection: true,
			animationSpeed: 1000,
			timeFormat: "24",
			lang: "de"
		  }
		},


		// ==== Nachrichten (Tagesschau) ====
		{
			module: "newsfeed",
			position: "bottom_right", // mittiger
			config: {
				feeds: [
					{
						title: "Tagesschau",
						url: "https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml"
					}
				],
				showAsList: true,
				showSourceTitle: true,
				showPublishDate: true,
				updateInterval: 10 * 60 * 1000,
				broadcastNewsFeeds: true,
				broadcastNewsUpdates: true,
				ignoreOldItems: true,
				scrollLength: 1000,
				timeout: 10000,
				wrapTitle: true,
				wrapDescription: true,
				showArticleAs: "list",            // mehrere gleichzeitig
				maxNewsItems: 2                   // <= 2 Schlagzeilen gleichzeitig
			},
			classes: "large stateA" // größere Schrift
		},

		// ==== Müllkalender ====
		{
			module: "calendar",
			header: "Müllabfuhr",
			position: "top_center",
			classes: "custom-calendar stateA",
			config: {
				calendars: [
					{
						symbol: "trash-can",
						url: "YOUR_TRASH_CALENDAR_URL",
						colored: true
					}
				],
				maximumEntries: 4,
				fetchInterval: 6 * 60 * 60 * 1000,
				dateFormat: "dddd, DD.MM.",
				timeFormat: "relative",
				getRelative: 2
			}
		},


		// stateA: infos, stateB: slideshow
		/*{
		  module: "MMM-ModuleScheduler",
		  config: {
			global_schedule: [
			  { from: "0/2 * * * *", to: "1/2 * * * *", groupClass: "stateA" },
			  { from: "1/2 * * * *", to: "0/2 * * * *", groupClass: "stateB" }
			],
			onStartupShow: true
		  }
		}*/

		/*{
		  module: "MMM-ModuleScheduler",
		  config: {
			global_schedule: [
			  // stateA: Infos (1 Minute)
			  {
				from: "0/2 * * * *",
				to: "1/2 * * * *",
				groupClass: "stateA",
				// zusätzlich statisches Hintergrundbild aktivieren
				exec: [
				  {
					notification: "BACKGROUNDSLIDESHOW_URL",
					payload: { url: "/home/pi/MagicMirror/wallpaper.jpg" }
				  }
				]
			  },
			  // stateB: Fotos (1 Minute)
			  {
				from: "1/2 * * * *",
				to: "0/2 * * * *",
				groupClass: "stateB",
				// Slideshow starten
				exec: [
				  {
					notification: "BACKGROUNDSLIDESHOW_URLS",
					payload: { urls: ["/home/pi/icloud/images"] }
				  },
				  {
					notification: "BACKGROUNDSLIDESHOW_PLAY"
				  }
				]
			  }
			],
			onStartupShow: true
		  }
		}*/


		{
		  module: "MMM-ModuleScheduler",
		  config: {
			/*global_schedule: [
			  // ==== STATE A ====
			  // Alle 2 Minuten für 1 Minute: Infos anzeigen
			  {
				from: "0/2 * * * *", // jede gerade Minute
				to: "1/2 * * * *",   // nach 1 Minute
				groupClass: "stateA"
			  },
			  // ==== STATE B ====
			  // Alle 2 Minuten für 1 Minute: Fotos anzeigen
			  {
				from: "1/2 * * * *", // jede ungerade Minute
				to: "0/2 * * * *",   // nach 1 Minute
				groupClass: "stateB"
			  }
			],*/
			  global_schedule: [
			  // ==== STATE A (Infos/Wallpaper) ====
			  // Zeitfenster 1: Minute 0-14 (15 Minuten)
			  {
				from: "0 * * * *",
				to: "15 * * * *",
				groupClass: "stateA"
			  },
			  // Zeitfenster 2: Minute 30-44 (15 Minuten)
			  {
				from: "30 * * * *",
				to: "45 * * * *",
				groupClass: "stateA"
			  },

			  // ==== STATE B (Fotos/Slideshow) ====
			  // Zeitfenster 1: Minute 15-29 (15 Minuten)
			  {
				from: "15 * * * *",
				to: "30 * * * *",
				groupClass: "stateB"
			  },
			  // Zeitfenster 2: Minute 45-59 (15 Minuten)
			  {
				from: "45 * * * *",
				to: "59 * * * *",
				groupClass: "stateB"
			  }
			],

			// ==== NOTIFICATION SCHEDULES ====
			notification_schedule: [
			  // --- STATE A aktiviert: statisches Hintergrundbild ---
			  {
				notification: "BACKGROUNDSLIDESHOW_URLS",
				schedule: "0,30 * * * *", // alle 2 Minuten bei Start von stateA
				payload: {
				  urls: ["modules/MMM-BackgroundSlideshow/wallpaper.jpg"]
				}
			  },
			  // --- STATE B aktiviert: Slideshow starten ---
			  /*{
				notification: "BACKGROUNDSLIDESHOW_URLS",
				schedule: "1/2 * * * *", // alle 2 Minuten bei Start von stateB
				payload: {
				  urls: ["/home/pi/icloud/images"]
				}
			  },*/
			  {
				notification: "BACKGROUNDSLIDESHOW_URLS",
				schedule: "15,45 * * * *",
				payload: {
					urls: []
				}
			  },
			  {
				notification: "BACKGROUNDSLIDESHOW_PAUSE",
				schedule: "15,45 * * * *",
			  }
			],

			// ==== OPTIONALES VERHALTEN ====
			onStartupShow: true
		  }
		}


	]
};


/*************** DO NOT EDIT BELOW ***************/
if (typeof module !== "undefined") { module.exports = config; }

