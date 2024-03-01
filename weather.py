import asyncio
import aiohttp
import datetime as dt
from datetime import datetime, timedelta, timezone
import math
import traceback
import locale

async def fetch_weather_data():
    async with aiohttp.ClientSession() as session:
        params = {
            "latitude": 48.5,
            "longitude": 34.9,
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "precipitation", "rain", "showers", "snowfall", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset", "daylight_duration", "sunshine_duration", "uv_index_max", "uv_index_clear_sky_max", "precipitation_sum", "rain_sum", "showers_sum", "snowfall_sum", "precipitation_hours", "precipitation_probability_max", "wind_speed_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum"],
            "timezone": "Europe/Berlin",
            "past_days": 1,
            "forecast_days": 3
        }
        async with session.get("https://api.open-meteo.com/v1/dwd-icon", params=params) as weather_data_raw:
            weather = await weather_data_raw.json()
            # print(weather)
            return await weather_data_raw.json()

async def interpolate_wind_description(wind_value, wind_mapping):
    keys = sorted(wind_mapping.keys())
    for i in range(len(keys)-1):
        if keys[i] <= wind_value <= keys[i+1]:
            return wind_mapping[keys[i]] + " -> " + wind_mapping[keys[i+1]]
    return wind_mapping.get(wind_value, "Unknown")

async def moon(): 
    now = datetime.now(timezone.utc)
    epoch = datetime(2000, 1, 6, 18, 14, 0, tzinfo=timezone.utc)
    moon_cycle = 29.53058867
    delta_since_epoch = now - epoch
    days_since_epoch = delta_since_epoch.total_seconds() / 86400
    phase_angle = 2 * math.pi * (days_since_epoch % moon_cycle) / moon_cycle
    if 0 <= phase_angle <= math.pi / 14:
        phase = "🌑 новий Місяць"
    elif math.pi / 14 < phase_angle <= math.pi / 14 * 3:
        phase = "🌒 молодий Місяць"
    elif math.pi / 14 * 3 < phase_angle <= math.pi / 14 * 5:
        phase = "🌓 перша чверть"
    elif math.pi / 14 * 5 < phase_angle <= math.pi / 14 * 9:
        phase = "🌔 прибуваючий Місяць"
    elif math.pi / 14 * 9 < phase_angle <= math.pi / 14 * 10:
        phase = "🌕 повний Місяць"
    elif math.pi / 14 * 10 < phase_angle <= math.pi / 14 * 12:
        phase = "🌖 спадаючий Місяць"
    elif math.pi / 14 * 12 < phase_angle <= math.pi / 14 * 13:
        phase = "🌗 остання чверть"
    else:
        phase = "🌘 cтарий Місяць"

    return phase

async def hPa_to_mmHg(pressure_hPa):
    conversion_factor = 0.7500616827
    pressure_mmHg = round(pressure_hPa * conversion_factor, 2)
    return pressure_mmHg

