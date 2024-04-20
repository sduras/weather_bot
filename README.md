There is sophisticated [Open-Meteo API Python Client](https://pypi.org/project/openmeteo-requests/), which allows get weather data from the Open-Meteo Weather API based on Python library **requests**. This client is primarily designed for data-scientists to process weather data. It uses Open-Meteo with cache and retry on error and requires installation of extra libraries such as **requests-cache**, **retry-requests**, **numpy** and **pandas**.

I personally do not need this functionality, so I wrote a script for this task, which requires only [aiohttp](https://pypi.org/project/aiohttp/), asynchronous HTTP client/server framework for asyncio and Python. This script offers a simpler solution for those who just want clear, concise weather information delivered conveniently through Telegram messages.

The program pulls weather data from the Deutscher Wetterdienst (DWD), [Deutscher Wetterdienst (DWD)](https://www.dwd.de), the trusted German weather service. This data is then formatted into clear, easy-to-understand notifications delivered directly to Telegram. Program uses [Vercel serverless functions](https://vercel.com/docs/functions/runtimes/python) and [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/) for notifications. The resulting weather bot provides detailed information for today and tomorrow, including:

- Current weather conditions (e.g., clear, partly cloudy, rainy)
- Temperature range and apparent temperature
- Wind speed and direction
- Sunshine & daylight duration
- Precipitation amount
- Tomorrow's weather with a comparison to today
- Moon phase (e.g., new moon, waxing crescent)

The working prototype is [here](https://t.me/slw287r_bot). Currently, it shows weather for 🇺🇦 Dnipro, but can be configured for a different location.
