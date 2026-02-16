#!/usr/bin/env python3
"""
Weather Dashboard
=================
Current weather, hourly forecast, multi-day forecast, and city
comparison using the free Open-Meteo API (no API key needed).

Usage:
    python weather_dashboard.py             # Interactive mode
    python weather_dashboard.py --help      # Show help

Learn more: https://raccoonette.gumroad.com/l/Python-for-automating-every-day-tasks
"""

import sys
from datetime import datetime

import requests


class WeatherDashboard:
    """Weather data powered by the free Open-Meteo API."""

    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    WEATHER_CODES = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm + hail", 99: "Thunderstorm + heavy hail",
    }

    COMPASS = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ]

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    def get_coordinates(self, city: str):
        """Return (lat, lon, display_name) or None."""
        try:
            resp = requests.get(
                self.GEOCODING_URL,
                params={"name": city, "count": 1, "language": "en", "format": "json"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            if "results" in data and data["results"]:
                r = data["results"][0]
                return r["latitude"], r["longitude"], f"{r['name']}, {r.get('country', '')}"
        except requests.RequestException as exc:
            print(f"Geocoding error: {exc}")
        return None

    def get_weather(self, lat: float, lon: float) -> dict:
        params = {
            "latitude": lat, "longitude": lon,
            "current": [
                "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                "precipitation", "weather_code", "wind_speed_10m", "wind_direction_10m",
            ],
            "hourly": ["temperature_2m", "precipitation_probability", "weather_code"],
            "daily": [
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "precipitation_probability_max",
            ],
            "timezone": "auto", "forecast_days": 7,
        }
        try:
            resp = requests.get(self.WEATHER_URL, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            print(f"Weather API error: {exc}")
            return None

    def _desc(self, code: int) -> str:
        return self.WEATHER_CODES.get(code, f"Unknown ({code})")

    def _wind_dir(self, deg: float) -> str:
        return self.COMPASS[round(deg / 22.5) % 16]

    # ------------------------------------------------------------------
    # Display methods
    # ------------------------------------------------------------------

    def current(self, city: str):
        coords = self.get_coordinates(city)
        if not coords:
            return
        lat, lon, name = coords
        w = self.get_weather(lat, lon)
        if not w:
            return
        c = w["current"]
        print(f"\nCurrent Weather for {name}")
        print("=" * 50)
        print(f"Conditions:  {self._desc(c['weather_code'])}")
        print(f"Temperature: {c['temperature_2m']} C (feels like {c['apparent_temperature']} C)")
        print(f"Humidity:    {c['relative_humidity_2m']}%")
        print(f"Wind:        {c['wind_speed_10m']} km/h {self._wind_dir(c['wind_direction_10m'])}")
        if c.get("precipitation", 0) > 0:
            print(f"Precipitation: {c['precipitation']} mm")

    def forecast(self, city: str, days: int = 5):
        coords = self.get_coordinates(city)
        if not coords:
            return
        lat, lon, name = coords
        w = self.get_weather(lat, lon)
        if not w:
            return
        d = w["daily"]
        print(f"\n{days}-Day Forecast for {name}")
        print("=" * 60)
        for i in range(min(days, len(d["time"]))):
            dt = datetime.strptime(d["time"][i], "%Y-%m-%d").strftime("%a, %b %d")
            cond = self._desc(d["weather_code"][i])
            print(f"\n{dt}")
            print(f"  {cond}")
            print(f"  High: {d['temperature_2m_max'][i]} C  Low: {d['temperature_2m_min'][i]} C")
            print(f"  Precipitation chance: {d['precipitation_probability_max'][i]}%")

    def hourly(self, city: str, hours: int = 12):
        coords = self.get_coordinates(city)
        if not coords:
            return
        lat, lon, name = coords
        w = self.get_weather(lat, lon)
        if not w:
            return
        h = w["hourly"]
        now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
        start = next((i for i, t in enumerate(h["time"]) if t >= now_str), 0)
        print(f"\nHourly Forecast for {name} (next {hours} hours)")
        print("=" * 60)
        print(f"{'Time':<10} {'Temp':<8} {'Precip%':<9} Conditions")
        print("-" * 60)
        for i in range(start, min(start + hours, len(h["time"]))):
            t = datetime.strptime(h["time"][i], "%Y-%m-%dT%H:%M").strftime("%H:%M")
            print(f"{t:<10} {h['temperature_2m'][i]:>5.1f} C  {h['precipitation_probability'][i]:>5}%    {self._desc(h['weather_code'][i])}")

    def compare(self, cities: list):
        print("\nWeather Comparison")
        print("=" * 70)
        print(f"{'City':<25} {'Temp':<10} {'Humidity':<10} Conditions")
        print("-" * 70)
        for city in cities:
            coords = self.get_coordinates(city)
            if not coords:
                continue
            lat, lon, name = coords
            w = self.get_weather(lat, lon)
            if not w:
                continue
            c = w["current"]
            label = (name[:23] + "..") if len(name) > 25 else name
            print(f"{label:<25} {c['temperature_2m']:>6.1f} C  {c['relative_humidity_2m']:>6}%    {self._desc(c['weather_code'])}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    dash = WeatherDashboard()
    print("Weather Dashboard  (free Open-Meteo API)")
    print("=" * 50)
    print("Commands: current, forecast, hourly, compare, quit\n")

    while True:
        try:
            parts = input(">>> ").strip().split()
            if not parts:
                continue
            cmd = parts[0].lower()
            if cmd in ("quit", "exit"):
                break
            elif cmd == "current" and len(parts) >= 2:
                dash.current(" ".join(parts[1:]))
            elif cmd == "forecast" and len(parts) >= 2:
                dash.forecast(" ".join(parts[1:]))
            elif cmd == "hourly" and len(parts) >= 2:
                dash.hourly(" ".join(parts[1:]))
            elif cmd == "compare" and len(parts) >= 3:
                dash.compare(parts[1:])
            else:
                print("Try: current <city>, forecast <city>, hourly <city>, compare <c1> <c2>")
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
