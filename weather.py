"""Weather Data CLI.

A command-line application that fetches and displays current weather data
for any city using the OpenWeatherMap API.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any

from dotenv import load_dotenv
import requests

# Ensure UTF-8 output encoding across all operating systems (e.g. for the '°' symbol)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# OpenWeatherMap API Current Weather endpoint
API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
REQUEST_TIMEOUT = 10  # Request timeout in seconds


def get_api_key() -> str:
    """Retrieve the OpenWeatherMap API key from environment variables or .env file.

    Loads key-value pairs from a local .env file if available, then reads
    the OPENWEATHER_API_KEY environment variable. If the key is missing
    or set to a default placeholder, displays clear setup instructions and exits.

    Returns:
        str: A valid, non-empty OpenWeatherMap API key string.
    """
    load_dotenv()
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()

    placeholders = {
        "",
        "your_api_key_here",
        "your_openweather_api_key_here",
        "replace_with_your_api_key",
    }

    if api_key.lower() in placeholders:
        print(
            "\n"
            "============================================================\n"
            "  Error: OpenWeatherMap API key is missing or not configured\n"
            "============================================================\n"
            "To use this CLI, please configure your API key:\n\n"
            "  1. Copy '.env.example' to create a '.env' file:\n"
            "       Windows (cmd/powershell): copy .env.example .env\n"
            "       macOS/Linux:              cp .env.example .env\n\n"
            "  2. Open '.env' in your text editor and add your key:\n"
            "       OPENWEATHER_API_KEY=your_actual_key_here\n\n"
            "  3. Alternatively, export it directly in your terminal:\n"
            "       PowerShell:  $env:OPENWEATHER_API_KEY=\"your_key_here\"\n"
            "       Bash/Zsh:    export OPENWEATHER_API_KEY=\"your_key_here\"\n\n"
            "Need an API key? Get one for free at:\n"
            "  https://home.openweathermap.org/users/sign_up\n"
            "============================================================\n",
            file=sys.stderr,
        )
        sys.exit(1)

    return api_key


def fetch_weather(city: str, api_key: str) -> dict[str, Any] | None:
    """Fetch current weather data for a given city from OpenWeatherMap.

    Args:
        city: Name of the city (e.g., 'London' or 'New Delhi').
        api_key: A valid OpenWeatherMap API key.

    Returns:
        dict[str, Any] | None: Raw JSON dictionary from the API if successful,
        or None if an error occurs.
    """
    cleaned_city = city.strip()
    if not cleaned_city:
        print("Error: City name cannot be empty. Please enter a valid city name.")
        return None

    params = {
        "q": cleaned_city,
        "appid": api_key,
        "units": "metric",
    }

    try:
        response = requests.get(API_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)

        # Successful request
        if response.status_code == 200:
            try:
                data: dict[str, Any] = response.json()
                return data
            except ValueError:
                print("Error: Received malformed JSON response from OpenWeatherMap.")
                return None

        # Handle specific HTTP error status codes gracefully
        if response.status_code == 401:
            print(
                "Error (HTTP 401 Unauthorized): Invalid API key.\n"
                "Please verify your OPENWEATHER_API_KEY in your .env file or environment."
            )
            return None

        if response.status_code == 404:
            print(
                f"Error (HTTP 404 Not Found): City '{cleaned_city}' was not found.\n"
                "Please check the spelling and try again."
            )
            return None

        if response.status_code == 429:
            print(
                "Error (HTTP 429 Too Many Requests): API rate limit exceeded.\n"
                "OpenWeatherMap free tier allows 60 calls/minute. Please wait and try again."
            )
            return None

        # Any other unexpected HTTP status
        print(
            f"Error: API returned unexpected status code {response.status_code} "
            f"({response.reason})."
        )
        return None

    # Handle network and connection exceptions
    except requests.exceptions.ConnectionError:
        print(
            "Error: Network connection error. Unable to reach OpenWeatherMap servers.\n"
            "Please check your internet connection."
        )
        return None
    except requests.exceptions.Timeout:
        print(
            f"Error: Connection timed out after {REQUEST_TIMEOUT} seconds while contacting OpenWeatherMap.\n"
            "Please try again in a few moments."
        )
        return None
    except requests.exceptions.RequestException as exc:
        print(f"Error: An unexpected network error occurred: {exc}")
        return None


def parse_weather(data: dict[str, Any]) -> dict[str, Any] | None:
    """Extract and format essential weather fields from the raw API response.

    Extracts:
        - City name and country code
        - Weather condition description
        - Current, feels-like, min, and max temperatures (°C)
        - Humidity percentage and atmospheric pressure (hPa)
        - Wind speed (m/s)
        - Sunrise and sunset times converted to the city's local time

    Args:
        data: Raw JSON dictionary returned by OpenWeatherMap.

    Returns:
        dict[str, Any] | None: A clean dictionary with parsed values,
        or None if required fields are missing or invalid.
    """
    try:
        city_name = data["name"]
        sys_data = data.get("sys", {})
        country = sys_data.get("country", "")

        main_data = data["main"]
        temperature = float(main_data["temp"])
        feels_like = float(main_data["feels_like"])
        temp_min = float(main_data["temp_min"])
        temp_max = float(main_data["temp_max"])
        humidity = int(main_data["humidity"])
        pressure = int(main_data["pressure"])

        wind_data = data.get("wind", {})
        wind_speed = float(wind_data.get("speed", 0.0))

        weather_list = data.get("weather", [])
        if not weather_list or not isinstance(weather_list, list):
            raise KeyError("weather")
        condition = weather_list[0].get("description", "Unknown").capitalize()

        # OpenWeatherMap provides 'timezone' as an offset in seconds from UTC
        timezone_offset = data.get("timezone", 0)
        local_timezone = timezone(timedelta(seconds=timezone_offset))

        sunrise_timestamp = sys_data.get("sunrise")
        sunset_timestamp = sys_data.get("sunset")

        sunrise_time = (
            datetime.fromtimestamp(sunrise_timestamp, tz=local_timezone).strftime("%I:%M %p")
            if sunrise_timestamp
            else "N/A"
        )
        sunset_time = (
            datetime.fromtimestamp(sunset_timestamp, tz=local_timezone).strftime("%I:%M %p")
            if sunset_timestamp
            else "N/A"
        )

        return {
            "city": city_name,
            "country": country,
            "condition": condition,
            "temperature": temperature,
            "feels_like": feels_like,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "sunrise": sunrise_time,
            "sunset": sunset_time,
        }

    except (KeyError, IndexError, TypeError, ValueError) as exc:
        print(f"Error: Failed to process weather data due to missing or invalid fields ({exc}).")
        return None


def display_weather(info: dict[str, Any]) -> None:
    """Print weather information in a clean, neatly aligned block.

    Args:
        info: Structured dictionary containing parsed weather metrics.
    """
    location = f"{info['city']}, {info['country']}" if info.get("country") else info["city"]

    separator = "=" * 40
    print(separator)
    print(f"Weather in {location}")
    print(separator)
    print(f"Condition   : {info['condition']}")
    print(f"Temperature : {info['temperature']:.1f} °C (feels like {info['feels_like']:.1f} °C)")
    print(f"Min / Max   : {info['temp_min']:.1f} °C / {info['temp_max']:.1f} °C")
    print(f"Humidity    : {info['humidity']}%")
    print(f"Wind Speed  : {info['wind_speed']:.1f} m/s")
    print(f"Pressure    : {info['pressure']} hPa")
    print(f"Sunrise     : {info['sunrise']}")
    print(f"Sunset      : {info['sunset']}")
    print(separator)


def process_city_weather(city: str, api_key: str) -> bool:
    """Helper function to fetch, parse, and display weather for a city.

    Args:
        city: Name of the city to look up.
        api_key: OpenWeatherMap API key.

    Returns:
        bool: True if lookup and display were successful, False otherwise.
    """
    data = fetch_weather(city, api_key)
    if data is None:
        return False

    info = parse_weather(data)
    if info is None:
        return False

    display_weather(info)
    return True


def parse_arguments() -> argparse.Namespace:
    """Configure and parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog="weather.py",
        description="Weather Data CLI: Look up current weather conditions for any city.",
        epilog="Examples:\n"
               "  python weather.py London\n"
               "  python weather.py --city \"New Delhi\"\n"
               "  python weather.py (starts interactive lookup loop)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "positional_city",
        nargs="?",
        metavar="CITY",
        help="City name to query (e.g. 'London' or 'Tokyo').",
    )
    parser.add_argument(
        "-c",
        "--city",
        dest="flag_city",
        metavar="CITY",
        help="City name to query (e.g. --city 'New Delhi').",
    )
    return parser.parse_args()


