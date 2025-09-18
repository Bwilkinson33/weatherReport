import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, date, timedelta

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
    Fetches the hourly weather forecast for tomorrow from the Open-Meteo API.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation_probability,weathercode",
        "timezone": "America/New_York",
        "forecast_days": 2
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "hourly" not in data:
        return "Could not retrieve hourly forecast."

    # Process hourly data for tomorrow
    hourly_data = data["hourly"]
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    tomorrow_forecast = {
        "time": [],
        "temperature_2m": [],
        "precipitation_probability": [],
        "weathercode": []
    }

    for i, time_str in enumerate(hourly_data["time"]):
        if time_str.startswith(tomorrow):
            tomorrow_forecast["time"].append(time_str)
            tomorrow_forecast["temperature_2m"].append(hourly_data["temperature_2m"][i])
            tomorrow_forecast["precipitation_probability"].append(hourly_data["precipitation_probability"][i])
            tomorrow_forecast["weathercode"].append(hourly_data["weathercode"][i])

    if not tomorrow_forecast["time"]:
         return "Could not find forecast data for tomorrow."

    return tomorrow_forecast


def generate_weather_report(forecast):
    """
    Generates a weather report by summarizing hourly data using the Google Generative AI API.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "GEMINI_API_KEY not found in environment variables."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

    # Format the hourly data into a string for the prompt
    hourly_data_str = "Time | Temp (°C) | Rain Chance (%) | Condition\n"
    hourly_data_str += "---|---|---|---\n"
    for i in range(len(forecast["time"])):
        time = forecast["time"][i].split("T")[1]
        temp = forecast["temperature_2m"][i]
        precip_prob = forecast["precipitation_probability"][i]
        weather_desc = WMO_CODES.get(forecast["weathercode"][i], "Unknown")
        hourly_data_str += f"{time} | {temp}°C | {precip_prob}% | {weather_desc}\n"

    prompt = f"""
    You are a creative weather forecaster. Your task is to generate a fun, emoji-filled weather report for the day, with a style that would appeal to college kids. It should sound like a normal person wrote it, not an AI.

    Here is the detailed hourly forecast data for the day:
    {hourly_data_str}

    Based on this data, please do the following:
    1. Summarize the overall weather for the day. Is it mostly sunny, cloudy, rainy?
    2. Find the highest and lowest temperatures for the day from the hourly data.
    3. Convert all temperatures to Fahrenheit for the final report.
    4. Mention the chance of rain if it's significant (ONLY if the chance is above 50%) at any point during the day.
    5. Write the report in a fun, creative, and conversational tone, using plenty of relevant emojis. Do not use hashtags.

    Here is an example of the desired *style* (do not copy the content, just the gist of it):
    "Today’s track conditions :racing_car: :dash: are extremely dry :dromedary_camel: with a whopping 0% rain coverage. :potted_plant: :seedling: Medium tyres :wheel: definitely reccomended to combat today’s temps climbing from a low of 67° to a high of 84°. :hot_face: :fire: It’s also very sunny. All day. So much sun. :sunny: :sunny: :sunny:"

    Now, generate the new report based on the provided hourly data. Try to keep it around the length of the example, maybe two or three sentences longer.
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
