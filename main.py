import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# WMO Weather interpretation codes
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light intensity",
    53: "Drizzle: Moderate intensity",
    55: "Drizzle: Dense intensity",
    56: "Freezing Drizzle: Light intensity",
    57: "Freezing Drizzle: Dense intensity",
    61: "Rain: Slight intensity",
    63: "Rain: Moderate intensity",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light intensity",
    67: "Freezing Rain: Heavy intensity",
    71: "Snow fall: Slight intensity",
    73: "Snow fall: Moderate intensity",
    75: "Snow fall: Heavy intensity",
    77: "Snow grains",
    80: "Rain showers: Slight intensity",
    81: "Rain showers: Moderate intensity",
    82: "Rain showers: Violent intensity",
    85: "Snow showers: Slight intensity",
    86: "Snow showers: Heavy intensity",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather_forecast(latitude, longitude):
    """
    Fetches the weather forecast from the Open-Meteo API.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "America/New_York",
        "forecast_days": 2
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "daily" not in data:
        return "Could not retrieve daily forecast."

    # Extract tomorrow's forecast data
    tomorrow_data = {
        "date": data["daily"]["time"][1],
        "weather_code": data["daily"]["weathercode"][1],
        "temp_max": data["daily"]["temperature_2m_max"][1],
        "temp_min": data["daily"]["temperature_2m_min"][1],
        "precipitation": data["daily"]["precipitation_sum"][1]
    }
    return tomorrow_data


def generate_weather_report(forecast):
    """
    Generates a weather report using the Google Generative AI API.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "GEMINI_API_KEY not found in environment variables."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

    weather_description = WMO_CODES.get(forecast["weather_code"], "Unknown weather code")

    prompt = f"""
    Generate a creative and emoji-filled weather report for tomorrow, in a fun themed style that would be good with college kids. also convert to farenheit for the actual response. It should sound like a normal person wrote it as well so not too ai generated.

    The date is {forecast['date']}.

    The weather condition is: {weather_description}.

    The maximum temperature will be {forecast['temp_max']}°C.

    The minimum temperature will be {forecast['temp_min']}°C.

    The total precipitation will be {forecast['precipitation']}mm.



    Here is an example of the style I want, it doesnt have to be racing themed, just get the vibes right, no hashtags:

    "Today’s track conditions :racing_car: :dash: are extremely dry :dromedary_camel: with a whopping 0% rain coverage. :potted_plant:  :seedling:  Medium tyres :wheel: definitely reccomended to combat today’s temps climbing from a low of 67° to a high of 84°. :hot_face: :fire: It’s also very sunny. All day. So much sun. :sunny: :sunny: :sunny:"



    Please generate a new report in this style, using the provided weather data. Be creative and use lots of emojis.
    """

    response = model.generate_content(prompt)
    return response.text

def generate_mock_weather_report(forecast):
    """
    Generates a mock weather report without calling the AI API.
    """
    weather_description = WMO_CODES.get(forecast["weather_code"], "Unknown weather code")
    report = f"""
    Here is the weather report for {forecast['date']}:
    - Weather: {weather_description}
    - High: {forecast['temp_max']}°C
    - Low: {forecast['temp_min']}°C
    - Precipitation: {forecast['precipitation']}mm
    """
    return report

def send_to_discord(report):
    """
    Sends the weather report to a Discord channel using a webhook.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL not found in environment variables.")
        return

    data = {"content": report}
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("Successfully sent report to Discord.")
    else:
        print(f"Failed to send report to Discord. Status code: {response.status_code}")


def main():
    """
    Main function to run the weather report generator.
    """
    load_dotenv()

    # Coordinates for Georgia Institute of Technology
    # As found from google search: 33.776° N, 84.396° W
    latitude = 33.776
    longitude = -84.396

    forecast = get_weather_forecast(latitude, longitude)
    if isinstance(forecast, str):
        print(forecast)
        return

    # The script is now set to use the AI-generated report by default.
    # If you want to use the mock report for testing, comment out the following line
    # and uncomment the line after it.
    report = generate_weather_report(forecast)
    # report = generate_mock_weather_report(forecast)

    send_to_discord(report)


if __name__ == "__main__":
    main()