def interactive_loop(api_key: str) -> None:
    """Run an interactive prompt loop allowing repeated city weather lookups.

    Args:
        api_key: OpenWeatherMap API key.
    """
    print("\n" + "=" * 40)
    print("      Welcome to Weather Data CLI      ")
    print("=" * 40)
    print("Type a city name to view its weather.")
    print("Type 'quit' or 'exit' (or press Ctrl+C) to exit.\n")

    while True:
        try:
            city_input = input("Enter city name: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Weather Data CLI. Goodbye!")
            break

        if not city_input:
            print("City name cannot be empty. Please enter a city name.\n")
            continue

        if city_input.lower() in {"quit", "exit", "q"}:
            print("Exiting Weather Data CLI. Goodbye!")
            break

        process_city_weather(city_input, api_key)
        print()  # Add an empty line between subsequent queries


def main() -> None:
    """Main CLI entry point."""
    args = parse_arguments()

    # Determine city from flag or positional argument
    if args.flag_city is not None:
        city = args.flag_city
    elif args.positional_city is not None:
        city = args.positional_city
    else:
        city = None

    # Validate that an API key is present before proceeding
    api_key = get_api_key()

    if city is not None:
        # One-shot command-line query
        success = process_city_weather(city, api_key)
        if not success:
            sys.exit(1)
    else:
        # Interactive mode when no city argument is supplied
        interactive_loop(api_key)


if __name__ == "__main__":
    main()