async def weather_reports():
    current_data = await fetch_weather_data()
    current_weather = current_data['current']
    datetime_str = current_weather['time']
    date_str, time_str = datetime_str.split('T')
    date_str = date_str.strip('{}')
    time_str = time_str.strip('{}')
    locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')
    date_obj = dt.datetime.strptime(date_str, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%A').lstrip('0')
    current_time = time_str
    current_date = formatted_date
    current_temperature = int(current_weather['temperature_2m'])
    current_apparent_temperature = int(current_weather['apparent_temperature'])
    current_pressure = int(current_weather['surface_pressure'])
    pressure_hPa = current_pressure
    current_pressure_mmHg = await hPa_to_mmHg(pressure_hPa)
    current_pressure = int(current_pressure_mmHg)
    if current_pressure < 740:
        description = "(⚠️  низький)"
    elif current_pressure <= 770:
        description = "(нормальний)"
    else:
        description = "(високий)"
    current_pressure = f"{current_pressure} мм. {description}"
    weather_code_mapping = {
        0.0: "☀️   ясне небо",
        1.0: "☀️   в основному ясно",
        2.0: "🌤  часткова хмарність",
        3.0: "🌥  хмарно",
        45.0: "🌫  туман",
        48.0: "❄️   паморозь",
        51.0: "🌫️  легка мряка",
        53.0: "🔲  помірна мряка",
        55.0: "🔳  повна мряка",
        56.0: "💧  крижаний дощ",
        57.0: "💦  сильний крижаний дощ",
        61.0: "🌧️  невеликий дощ",
        63.0: "🌧️  помірний дощ",
        65.0: "💧  сильний дощ",
        66.0: "⛸️   ожеледиця",
        67.0: "🤸  сильна ожеледиця",
        71.0: "❄️   невеликий снігопад",
        73.0: "❄️   середній снігопад",
        75.0: "❄️   сильний снігопад",
        77.0: "🧊  град",
        80.0: "🌨️  легкий дощ зі снігом",
        81.0: "🌨️  дощ зі снігом",
        82.0: "☂️   сильний дощ зі снігом",
        85.0: "💨  легкі хуртовини",
        86.0: "🌪️  сильні хуртовини",
        95.0: "⚡ гроза",
        96.0: "⛈️   гроза з градом",
        99.0: "⛈️   гроза з важким градом"
    }
    current_weather_code = int(current_weather['weather_code'])
    current_weather_description = weather_code_mapping.get( current_weather_code, "Unknown")
    wind_mapping = {
    0.0: "північний",
    45.0: "північно-східний",
    90.0: "східний",
    135.0: "південно-східний",
    180.0: "південний",
    225.0: "південно-західний",
    270.0: "західний",
    315.0: "північно-західний",
    360.0: "північний"
    }
    wind_speed_mapping = {
    (0.0, 0.3 * 3.6): "🦋 штиль",
    (0.4 * 3.6, 1.5 * 3.6): "тихий",
    (1.6 * 3.6, 3.4 * 3.6): "легкий",
    (3.5 * 3.6, 5.4 * 3.6): "слабкий",
    (5.5 * 3.6, 7.9 * 3.6): "помірний", 
    (8.0 * 3.6, 10.7 * 3.6): "свіжий",
    (10.8 * 3.6, 13.8 * 3.6): "💨  сильний",
    (13.9 * 3.6, 17.1 * 3.6): "⚠️   дуже сильний",
    (17.2 * 3.6, 20.7 * 3.6): "⚠️   надзвичайно сильний",
    (20.8 * 3.6, 24.4 * 3.6): "🔴  шторм!",
    (24.5 * 3.6, 28.4 * 3.6): "🔴 сильний шторм",
    (28.5 * 3.6, 32.6 * 3.6): "🔴 страшний шторм",
    (32.7 * 3.6, float('inf')): "🙀 ураган",
    }

    current_wind_speed = int(current_weather['wind_speed_10m'])
    current_wind_speed_description = next((description for speed_range, description in wind_speed_mapping.items() if speed_range[0] <= current_wind_speed < speed_range[1]), "Unknown")  
    current_wind_direction = int(current_weather['wind_direction_10m'])
    current_wind_description = await interpolate_wind_description(current_wind_direction, wind_mapping)

    daily_data = await fetch_weather_data()
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    # yesterday = today - timedelta(days=1)
    seconds_per_hour = 3600
    seconds_per_minute = 60
    # yesterday_data = daily_data["daily"]['time'].index(yesterday.strftime("%Y-%m-%d"))
    today_data = daily_data["daily"]['time'].index(today.strftime("%Y-%m-%d"))
    tomorrow_data = daily_data["daily"]['time'].index(tomorrow.strftime("%Y-%m-%d"))
    today_sunshine = daily_data["daily"]["sunshine_duration"][today_data] / seconds_per_hour
    tomorrow_sunshine = daily_data["daily"]["sunshine_duration"][tomorrow_data] / seconds_per_hour
    today_daylight = daily_data["daily"]["daylight_duration"][today_data] / seconds_per_hour
    today_daylight_rounded = int(today_daylight)
    tomorrow_daylight = daily_data["daily"]["daylight_duration"][tomorrow_data] / seconds_per_hour
    tomorrow_daylight_rounded = int(tomorrow_daylight)
    daylight_difference = ((tomorrow_daylight * seconds_per_hour) - (today_daylight * seconds_per_hour)) // seconds_per_minute
    direction = "більше" if daylight_difference > 0 else "менше"
    today_code = daily_data["daily"]["weather_code"][today_data]
    tomorrow_code =  daily_data["daily"]["weather_code"][tomorrow_data]
    today_weather_description = weather_code_mapping.get(today_code, "Unknown")
    tomorrow_weather_description = weather_code_mapping.get(tomorrow_code, "Unknown")
    today_wind = daily_data["daily"]["wind_direction_10m_dominant"][today_data]
    tomorrow_wind = daily_data["daily"]["wind_direction_10m_dominant"][tomorrow_data] 
    today_wind_description = await interpolate_wind_description(today_wind, wind_mapping)
    tomorrow_wind_description = await interpolate_wind_description(tomorrow_wind, wind_mapping)
    today_wind_description = await interpolate_wind_description(today_wind, wind_mapping)
    tomorrow_wind_description = await interpolate_wind_description(tomorrow_wind, wind_mapping)
    today_wind_speed = int(daily_data["daily"]["wind_speed_10m_max"][today_data])
    tomorrow_wind_speed = int(daily_data["daily"]["wind_speed_10m_max"][tomorrow_data])
    today_wind_speed_description = next((description for speed_range, description in wind_speed_mapping.items() if speed_range[0] <= today_wind_speed < speed_range[1]), "Unknown")  
    tomorrow_wind_speed_description = next((description for speed_range, description in wind_speed_mapping.items() if speed_range[0] <= tomorrow_wind_speed < speed_range[1]), "Unknown")
    moon_phase = await moon()
    today_temp_max = daily_data["daily"]["temperature_2m_max"][today_data]
    today_temp_max_rounded = int(today_temp_max)
    today_temp_min = daily_data["daily"]["temperature_2m_min"][today_data]
    today_temp_min_rounded = int(today_temp_min) 
    today_apparent_temp = daily_data["daily"]["apparent_temperature_max"][today_data]
    today_apparent_temp_rounded = int(today_apparent_temp)
    tomorrow_temp_max = daily_data["daily"]["temperature_2m_max"][tomorrow_data]
    tomorrow_temp_max_rounded = int(tomorrow_temp_max)
    tomorrow_temp_min = daily_data["daily"]["temperature_2m_min"][tomorrow_data]
    tomorrow_temp_min_rounded = int(tomorrow_temp_min)
    tomorrow_apparent_temp = daily_data["daily"]["apparent_temperature_max"][tomorrow_data]
    tomorrow_apparent_temp_rounded = int(tomorrow_apparent_temp)
    today_precipitation = int(daily_data["daily"]["precipitation_sum"][today_data])
    tomorrow_precipitation = int(daily_data["daily"]["precipitation_sum"][tomorrow_data])

    precipitation_mapping = {
    (0.0, 0.1): "без опадів",
    (0.2, 2.5): "☂️   невеликі опади",
    (2.6, 10.0): "️☔  середні опади",
    (11.0, 25.0): "☔  cильні опади",
    (26.0, 50.0): "⛈️   злива",
    (51.0, float('inf')): "⚠️  екстремальні опади",
}

    today_precipitation_description = next((description for speed_range, description in precipitation_mapping.items() if speed_range[0] <= today_precipitation < speed_range[1]), "Unknown")  
    tomorrow_precipitation_description = next((description for speed_range, description in precipitation_mapping.items() if speed_range[0] <= tomorrow_precipitation < speed_range[1]), "Unknown")

    today_report = f"Зараз <b>{current_date}, {current_time}</b>. Температура {current_temperature}°C, відчувається як {current_apparent_temperature}°C. Атмосферний тиск {current_pressure}. Протягом дня {today_precipitation_description}. Вітер {current_wind_description}, {current_wind_speed_description}, {current_weather_description}. Тривалість світлового дня {today_daylight_rounded} год., {moon_phase}."

    tomorrow_report = f"<b>Завтра</b> {tomorrow_weather_description}, {tomorrow_precipitation_description}. Tемпература від {tomorrow_temp_min_rounded} до {tomorrow_temp_max_rounded}°C. Вітер {tomorrow_wind_speed_description}, {tomorrow_wind_description}. Tривалість світлового дня на {abs(daylight_difference):.0f} хв. {direction}, ніж сьогодні."

    print(today_report, tomorrow_report)
    return today_report, tomorrow_report


def get_weather_data_sync():
    event_loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(event_loop)
        formatted_data = event_loop.run_until_complete(weather_reports())
        return formatted_data
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error: {e}")
    finally:
        event_loop.close()

if __name__ == "__main__":
    asyncio.run(weather_reports())
